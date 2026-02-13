-- Vector embeddings table for RAG similarity search
-- Uses LIST partitioning by agent_id for efficient per-Agent queries
-- Each Agent gets its own partition with independent IVFFlat index

-- pgvector extension (should already exist from 00_init.sql)
CREATE EXTENSION IF NOT EXISTS vector;

-- Drop existing table if exists (for migration)
DROP TABLE IF EXISTS snap_vec_ebd CASCADE;

-- Create partitioned parent table
-- Note: PRIMARY KEY must include the partition key (agent_id)
-- Foreign key on agent_id is not supported on partitioned tables
CREATE TABLE snap_vec_ebd (
    id UUID DEFAULT uuid_generate_v4(),
    agent_id UUID NOT NULL,
    file_id UUID NOT NULL REFERENCES files(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    embedding vector,
    chunk_index INTEGER,
    extra JSONB,
    use_yn VARCHAR(1) DEFAULT 'Y',
    created_by VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_by VARCHAR(255),
    updated_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (id, agent_id)
) PARTITION BY LIST (agent_id);

-- Default partition for any data that doesn't match a specific partition
-- This catches orphaned data or handles race conditions during partition creation
CREATE TABLE snap_vec_ebd_default PARTITION OF snap_vec_ebd DEFAULT;

-- Basic indexes on default partition (vector index created dynamically per partition)
CREATE INDEX idx_snap_vec_ebd_default_file_id ON snap_vec_ebd_default(file_id);

-- Comment explaining partition management
COMMENT ON TABLE snap_vec_ebd IS
'Partitioned table for vector embeddings. Each Agent gets its own partition created dynamically via VectorStore.create_partition(). Partitions are named snap_vec_ebd_<agent_id_with_underscores>.';
