import os

from dotenv import load_dotenv

from youtube_rss.paths import ENV_FILE

# --- Load Environment
load_dotenv(dotenv_path=ENV_FILE)

# --- Bind Environment variables

# Server
SERVER_IP = str(os.environ.get("SERVER_IP", "0.0.0.0"))
SERVER_PORT = int(os.environ.get("SERVER_PORT", 5000))
BASE_DOMAIN = str(os.environ.get("BASE_DOMAIN", f"{SERVER_IP}:{SERVER_PORT}"))
BASE_URL = str(os.environ.get("BASE_URL", f"http://{BASE_DOMAIN}"))

# Proxy
PROXY_HOST = str(os.environ.get("PROXY_HOST", "localhost"))

# Database
DATABASE_ECHO = os.environ.get("DATABASE_ECHO", "True") == "True"

# Cache
USE_CACHE = bool(os.environ.get("USE_CACHE", True))
BUILD_FEED_CACHE_INTERVAL_MINUTES = int(os.environ.get("BUILD_FEED_CACHE_INTERVAL_MINUTES", 10))

# Build Feed
BUILD_FEED_RECENT_VIDEOS = int(os.environ.get("BUILD_FEED_RECENT_VIDEOS", 20))
BUILD_FEED_DATEAFTER = str(os.environ.get("BUILD_FEED_DATEAFTER", "now-2month"))
