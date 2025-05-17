from fastapi import FastAPI, HTTPException
from structlog import get_logger

from downloader.logging.config import *  # noqa
from downloader.tasks import download_audio, download_video
from downloader.types import Download

log = get_logger(__name__)
app = FastAPI(docs_url=None, redoc_url=None)


@app.post("/video")
async def video(item: Download):
    if not item.url:
        raise HTTPException(status_code=400, detail="URL is required")

    log.info("Queued video", url=item.url, path=item.path)
    _ = download_video.delay(item.dict())
    return {"status": "queued video"}


@app.post("/audio")
async def audio(item: Download):
    if not item.url:
        raise HTTPException(status_code=400, detail="URL is required")

    log.info("Queued audio", url=item.url, path=item.path)
    _ = download_audio.delay(item.dict())
    return {"status": "queued audio"}
