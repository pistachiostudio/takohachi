FROM python:3.11-slim as build

RUN python -m pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.in-project true && \
    rm -rf /root/.cache/pypoetry

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN poetry install --only main

FROM python:3.11-alpine

# ローカルマシン(日本) のときは効果あるかも
# RUN sed -i 's@archive.ubuntu.com@ftp.jaist.ac.jp/pub/Linux@g' /etc/apt/sources.list
#一旦play.pyの導入は見送るのでとりあえずffmpegはコメントアウト
#RUN apt-get update \
#    && apt-get -y upgrade \
#    && apt-get install -y ffmpeg

COPY --from=build /app/.venv /app/.venv

COPY src /app
WORKDIR /app

ENTRYPOINT ["/app/.venv/bin/python", "main.py"]
CMD []
