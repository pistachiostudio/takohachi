ARG PYTHON_ENV=python:3.11-slim


FROM $PYTHON_ENV as build

RUN pip install poetry && poetry config virtualenvs.in-project true

RUN mkdir -p /app
WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN poetry install --only main


FROM $PYTHON_ENV as prod

# ローカルマシン(日本) のときは効果あるかも
# RUN sed -i 's@archive.ubuntu.com@ftp.jaist.ac.jp/pub/Linux@g' /etc/apt/sources.list
#一旦play.pyの導入は見送るのでとりあえずffmpegはコメントアウト
#RUN apt-get update \
#    && apt-get -y upgrade \
#    && apt-get install -y ffmpeg

COPY --from=build /app/.venv /app/.venv

COPY src /app
WORKDIR /app

ENTRYPOINT ["./.venv/bin/python"]
CMD ["main.py"]

