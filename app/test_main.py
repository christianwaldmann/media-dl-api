from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_download_audio():
    response = client.post(
        "/download/audio/",
        json={"url": "https://www.youtube.com/watch?v=Xr10hMoFngQ"}
    )
    assert response.status_code == 200


def test_download_audio_invalid_url():
    response = client.post(
        "/download/audio/",
        json={"url": "https://www.youtube.com/watch?v=aaaaaaaaaaa"}
    )
    assert response.status_code == 404


def test_download_video():
    response = client.post(
        "/download/video/",
        json={"url": "https://www.youtube.com/watch?v=Xr10hMoFngQ"}
    )
    assert response.status_code == 200


def test_download_video_invalid_url():
    response = client.post(
        "/download/video/",
        json={"url": "https://www.youtube.com/watch?v=aaaaaaaaaaa"}
    )
    assert response.status_code == 404


def test_url_audio():
    response = client.post(
        "/url/audio/",
        json={"url": "https://www.youtube.com/watch?v=Xr10hMoFngQ"}
    )
    assert response.status_code == 200


def test_url_audio_invalid_url():
    response = client.post(
        "/url/audio/",
        json={"url": "https://www.youtube.com/watch?v=aaaaaaaaaaa"}
    )
    assert response.status_code == 404


def test_url_video():
    response = client.post(
        "/url/video/",
        json={"url": "https://www.youtube.com/watch?v=Xr10hMoFngQ"}
    )
    assert response.status_code == 404


def test_url_video_invalid_url():
    response = client.post(
        "/url/video/",
        json={"url": "https://www.youtube.com/watch?v=aaaaaaaaaaa"}
    )
    assert response.status_code == 404
