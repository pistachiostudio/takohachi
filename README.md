# <img src="https://user-images.githubusercontent.com/4445606/136433333-96b165e0-447c-481a-9e91-50f02b5689d4.png" width="50px"> Discord Bot `タコ八` <img src="https://user-images.githubusercontent.com/4445606/136433333-96b165e0-447c-481a-9e91-50f02b5689d4.png" width="50px">



ピスタチオゲーム部親睦会というDiscordサーバーで動いている Bot です。
Discord サーバーへの加入は[こちら](https://discord.com/invite/6XbCyRF)から！

## Cogs

- コマンド `!!mt` で特定地域の現在時間を返す（米東海岸の友達の現在時刻を素早く表示）（スロット付き）

  ![image](https://user-images.githubusercontent.com/4445606/149986085-ad7262ec-0d9f-433a-9e40-6917019e9583.png)

- 新しいVCがスタートしたら特定のテキストチャンネルへアラートを投稿

  ![image](https://user-images.githubusercontent.com/4445606/125953884-10528778-3b56-414f-972e-197d35e51b64.png)  

- 画像付きのチャットへ特定の絵文字でリアクションをするとその画像を指定のGoogle Driveフォルダへアップロード

  ![image](https://user-images.githubusercontent.com/4445606/125954117-b54ef041-254f-4bf9-855e-d62e614aeb0e.png)  

- コマンド `!!apedxtracker <PLATFORM> <ID>` でApex LegendsのランクポイントをトラッカーサイトのAPIを叩いて返す。
 
  ![image](https://user-images.githubusercontent.com/4445606/137535053-bf274d66-5387-4ddf-a0fb-788c208efd60.png)

- コマンド `!!sp <SERTCH>` `!!spartist <ARTIST>` Spotifyから曲情報やアーティスト情報を返す。

  ![image](https://user-images.githubusercontent.com/4445606/136231698-5a9d10be-1e5f-4155-9a94-c6b2a4956efc.png)  

  ![image](https://user-images.githubusercontent.com/4445606/136231834-b1daf6f6-cb76-4857-b70b-7d4a84507ebe.png)  

- コマンド `!!addssl <URL>` ピスタチオゲーム部が監視を続ける周辺のSSL未対応のHPのチェッカー [SSL Checker](https://ssl-checker.vercel.app/) のデータベースへのURL登録。

  ![image](https://user-images.githubusercontent.com/4445606/136697259-b696b6d8-5162-40ef-a3ff-fbf6c12239b0.png)  

- チャットのパーマリンクが投稿された場合に内容を展開する。[dispander](https://github.com/DiscordBotPortalJP/dispander)をそのままお借りしています。

  ![image](https://user-images.githubusercontent.com/4445606/125954215-2ff8b9b1-8e5e-4c9c-a45c-0a79409e8fd3.png)

- コマンド `!!whatToday` [wikipediaのHTML](https://ja.wikipedia.org/wiki/Wikipedia:%E4%BB%8A%E6%97%A5%E3%81%AF%E4%BD%95%E3%81%AE%E6%97%A5_7%E6%9C%88)から取得したその日の出来事をかえす。

  ![image](https://user-images.githubusercontent.com/4445606/125954287-51a42d02-61ec-4c1e-b114-5faf225c0b50.png)

- コマンド `!!count` が書き込まれたテキストチャンネルの現在のメッセージの総件数を知らせる。

  ![image](https://user-images.githubusercontent.com/4445606/137533505-b2b87f80-c17d-4bf0-8a45-38abb26d91c4.png)

- 半角カタカナが使用されたらリアクションで知らせる（通称:半角警察）、全角英数字が使用されたらリアクションで知らせる（全角警察）

  ![image](https://user-images.githubusercontent.com/4445606/125954408-8d8b9f38-c5ff-4d0f-b524-82aeb938b2da.png) 

- 特定の絵文字でリアクションされた回数をユーザーごとに記録する

  ![スクリーンショット 2022-01-19 021505](https://user-images.githubusercontent.com/4445606/149985902-b5714b7e-1086-466c-8c3d-64f495557c0b.png)

- 記録した警告カードの集計を返す。`!!card`でトップ5、`!!cardall`ですべて。

  ![image](https://user-images.githubusercontent.com/4445606/150370012-61c017a1-a448-4bb6-8c9a-ddfc53d06b40.png)
  
  
- サーバー内でしか使われない難読ワードをデータベースに登録しアクセスできる。`!!dic <WORDS>`
  ![image](https://user-images.githubusercontent.com/4445606/154196740-08380a57-5a4a-41f0-aba3-c99531e68406.png)



## Deproyment

**環境変数の設定**

- KEY = TOKEN
- VALUE = 取得した Discord のトークン
- 設定方法は公式ドキュメントを参考にする([設定と環境設定 - Heroku Dashboard を使用する](https://devcenter.heroku.com/ja/articles/config-vars#using-the-heroku-dashboard))
	- その他参考
		- [Qiita - 【Heroku】Herokuで環境変数を設定する方法](https://qiita.com/mzmz__02/items/64db94b8fc67ee0a9068)

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
