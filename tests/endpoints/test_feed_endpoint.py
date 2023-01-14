from typing import Any

from pathlib import Path
from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from sqlmodel import Session

from youtube_rss import crud
from youtube_rss.services.feed import build_rss_file


def test_get_rss_not_found(client: TestClient) -> None:
    response = client.get("/feed/non_existent_source")
    assert response.status_code == 404
    assert response.json()["detail"] == [
        "RSS file (non_existent_source.rss) does not exist for (source_id='non_existent_source')"
    ]


async def test_build_and_get_rss_success(
    db_with_source_videos: Session,
    tmp_path: Path,
    monkeypatch: MagicMock,
    client: TestClient,
) -> None:
    def mock(**kwargs: Any) -> Path:
        print(kwargs)
        return tmp_path / f"{source_id}.rss"

    # Build an RSS file for a test source
    source_id = "7hyhcvzT"
    source = await crud.source.get(id=source_id, db=db_with_source_videos)

    monkeypatch.setattr(
        "youtube_rss.services.feed.get_rss_file_path",
        mock,
    )
    # monkeypatch.return_value = tmp_rss_file_path

    rss_file = await build_rss_file(source=source)
    assert rss_file == tmp_path / f"{source_id}.rss"

    # Try accessing the RSS file
    response = client.get(f"/feed/{source_id}")
    assert response.status_code == 200
