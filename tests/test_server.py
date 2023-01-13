from unittest.mock import patch

import pytest

from youtube_rss import config
from youtube_rss.core.server import start_server


def test_start_server(monkeypatch):
    with patch("uvicorn.run") as mock_run:
        start_server()
        mock_run.assert_called_once()
        assert mock_run.call_args[1]["host"] == config.SERVER_IP
        assert mock_run.call_args[1]["port"] == config.SERVER_PORT
        assert mock_run.call_args[1]["log_level"] == config.LOG_LEVEL.lower()
        assert mock_run.call_args[1]["reload"] == config.UVICORN_RELOAD
        assert mock_run.call_args[1]["app_dir"] == ""
