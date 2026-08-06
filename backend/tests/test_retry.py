"""Retry policy tests — no database required.

These exercise `with_retry` against real asyncpg exception types rather
than mocks, because the retry decision hinges on the SQLSTATE attribute
those exceptions carry. `base_delay=0` keeps the whole file under a few
milliseconds.
"""

import asyncpg
import pytest
from backend.database.database import to_vector_literal, with_retry

async def test_retries_until_success():
    attempts = 0

    async def flaky():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise asyncpg.exceptions.SerializationError("40001 conflict")
        return "ok"

async def test_does_not_retry_other_errors():
    """A unique violation means a bug in our code, not a conflict.
    Retrying would fail four more times and bury the real error."""
    attempts = 0

    async def broken():
        nonlocal attempts
        attempts += 1
        raise asyncpg.exceptions.UniqueViolationError("duplicate key")

    with pytest.raises(asyncpg.exceptions.UniqueViolationError):
        await with_retry(broken, base_delay=0)

    assert attempts == 1, "non-retryable errors must fail on the first attempt"

async def test_gives_up_after_max_attempts():
    attempts = 0

    async def always_conflicts():
        nonlocal attempts
        attempts += 1
        raise asyncpg.exceptions.SerializationError("40001 conflict")

    with pytest.raises(asyncpg.exceptions.SerializationError):
        await with_retry(always_conflicts, max_attempts=4, base_delay=0)

    assert attempts == 4

async def test_succeeds_first_time():
    async def fine():
        return 42

    assert await with_retry(fine, base_delay=0) == 42


def test_vector_literal_format():
    assert to_vector_literal([0.1, 0.2, 0.3]) == "[0.1,0.2,0.3]"


def test_vector_literal_accepts_ints():
    """Guards the float() coercion — an int list should still produce
    float literals, so the intent stays explicit in the SQL."""
    assert to_vector_literal([1, 2]) == "[1.0,2.0]"