-- 002_auth.sql — add authentication columns and session table (T37)

ALTER TABLE companies ADD COLUMN IF NOT EXISTS email STRING UNIQUE;
ALTER TABLE companies ADD COLUMN IF NOT EXISTS password_hash STRING;

CREATE TABLE IF NOT EXISTS sessions (
    token UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions (token);
