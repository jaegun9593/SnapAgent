-- Initialize PostgreSQL database with required extensions
-- This script runs automatically when the database is first created

-- Install pgvector extension for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Install uuid extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Verify extensions
SELECT extname, extversion FROM pg_extension WHERE extname IN ('vector', 'uuid-ossp');
