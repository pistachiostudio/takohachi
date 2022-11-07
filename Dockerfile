FROM python:3.11

WORKDIR /app
COPY requirements.txt /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
