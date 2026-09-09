"""Unit tests for debounce controller."""

import time
import threading
from src.watcher.debounce import DebounceController


def test_debounce_triggers_after_quiet_period():
    trigger_count = 0
    lock = threading.Lock()

    def on_trigger():
        nonlocal trigger_count
        with lock:
            trigger_count += 1

    ctrl = DebounceController("TestProj", debounce_seconds=1, on_trigger=on_trigger)

    # Fire 3 quick events
    ctrl.notify_change()
    time.sleep(0.3)
    ctrl.notify_change()
    time.sleep(0.3)
    ctrl.notify_change()

    # Still shouldn't have fired
    assert trigger_count == 0
    assert ctrl.is_pending is True

    # Wait for the remaining time + margin
    time.sleep(1.2)
    assert trigger_count == 1
    assert ctrl.is_pending is False


def test_debounce_trigger_now_immediate():
    triggered = False

    def on_trigger():
        nonlocal triggered
        triggered = True

    ctrl = DebounceController("TestProj", debounce_seconds=60, on_trigger=on_trigger)
    ctrl.notify_change()
    assert ctrl.is_pending is True

    # Immediate trigger
    ctrl.trigger_now()
    assert triggered is True
    assert ctrl.is_pending is False


def test_debounce_cancel():
    triggered = False

    def on_trigger():
        nonlocal triggered
        triggered = True

    ctrl = DebounceController("TestProj", debounce_seconds=1, on_trigger=on_trigger)
    ctrl.notify_change()
    ctrl.cancel()
    assert ctrl.is_pending is False

    time.sleep(1.2)
    assert triggered is False
