"""
Text chunking utilities for the memory pipeline.

The chunking stage prepares raw content before generating vector embeddings.
Smaller chunks improve embedding quality and allow more precise similarity search.
"""

def chunk_text(content: str, chunk_size: int = 500):

    """
        Split text content into smaller chunks.

        Args:
            content: Raw text content to split.
            chunk_size: Maximum number of words per chunk.

        Returns:
            A list of text chunks.
    """

    words = content.split()

    chunks = []

    # Split wordsd into fixed-size groups to prepare
    # each chunk for embedding generation.

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)

    return chunks
