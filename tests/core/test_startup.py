"""Unit tests for WindowsStartup helper."""

from src.core.startup import WindowsStartup


def test_startup_command_construction():
    cmd = WindowsStartup.get_executable_command()
    assert "--tray" in cmd
    assert len(cmd) > 10
