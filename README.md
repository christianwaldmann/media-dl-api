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
- Downloaded files get automatically deleted on the server after each request 


## Setup

The easiest way to get it up and running is via docker-compose:

````yaml
version: "3.8"

services:
    api:
        image: ghcr.io/christianwaldmann/media-dl-api:latest
        ports:
            - 8000:8000
        command: uvicorn app.main:app --host 0.0.0.0
        restart: always
````

## Usage

For a more detailed API documentation visit [http://localhost:8000/docs](http://localhost:8000/docs).

#### Download a video: `POST /download/video`

````
curl -X POST http://localhost:8000/download/video/ -H "Content-Type: application/json" -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}' -O -J
````

#### Download the audio of a video: `POST /download/audio`

````
curl -X POST http://localhost:8000/download/audio/ -H "Content-Type: application/json" -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}' -O -J
````

