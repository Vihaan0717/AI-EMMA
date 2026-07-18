-- PROJECT ZERO — Supabase Schema
-- Run this in Supabase SQL Editor
-- Enables pgvector for semantic search

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ═══════════════════════════════════════════════════
-- MEMORIES TABLE (The Vault - Drop Zone)
-- ═══════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS memories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content TEXT NOT NULL,
    category TEXT DEFAULT 'general',
    tags TEXT[] DEFAULT '{}',
    sender TEXT DEFAULT 'user',
    emotion TEXT DEFAULT 'neutral',
    importance FLOAT DEFAULT 0.5,
    -- Vector embedding for semantic search (1536 dims for ada, 384 for small models)
    embedding VECTOR(384),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    recalled_count INTEGER DEFAULT 0,
    last_recalled TIMESTAMPTZ,
    source TEXT DEFAULT 'manual',
    session_id TEXT
);

-- Semantic search index
CREATE INDEX IF NOT EXISTS memories_embedding_idx
    ON memories USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Fast text search index
CREATE INDEX IF NOT EXISTS memories_content_idx
    ON memories USING GIN (to_tsvector('english', content));

-- Category and date indexes
CREATE INDEX IF NOT EXISTS memories_category_idx ON memories(category);
CREATE INDEX IF NOT EXISTS memories_created_idx ON memories(created_at DESC);
CREATE INDEX IF NOT EXISTS memories_sender_idx ON memories(sender);

-- ═══════════════════════════════════════════════════
-- CONVERSATIONS TABLE (Full History)
-- ═══════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id TEXT NOT NULL,
    message TEXT NOT NULL,
    response TEXT NOT NULL,
    persona TEXT DEFAULT 'jarvis',
    emotion TEXT DEFAULT 'neutral',
    intent TEXT DEFAULT 'conversation',
    language TEXT DEFAULT 'english',
    sender TEXT DEFAULT 'user',
    source TEXT DEFAULT 'api',
    confidence FLOAT DEFAULT 0.8,
    processing_ms FLOAT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS conv_session_idx ON conversations(session_id);
CREATE INDEX IF NOT EXISTS conv_created_idx ON conversations(created_at DESC);
CREATE INDEX IF NOT EXISTS conv_sender_idx ON conversations(sender);

-- ═══════════════════════════════════════════════════
-- IDENTITY TABLE (Who the user IS)
-- ═══════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS identity (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    attribute TEXT UNIQUE NOT NULL,
    value TEXT NOT NULL,
    confidence FLOAT DEFAULT 0.8,
    source TEXT DEFAULT 'stated',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ═══════════════════════════════════════════════════
-- KNOWLEDGE TABLE (Learned Facts)
-- ═══════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS knowledge (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fact TEXT UNIQUE NOT NULL,
    category TEXT DEFAULT 'general',
    confidence FLOAT DEFAULT 0.7,
    source TEXT DEFAULT 'conversation',
    embedding VECTOR(384),
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS knowledge_embedding_idx
    ON knowledge USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 50);

-- ═══════════════════════════════════════════════════
-- TASKS TABLE (Automation Queue)
-- ═══════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    description TEXT,
    task_type TEXT DEFAULT 'general',
    status TEXT DEFAULT 'pending',
    priority INTEGER DEFAULT 5,
    assigned_agent TEXT,
    input_data JSONB DEFAULT '{}',
    output_data JSONB DEFAULT '{}',
    error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3
);

CREATE INDEX IF NOT EXISTS tasks_status_idx ON tasks(status);
CREATE INDEX IF NOT EXISTS tasks_type_idx ON tasks(task_type);
CREATE INDEX IF NOT EXISTS tasks_priority_idx ON tasks(priority DESC);

-- ═══════════════════════════════════════════════════
-- PEOPLE TABLE (Relationships - M6)
-- ═══════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS people (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT UNIQUE NOT NULL,
    relationship TEXT DEFAULT 'unknown',
    phone TEXT,
    facts JSONB DEFAULT '{}',
    sentiment FLOAT DEFAULT 0.5,
    interaction_count INTEGER DEFAULT 0,
    first_seen TIMESTAMPTZ DEFAULT NOW(),
    last_seen TIMESTAMPTZ DEFAULT NOW()
);

-- ═══════════════════════════════════════════════════
-- SYSTEM LOGS TABLE
-- ═══════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS system_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    level TEXT NOT NULL,
    service TEXT NOT NULL,
    message TEXT NOT NULL,
    details JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS logs_level_idx ON system_logs(level);
CREATE INDEX IF NOT EXISTS logs_service_idx ON system_logs(service);
CREATE INDEX IF NOT EXISTS logs_created_idx ON system_logs(created_at DESC);

-- ═══════════════════════════════════════════════════
-- FUNCTIONS (Stored Procedures)
-- ═══════════════════════════════════════════════════

-- Semantic search function
CREATE OR REPLACE FUNCTION search_memories(
    query_embedding VECTOR(384),
    match_threshold FLOAT DEFAULT 0.5,
    match_count INT DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    category TEXT,
    emotion TEXT,
    similarity FLOAT,
    created_at TIMESTAMPTZ
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        m.id,
        m.content,
        m.category,
        m.emotion,
        1 - (m.embedding <=> query_embedding) AS similarity,
        m.created_at
    FROM memories m
    WHERE 1 - (m.embedding <=> query_embedding) > match_threshold
        AND m.embedding IS NOT NULL
    ORDER BY similarity DESC
    LIMIT match_count;
END;
$$;

-- Auto-update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_identity_updated_at
    BEFORE UPDATE ON identity
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_knowledge_updated_at
    BEFORE UPDATE ON knowledge
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Cleanup expired memories function
CREATE OR REPLACE FUNCTION cleanup_expired_memories()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM memories
    WHERE expires_at IS NOT NULL
        AND expires_at < NOW();
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- ═══════════════════════════════════════════════════
-- ROW LEVEL SECURITY (Optional but recommended)
-- ═══════════════════════════════════════════════════
ALTER TABLE memories ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;

-- Allow service role full access
CREATE POLICY "Service role access" ON memories
    FOR ALL USING (true);

CREATE POLICY "Service role access" ON conversations
    FOR ALL USING (true);

-- ═══════════════════════════════════════════════════
-- INITIAL SEED DATA
-- ═══════════════════════════════════════════════════
INSERT INTO identity (attribute, value, confidence, source)
VALUES
    ('system_name', 'NEXUS-X ULTIMATE', 1.0, 'system'),
    ('personality_jarvis', 'active', 1.0, 'system'),
    ('personality_arion', 'active', 1.0, 'system'),
    ('version', '2.0.0', 1.0, 'system')
ON CONFLICT (attribute) DO NOTHING;
