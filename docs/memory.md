# GrowthPilot Memory Layer - CockroachDB Vector Spike

## Objective

Validate CockroachDB's vector capabilities for GrowthPilot's persistent AI memory system.

This spike verifies:

- Vector storage support
- Vector indexing
- Python application insertion
- Vector similarity calculation
- CockroachDB suitability as an AI memory layer

---

# Environment

## Database

- Database: CockroachDB Cloud
- Version: CockroachDB CCL v26.2.1
- Region: AWS eu-west-2
- Database: defaultdb
- SQL User: larry

Connection was successfully tested using:

- CockroachDB SQL CLI
- Python 3.14
- psycopg2-binary

---

# 1. Create Vector Table

Created a table to store AI memory content and embeddings.

```sql
CREATE TABLE vector_test (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    content STRING NULL,
    embedding VECTOR(1024) NULL,
    CONSTRAINT vector_test_pkey PRIMARY KEY (id ASC)
);
```

## Result

Table created successfully.

Schema:

```
vector_test

id          UUID
content     STRING
embedding   VECTOR(1024)
```

---

# 2. Embedding Dimension Decision

Selected embedding dimension:

```
1024
```

Reason:

- Amazon Titan Text Embeddings v2 supports 1024 dimensions.
- CockroachDB supports VECTOR(1024).
- This keeps the database schema compatible with the future GrowthPilot embedding pipeline.

---

# 3. Create Vector Index

Created vector index:

```sql
CREATE VECTOR INDEX memory_embedding_idx
ON vector_test(embedding);
```

## Result

```
CREATE INDEX
```

The vector index was created successfully and will support efficient similarity search.

---

# 4. Python Vector Insert Test

Created:

```
insert_vector.py
```

Purpose:

Verify that an external Python application can insert vector embeddings into CockroachDB.

Technology flow:

```
Python Application
        |
        ↓
psycopg2-binary
        |
        ↓
CockroachDB Cloud
        |
        ↓
VECTOR(1024)
```

Insert query:

```sql
INSERT INTO vector_test (content, embedding)
VALUES (%s, %s)
```

Inserted test memory:

```
Sustainable products are too expensive
```

with a 1024-dimensional vector.

## Result

Successful insertion.

Verified:

- Python application connected successfully.
- SSL connection succeeded.
- Vector data was inserted.
- Transaction was committed successfully.

---

# 5. Verify Stored Vector Data

Checked stored memory:

```sql
SELECT id, content FROM vector_test;
```

Result:

```
Sustainable products are too expensive
```

Verified vector dimension:

```sql
SELECT id, vector_dims(embedding)
FROM vector_test;
```

Result:

```
1024
```

Finding:

- The vector was stored correctly.
- The embedding dimension matches VECTOR(1024).

---

# 6. Vector Distance Operator Test

Tested CockroachDB vector similarity calculation.

Query:

```sql
SELECT
    a.content AS memory_a,
    b.content AS memory_b,
    a.embedding <=> b.embedding AS distance
FROM vector_test a
JOIN vector_test b
ON a.id < b.id;
```

## Explanation

This query:

- Uses a self-join to compare vectors stored in the same table.
- Creates pairs of memory records.
- Uses the `<=>` operator to calculate vector distance.
- Uses `a.id < b.id` to avoid duplicate comparisons.
- Prevents comparing a vector with itself.

The purpose is to validate that CockroachDB can calculate similarity between stored AI memories.

---

# 7. Self Vector Comparison Test

Tested comparing a vector with itself.

Query:

```sql
SELECT
    content,
    embedding <=> embedding AS distance
FROM vector_test;
```

Result:

```
distance = 0
```

Finding:

A vector compared with itself returns zero distance.

This confirms that the vector distance operator works correctly.

---

# 8. Vector Direction Test

During testing, two vectors:

```
[0.1, 0.1, 0.1, ...]
```

and:

```
[0.2, 0.2, 0.2, ...]
```

returned:

```
distance = 0
```

Finding:

Cosine-style distance measures vector direction rather than absolute magnitude.

Vectors with the same direction can have zero distance even if their values are different.

---

# T5 Final Findings

Completed validation:

✅ CockroachDB Cloud connection works.

✅ Native vector storage works:

```sql
VECTOR(1024)
```

✅ Vector index creation works.

✅ Python insertion works using:

```
psycopg2-binary
```

✅ Stored embeddings can be retrieved.

✅ Vector dimensions can be verified.

✅ Vector similarity calculation works using:

```
<=>
```

---

# Conclusion

CockroachDB successfully provides the required capabilities for GrowthPilot's persistent AI memory layer.

Validated capabilities:

- Store AI embeddings
- Index vector data
- Compare memory embeddings
- Support future semantic search workflows

Future GrowthPilot memory architecture:

```
User Input
    |
    ↓
Embedding Model
    |
    ↓
VECTOR(1024)
    |
    ↓
CockroachDB Memory Storage
    |
    ↓
Vector Similarity Search
    |
    ↓
Relevant AI Memories
```

