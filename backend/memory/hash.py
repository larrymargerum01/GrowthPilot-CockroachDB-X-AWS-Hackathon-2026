import hashlib


def create_content_hash(content: str) -> str:
    """
    Create a deterministic hash for memory deduplication.
    """

    normalized = content.strip().lower()

    return hashlib.sha256(
        normalized.encode("utf-8")
    ).hexdigest()