import os

import gspread
from discord.ext import commands

# ServiceAccountCredentials：Googleの各サービスへアクセスできるservice変数を生成。
from oauth2client.service_account import ServiceAccountCredentials


class CardCount(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # botのリアクションは無視する
        if payload.member.bot:
            return

        yellow_card = "<:p05_card_yellow:934125477424140308>"
        red_card = "<:p05_card_red:934125543111131187>"
        shake_yellow_card = "<a:p00_card_yellow:934125609544745030>"
        shake_red_card = "<a:p00_card_red:934125658529988648>"
        siren_red = "<a:p00_siren:801424753419354133>"
        siren_blue = "<a:p00_sirenblue:802091428057579521>"
        siren_purple = "<a:p00_sirenpurple:805201572111974401>"
        siren_emoji = "<:p05_siren:801693375043862580>"

        count_list = [
            yellow_card,
            red_card,
            shake_yellow_card,
            shake_red_card,
            siren_red,
            siren_blue,
            siren_purple,
            siren_emoji,
        ]
        yellow_list = [yellow_card, shake_yellow_card]
        red_list = [red_card, shake_red_card]
        siren_list = [siren_red, siren_blue, siren_purple, siren_emoji]

        # count_list共通処理
        if str(payload.emoji) not in count_list:
            return
        else:
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            author_name = message.author
            user_id = message.author.id

            # 環境変数を設定
            CARDCOUNT_KEY = os.environ["CARDCOUNT_KEY"]

            # 2つのAPIを記述しないとリフレッシュトークンを3600秒毎に発行し続けなければならないです！
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive",
            ]

            # 認証情報設定
            # ダウンロードしたjsonファイル名をクレデンシャル変数に設定（秘密鍵、Pythonファイルから読み込みしやすい位置に置く）
            addssl_json_keyfile = "addssl_client_secrets.json"
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                addssl_json_keyfile, scope
            )

            # OAuth2の資格情報を使用してGoogle APIにログインします。
            gc = gspread.authorize(credentials)

            # 共有設定したスプレッドシートのシート1を開く
            worksheet = gc.open_by_key(CARDCOUNT_KEY).sheet1

            # ワークシートからauthor_nameの文字列があるか検索。ある場合はセルの値を返す
            cell = worksheet.find(str(author_name))

            # ここから絵文字の種類で分岐
            # 絵文字がイエローカードの場合
            if str(payload.emoji) in yellow_list:
                # author_nameが新規の場合
                if cell is None:
                    export_value = [str(author_name), 1, 0, 0]
                    worksheet.append_row(export_value)
                    add_cell = worksheet.find(str(author_name))
                    add_sum = f"=SUM(B{add_cell.row}:D{add_cell.row})"
                    worksheet.update_cell(int(add_cell.row), 5, add_sum)
                    worksheet.update_cell(int(add_cell.row), 6, str(user_id))

                # author_nameがすでにある場合はカウントアップ
                else:
                    update_col = int(cell.col) + 1
                    cell_value = worksheet.cell(cell.row, update_col).value
                    update_value = int(cell_value) + 1
                    worksheet.update_cell(cell.row, update_col, update_value)

            # E列のTTLを降順でソートする Sort sheet A -> Z by column 'E'
            worksheet.sort((5, "des"))

            # 絵文字がレッドカードの場合
            if str(payload.emoji) in red_list:
                # author_nameが新規の場合
                if cell is None:
                    export_value = [str(author_name), 0, 1, 0]
                    worksheet.append_row(export_value)
                    add_cell = worksheet.find(str(author_name))
                    add_sum = f"=SUM(B{add_cell.row}:D{add_cell.row})"
                    worksheet.update_cell(int(add_cell.row), 5, add_sum)
                    worksheet.update_cell(int(add_cell.row), 6, str(user_id))

                # author_nameがすでにある場合はカウントアップ
                else:
                    update_col = int(cell.col) + 2
                    cell_value = worksheet.cell(cell.row, update_col).value
                    update_value = int(cell_value) + 1
                    worksheet.update_cell(cell.row, update_col, update_value)

            # E列のTTLを降順でソートする Sort sheet A -> Z by column 'E'
            worksheet.sort((5, "des"))

            # 絵文字がパトランプの場合
            if str(payload.emoji) in siren_list:
                # author_nameが新規の場合
                if cell is None:
                    export_value = [str(author_name), 0, 0, 1]
                    worksheet.append_row(export_value)
                    add_cell = worksheet.find(str(author_name))
                    add_sum = f"=SUM(B{add_cell.row}:D{add_cell.row})"
                    worksheet.update_cell(int(add_cell.row), 5, add_sum)
                    worksheet.update_cell(int(add_cell.row), 6, str(user_id))

                # author_nameがすでにある場合はカウントアップ
                else:
                    update_col = int(cell.col) + 3
                    cell_value = worksheet.cell(cell.row, update_col).value
                    update_value = int(cell_value) + 1
                    worksheet.update_cell(cell.row, update_col, update_value)

            # E列のTTLを降順でソートする Sort sheet A -> Z by column 'E'
            worksheet.sort((5, "des"))


async def setup(bot: commands.Bot):
    await bot.add_cog(CardCount(bot))
