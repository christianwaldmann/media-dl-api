from fastapi import FastAPI, Depends
from fastapi.responses import FileResponse
from tempfile import TemporaryDirectory
from yt_dlp import DownloadError, YoutubeDL


app = FastAPI(
    title="Youtube Download API",
    description="",
    version="0.0.1"
)


async def get_temp_dir():
    tempdir = TemporaryDirectory()
    try:
        yield tempdir.name
    finally:
        tempdir.cleanup()


@app.get("/download/audio/{video_url:path}", summary="download audio from a youtube video")
async def download_audio(video_url: str, tempdirname: str = Depends(get_temp_dir)) -> FileResponse:
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
    # print(help(YoutubeDL))
    return _download_and_send_to_client(video_url, tempdirname, ydl_opts, fileext="mp3")


@app.get("/download/video/{video_url:path}", summary="download youtube video")
async def download_video(video_url: str, tempdirname: str = Depends(get_temp_dir)) -> FileResponse:
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
        with YoutubeDL(ydl_options) as dl:
            info = dl.extract_info(video_url, download=True)
    except DownloadError as e:
        raise e

    # Send file from server to client
    video_id = info["id"]
    if fileext:
        filename = f"{video_id}.{fileext}"
    else:
        video_ext = info["ext"]
        filename = f"{video_id}.{video_ext}"
    filepath = f"{output_dir}/{filename}"
    return FileResponse(filepath, filename=filename)


@app.get("/url/audio/{video_url:path}", summary="get the download url for the audio from a youtube video")
async def download_url_audio(video_url: str) -> str:
    """
    Get the download url for the audio from a youtube video.
    """
    ydl_opts = {
        'format': 'bestaudio/best',
        "noplaylist": True,
    }
    return _get_download_url(video_url, ydl_opts)


@app.get("/url/video/{video_url:path}", summary="get the download url for a youtube video")
async def download_url_video(video_url: str) -> str:
    """
    Get the download url for a youtube video.
    """
    ydl_opts = {
        'format': '(bestvideo[width>=1920]/bestvideo)+bestaudio/best',
        "noplaylist": True,
    }
    return _get_download_url(video_url, ydl_opts)


def _get_download_url(video_url, ydl_options):
    with YoutubeDL(ydl_options) as ydl:
        info = ydl.extract_info(video_url, download=False)

    # Send download url to client
    url = info.get("url", "None")
    return url
