FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# ローカルマシン(日本) のときは効果あるかも
# RUN sed -i 's@archive.ubuntu.com@ftp.jaist.ac.jp/pub/Linux@g' /etc/apt/sources.list
#一旦play.pyの導入は見送るのでとりあえずffmpegはコメントアウト
#RUN apt-get update \
#    && apt-get -y upgrade \
#    && apt-get install -y ffmpeg

# COPY したいファイルは明示的に書く
WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src/

RUN uv sync --frozen

ENTRYPOINT ["uv", "run", "python", "main.py"]
CMD []
