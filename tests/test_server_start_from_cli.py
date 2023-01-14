from typing import Any

from unittest.mock import MagicMock

import pytest
import uvicorn
from typer import Exit

from youtube_rss import get_version, settings
from youtube_rss.core.cli import typer_app, version_callback
from youtube_rss.core.server import start_server


def test_version_callback(mocker):
    mock_console = mocker.patch("youtube_rss.core.cli.console")

    try:
        version_callback(print_version=True)
    except Exit:
        pass
    version = get_version()
    print(version)
    mock_console.print.assert_called_with(
        f"[yellow]{settings.project_name}[/] version: [bold blue]{version}[/]"
    )


def test_start_server_success(monkeypatch: MagicMock) -> None:
    monkeypatch.setattr(uvicorn, "run", lambda *args, **kwargs: None)
    start_server()
    assert True


def test_start_server_host_port(monkeypatch: MagicMock) -> None:
    def mock_run(*args: Any, **kwargs: Any) -> None:
        assert kwargs["host"] == settings.server_host
        assert kwargs["port"] == settings.server_port

    monkeypatch.setattr(uvicorn, "run", mock_run)
    start_server()


def test_start_server_log_level(monkeypatch: MagicMock) -> None:
    def mock_run(*args: Any, **kwargs: Any) -> None:
        assert kwargs["log_level"] == settings.log_level.lower()

    monkeypatch.setattr(uvicorn, "run", mock_run)
    start_server()
