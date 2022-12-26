import os

from youtube_rss.config import SERVER_IP, SERVER_PORT

PACKAGE_NAME = "youtube_rss"
PACKAGE_DESCRIPTION = "A python project created by Martokk."
BASE_DOMAIN = str(os.environ.get("BASE_DOMAIN", f"http://{SERVER_IP}:{SERVER_PORT}"))
