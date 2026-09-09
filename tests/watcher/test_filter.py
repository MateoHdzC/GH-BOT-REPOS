"""Unit tests for path filter and exclusions."""

from pathlib import Path
from src.watcher.filter import PathFilter


def test_path_filter_git_directory():
    pf = PathFilter()
    base = Path("C:/projects/demo")

    assert pf.should_ignore(base / ".git" / "index", base) is True
    assert pf.should_ignore(base / ".git" / "HEAD", base) is True
    assert pf.should_ignore(base / ".git", base) is True


def test_path_filter_env_and_secrets():
    pf = PathFilter()
    base = Path("C:/projects/demo")

    assert pf.should_ignore(base / ".env", base) is True
    assert pf.should_ignore(base / ".env.local", base) is True
    assert pf.should_ignore(base / "id_rsa.key", base) is True
    assert pf.should_ignore(base / "cert.pem", base) is True


def test_path_filter_node_modules_and_venv():
    pf = PathFilter()
    base = Path("C:/projects/demo")

    assert pf.should_ignore(base / "node_modules" / "package" / "index.js", base) is True
    assert pf.should_ignore(base / ".venv" / "Lib" / "site.py", base) is True
    assert pf.should_ignore(base / "__pycache__" / "test.cpython-313.pyc", base) is True


def test_path_filter_allows_normal_source_files():
    pf = PathFilter()
    base = Path("C:/projects/demo")

    assert pf.should_ignore(base / "src" / "main.py", base) is False
    assert pf.should_ignore(base / "README.md", base) is False
    assert pf.should_ignore(base / "assets" / "style.css", base) is False
