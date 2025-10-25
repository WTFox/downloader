import os
import subprocess

import structlog
from celery import Celery
from structlog import get_logger
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

from downloader.constants import constants as c
from downloader.logging.config import *  # noqa
from downloader.pushover import notify

log: structlog.stdlib.BoundLogger = get_logger(__name__)
worker = Celery(__name__, broker=f"redis://{os.getenv("REDIS_HOST")}:6379/0")


@worker.task
def download_video(item: dict[str, str]):
    cmd = c.yt_dlp_video_cmd(item["url"], item["path"])
    download(item["url"], cmd, "Video")


@worker.task
def download_audio(item: dict[str, str]):
    cmd = c.yt_dlp_audio_cmd(item["url"], item["path"])
    download(item["url"], cmd, "Audio")


def download(url: str, cmd: list[str], media_type: str):
    msg = notify_msg_from_url(url)
    notify(title=f"Downloader [{media_type}]", message=msg)
    log.info("Running command [%s]: %s", media_type, " ".join(cmd))
    ret = subprocess.call(cmd)
    if ret != 0:
        log.error("Failed to download [%s] %s", media_type, url)
        notify(title=f"Downloader [{media_type}]", message=f"Failed to download {url}")
        return

    log.info("Finished downloading [%s] %s", media_type, url)
    notify(title=f"Downloader [{media_type}]", message=f"Finished downloading {url}")


def notify_msg_from_url(url: str):
    try:
        log.info("Getting info for %s", url)
        video_info = YoutubeDL({"cookiefile": "/Goodz/Misc/cookies.txt"}).extract_info(
            url,
            download=False,  # type: ignore
        )
        if video_info is None:
            raise DownloadError("No info")

        fulltitle, channel, duration_string, extractor_key = (
            video_info.get("fulltitle"),
            video_info.get("channel"),
            video_info.get("duration_string"),
            video_info.get("extractor_key"),
        )
        msg = f"[{extractor_key}]: {channel}: {fulltitle}\n{duration_string}\n{url}"

    except DownloadError as e:
        log.error("Failed to get video info: %s", e)
        msg = url

    return msg
