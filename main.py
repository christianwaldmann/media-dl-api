from fastapi import FastAPI, Depends
from fastapi.responses import  FileResponse
from tempfile import TemporaryDirectory
from yt_dlp import DownloadError, YoutubeDL


app = FastAPI()


async def get_temp_dir():
    tempdir = TemporaryDirectory()
    try:
        yield tempdir.name
    finally:
        tempdir.cleanup()


@app.get("/download/audio/{video_url:path}", summary="download audio from a youtube video")
async def download_video(video_url: str, tempdirname: str = Depends(get_temp_dir)):
    """
    Download audio from a youtube video.

    This will download the audio on the server temporarily to disk and then send it to the client.
    """
    # def dl_progress_hook(d):
    #     global dl_progress
    #     if d["status"] == "downloading" and d["downloaded_bytes"] > 0:
    #         return StreamingResponse(iterfile(filepath), media_type="video/mp4")

    ydl_opts = {
        'format': 'bestaudio/best',
        "outtmpl": f"{tempdirname}/%(id)s.%(ext)s",
        "noplaylist": True,
        "verbose": True,
        # "progress_hooks": [dl_progress_hook],
    }

    # Download file to disk on server (temporary directory)
    try:
        with YoutubeDL(ydl_opts) as dl:
            meta = dl.extract_info(video_url, download=True)
    except DownloadError as e:
        raise e

    # Send file from server to client
    video_id = meta["id"]
    video_ext = meta["ext"]
    filename = f"{video_id}.{video_ext}"
    filepath = f"{tempdirname}/{filename}"
    return FileResponse(filepath, filename=filename)


@app.get("/download/url/{video_url:path}", summary="get the download url for the audio from a youtube video")
async def download_url(video_url: str):
    """
    Get the download url for the audio from a youtube video.
    """
    ydl_opts = {
        'format': 'bestaudio/best',
        "noplaylist": True,
    }

    # Get download url
    with YoutubeDL(ydl_opts) as ydl:
        song_info = ydl.extract_info(video_url, download=False)

    # Send download url to client
    audio_url = song_info["url"]
    return {
        "url": audio_url
    }
