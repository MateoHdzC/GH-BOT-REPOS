
import tempfile
from pathlib import Path
import pytest

from src.config.manager import ConfigManager
from src.config.models import AppConfig, ProjectConfig, ProjectMode, ProjectStatus

def test_project_config_serialization():
    proj = ProjectConfig(
        name="TestProject",
        path=str(Path("C:/test/path").resolve()),
        remote="https://github.com/user/test.git",
        branch="main",
        mode=ProjectMode.AUTO,
        debounce_seconds=120,
        enabled=True,
    )
    d = proj.to_dict()
    assert d["name"] == "TestProject"
    assert d["mode"] == "AUTO"
    assert d["debounce_seconds"] == 120

    deserialized = ProjectConfig.from_dict(d)
    assert deserialized.name == proj.name
    assert deserialized.mode == ProjectMode.AUTO
    assert deserialized.debounce_seconds == 120

def test_config_manager_crud():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "projects.json"
        mgr = ConfigManager(config_path)

        p1 = ProjectConfig(name="P1", path=str(Path(tmpdir) / "p1"))
        p2 = ProjectConfig(name="P2", path=str(Path(tmpdir) / "p2"))

        assert mgr.add_project(p1) is True
        assert mgr.add_project(p2) is True
        assert len(mgr.get_projects()) == 2

        assert mgr.add_project(p1) is False

        fetched = mgr.get_project_by_name("p1")
        assert fetched is not None
        assert fetched.name == "P1"

        assert mgr.set_project_mode(p1.path, ProjectMode.PAUSED) is True
        assert mgr.get_project_by_path(p1.path).mode == ProjectMode.PAUSED

        assert mgr.remove_project(p1.path) is True
        assert len(mgr.get_projects()) == 1
        assert mgr.get_project_by_path(p1.path) is None

        mgr2 = ConfigManager(config_path)
        assert len(mgr2.get_projects()) == 1
        assert mgr2.get_projects()[0].name == "P2"
