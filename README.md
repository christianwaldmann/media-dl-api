<div align="center" width="100%">
    <h2>media-dl-api</h2>
    <p>API to download videos or just their audio</p>
    <a target="_blank" href="https://github.com/christianwaldmann/media-dl-api/actions"><img src="https://img.shields.io/github/actions/workflow/status/christianwaldmann/media-dl-api/publish.yml" /></a>
<!--     <a target="_blank" href="https://github.com/christianwaldmann/media-dl-api/stargazers"><img src="https://img.shields.io/github/stars/christianwaldmann/media-dl-api" /></a> -->
    <a target="_blank" href="https://github.com/christianwaldmann/media-dl-api/tags"><img src="https://img.shields.io/github/v/tag/christianwaldmann/media-dl-api" /></a>
    <a target="_blank" href="https://github.com/christianwaldmann/media-dl-api/blob/main/LICENSE"><img src="https://img.shields.io/github/license/christianwaldmann/media-dl-api" /></a>
    <a target="_blank" href="https://github.com/christianwaldmann/media-dl-api/commits/master"><img src="https://img.shields.io/github/last-commit/christianwaldmann/media-dl-api" /></a>
</div>

## Features

- Endpoints to download videos or a video's audio
- Easy to use


## Setup

The easiest way to get it up and running is via docker-compose:

````yaml
services:
    api:
        build: ghcr.io/christianwaldmann/media-dl-api:latest
        ports:
            - 8000:8000
        command: uvicorn app.main:app --host 0.0.0.0
        restart: always
        volumes:
            - temp-download-dir:/tmp
        environment:
            - CELERY_BROKER_URL=redis://redis:6379/0
            - CELERY_RESULT_BACKEND=redis://redis:6379/0
        depends_on:
            -   redis

    worker:
        build: ghcr.io/christianwaldmann/media-dl-api:latest
        command: celery --app=app.worker.celery worker --loglevel=info
        restart: always
        volumes:
            - temp-download-dir:/tmp
        environment:
            - CELERY_BROKER_URL=redis://redis:6379/0
            - CELERY_RESULT_BACKEND=redis://redis:6379/0
        depends_on:
            - api
            - redis

    redis:
        image: redis:6-alpine
        restart: always

volumes:
    temp-download-dir:

````

## Usage

For a more detailed API documentation visit [http://localhost:8000/docs](http://localhost:8000/docs).

#### Start task to download video: `POST /download/video/`

````
curl -X POST http://localhost:8000/download/video/ -H "Content-Type: application/json" -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
````

#### Start task to download the audio of a video: `POST /download/audio/`

````
curl -X POST http://localhost:8000/download/audio/ -H "Content-Type: application/json" -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
````

#### Get task status: `GET /task/<task_id>/status/`

````
curl http://localhost:8000/task/<task_id>/status/
````

#### Download file: `GET /task/<task_id>/file/`

````
curl http://localhost:8000/task/<task_id>/file/ -O -J
````
