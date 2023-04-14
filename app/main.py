import shutil
from pathlib import Path
from celery.result import AsyncResult
from fastapi import FastAPI, Depends, Request, HTTPException, status
from fastapi.responses import FileResponse
from tempfile import mkdtemp
import time
import uuid
from fastapi.middleware.cors import CORSMiddleware
from starlette.background import BackgroundTask

from app.logger import get_logger
from app.models.Task import Task, TaskOut
from app.models.Video import Video
from app.worker import download_task


logger = get_logger(__name__)


app = FastAPI(
    title="media-dl-api",
    description="",
)


origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://api:3000",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition", "Content-Length"]
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log every request to an endpoint
    """
    request_id = str(uuid.uuid4())[:8]
    logger.info(f"rid={request_id}, start request, path=\"{request.url.path}\", ip_address=\"{request.client.host}\"")
    start_time = time.time()

    response = await call_next(request)

    process_time = (time.time() - start_time) * 1000
    formatted_process_time = '{0:.2f}'.format(process_time)
    logger.info(f"rid={request_id}, end request, completed_in={formatted_process_time}ms, status_code={response.status_code}")
    return response


async def get_temp_dir():
    yield mkdtemp()


def remove_temp_dir(temp_dir):
    shutil.rmtree(temp_dir)


@app.post("/download/audio/", summary="start task to download audio from video", status_code=status.HTTP_202_ACCEPTED)
async def download_audio(video: Video, tempdirname: str = Depends(get_temp_dir)) -> Task:
    """
    Start task to download audio from a video.

    This will download the audio on the server to disk.
    """
    ydl_opts = {
        "writethumbnail": True,
        'format': 'bestaudio/best',
        "outtmpl": f"{tempdirname}/%(id)s.%(ext)s",
        "noplaylist": True,
        "prefer_ffmpeg": True,
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            },
            {
                'key': 'EmbedThumbnail',
            },
            {
                'key': 'FFmpegMetadata',
            }
        ],
    }
    task = download_task.delay(video.url, tempdirname, ydl_opts, fileext="mp3")
    return Task(id=task.id)


@app.post("/download/video/", summary="start task to download video", status_code=status.HTTP_202_ACCEPTED)
async def download_video(video: Video, tempdirname: str = Depends(get_temp_dir)) -> Task:
    """
    Start task to download video.

    This will download the video on the server to disk.
    """
    ydl_opts = {
        "writethumbnail": True,
        'format': '(bestvideo[width>=1920]/bestvideo)+bestaudio/best',
        "outtmpl": f"{tempdirname}/%(id)s.%(ext)s",
        "noplaylist": True,
        "prefer_ffmpeg": True,
    }
    task = download_task.delay(video.url, tempdirname, ydl_opts)
    return Task(id=task.id)


@app.get("/task/{task_id}/status", summary="get status information about a task")
async def get_status(task_id: str) -> TaskOut:
    """
    Get status information about a task.
    """
    result = AsyncResult(task_id)

    # Get downloaded and total bytes
    if result.state == "PROGRESS" or result.state == "SUCCESS":
        done = result.info.get("done", 0)
        total = result.info.get("total", 1)
    else:
        done = 0
        total = 0

    return TaskOut(
        id=result.task_id,
        status=result.status,
        done=done,
        total=total,
    )


@app.get("/task/{task_id}/file", summary="download the video/audio file from the server")
async def get_file(task_id: str) -> FileResponse:
    """
    Download the video/audio file from the server. Only available after the task finished successfully.

    This will delete the file on the server afterward.
    """
    task_result = AsyncResult(task_id)
    meta = task_result.result

    # Check that task is not currently running
    if task_result.state == "PROGRESS":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Task with id {task_id} is currently in progress and didn't finish yet")

    # Check that task is finished
    if not task_result.ready():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with id {task_id} doesn't exist")

    # Check that task finished successfully
    if task_result.status != "SUCCESS":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Task with id {task_id} exited with status {task_result.status}")

    # Check that file still exists
    if not Path(meta["filepath"]).exists():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"File \"{meta['filepath']}\" not found. Most likely there was already an earlier request wgich deleted the file.")

    # Send file to client and delete it on the server afterward
    temp_dir = Path(meta["filepath"]).parent
    return FileResponse(
        meta["filepath"],
        filename=meta["filename"],
        media_type="application/octet-stream",
        background=BackgroundTask(remove_temp_dir, temp_dir),
    )
    # TODO: right now files get only deleted after their first request -> if there is never any request, they dont get deleted --> idea: periodic cleanup


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
