# 🐙 Discord Bot `タコ八` 🐙


これは[ピスタチオゲーム部親睦会](https://discord.gg/pistachiogaming)というDiscordサーバーのためのユースレスBotです。コードは自由にお使いください。

## ⚙ Cogs

https://github.com/pistachiostudio/takohachi/tree/master/cogs

## 🏭 Deployment note

### on Heroku dyno

- heroku.yml
- Procfile
- requirements.txt

### on VPS service

- Dockerfile
- docker-compose.yml
- requirements.txt

## 🐳 Docker

### 1. Clone this repository

```bash
$ git clone https://github.com/pistachiostudio/takohachi.git
```

### 2. Create `.env` file on the root directory

```bash
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

🔫 Yeah bot is on ready!!

## 🎨 Icon
| by [Go Inagaki](https://hodwn.com/go-inagaki/)                                                                                 | by [Imoya](https://twitter.com/arakudai2)                                                                                      | 
| ------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------ | 
| <img src="https://user-images.githubusercontent.com/4445606/136433333-96b165e0-447c-481a-9e91-50f02b5689d4.png" width="500px"> | <img src="https://user-images.githubusercontent.com/4445606/136697820-c7526860-2b48-4a34-b32a-06b38fbb76a1.png" width="500px"> | 


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
©2022 Pistachio Gaming & Pistachio Studio.