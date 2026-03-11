"""Shared pytest configuration for local integration tests."""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

import pytest
import pytest_socket


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _ensure_homeassistant_on_path() -> None:
    """Add local Home Assistant Core sources when HA is not installed."""
    try:
        import homeassistant  # noqa: F401
        return
    except ModuleNotFoundError:
        pass

    configured_path = os.environ.get("HA_CORE_PATH", "D:/HA_Lib_Core")
    ha_core_path = Path(configured_path)
    if ha_core_path.exists() and str(ha_core_path) not in sys.path:
        sys.path.insert(0, str(ha_core_path))


_ensure_homeassistant_on_path()


@pytest.hookimpl(trylast=True)
def pytest_runtest_setup() -> None:
    """Keep sockets enabled for HA event loop creation on Windows."""
    pytest_socket.enable_socket()


@pytest.fixture
def event_loop_policy(socket_enabled: None) -> asyncio.AbstractEventLoopPolicy:
    """Provide an event loop policy with sockets enabled."""
    return asyncio.get_event_loop_policy()
