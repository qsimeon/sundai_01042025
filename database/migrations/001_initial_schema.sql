-- Posts table: Track generated posts through lifecycle
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    image_prompt TEXT,
    image_path TEXT,
    post_type TEXT NOT NULL,
    platform TEXT NOT NULL,
    status TEXT NOT NULL,
    character_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP,
    published_at TIMESTAMP,
    mastodon_url TEXT,
    mastodon_id TEXT,
    rejection_reason TEXT
);

-- Replies table: Track generated replies
CREATE TABLE IF NOT EXISTS replies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id TEXT NOT NULL,
    reply_content TEXT NOT NULL,
    should_reply BOOLEAN,
    reasoning TEXT,
    relevance_score INTEGER,
    status TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP,
    published_at TIMESTAMP,
    mastodon_url TEXT,
    rejection_reason TEXT
);

-- Images table: Track generated images
CREATE TABLE IF NOT EXISTS images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt TEXT NOT NULL,
    file_path TEXT NOT NULL,
    model TEXT,
    aspect_ratio TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    post_id INTEGER,
    FOREIGN KEY(post_id) REFERENCES posts(id)
);

-- Approvals table: Track Telegram approval workflow
CREATE TABLE IF NOT EXISTS approvals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_type TEXT NOT NULL,
    content_id INTEGER NOT NULL,
    telegram_message_id INTEGER,
    approved BOOLEAN,
    rejection_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    responded_at TIMESTAMP
);

-- Rejection feedback: Store for AI improvement
CREATE TABLE IF NOT EXISTS rejection_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_type TEXT NOT NULL,
    content_preview TEXT,
    rejection_reason TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- API usage tracking: Monitor costs and performance
CREATE TABLE IF NOT EXISTS api_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    endpoint TEXT NOT NULL,
    method TEXT NOT NULL,
    status_code INTEGER,
    response_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_posts_status ON posts(status);
CREATE INDEX IF NOT EXISTS idx_posts_created ON posts(created_at);
CREATE INDEX IF NOT EXISTS idx_replies_status ON replies(status);
CREATE INDEX IF NOT EXISTS idx_approvals_created ON approvals(created_at);
CREATE INDEX IF NOT EXISTS idx_images_created ON images(created_at);
