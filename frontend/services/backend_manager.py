import os
import sys
import time
import socket
import logging
import subprocess
from pathlib import Path
from typing import Optional

logger = logging.getLogger("backend_manager")

# Global handle to prevent duplicate processes within the same Python session
_backend_process: Optional[subprocess.Popen] = None
_startup_attempted_time: float = 0.0


def sync_secrets_to_env() -> None:
    """
    Copies variables from streamlit.secrets into os.environ so that
    backend services, Supabase, Groq, and API clients have access.
    """
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            for key, val in st.secrets.items():
                if isinstance(val, (str, int, float, bool)):
                    if key not in os.environ:
                        os.environ[key] = str(val)
                elif isinstance(val, dict):
                    for sub_k, sub_v in val.items():
                        if isinstance(sub_v, (str, int, float, bool)) and sub_k not in os.environ:
                            os.environ[sub_k] = str(sub_v)
    except Exception:
        pass


def is_port_in_use(port: int = 8000, host: str = "127.0.0.1") -> bool:
    """Check if the given localhost port has a listening socket."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


def is_backend_online(timeout: float = 2.0) -> bool:
    """Checks if the configured backend URL responds to /health or /api/v1/health."""
    sync_secrets_to_env()
    from frontend.services.api_client import check_health
    try:
        health = check_health(timeout=timeout)
        return health.get("status") == "healthy" or "status" in health
    except Exception:
        return False


def start_backend_process() -> bool:
    """
    Launches uvicorn backend.main:app as a background daemon process.
    Returns True if launched or already running.
    """
    global _backend_process, _startup_attempted_time

    sync_secrets_to_env()
    backend_url = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").lower()

    # If configured with an external URL, do not launch local process
    if "127.0.0.1" not in backend_url and "localhost" not in backend_url:
        return is_backend_online()

    if is_backend_online(timeout=1.0):
        return True

    # Debounce startup attempts within 30 seconds
    now = time.time()
    if now - _startup_attempted_time < 30.0 and _backend_process is not None:
        if _backend_process.poll() is None:
            # Process is still starting up
            return False

    _startup_attempted_time = now
    root_dir = Path(__file__).resolve().parent.parent.parent

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "backend.main:app",
        "--host",
        "0.0.0.0",
        "--port",
        "8000",
    ]

    try:
        _backend_process = subprocess.Popen(
            cmd,
            cwd=str(root_dir),
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except Exception as exc:
        logger.error(f"Failed to start backend process: {exc}")
        return False


def ensure_backend_running(auto_start: bool = True, wait_seconds: int = 6) -> bool:
    """
    Ensures backend is online. If offline and auto_start=True, starts it and waits.
    """
    sync_secrets_to_env()

    if is_backend_online(timeout=1.5):
        return True

    backend_url = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").lower()
    if "127.0.0.1" not in backend_url and "localhost" not in backend_url:
        # Remote backend: just check online status
        return is_backend_online(timeout=2.0)

    if not auto_start:
        return False

    start_backend_process()

    # Poll until ready or timeout
    start_time = time.time()
    while time.time() - start_time < wait_seconds:
        time.sleep(1.0)
        if is_backend_online(timeout=1.0):
            return True

    return False
