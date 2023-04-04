from fastapi import FastAPI, Depends, Request
from fastapi.responses import FileResponse
from tempfile import TemporaryDirectory
import yt_dlp
import uvicorn
import logging
import time
import uuid


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
file_handler = logging.FileHandler('log.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


app = FastAPI(
    title="Youtube Download API",
    description="",
    version="0.0.1"
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log every request to an endpoint
    """
    request_id = str(uuid.uuid4())[:8]
    logger.info(f"rid={request_id}, start request, path=\"{request.url.path}\"")
    start_time = time.time()

    response = await call_next(request)

    process_time = (time.time() - start_time) * 1000
    formatted_process_time = '{0:.2f}'.format(process_time)
    logger.info(f"rid={request_id}, end request, completed_in={formatted_process_time}ms, status_code={response.status_code}")
    return response


async def get_temp_dir():
    tempdir = TemporaryDirectory()
    try:
        yield tempdir.name
    finally:
        tempdir.cleanup()


@app.get("/download/audio/{video_url:path}", summary="download audio from a youtube video")
async def download_audio(video_url: str, request: Request, tempdirname: str = Depends(get_temp_dir)) -> FileResponse:
    """
    Download audio from a youtube video.

    This will download the audio on the server temporarily to disk and then send it to the client.
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
    return _download_and_send_to_client(video_url, tempdirname, ydl_opts, fileext="mp3")


@app.get("/download/video/{video_url:path}", summary="download youtube video")
async def download_video(video_url: str, request: Request, tempdirname: str = Depends(get_temp_dir)) -> FileResponse:
    """
    Download youtube video.

    This will download the video on the server temporarily to disk and then send it to the client.
    """
    ydl_opts = {
        "writethumbnail": True,
        'format': '(bestvideo[width>=1920]/bestvideo)+bestaudio/best',
        "outtmpl": f"{tempdirname}/%(id)s.%(ext)s",
        "noplaylist": True,
        "prefer_ffmpeg": True,
    }
    return _download_and_send_to_client(video_url, tempdirname, ydl_opts)


def _download_and_send_to_client(video_url, output_dir, ydl_options, fileext=None):
    # Download file to disk on server
    try:
        with yt_dlp.YoutubeDL(ydl_options) as dl:
            info = dl.extract_info(video_url, download=True)
    except yt_dlp.DownloadError as e:
        raise e

    # Send file from server to client
    video_id = info["id"]
    if fileext:
        filename = f"{video_id}.{fileext}"
    else:
        video_ext = info["ext"]
        filename = f"{video_id}.{video_ext}"
    filepath = f"{output_dir}/{filename}"
    logger.debug(f"downloaded video \"{video_url}\"")
    return FileResponse(filepath, filename=filename)


@app.get("/url/audio/{video_url:path}", summary="get the download url for the audio from a youtube video")
async def download_url_audio(video_url: str, request: Request) -> str:
    """
    Get the download url for the audio from a youtube video.
    """
    ydl_opts = {
        'format': 'bestaudio/best',
        "noplaylist": True,
    }
    return _get_download_url(video_url, ydl_opts)


@app.get("/url/video/{video_url:path}", summary="get the download url for a youtube video")
async def download_url_video(video_url: str, request: Request) -> str:
    """
    Get the download url for a youtube video.
    """
    ydl_opts = {
        'format': '(bestvideo[width>=1920]/bestvideo)+bestaudio/best',
        "noplaylist": True,
    }
    return _get_download_url(video_url, ydl_opts)


def _get_download_url(video_url, ydl_options):
    with yt_dlp.YoutubeDL(ydl_options) as ydl:
        info = ydl.extract_info(video_url, download=False)

    # Send download url to client
    url = info.get("url", "None")
    logger.debug(f"extracted url from video \"{video_url}\": \"{url}\"")
    return url
