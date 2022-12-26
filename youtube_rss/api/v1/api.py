from fastapi import APIRouter

from youtube_rss.api.v1.endpoints import feed, source, video

api_router = APIRouter()
api_router.include_router(video.router, prefix="/video", tags=["Video"])
api_router.include_router(source.router, prefix="/source", tags=["Source"])
api_router.include_router(feed.router, prefix="/feed", tags=["Feed"])
