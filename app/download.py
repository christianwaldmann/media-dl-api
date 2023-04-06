import yt_dlp


def download(video_url, ydl_options):
    """
    Download file to disk
    """
    with yt_dlp.YoutubeDL(ydl_options) as dl:
        info = dl.extract_info(video_url, download=True)
    return info


def get_download_url(video_url, ydl_options):
    """
    Get download url
    """
    with yt_dlp.YoutubeDL(ydl_options) as ydl:
        info = ydl.extract_info(video_url, download=False)

    try:
        url = info["url"]
    except KeyError:
        raise ValueError(f"No download url found for video \"{video_url}\"")
    return url
