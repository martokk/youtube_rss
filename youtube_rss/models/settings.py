from pydantic import BaseSettings


class Settings(BaseSettings):
    # Environment Settings #
    env_name: str = "Unknown"
    debug: bool = True

    # Log
    log_level: str = "INFO"

    # Database
    database_echo: bool = False

    # Server
    server_host: str = "0.0.0.0"
    server_port: int = 5000
    base_domain: str = "localhost:5000"
    base_url: str = "http://localhost:5000"
    proxy_host: str = "127.0.0.1"
    uvicorn_reload: bool = True
    uvicorn_entrypoint: str = "youtube_rss.core.app:app"

    # API
    api_v1_prefix: str = "/api/v1"
    jwt_access_secret_key: str = "jwt_access_secret_key"
    jwt_refresh_secret_key: str = "jwt_refresh_secret_key"
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 10080
    algorithm: str = "HS256"

    # Notify
    telegram_api_token: str = ""
    telegram_chat_id: int = 0
    notify_on_start: bool = True

    # Project Settings
    project_name: str = "Project Name"
    project_description: str = "Project description."

    # Refresh Feeds
    refresh_sources_interval_minutes: int = 15
    refresh_videos_interval_minutes: int = 30
    max_video_age_hours: int = 8

    # Build Feeds
    build_feed_recent_videos: int = 10
    build_feed_dateafter: str = "now-2month"
