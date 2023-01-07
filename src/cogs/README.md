# cogs

### addssl.py

- コマンド `!!addssl <URL>` ピスタチオゲーム部が監視を続ける周辺のSSL未対応のHPのチェッカー [SSL Checker](https://github.com/pistachiostudio/main/blob/main/docs/sslchecker.md) のデータベースへのURL登録します。

  ![image](https://user-images.githubusercontent.com/4445606/136697259-b696b6d8-5162-40ef-a3ff-fbf6c12239b0.png)

### apex_tracker.py

- コマンド `!!apedxtracker <PLATFORM> <ID>` でApex LegendsのランクポイントをトラッカーサイトのAPIを叩いて返します。

  ![image](https://user-images.githubusercontent.com/4445606/137535053-bf274d66-5387-4ddf-a0fb-788c208efd60.png)

### autodelete.py

- 指定したチャンネルで指定した時間経過したテキストチャットを順次削除していきます。チャンネルIDと削除する時間を辞書型で記述します。

### bath.py

- コマンド `!!b` で自分のニックネームの前に🛀マークをつけます。AFKですよーという意味で使っています。もう一度同じコマンドで外します。

  ![image](https://user-images.githubusercontent.com/4445606/166937456-eac34e18-49c9-4d89-8b8a-3c4e2a7fa8bf.png)

### card_count.py

- card_list.pyで記録した警告カードの集計を返す。`!!card`でトップ5、`!!cardall`ですべて。gspをデータベース代わりに使用しています。

  ![image](https://user-images.githubusercontent.com/4445606/166938276-d2f1d1e2-7486-4665-a178-44976cbcf53f.png)

### card_list.py

- イエローカードやレッドカード、パトランプなどサーバー内の特定の絵文字でリアクションされたら回数を集計していきます。サーバー内ではカードが多いほど評価が高いです。決して警告などの集計ではなく、ポジティブなものです。

  ![image](https://user-images.githubusercontent.com/4445606/166941784-aa038c32-288c-4f06-b5ac-7369292c11ff.png)

### commandslist.py

- ヘルプコマンドコマンド `!!help` です。

  ![image](https://user-images.githubusercontent.com/4445606/166939285-0d548be6-b13b-4c34-a38b-be28db3080cb.png)

### currency.py

- work in progress! まだ動いていません。
- サーバー内で遊べる通貨機能。実装予定機能は[issue](https://github.com/pistachiostudio/takohachi/issues/42)にあります。

### delete_image.py

- save_image.pyの削除機能。現在動いてないです。wip

### dice.py

- Valorantのマップをランダムに返すだけです。みんなでカスタムやるときのマップピック用に作りました。
- [Valorant-API](https://valorant-api.com/)を叩くのでマップが増えてもOKです。

  ![image](https://user-images.githubusercontent.com/4445606/171447967-1c4885da-7db6-4797-835a-307d579b5b28.png)

### happy_new_year.py

- コマンド `!!hny` (Happy New Year) でおみくじを返します。年に1度しか使われないコマンドです。

  ![image](https://user-images.githubusercontent.com/4445606/211082172-382bf40c-5f42-47fe-a4de-4bd9206c98ad.png)

### marimo.py

- コマンド `!!mt` で米東海岸の友達の現在時刻を素早く表示の現在時間を返す。なぜかスロット付きです。

  ![image](https://user-images.githubusercontent.com/4445606/149986085-ad7262ec-0d9f-433a-9e40-6917019e9583.png)

### message_count.py

- コマンド `!!count` が書き込まれたテキストチャンネルの現在のメッセージの総件数を知らせます。このDiscordサーバーは12時間経過でメッセージをすべて削除しています。

  ![image](https://user-images.githubusercontent.com/4445606/137533505-b2b87f80-c17d-4bf0-8a45-38abb26d91c4.png)

- `!!countall` で特定の汎用チャンネル4つの合計のメッセージ数を返します。

  ![image](https://user-images.githubusercontent.com/4445606/166941142-f2f3a5ad-3f9a-4cdf-997e-6997cb101bd6.png)

### ping.py

- コマンド `!!ping` でping値を測定します。

  ![image](https://user-images.githubusercontent.com/4445606/211082508-abe5ffac-c672-4a32-843d-98d193f826d9.png)

### play.py

- VCに入った状態でコマンド `!!play` で打つことで、BotもVCに参加し、mp3ディレクトリにある音楽を再生します。テキストチャンネルで簡易的なプレイヤーを表示しています。

  ![image](https://user-images.githubusercontent.com/4445606/211081249-1ec122b8-c3d9-4f02-b953-36f3e6a4ff03.png)

### save_image.py

- 画像や動画など、ファイル添付されたテキストチャットに対し、特定の絵文字でリアクションをすることで、添付ファイルを指定のGoogle Driveフォルダへアップロードします。12時間でメッセージが削除されるため、かわいいペットの画像など、記録したい画像などはリアクションで保存しています。

  ![image](https://user-images.githubusercontent.com/4445606/125954117-b54ef041-254f-4bf9-855e-d62e614aeb0e.png)

### spotify.py

- コマンド `!!sp <SERTCH>` `!!spartist <ARTIST>` でSpotifyから曲情報やアーティスト情報を返す。いろんな曲の情報が取れます。

  ![image](https://user-images.githubusercontent.com/4445606/136231698-5a9d10be-1e5f-4155-9a94-c6b2a4956efc.png)

  ![image](https://user-images.githubusercontent.com/4445606/136231834-b1daf6f6-cb76-4857-b70b-7d4a84507ebe.png)

### text_channel.py

- コマンド `!!top` でコマンドを打ったテキストチャンネルの一番最所の投稿まで飛べるリンクを表示します。

  ![image](https://user-images.githubusercontent.com/4445606/211079913-f8afefa7-0723-4f75-8754-db73ba49b51d.png)

### trigger.py

- サーバー用のカスタムレスポンスのための機能です。サーバーの全員が追加や編集を簡単にできるということ考えたらやっぱりgspになりました。レスポンスにすこし時間がかかりますが、誰でも追加や編集ができることはなにものにも代えがたいです。

  ![image](https://user-images.githubusercontent.com/4445606/166942996-7144755f-91ff-4c4c-bd3f-a60404794585.png)

  ![image](https://user-images.githubusercontent.com/4445606/166943142-5c61051c-639b-4976-b116-5d13a452d346.png)

### valorant_api.py

- コマンド `!!vr` でValorantのユーザーの現在のランクやELOを取得します。
- コマンド `!!vnews` でValorantの最新のニュースやパッチ情報を取得します。

  ![image](https://user-images.githubusercontent.com/4445606/191848416-7a326d24-16a8-4bc0-942a-f82463b4c191.png)

  ![image](https://user-images.githubusercontent.com/4445606/191848446-38033a30-5666-498c-bf08-ba3c4a29699a.png)

### vc_role.py

- 特定のVCに入った人に対して特定のロールを付与し、出たらそのロールを取ります。
- VCにいる人だけが見えるテキストチャットのために使用しています。

  ![スクリーンショット 2022-08-27 151148](https://user-images.githubusercontent.com/4445606/187017574-373a4ff7-ae78-4119-a624-1c7cd69a4c13.png)

### vcwhite.py

- 新しいVCがスタートしたら特定のテキストチャンネルへアラートを投稿します。

  ![image](https://user-images.githubusercontent.com/4445606/125953884-10528778-3b56-414f-972e-197d35e51b64.png)

### what_today.py

- コマンド `!!whatToday` で[wikipediaのHTML](https://ja.wikipedia.org/wiki/Wikipedia:%E4%BB%8A%E6%97%A5%E3%81%AF%E4%BD%95%E3%81%AE%E6%97%A5_7%E6%9C%88)から取得したその日の出来事を返します。

  ![image](https://user-images.githubusercontent.com/4445606/125954287-51a42d02-61ec-4c1e-b114-5faf225c0b50.png)

### wt_task.py

- 上記 what_today.py を `@tasks.loop` で毎朝7時にも「今日はなんの日?」を投稿しています。

  ![image](https://user-images.githubusercontent.com/4445606/166943894-4f8d7bd1-58fe-4765-a331-360d2f88c192.png)

# others

- 半角カタカナが使用されたらリアクションで知らせる（通称:半角警察）、全角英数字が使用されたらリアクションで知らせる（全角警察）ウザかったので現在は停止中。

  ![image](https://user-images.githubusercontent.com/4445606/125954408-8d8b9f38-c5ff-4d0f-b524-82aeb938b2da.png)
