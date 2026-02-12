-- Agent sub-agents junction table
CREATE TABLE IF NOT EXISTS agent_sub_agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    parent_agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    child_agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    sort_order INTEGER DEFAULT 0,
    created_by VARCHAR(255) REFERENCES users(email) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_by VARCHAR(255) REFERENCES users(email) ON DELETE SET NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    use_yn CHAR(1) DEFAULT 'Y' NOT NULL CHECK (use_yn IN ('Y', 'N')),
    CONSTRAINT uq_agent_sub_agent UNIQUE (parent_agent_id, child_agent_id)
);

CREATE INDEX IF NOT EXISTS idx_agent_sub_agents_parent ON agent_sub_agents(parent_agent_id);
