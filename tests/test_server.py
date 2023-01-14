from unittest.mock import patch

import pytest

from youtube_rss import settings
from youtube_rss.core.server import start_server


def test_start_server(monkeypatch):
    with patch("uvicorn.run") as mock_run:
        start_server()
        mock_run.assert_called_once()
        assert mock_run.call_args[1]["host"] == settings.server_host
        assert mock_run.call_args[1]["port"] == settings.server_port
        assert mock_run.call_args[1]["log_level"] == settings.log_level.lower()
        assert mock_run.call_args[1]["reload"] == settings.uvicorn_reload
        assert mock_run.call_args[1]["app_dir"] == ""
