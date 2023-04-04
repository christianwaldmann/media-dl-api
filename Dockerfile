FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9
WORKDIR /App
ENV PYTHONUNBUFFERED 1
RUN apt-get -y update
RUN apt-get install -y ffmpeg
COPY ./requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . .
