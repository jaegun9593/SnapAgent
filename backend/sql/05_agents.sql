-- Agents table
CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_email VARCHAR(255) NOT NULL REFERENCES users(email) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    system_prompt TEXT,
    template_id UUID REFERENCES templates(id) ON DELETE SET NULL,
    model_id UUID REFERENCES models(id) ON DELETE RESTRICT,
    embedding_model_id UUID REFERENCES models(id) ON DELETE SET NULL,
    config JSONB,
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'configured', 'processing', 'ready', 'active', 'inactive', 'error')),
    created_by VARCHAR(255) REFERENCES users(email) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_by VARCHAR(255) REFERENCES users(email) ON DELETE SET NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    use_yn CHAR(1) DEFAULT 'Y' NOT NULL CHECK (use_yn IN ('Y', 'N'))
);

CREATE INDEX IF NOT EXISTS idx_agents_user ON agents(user_email);
CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);
CREATE INDEX IF NOT EXISTS idx_agents_use_yn ON agents(use_yn);
