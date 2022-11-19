FROM python:3.11

WORKDIR /app
COPY requirements.txt /app

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

RUN apt update \
    && apt -y upgrade \
    && apt install -y ffmpeg
