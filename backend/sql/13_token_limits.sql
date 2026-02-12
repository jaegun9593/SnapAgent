-- Token limits table
CREATE TABLE IF NOT EXISTS token_limits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_email VARCHAR(255) REFERENCES users(email) ON DELETE CASCADE,
    limit_type VARCHAR(50) NOT NULL CHECK (limit_type IN ('daily', 'monthly', 'total')),
    max_tokens INTEGER,
    max_api_calls INTEGER,
    is_active BOOLEAN DEFAULT true,
    created_by VARCHAR(255) REFERENCES users(email) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_by VARCHAR(255) REFERENCES users(email) ON DELETE SET NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    use_yn CHAR(1) DEFAULT 'Y' NOT NULL CHECK (use_yn IN ('Y', 'N'))
);

CREATE INDEX IF NOT EXISTS idx_token_limits_user ON token_limits(user_email);
CREATE INDEX IF NOT EXISTS idx_token_limits_active ON token_limits(is_active);
