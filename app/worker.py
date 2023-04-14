import os
from functools import partial
from copy import deepcopy

import yt_dlp
from celery import Celery
from celery.result import AsyncResult

from app.download import download, download_hook
from app.logger import get_logger
from app.models.Task import TaskFailure


logger = get_logger(__name__)


celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")


@celery.task(name="download_task", bind=True)
def download_task(self, video_url: str, output_dir: str, ydl_options: dict, fileext=None):
    logger.debug(f"Start download task for url \"{video_url}\"")

    # Add download hook for progress updates
    download_hook_ = partial(download_hook, task_obj=self)
    ydl_options["progress_hooks"] = [download_hook_]

    # Download file to disk on server (and update state while downloading)
    try:
        info = download(video_url, ydl_options)
    except yt_dlp.DownloadError:
        raise TaskFailure(f"Error downloading video \"{video_url}\". Video not found or other downloading error")

    # Get file name and path
    video_id = info["id"]
    if fileext:
        filename = f"{video_id}.{fileext}"
    else:
        video_ext = info["ext"]
        filename = f"{video_id}.{video_ext}"
    filepath = f"{output_dir}/{filename}"

    # Update meta data by adding filepath and filename
    task_result = AsyncResult(self.request.id)
    new_meta = deepcopy(task_result.info)
    new_meta["filepath"] = filepath
    new_meta["filename"] = filename
    return new_meta

