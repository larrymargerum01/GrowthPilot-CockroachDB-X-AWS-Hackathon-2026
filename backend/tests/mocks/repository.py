class MockMemoryRepository:
    def __init__(self):
        self.memories = []

    async def get_by_content_hash(
        self,
        company_id,
        content_hash,
    ):
        for memory in self.memories:
            if (
                memory["company_id"] == company_id
                and memory["content_hash"] == content_hash
            ):
                return memory["id"]

        return None

    async def save_memory(
        self,
        company_id,
        memory_type,
        content,
        content_hash,
        metadata,
        importance,
        embedding,
    ):
        memory_id = len(self.memories) + 1

        self.memories.append(
            {
                "id": memory_id,
                "company_id": company_id,
                "content": content,
                "content_hash": content_hash,
                "embedding": embedding,
            }
        )

        return memory_id

    async def save_memories_batch(self, memories):
        """
        Mock batch memory persistence.
        """

        ids = []

        for memory in memories:
            memory_id = len(self.memories) + 1

            self.memories.append({
                    "id": memory_id,
                    **memory
            })

            ids.append(memory_id)

        return ids