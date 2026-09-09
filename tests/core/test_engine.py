"""Unit tests for Engine lifecycle and project registration."""

import tempfile
from pathlib import Path
import pytest

from src.config.manager import ConfigManager
from src.config.models import ProjectConfig, ProjectMode
from src.core.engine import Engine


def test_engine_add_and_manage_projects():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "projects.json"
        cfg_mgr = ConfigManager(config_path)
        engine = Engine(cfg_mgr)

        proj_dir = Path(tmpdir) / "demo_repo"
        proj_dir.mkdir()

        p = ProjectConfig(
            name="EngineDemo",
            path=str(proj_dir),
            mode=ProjectMode.AUTO,
        )

        assert engine.add_project(p) is True
        assert len(engine.get_all_managers()) == 1

        # Pause project
        assert engine.set_project_mode(p.path, ProjectMode.PAUSED) is True
        pm = engine.get_manager(p.path)
        assert pm.config.mode == ProjectMode.PAUSED

        # Dashboard stats
        stats = engine.get_dashboard_stats()
        assert stats["total_projects"] == 1
        assert stats["paused_projects"] == 1
        assert stats["active_projects"] == 0

        # Remove
        assert engine.remove_project(p.path) is True
        assert len(engine.get_all_managers()) == 0

        engine.stop()
