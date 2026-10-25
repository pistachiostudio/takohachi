FROM python:3.12-slim-bookworm
# uv のイメージはバージョンとダイジェストで固定する(:latest だと中身が知らないうちに差し替わりうる)
COPY --from=ghcr.io/astral-sh/uv:0.13.5@sha256:32a7bb39b496babbd997b0a39a4d66c126bdaf5661b302bf6f06abda8deca6ff /uv /uvx /bin/

# Railwayのようにコンテナのstdout/stderrをログとして収集する環境で
# print/loggingの出力がバッファに溜まって見えなくなるのを防ぐ
ENV PYTHONUNBUFFERED=1

# COPY したいファイルは明示的に書く
WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src/

# 本番イメージには開発用の依存(pytest, pre-commit など)を入れない
RUN uv sync --frozen --no-dev && mkdir -p /data /logs

ENTRYPOINT ["uv", "run", "--frozen", "--no-dev", "python", "src/main.py"]
CMD []
