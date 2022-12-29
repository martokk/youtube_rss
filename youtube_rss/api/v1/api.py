from fastapi import APIRouter

from youtube_rss.api.v1.endpoints import feed, mp4, source, video

api_router = APIRouter()
api_router.include_router(video.router, prefix="/video", tags=["Video"])
api_router.include_router(source.router, prefix="/source", tags=["Source"])
api_router.include_router(feed.router, prefix="/feed", tags=["Feed"])
api_router.include_router(mp4.router, prefix="/mp4", tags=["Mp4"])
