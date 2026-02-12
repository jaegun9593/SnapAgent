-- Vector embeddings table
CREATE TABLE IF NOT EXISTS snap_vec_ebd (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    file_id UUID NOT NULL REFERENCES files(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    embedding vector(1536),
    chunk_index INTEGER,
    extra JSONB,
    use_yn CHAR(1) DEFAULT 'Y',
    created_by VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_by VARCHAR(255),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_snap_vec_ebd_agent ON snap_vec_ebd(agent_id);
CREATE INDEX IF NOT EXISTS idx_snap_vec_ebd_file ON snap_vec_ebd(file_id);
CREATE INDEX IF NOT EXISTS idx_snap_vec_ebd_use_yn ON snap_vec_ebd(use_yn);
