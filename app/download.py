import yt_dlp


def download(video_url, ydl_options):
    """
    Download file to disk
    """
    with yt_dlp.YoutubeDL(ydl_options) as dl:
        info = dl.extract_info(video_url, download=True)
    return info


def download_hook(d, task_obj):
    if d["status"] == "finished":
        return
    if d["status"] == "downloading":
        downloaded_bytes = d["downloaded_bytes"]
        total_bytes = d["total_bytes_estimate"]
        task_obj.update_state(state="PROGRESS", meta={"done": downloaded_bytes, "total": total_bytes})
