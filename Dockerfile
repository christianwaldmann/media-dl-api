FROM python:3.9
WORKDIR /app
ENV PYTHONUNBUFFERED 1
RUN apt-get -y update
RUN apt-get install -y ffmpeg
COPY ./requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
