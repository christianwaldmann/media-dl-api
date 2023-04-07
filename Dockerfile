FROM python:3.9-slim-buster
WORKDIR /app
ENV PYTHONUNBUFFERED 1
RUN apt-get -y update && apt-get install -y ffmpeg
COPY ./requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY ./app ./app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
