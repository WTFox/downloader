import os

import requests
import structlog
from structlog import get_logger

from downloader.constants import Constants as c

log: structlog.stdlib.BoundLogger = get_logger(__name__)


def notify(message: str, title="Downloader", user=None, token=None, post=requests.post):
    """Send a notification to Pushover."""

    if not all([user, token]):
        user = os.environ.get("PUSHOVER_USER")
        token = os.environ.get("PUSHOVER_TOKEN")

        if not all([user, token]):
            log.warning("Pushover user and token not set. Not sending notification.")
            return

    log.info("Sending notification", message=message, title=title)
    return post(
        c.PUSHOVER_URL,
        data={
            "user": user,
            "token": token,
            "title": title,
            "message": message,
        },
    )
