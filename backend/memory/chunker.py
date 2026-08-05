"""
Text chunking utilities for the memory pipeline.

The chunking stage prepares raw content before generating
vector embeddings.
"""


class TextChunker:
    """
    Splits text into smaller chunks before embedding generation.
    """


    def chunk_text(self, content: str, chunk_size: int = 500) -> list[str]:
        """
        Split text content into smaller chunks.

        Args:
            content:
                Raw text content.

            chunk_size:
                Maximum number of words per chunk.

        Returns:
            List of text chunks.
        """

        if chunk_size <= 0:
            raise ValueError(
                "chunk_size must be greater than zero"
            )

        words = content.split()

        chunks = []

        for i in range(0, len(words), chunk_size):

            chunk = " ".join(
                words[i:i + chunk_size]
            )

            chunks.append(chunk)

        return chunks