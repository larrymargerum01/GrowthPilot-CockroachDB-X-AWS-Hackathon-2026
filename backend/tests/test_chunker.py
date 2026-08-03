from backend.memory.chunker import chunk_text

def test_chunk_text():
    """
    Verify that short content remains as a single chunk.
    """

    content = "This is a simple memory test"

    chunks = chunk_text(content)

    assert len(chunks) == 1
    assert chunks[0] == content


def test_chunk_text_multiple_chunks():
    """
        Verify that large content is split into
        correctly sized chunks.
    """

    # Simulate a long document that needs multiple embeddings. 
    content = "word " * 1200

    chunks = chunk_text(content, chunk_size=500)

    assert len(chunks) == 3
    assert len(chunks[0].split()) == 500
    assert len(chunks[1].split()) == 500
    assert len(chunks[2].split()) == 200
