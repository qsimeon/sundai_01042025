"""
GCP Secret Manager Integration

Transparently loads secrets from GCP Secret Manager when running on GCP.
Automatically falls back to environment variables (.env) for local development.

This module monkey-patches os.getenv() to first check GCP Secret Manager,
enabling zero-code changes to existing applications.
"""

import os
import sys
from functools import lru_cache
from typing import Optional


# Original os.getenv function - save before monkey-patching
_original_getenv = os.getenv

# Cache for secrets to avoid repeated API calls
_secret_cache = {}


def _is_running_on_gcp() -> bool:
    """
    Detect if running on GCP by checking metadata server.

    Returns:
        bool: True if running on GCP, False otherwise
    """
    try:
        import requests
        # GCP metadata server is only accessible from GCP instances
        # Use a short timeout since this will hang if not on GCP
        response = requests.get(
            "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/email",
            headers={"Metadata-Flavor": "Google"},
            timeout=0.1
        )
        return response.status_code == 200
    except Exception:
        return False


def _get_secret_from_gcp(secret_name: str) -> Optional[str]:
    """
    Fetch a secret from GCP Secret Manager.

    Args:
        secret_name: Name of the secret (e.g., 'TELEGRAM_BOT_TOKEN')

    Returns:
        str: Secret value if found, None otherwise
    """
    # Check cache first
    if secret_name in _secret_cache:
        return _secret_cache[secret_name]

    try:
        from google.cloud import secretmanager
        import google.auth

        # Get GCP project ID from metadata server
        import requests
        response = requests.get(
            "http://metadata.google.internal/computeMetadata/v1/project/project-id",
            headers={"Metadata-Flavor": "Google"},
            timeout=1
        )
        project_id = response.text

        # Create Secret Manager client
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"

        # Access the secret
        response = client.access_secret_version(request={"name": name})
        secret_value = response.payload.data.decode("UTF-8")

        # Cache the secret
        _secret_cache[secret_name] = secret_value
        return secret_value

    except Exception as e:
        print(f"⚠️  Failed to fetch '{secret_name}' from Secret Manager: {e}", file=sys.stderr)
        return None


def _custom_getenv(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Enhanced os.getenv that tries GCP Secret Manager first (on GCP),
    then falls back to environment variables.

    Args:
        key: Environment variable name
        default: Default value if not found

    Returns:
        str: Environment variable value or default
    """
    # If running on GCP, try Secret Manager first
    if _is_running_on_gcp():
        secret_value = _get_secret_from_gcp(key)
        if secret_value is not None:
            return secret_value

    # Fall back to environment variables
    return _original_getenv(key, default)


def get_secret_manager():
    """
    Initialize the Secret Manager integration by monkey-patching os.getenv().

    Call this at the start of your application:
        from src.secrets_manager import get_secret_manager
        get_secret_manager()

    After calling, all os.getenv() calls will transparently check GCP Secret Manager
    when running on GCP, with automatic fallback to .env for local development.
    """
    # Only monkey-patch if we're on GCP (avoid overhead for local dev)
    if _is_running_on_gcp():
        print("🔐 Detected GCP environment - using Secret Manager for credentials", file=sys.stderr)
        os.getenv = _custom_getenv
    else:
        print("📝 Local development mode - using environment variables", file=sys.stderr)


# Utility function to manually get a secret (for testing)
def get_secret(secret_name: str) -> Optional[str]:
    """
    Manually fetch a secret from GCP Secret Manager.

    Args:
        secret_name: Name of the secret

    Returns:
        str: Secret value if found, None otherwise
    """
    if _is_running_on_gcp():
        return _get_secret_from_gcp(secret_name)
    else:
        return _original_getenv(secret_name)
