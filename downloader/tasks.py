import subprocess
from typing import List

from celery import Celery
from structlog import get_logger
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

from downloader.constants import constants as c
from downloader.logging.config import *  # noqa
from downloader.pushover import notify

log = get_logger(__name__)
worker = Celery(__name__, broker="redis://redis:6379/0")


@worker.task
def download_video(url: str):
    cmd = c.yt_dlp_video_cmd(url)
    download(url, cmd)


@worker.task
def download_audio(url: str):
    cmd = c.yt_dlp_audio_cmd(url)
    download(url, cmd)


def download(url: str, cmd: List[str]):
    msg = notify_msg_from_url(url)
    notify(msg)
    log.info("Running command: %s", " ".join(cmd))
    ret = subprocess.call(cmd)
    if ret != 0:
        log.error("Failed to download %s", url)
        notify(f"Failed to download {url}")
        return

    log.info("Finished downloading %s", url)
    notify(f"Finished downloading {url}")


def notify_msg_from_url(url: str):
    try:
        log.info("Getting video info for %s", url)
        video_info = YoutubeDL().extract_info(url, download=False)
        if video_info is None:
            raise DownloadError("No video info")

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
