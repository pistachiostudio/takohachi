<samp>
<p align="center">
<img src="./images/takohachi_w_senjafuda.png" width="250px">
</p>

# <p align="center">🐙 Takohachi 🐙</p>

<p align="center">
<a href="https://github.com/search?q=repo%3Apistachiostudio%2Ftakohachi++language%3APython&type=code"><img alt="GitHub top language" src="https://img.shields.io/github/languages/top/pistachiostudio/takohachi"></a>
<a href="https://github.com/pistachiostudio/takohachi/actions/workflows/ci.yml"><img alt="GitHub Workflow Status" src="https://github.com/pistachiostudio/takohachi/actions/workflows/ci.yml/badge.svg"></a>
<a href="https://github.com/charliermarsh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json" alt="Ruff" style="max-width:100%;"></a>
<a href="https://github.com/pistachiostudio/takohachi/issues"><img alt="GitHub issues" src="https://img.shields.io/github/issues/pistachiostudio/takohachi"></a>
<a href="https://discord.gg/pistachiogaming"><img alt="Discord" src="https://img.shields.io/discord/731366036649279518"></a>
<a href="https://open.vscode.dev/pistachiostudio/takohachi"><img alt="open in vscode" src="https://img.shields.io/badge/codes-open%20in%20VSCode-blue"></a>
</p>
<p align="center">Takohachi is useless Discord bot.<br>But he has romance.</p>


## 🐙 About

これは[ピスタチオゲーム部親睦会](https://discord.gg/pistachiogaming)というDiscordサーバーのためのユースレスBotです。

## ⚙ Functions

https://github.com/pistachiostudio/takohachi/tree/main/src/cogs

## 🪂 installing Packages & Dependencies

### With uv🌾

[An extremely fast Python package and project manager, written in Rust.](https://docs.astral.sh/uv/)


```bash
$ uv sync
```

## 🚄 Auto deployment on Railway

Takohachi は現在 [Railway](https://railway.app/) にデプロイされている。

- `main` ブランチへの push をトリガーに、Railway 側の連携によって自動でビルド・デプロイされる。
- ビルドはリポジトリの [Dockerfile](./Dockerfile) を使用。
- 環境変数は Railway プロジェクトの Variables で管理する（詳細は下記「Create `.env` file」を参照）。

```mermaid
flowchart LR

Z(Codes)
B(main<br>branch)
C(Docker Build)
D[(SQLite)]
I(Env Vars)
J(((Discord)))

subgraph Local
Z
end

subgraph GitHub
B
end

subgraph Railway
C
D
I
end

Z -- Push --> B
B -- Auto deploy --> C
I -- inject --> C
C o--o D
C <--> J
```

## 🐳 Local Development with Docker

Railway 上の本番環境とは別に、ローカルでも同じ Dockerfile を使って動作確認ができる。

### 1. Clone this repository

```bash
$ git clone https://github.com/pistachiostudio/takohachi.git
```

### 2. Create `.env` file on the root directory

```bash
OPENAI_API_KEY=''
TOKEN=''
PREFIX='!!'
CARDCOUNT_KEY=''
CLIENT_SECRET=''
DATABASE_URL=''
DIC_KEY=''
DRIVE_FOLDER_ID=''
GOOGLE_APPLICATION_CREDENTIALS=''
INU_VC_ID=''
NEKO_VC_ID=''
KAME_VC_ID=''
KYORYU_VC_ID=''
LOG_TEXT_CHANNEL_ID=''
SPOTIFY_CLIENT_ID=''
SPOTIFY_CLIENT_SECRET=''
SSLADD_KEY=''
TAKOHACHI_JSON=''
TRN_API_KEY=''
```

### 3. Run

```bash
$ docker compose up -d
```

🔫 Yeah_bot_is_on_ready!!

## 🎨 Icons
| by [Go Inagaki](https://hodwn.com/go-inagaki/)                                                                                 | by [Imoya](https://twitter.com/arakudai2)                                                                                      |
| ------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| <img src="./images/icon_tako_hachi_BG_less.png" width="500px"> | <img src="./images/imo_takohachi_bgless.png" width="500px"> |


## 🐕 Pistachio Studio

川崎のヒップホップ/録音/プロデューサーチーム。ヒップホップクルー = [CBS](https://youtu.be/A3oshdbRbBI)とそのバックバンドChicken Is Niceを中心に15年以上活動中。
全員30超え、仕事あり、家庭あり、ガキもあり、ペットもあり、かなり限界ながらも活動中。
[chelmico](https://www.youtube.com/watch?v=76sNmqMzUuI)というラップユニットの裏方や、シンガーソングライター [iri](https://www.youtube.com/watch?v=3WlOZTy072k)のプロデュースなどもやっています。
[**ピスタチオゲーム部親睦会**](https://discord.gg/6XbCyRF)はPistachio Studioのメンバーが中心となって発足したエンジョイゲームコミュニティです。

## 🔗 Links

- [Pistachio Studio home](https://pistachiostudio.net/)
- [Instagram](http://instagram.com/pistachiostudio)
- [Twitter](https://twitter.com/pstchstd)
- [YouTube](https://www.youtube.com/c/pistachiostudiokngw)
- [Soundcloud](https://soundcloud.com/pistachio-studio)
- [Spotify Playlist](https://open.spotify.com/user/2wf7ulo34ef46fu3awnq984wj?si=mm3fQfatR1OF2Kgr_uieGw)

## 🤝 License

Takohachi is released under the MIT license.
©2024 Pistachio Gaming & Pistachio Studio.

</samp>
