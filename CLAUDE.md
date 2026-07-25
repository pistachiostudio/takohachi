# CLAUDE.md

このファイルは、このリポジトリで作業する Claude Code (claude.ai/code) に向けたガイダンスです。

## 🚫 Git操作に関する重要なルール

- **絶対にユーザーの明示的な指示なしに `git commit` や `git push` を実行しないこと。**
- **プルリクエストの作成も、ユーザーの明示的な指示があるまで行わないこと。**
- 変更内容の提案・実装までは自律的に進めてよいが、それをコミット・プッシュ・PR化するかどうかは必ずユーザーに確認する。
- 「これでコミットして」「PRを作って」のように明示的に指示された場合のみ実行する。過去に一度許可されたからといって、以降も同様の操作を無許可で行ってよいわけではない。

## プロジェクト概要

Takohachi (たこ八) は、Discordサーバー「ピスタチオゲーム部親睦会」向けのユースレスDiscord Bot。Python + discord.py で実装されている。

- 依存管理: [uv](https://docs.astral.sh/uv/)
- Python: 3.12
- 主要ライブラリ: discord.py, gspread, spotipy, httpx など
- 各機能(Cog)の一覧は [src/cogs/README.md](src/cogs/README.md) を参照

## デプロイ

- 本番環境は **Railway** にデプロイされている。
- `main` ブランチへの push をトリガーに Railway 側の連携で自動ビルド・デプロイされる。
- Lightsail 時代の SSH デプロイ用ワークフロー(`.github/workflows/deploy.yml`)は Railway 移行に伴い削除済み。
- PR Environments を検証中（動作確認のための無害な変更）。

## 開発コマンド

```bash
# 依存関係のインストール
uv sync

# テスト実行
uv run pytest tests

# Lint / Format チェック (pre-commit)
uv run pre-commit run --all-files

# Docker Composeでのローカル起動
docker compose up -d
```

## CI

- `.github/workflows/ci.yml` : push / PR で `pre-commit` と `pytest` を実行。
