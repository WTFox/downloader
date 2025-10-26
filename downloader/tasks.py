import os
import subprocess
from datetime import datetime

import structlog
from celery import Celery
from structlog import get_logger
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

from downloader.constants import constants as c
from downloader.database import get_session_context
from downloader.logging.config import *  # noqa
from downloader.models import DownloadLog
from downloader.pushover import notify

log: structlog.stdlib.BoundLogger = get_logger(__name__)
worker = Celery(__name__, broker=f"redis://{os.getenv('REDIS_HOST')}:6379/0")


@worker.task
def download_video(item: dict[str, str]):
    cmd = c.yt_dlp_video_cmd(item["url"], item["path"])
    download(item["url"], cmd, "Video")


@worker.task
def download_audio(item: dict[str, str]):
    cmd = c.yt_dlp_audio_cmd(item["url"], item["path"])
    download(item["url"], cmd, "Audio")


def download(url: str, cmd: list[str], media_type: str):
    # Create download log entry
    download_log = create_download_log(url, media_type)

    # Get notification message and metadata
    msg, duration_seconds = notify_msg_from_url(url)
    if duration_seconds is not None:
        download_log.duration_seconds = duration_seconds

    notify(title=f"Downloader [{media_type}]", message=msg)
    log.info("Running command [%s]: %s", media_type, " ".join(cmd))

    # Update status to processing
    update_download_log(download_log.id, status="processing", started_at=datetime.utcnow())

    # Execute download
    ret = subprocess.call(cmd)
    if ret != 0:
        log.error("Failed to download [%s] %s", media_type, url)
        update_download_log(
            download_log.id,
            success=False,
            status="failed",
            completed_at=datetime.utcnow(),
            error_message="Download command failed",
        )
        notify(title=f"Downloader [{media_type}]", message=f"Failed to download {url}")
        return

    log.info("Finished downloading [%s] %s", media_type, url)

    # Extract output path from command (it follows the -o flag)
    output_path = None
    try:
        o_index = cmd.index("-o")
        if o_index + 1 < len(cmd):
            output_path = cmd[o_index + 1]
    except (ValueError, IndexError):
        pass

    # Update download log with success
    update_download_log(
        download_log.id,
        success=True,
        status="completed",
        completed_at=datetime.utcnow(),
        output_path=output_path,
    )

    notify(title=f"Downloader [{media_type}]", message=f"Finished downloading {url}")


def create_download_log(url: str, media_type: str) -> DownloadLog:
    """Create a new download log entry."""
    try:
        with get_session_context() as session:
            download_log = DownloadLog(
                url=url,
                download_type=media_type,
                status="queued",
                requested_at=datetime.utcnow(),
            )
            session.add(download_log)
            session.flush()
            log_id = download_log.id
    except Exception as e:
        log.error("Failed to create download log entry: %s", e)
        raise

    return DownloadLog(id=log_id, url=url, download_type=media_type)


def update_download_log(
    log_id,
    status: str = None,
    success: bool = None,
    started_at: datetime = None,
    completed_at: datetime = None,
    error_message: str = None,
    output_path: str = None,
    file_size_bytes: int = None,
):
    """Update an existing download log entry."""
    try:
        with get_session_context() as session:
            download_log = session.query(DownloadLog).filter(DownloadLog.id == log_id).first()
            if not download_log:
                log.warning("Download log entry not found: %s", log_id)
                return

            if status is not None:
                download_log.status = status
            if success is not None:
                download_log.success = success
            if started_at is not None:
                download_log.started_at = started_at
            if completed_at is not None:
                download_log.completed_at = completed_at
            if error_message is not None:
                download_log.error_message = error_message
            if output_path is not None:
                download_log.output_path = output_path
            if file_size_bytes is not None:
                download_log.file_size_bytes = file_size_bytes

            session.commit()
    except Exception as e:
        log.error("Failed to update download log entry: %s", e)


def notify_msg_from_url(url: str) -> tuple[str, float | None]:
    """Get notification message and metadata from URL.

    Returns:
        Tuple of (message, duration_seconds)
    """
    duration_seconds = None
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
        duration_seconds = video_info.get("duration")  # Duration in seconds
        msg = f"[{extractor_key}]: {channel}: {fulltitle}\n{duration_string}\n{url}"

    except DownloadError as e:
        log.error("Failed to get video info: %s", e)
        msg = url

    return msg, duration_seconds
