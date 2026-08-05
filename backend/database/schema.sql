CREATE TABLE IF NOT EXISTS memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL,
    
    content TEXT NOT NULL,
    embedding VECTOR(1024),
    created_at TIMESTAMPTZ DEFAULT now(),

    VECTOR INDEX (
        company_id,
        embedding vector_cosine_ops
    )
)