CockroachDB is suitable as the persistent memory foundation for GrowthPilot.

---

# 9. Prefix Column + Tenant Isolation Spike (T5, Coral, 2026-08-04)

The section above validates vector storage in general but never tests the
`company_id` prefix column, which is the mechanism GrowthPilot actually
depends on for tenant isolation and search-space reduction (see
`memories` schema in the project interface contract). This section fills
that gap, run against `gtm-agent` (CockroachDB CCL v26.2.1, AWS eu-west-2).

## Setup

```sql
SET CLUSTER SETTING feature.vector_index.enabled = true;

CREATE TABLE spike_prefix (
    id          INT PRIMARY KEY,
    company_id  INT NOT NULL,
    embedding   VECTOR(3),
    VECTOR INDEX (company_id, embedding vector_cosine_ops)
);
```

Table created on the first attempt — prefix column and opclass are
combinable in a single inline `VECTOR INDEX` clause, no workaround needed.

```sql
SHOW CREATE TABLE spike_prefix;
```

```
VECTOR INDEX spike_prefix_company_id_embedding_idx (company_id, embedding vector_cosine_ops)
```

Index name is auto-generated (`<table>_<cols>_idx`). Table also carries
`schema_locked = true` by default in this CockroachDB version — unrelated to
vector indexing, just noting it in case it affects future `ALTER TABLE`.

## Data

```sql
INSERT INTO spike_prefix (id, company_id, embedding) VALUES
    (1, 100, '[1,0,0]'),
    (2, 100, '[0.9,0.1,0]'),
    (3, 100, '[0,1,0]'),
    (4, 200, '[1,0,0]');
```

## Findings

| Question | Result |
|---|---|
| CockroachDB version | CCL v26.2.1 |
| Chosen dimension | 1024 (Titan v2), tested here at 3 for hand-typed vectors |
| Chosen metric | cosine (`<=>` / `vector_cosine_ops`) |
| Prefix column + opclass combinable | **Yes**, in one inline `VECTOR INDEX` clause |
| Cross-tenant leakage | **None** — `WHERE company_id = 100` never returned company 200's row |
| Index used with `=` | **Yes** — plan shows `vector search` on `spike_prefix_company_id_embedding_idx`, `prefix spans: [/100 - /100]` |
| Index used with `>=` (range) | **No** — falls back to `FULL SCAN` on `spike_prefix_pkey`. CockroachDB even suggested an unrelated B-tree index. Confirms finding #3 in project notes: range predicates on the prefix column defeat the vector index. |
| Index used with `IN (...)` | **Yes** — plan shows `vector search` with `prefix spans: [/100 - /100] [/200 - /200]`, i.e. CockroachDB splits the `IN` list into independent exact spans and scans the index for each. |

## Implication for GrowthGraph (T36)

The cross-founder query must filter the prefix column with `IN (...)`
(or repeated `=`), never a range predicate, or it silently falls back to a
full table scan across every company's embeddings — both a performance
problem and a soft tenant-isolation smell (the row is still filtered
correctly by the `filter:` step, just not by the index).

Cleanup: `DROP TABLE spike_prefix;` run after this section, confirmed table
gone.

## Mapping to the production schema

`spike_prefix` used `INT` ids and `VECTOR(3)` so vectors could be typed by
hand. The real `memories` table (frozen in the interface contract) swaps
those for `UUID` and `VECTOR(1024)`, but the index clause is identical in
shape:

```sql
-- spike (this doc)
CREATE TABLE spike_prefix (
    id          INT PRIMARY KEY,
    company_id  INT NOT NULL,
    embedding   VECTOR(3),
    VECTOR INDEX (company_id, embedding vector_cosine_ops)
);

-- production (backend/memory, T7)
CREATE TABLE memories (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id   UUID NOT NULL REFERENCES companies(id),
    memory_type  STRING NOT NULL,
    content      STRING NOT NULL,
    content_hash STRING NOT NULL,
    metadata     JSONB NOT NULL DEFAULT '{}',
    embedding    VECTOR(1024),
    importance   FLOAT NOT NULL DEFAULT 0.5,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_accessed_at TIMESTAMPTZ,
    access_count INT NOT NULL DEFAULT 0,
    VECTOR INDEX (company_id, embedding vector_cosine_ops),
    INDEX idx_company_type_time (company_id, memory_type, created_at DESC),
    UNIQUE INDEX idx_dedup (company_id, content_hash)
);
```

Everything this doc validated transfers directly: `company_id` as the
prefix column, `vector_cosine_ops` as the opclass, `=`/`IN` as the only
predicate shapes that keep the vector index in the plan. The extra columns
(`memory_type`, `content_hash`, `importance`, access tracking) don't change
index behavior — they're outside the `VECTOR INDEX` clause, so this spike's
conclusions hold unchanged for T7.