CREATE TABLE IF NOT EXISTS memories (
    id UUID PRIMARY KEY DEFAULT get_random_uuid(),
    content TEXT NOT NULL,
    embedding VECTOR(1024),
    created_at TIMESTAMP DEFAULT now()
)