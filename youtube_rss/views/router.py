from fastapi import APIRouter

from youtube_rss.views.endpoints import sources

views_router = APIRouter()
views_router.include_router(sources.router, tags=["Views"])
