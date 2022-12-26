from typing import List

from fastapi import APIRouter, HTTPException, status

from youtube_rss.db.crud import source_crud
from youtube_rss.models.source import Source, SourceBase
from youtube_rss.services.source import get_source_metadata

router = APIRouter()


@router.get("/", response_model=List[Source], status_code=status.HTTP_200_OK)
async def get_all() -> List[Source]:
    return source_crud.get_all()


@router.post("/", response_model=Source, status_code=status.HTTP_201_CREATED)
async def create(source_base: SourceBase) -> Source:
    source_metadata = get_source_metadata(url=source_base.url)

    source_dict = {
        "source_id": source_metadata["uploader_id"],
        "name": source_metadata["uploader"],
        "url": source_base.url,
    }
    source = Source(**source_dict)
    return source_crud.create(source)


@router.get("/{source_id}", response_model=Source)
async def get(source_id: str) -> Source:
    db_source = source_crud.get(source_id=source_id)
    if db_source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source Not Found")
    return db_source


@router.patch("/{source_id}", response_model=Source)
async def update(source_id: str, source: Source) -> Source:
    db_source = source_crud.get(source_id=source_id)
    if db_source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source Not Found")

    update_data = source.dict()
    for field in source.dict():
        if field in update_data:
            setattr(db_source, field, update_data[field])
    source_crud.update(db_source)
    return source


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(source_id: str) -> bool:
    db_source = source_crud.get(source_id=source_id)
    if db_source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source Not Found")
    return source_crud.delete(db_source)
