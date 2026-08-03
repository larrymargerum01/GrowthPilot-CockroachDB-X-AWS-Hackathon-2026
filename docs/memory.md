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