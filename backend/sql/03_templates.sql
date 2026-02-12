-- Templates table
CREATE TABLE IF NOT EXISTS templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    tool_config JSONB,
    system_prompt_template TEXT,
    category VARCHAR(100),
    is_system BOOLEAN DEFAULT false,
    created_by VARCHAR(255) REFERENCES users(email) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_by VARCHAR(255) REFERENCES users(email) ON DELETE SET NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    use_yn CHAR(1) DEFAULT 'Y' NOT NULL CHECK (use_yn IN ('Y', 'N'))
);

CREATE INDEX IF NOT EXISTS idx_templates_category ON templates(category);
CREATE INDEX IF NOT EXISTS idx_templates_system ON templates(is_system);
CREATE INDEX IF NOT EXISTS idx_templates_use_yn ON templates(use_yn);
