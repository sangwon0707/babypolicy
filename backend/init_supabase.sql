-- BabyPolicy Database Initialization Script for Supabase
-- Run this in Supabase SQL Editor: https://supabase.com/dashboard/project/_/sql

-- 확장 기능 (UUID, 벡터)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

-- ========================
-- 1. 사용자 관리
-- ========================

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    password TEXT, -- for email/password auth
    provider TEXT, -- google, github, kakao 등
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    name TEXT,
    gender TEXT,
    region TEXT,
    income INT,
    family_size INT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_settings (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    notify_policy BOOLEAN DEFAULT true,
    notify_event BOOLEAN DEFAULT true,
    language TEXT DEFAULT 'ko',
    theme TEXT DEFAULT 'light'
);

-- ========================
-- 2. 정책 + RAG
-- ========================

CREATE TABLE IF NOT EXISTS policies (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT,
    region TEXT,
    eligibility JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS policy_chunks (
    id TEXT PRIMARY KEY,
    doc_id TEXT NOT NULL,
    chunk_index INT NOT NULL,
    content TEXT,
    metadata JSONB,
    embedding VECTOR(1024)
);

CREATE TABLE IF NOT EXISTS user_policies (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    policy_id TEXT REFERENCES policies(id) ON DELETE CASCADE,
    is_checked BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (user_id, policy_id)
);

CREATE TABLE IF NOT EXISTS pdf_files (
    id BIGSERIAL PRIMARY KEY,
    path TEXT NOT NULL UNIQUE,
    category JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- ========================
-- 3. 커뮤니티
-- ========================

CREATE TABLE IF NOT EXISTS categories (
    id VARCHAR(50) PRIMARY KEY,
    label VARCHAR(100) NOT NULL,
    description TEXT,
    color_code VARCHAR(7),
    icon_emoji VARCHAR(10),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default categories
INSERT INTO categories (id, label, description, icon_emoji, sort_order) VALUES
    ('tips', '육아 팁', '일상적인 육아 노하우와 팁', '💡', 1),
    ('policy', '정책 정보', '육아 관련 정책 토론', '📋', 2),
    ('support', '육아 지원', '정부 지원금 및 혜택', '💰', 3),
    ('health', '건강', '아이 건강 관련 정보', '🏥', 4),
    ('education', '교육', '유아 교육 정보', '📚', 5),
    ('free-talk', '자유수다', '자유로운 대화', '💬', 6)
ON CONFLICT (id) DO NOTHING;

CREATE TABLE IF NOT EXISTS posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    author_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category_id VARCHAR(50) NOT NULL REFERENCES categories(id),
    likes_count INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    views_count INTEGER DEFAULT 0,
    is_pinned BOOLEAN DEFAULT false,
    is_featured BOOLEAN DEFAULT false,
    status VARCHAR(20) DEFAULT 'published'
        CHECK (status IN ('draft', 'published', 'hidden', 'deleted')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    published_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS comments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    author_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    parent_id UUID REFERENCES comments(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    likes_count INTEGER DEFAULT 0,
    is_deleted BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS post_likes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(post_id, user_id)
);

CREATE TABLE IF NOT EXISTS comment_likes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    comment_id UUID NOT NULL REFERENCES comments(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(comment_id, user_id)
);

-- ========================
-- 4. 대화 & 메시지
-- ========================

CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200),
    conversation_type VARCHAR(30) DEFAULT 'general'
        CHECK (conversation_type IN ('general', 'policy_search', 'support_info', 'community_help')),
    is_archived BOOLEAN DEFAULT false,
    message_count INTEGER DEFAULT 0,
    topics_discussed TEXT[],
    user_context JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_message_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    message_type VARCHAR(30) DEFAULT 'text'
        CHECK (message_type IN ('text', 'policy_result', 'support_info', 'quick_action')),
    response_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    rag_sources JSONB,
    extracted_entities JSONB,
    confidence_score FLOAT,
    action_buttons JSONB
);

-- ========================
-- 5. 캘린더 & 알림
-- ========================

CREATE TABLE IF NOT EXISTS calendar_events (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title TEXT,
    description TEXT,
    event_date TIMESTAMP WITH TIME ZONE,
    is_policy_related BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS notifications (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    event_id BIGINT REFERENCES calendar_events(id) ON DELETE CASCADE,
    message TEXT,
    is_read BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ========================
-- Vector Search Setup
-- ========================

DROP INDEX IF EXISTS policy_chunks_embedding_ivfflat;
CREATE INDEX policy_chunks_embedding_ivfflat
  ON policy_chunks USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

DROP FUNCTION IF EXISTS match_policy_chunks(vector, int, jsonb);
DROP FUNCTION IF EXISTS match_policy_chunks(vector, int);

CREATE FUNCTION match_policy_chunks(
  query_embedding vector(1024),
  match_count int
) RETURNS TABLE (
  id text,
  doc_id text,
  chunk_index int,
  content text,
  metadata jsonb,
  embedding vector(1024)
) LANGUAGE plpgsql AS $$
BEGIN
  RETURN QUERY
  SELECT
    pc.id,
    pc.doc_id,
    pc.chunk_index,
    pc.content,
    pc.metadata,
    pc.embedding
  FROM policy_chunks AS pc
  ORDER BY pc.embedding <-> query_embedding
  LIMIT match_count;
END;
$$;

-- ========================
-- Indexes for Performance
-- ========================

CREATE INDEX IF NOT EXISTS idx_posts_category ON posts(category_id);
CREATE INDEX IF NOT EXISTS idx_posts_author ON posts(author_id);
CREATE INDEX IF NOT EXISTS idx_posts_created ON posts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_comments_post ON comments(post_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_conversations_user ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_policy_chunks_doc ON policy_chunks(doc_id);

-- Success message
SELECT 'BabyPolicy Database initialized successfully! 🎉' as status;
