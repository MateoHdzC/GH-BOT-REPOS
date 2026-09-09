"""Unit tests for RetryQueue."""

import time
from src.core.retry_queue import RetryQueue


def test_retry_queue_add_remove():
    rq = RetryQueue()

    item = rq.add_or_update(
        project_path="C:/proj/a",
        project_name="ProjA",
        remote="origin",
        branch="main",
        error="Network timeout",
    )
    assert item.attempts == 1
    assert len(rq.get_all()) == 1

    # Update attempt
    item2 = rq.add_or_update(
        project_path="C:/proj/a",
        project_name="ProjA",
        remote="origin",
        branch="main",
        error="Connection refused",
    )
    assert item2.attempts == 2

    # Remove
    rq.remove("C:/proj/a")
    assert len(rq.get_all()) == 0


def test_retry_queue_due_items():
    rq = RetryQueue()
    item = rq.add_or_update("C:/proj/b", "ProjB", "origin", "main", "Network down")

    # Manually backdate next_retry_time
    item.next_retry_time = time.time() - 1

    due = rq.get_due_items()
    assert len(due) == 1
    assert due[0].project_name == "ProjB"
