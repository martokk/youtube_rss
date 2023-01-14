from pydantic import BaseSettings


class Settings(BaseSettings):
    # Environment Settings #
    env_name: str
    debug: bool

    # Log
    log_level: str

    # Database
    database_echo: bool

    # Server
    server_host: str
    server_port: int
    base_domain: str
    base_url: str
    proxy_host: str
    uvicorn_reload: bool
    uvicorn_entrypoint: str

    # API
    api_v1_prefix: str
    jwt_access_secret_key: str
    jwt_refresh_secret_key: str
    access_token_expire_minutes: int
    refresh_token_expire_minutes: int
    algorithm: str

    # Notify
    telegram_api_token: str
    telegram_chat_id: int
    notify_on_start: bool

    # Project Settings
    project_name: str
    project_description: str

    # Refresh Feeds
    refresh_sources_interval_minutes: int
    refresh_videos_interval_minutes: int
    max_video_age_hours: int

    # Build Feeds
    build_feed_recent_videos: int
    build_feed_dateafter: str
