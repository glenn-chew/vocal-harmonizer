-- Supabase Database Setup Script
-- Run this in your Supabase SQL Editor

-- Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create compliance_rules table
CREATE TABLE IF NOT EXISTS compliance_rules (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    details TEXT,
    service_id TEXT,
    category TEXT,
    severity TEXT,
    provider TEXT,
    embedding VECTOR(1536),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create vector similarity search function
CREATE OR REPLACE FUNCTION match_compliance_rules(
    query_embedding VECTOR(1536),
    match_threshold FLOAT,
    match_count INT
)
RETURNS TABLE (
    id UUID,
    title TEXT,
    description TEXT,
    details TEXT,
    service_id TEXT,
    category TEXT,
    severity TEXT,
    provider TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE SQL
AS $$
    SELECT
        compliance_rules.id,
        compliance_rules.title,
        compliance_rules.description,
        compliance_rules.details,
        compliance_rules.service_id,
        compliance_rules.category,
        compliance_rules.severity,
        compliance_rules.provider,
        compliance_rules.metadata,
        1 - (compliance_rules.embedding <=> query_embedding) AS similarity
    FROM compliance_rules
    WHERE 1 - (compliance_rules.embedding <=> query_embedding) > match_threshold
    ORDER BY compliance_rules.embedding <=> query_embedding
    LIMIT match_count;
$$;

-- Create index for better performance
CREATE INDEX IF NOT EXISTS compliance_rules_embedding_idx 
ON compliance_rules USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Create index on service_id for faster filtering
CREATE INDEX IF NOT EXISTS compliance_rules_service_id_idx 
ON compliance_rules (service_id);

-- Create index on category for faster filtering
CREATE INDEX IF NOT EXISTS compliance_rules_category_idx 
ON compliance_rules (category);

-- Create index on provider for faster filtering
CREATE INDEX IF NOT EXISTS compliance_rules_provider_idx 
ON compliance_rules (provider);

