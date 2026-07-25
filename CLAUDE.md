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
- 旧2代目サービス(`nidaime-takohachi`)は削除済み。`takohachi`サービスのみが本番。

### PR Environments (プレビュー環境)

PR を作成すると、Railway が自動でテスト用の環境を立ち上げ、テスト用 Bot が Discord 上にオンラインになる。PR をクローズ/マージすると環境は自動で削除される。

- Railway の Project Settings > Environments > PR Environments が有効
- Base Environment に `pr-base`(`production` を複製し、`TOKEN` のみテスト用 Bot のトークンに差し替えた環境)を指定している
  - `pr-base` 自体は変数のテンプレートとしてのみ存在し、Auto Deploy は無効化・デプロイは Remove 済み（実際に Bot として起動させない）
- `TOKEN` 以外の変数(`GUILD_ID` や各チャンネル/VC ID 等)は本番と共通のため、テスト用 Bot は本番と同じ Discord サーバー・チャンネルで動く
  - `pr-base` の `TOKEN` を更新した場合、既存の PR 環境には反映されない（環境作成時にコピーされるだけのため）。反映するには PR 環境を作り直す（PR を close → reopen、または PR 環境を手動削除して再生成）
- wt_task や autodelete などの定期実行タスクは PR 環境でも動作し、本番と重複投稿する可能性がある(現時点では許容している)
- Railway 側のインフラは PR クローズ時に自動削除されるが、GitHub 側の Deployments レコード（`takohachi / takohachi-pr-{PR番号}` という environment 名で作られる）は残り続けて蓄積する
  - `.github/workflows/cleanup-pr-environment.yml` が PR クローズ(マージ含む)をトリガーに、対応する deployment を inactive 化した上で削除する

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
