#!/usr/bin/env python3
"""
One-command local launcher for Stock Intelligence.

Run from the repository root:
    python run.py

It starts the FastAPI backend and Vite frontend together and shuts both
processes down when you press Ctrl+C.
"""
from __future__ import annotations

import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FRONTEND = ROOT / "frontend"
PYTHON = sys.executable
PROCESSES: list[subprocess.Popen] = []


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def stop_all(*_args) -> None:
    for process in reversed(PROCESSES):
        if process.poll() is None:
            try:
                process.terminate()
            except OSError:
                pass

    deadline = time.time() + 5
    for process in reversed(PROCESSES):
        if process.poll() is None:
            while process.poll() is None and time.time() < deadline:
                time.sleep(0.1)
            if process.poll() is None:
                try:
                    process.kill()
                except OSError:
                    pass

    raise SystemExit(0)


def main() -> None:
    if not (FRONTEND / "package.json").exists():
        raise SystemExit("frontend/package.json not found. Run this from the repository root.")

    npm = "npm.cmd" if os.name == "nt" else "npm"
    if not command_exists(npm):
        raise SystemExit("Node.js/npm is required. Install Node.js, then run: python run.py")

    env = os.environ.copy()
    env.setdefault("VITE_API_BASE_URL", "http://127.0.0.1:8000")

    package_json = FRONTEND / "package.json"
    chart_package = FRONTEND / "node_modules" / "lightweight-charts" / "package.json"
    dependencies_missing = not (FRONTEND / "node_modules").exists() or not chart_package.exists()
    if dependencies_missing:
        print("[stock] Frontend dependencies are missing. Installing them...")
        result = subprocess.run([npm, "install"], cwd=FRONTEND, env=env)
        if result.returncode != 0:
            raise SystemExit("Frontend dependency installation failed.")

    signal.signal(signal.SIGINT, stop_all)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, stop_all)

    print("[stock] Starting backend: http://127.0.0.1:8000")
    backend = subprocess.Popen(
        [PYTHON, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=ROOT,
        env=env,
    )
    PROCESSES.append(backend)

    print("[stock] Starting frontend: http://127.0.0.1:5173")
    frontend = subprocess.Popen(
        [npm, "run", "dev", "--", "--host", "127.0.0.1", "--port", "5173"],
        cwd=FRONTEND,
        env=env,
    )
    PROCESSES.append(frontend)

    print("[stock] Both services are running. Open http://127.0.0.1:5173")
    print("[stock] Press Ctrl+C once to stop both.")

    try:
        while True:
            for name, process in (("backend", backend), ("frontend", frontend)):
                code = process.poll()
                if code is not None:
                    stop_all()
            time.sleep(0.5)
    finally:
        stop_all()


if __name__ == "__main__":
    main()
