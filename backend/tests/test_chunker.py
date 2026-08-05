from backend.memory.chunker import TextChunker


def test_chunk_text_splits_large_text():
    """
    Verify that text is split into multiple chunks
    based on chunk size.
    """

    chunker = TextChunker()

    text = " ".join(
        [f"word{i}" for i in range(1200)]
    )

    chunks = chunker.chunk_text(text, chunk_size=500)

    assert len(chunks) == 3

    assert len(chunks[0].split()) == 500
    assert len(chunks[1].split()) == 500
    assert len(chunks[2].split()) == 200


def test_chunk_text_returns_single_chunk_for_small_text():
    """
    Verify that small text does not get unnecessarily split.
    """

    chunker = TextChunker()

    text = "This is a small document."

    chunks = chunker.chunk_text(text, chunk_size=500)

    assert len(chunks) == 1
    assert chunks[0] == text


def test_chunk_text_handles_empty_input():
    """
    Verify empty content returns no chunks.
    """

    chunker = TextChunker()

    chunks = chunker.chunk_text("")

    assert chunks == []