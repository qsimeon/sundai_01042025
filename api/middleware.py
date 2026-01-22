import logging
import time
from typing import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from api.config import settings
from api.database import execute_insert


# Setup logging
log_path = settings.get_log_path()
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all API requests and responses"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        response = await call_next(request)

        process_time = int((time.time() - start_time) * 1000)

        # Log to database
        try:
            execute_insert(
                """INSERT INTO api_usage (endpoint, method, status_code, response_time_ms)
                   VALUES (?, ?, ?, ?)""",
                (request.url.path, request.method, response.status_code, process_time)
            )
        except Exception as e:
            logger.error(f"Failed to log API usage: {e}")

        # Log to file
        logger.info(
            f"{request.method} {request.url.path} - {response.status_code} "
            f"- {process_time}ms"
        )

        return response
