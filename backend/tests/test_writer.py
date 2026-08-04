from backend.memory.writer import MemoryWriter

class MockChunker:
    def chunk_text(self, text):
        return [
            "chunk one",
            "chunk two"
        ]

class MockEmbedding:
    def generate_embedding(self, text):
        return [0.1, 0.2]

class MockRepository:
    def __init__(self):
        self.saved = []

    def save_memory(self, content, embedding):
        self.saved.append((content, embedding))

        return "memory-id"

def test_memory_writer_pipeline():
    repository = MockRepository()

    writer = MemoryWriter(
        MockChunker(),
        MockEmbedding(),
        repository
    )

    result = writer.write(
        "hello world"
    )

    assert len(result) == 2
    assert len(repository.saved) == 2