-- System settings table for storing encrypted configuration (API keys, URLs)
CREATE TABLE IF NOT EXISTS system_settings (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    setting_key     VARCHAR(255) NOT NULL,
    setting_value   TEXT NOT NULL,
    is_encrypted    BOOLEAN NOT NULL DEFAULT FALSE,
    description     TEXT,
    created_by      VARCHAR(255) REFERENCES users(email) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by      VARCHAR(255) REFERENCES users(email) ON DELETE SET NULL,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    use_yn          CHAR(1) NOT NULL DEFAULT 'Y'
);

-- Unique constraint on setting_key for active records only
CREATE UNIQUE INDEX IF NOT EXISTS uq_system_settings_key_active
    ON system_settings (setting_key) WHERE use_yn = 'Y';

COMMENT ON TABLE system_settings IS 'System-wide configuration stored by admin (API keys encrypted with Fernet)';
