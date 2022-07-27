# <img src="https://user-images.githubusercontent.com/4445606/136433333-96b165e0-447c-481a-9e91-50f02b5689d4.png" width="50px"> Discord Bot `タコ八` <img src="https://user-images.githubusercontent.com/4445606/136433333-96b165e0-447c-481a-9e91-50f02b5689d4.png" width="50px">


[ピスタチオゲーム部親睦会](https://discord.gg/pistachiogaming)というDiscordサーバーのためにつくった Bot です。自由にお使いください。

## Cogs

https://github.com/pistachiostudio/takohachi/tree/master/cogs

## Deproyment note

タコ八はHerokuのフリープランで動いています。

### フロー

heroku の設定をしてある前提

1. 開発用 branch の作成
1. 実装
1. branchにpush
1. PRを作成
    - PR作成によってレビュー用のappが作成される。
    - レビュー用app用にもう一つDiscord botを用意している。
1. レビュー用appは作成されるが起動はしないので、手動でDynosをオンにする。
1. レビュー用のDiscord botが起動する。
    - このappは「24時間経過」「PRをクローズ」「PRをマージ」のどれかで削除される。
1. PRをマージすると自動的にProduction(本番環境タコ八)にビルドされる

ステージングappは不要と判断したので使用していない。

### 環境変数の設定

- KEY = TOKEN
- VALUE = 取得した Discord のトークン
- レビューと本番でコマンドのPrefixを変えるため、一部環境変数の設定が違う。

## Icon
| by [Go Inagaki](https://hodwn.com/go-inagaki/)                                                                                 | by [Imoya](https://twitter.com/arakudai2)                                                                                      | 
| ------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------ | 
| <img src="https://user-images.githubusercontent.com/4445606/136433333-96b165e0-447c-481a-9e91-50f02b5689d4.png" width="500px"> | <img src="https://user-images.githubusercontent.com/4445606/136697820-c7526860-2b48-4a34-b32a-06b38fbb76a1.png" width="500px"> | 


## Pistachio Studio

川崎のヒップホップ/録音/プロデューサーチーム。ヒップホップクルー = [CBS](https://youtu.be/A3oshdbRbBI)とそのバックバンドChicken Is Niceを中心に15年以上活動中。
全員30超え、仕事あり、家庭あり、ガキもあり、ペットもあり、かなり限界ながらも活動中。
[chelmico](https://www.youtube.com/watch?v=76sNmqMzUuI)というラップユニットの裏方や、シンガーソングライター [iri](https://www.youtube.com/watch?v=3WlOZTy072k)のプロデュースなどもやっています。
[**ピスタチオゲーム部親睦会**](https://discord.gg/6XbCyRF)はPistachio Studioのメンバーが中心となって発足したエンジョイゲームコミュニティです。

## Links

- [Pistachio Studio home](https://pistachiostudio.net/)
- [Instagram](http://instagram.com/pistachiostudio)
- [Twitter](https://twitter.com/pstchstd)
- [YouTube](https://www.youtube.com/c/pistachiostudiokngw)
- [Soundcloud](https://soundcloud.com/pistachio-studio)
- [Spotify Playlist](https://open.spotify.com/user/2wf7ulo34ef46fu3awnq984wj?si=mm3fQfatR1OF2Kgr_uieGw)

## License

Takohachi is released under the MIT license.  
©2022 Pistachio Gaming & Pistachio Studio.  
