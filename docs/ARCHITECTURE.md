# GH-BOT-REPOS — Windows Architecture Document

## Overview

`GH-BOT-REPOS` is a native Windows desktop application designed to run persistently in the background, monitoring multiple Git repositories simultaneously. It detects filesystem changes, applies an intelligent debounce window, runs a pre-commit security analysis, stages changes, creates commits, and pushes them to GitHub.

---

## High-Level Architecture

```
+-------------------------------------------------------------------------+
|                              CustomTkinter GUI                          |
|  +--------------------+  +--------------------------------------------+ |
|  |      Sidebar       |  | Viewport: Projects | Dashboard | Logs      | |
|  +--------------------+  +--------------------------------------------+ |
+------------------------------------+------------------------------------+
                                     |
                                     v
+------------------------------------+------------------------------------+
|                         Application Engine                              |
|  +-----------------------+   +-------------------+  +-----------------+ |
|  |   Project Managers    |   |    Retry Queue    |  |  Windows Tray   | |
|  +-----------------------+   +-------------------+  +-----------------+ |
+------------------+-------------------------+----------------------------+
                   |                         |
                   v                         v
+------------------+----------+    +---------+----------------------------+
|     Filesystem Watchers     |    |              GitManager              |
|  +-----------------------+  |    |  +--------------------------------+  |
|  | watchdog FileObserver |  |    |  | Subprocess Git CLI Execution   |  |
|  +-----------------------+  |    |  | Safety Guard Pre-commit        |  |
|  | PathFilter / Debounce |  |    |  | Windows Credential Manager     |  |
|  +-----------------------+  |    |  +--------------------------------+  |
+-----------------------------+    +--------------------------------------+
```

---

## Core Components

### 1. Configuration (`src/config`)
- **`models.py`**: Typed dataclasses for `ProjectConfig`, `AppConfig`, and enums (`ProjectMode`, `ProjectStatus`).
- **`manager.py`**: Thread-safe `ConfigManager` with atomic JSON writes via temp files.

### 2. File Monitoring & Debounce (`src/watcher`)
- **`filter.py`**: Glob and directory pattern matcher excluding `.git`, `.venv`, `node_modules`, `.env`, and secret files.
- **`debounce.py`**: Reactive timer resetting upon successive events and firing after a clean quiet window.
- **`service.py`**: `watchdog.observers.Observer` thread per repository path.

### 3. Git Operations & Security (`src/git`)
- **`manager.py`**: Subprocess executor for `git status`, `git add`, `git commit`, `git push`. Enforces strict blocks against `push --force` and `reset --hard`.
- **`credentials.py`**: Windows Credential Manager integration through `keyring` and Windows DPAPI. Validates tokens via GitHub API.

### 4. Core Lifecycle & Safety (`src/core`)
- **`safety_guard.py`**: Inspects files prior to staging to block secrets (`.env`, `*.pem`, `id_rsa`) and massive deletions.
- **`retry_queue.py`**: Reschedules failed pushes with exponential backoff.
- **`startup.py`**: Manages `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`.
- **`engine.py`**: Central coordinator for all active project managers and background threads.

### 5. Desktop UI & Tray (`src/ui`)
- **`theme.py`**: Dark mode palette (`#141416`, `#1C1C1F`, `#232328`, `#0A84FF`, `#30D158`, `#FF9F0A`, `#FF453A`).
- **`tray.py`**: Windows System Tray integration with `pystray`.
- **`app.py`**: CustomTkinter main loop and close-to-tray protocol.
