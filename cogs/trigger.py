import os
import discord
from discord.ext import commands
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional


DIC_KEY = os.environ["DIC_KEY"]


class Trigger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if not message.content.startswith('!!'):
            return

        # 2つのAPIを記述しないとリフレッシュトークンを3600秒毎に発行し続けなければならないです！
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        # 認証情報設定
        # ダウンロードしたjsonファイル名をクレデンシャル変数に設定（秘密鍵、Pythonファイルから読み込みしやすい位置に置く）
        addssl_json_keyfile = 'addssl_client_secrets.json'
        credentials = ServiceAccountCredentials.from_json_keyfile_name(addssl_json_keyfile, scope)
        # OAuth2の資格情報を使用してGoogle APIにログインします。
        gc = gspread.authorize(credentials)

        # 共有設定したスプレッドシートのtriggerシートを開く
        worksheet = gc.open_by_key(DIC_KEY).worksheet('trigger')

        trigger = message.content.lstrip('!!')
        trigger_cell = worksheet.find(str(trigger), in_column=1, case_sensitive=False)

        if trigger_cell is None:
            return
        else:
            # ヘッダー行データをスプレッドシートから取得
            header_list: List[str] = worksheet.row_values(2)

            # トリガー行データをスプレッドシートから取得
            trigger_value_list: List[str] = worksheet.row_values(trigger_cell.row)

            pad_len = len(header_list) - len(trigger_value_list)
            pad_list = ["" for _ in range(pad_len)]
            trigger_value_list.extend(pad_list)
            print(trigger_value_list)

            # 取得対象のカラム名リスト
            colomn_names = ["response", "title", "description", "right_small_image_URL", "big_image_URL"]

            # メッセージ用の値を格納する辞書
            embed_dict: Dict[str, Optional[str]] = {}

            for col_name in colomn_names:
                col_index = self._get_index(header_list, col_name)
                print("colindex", col_index)
                if col_index is None:
                    value = None
                else:
                    value = trigger_value_list[col_index]
                embed_dict[col_name] = value
            
            print(embed_dict)

            if embed_dict["response"]:
                await message.channel.send(f'{embed_dict["response"]}')
            else:
                embed = discord.Embed()
                JST = timezone(timedelta(hours=+9), "JST")
                embed.timestamp = datetime.now(JST)
                if embed_dict["title"]:
                    embed.title = f'test: {embed_dict["title"]}'
                if embed_dict["description"]:
                    embed.description = f'{embed_dict["description"]}\n\n[Check DB](https://docs.google.com/spreadsheets/d/15QCsHsmtZAs1FtiCplLmybU80WyxWw4C7G6ESf2b9f4/edit#gid=1264027664&range=A1)'
                if embed_dict["right_small_image_URL"]:
                    embed.set_thumbnail(url=f'{embed_dict["right_small_image_URL"]}')
                if embed_dict["big_image_URL"]:
                    embed.set_image(url=f'{embed_dict["big_image_URL"]}')
                embed.color = discord.Color.dark_blue()
                await message.channel.send(embed=embed)

    def _get_index(self, target: List[str], value: str) -> Optional[int]:
        try:
            index = target.index(value)
            return index
        except ValueError:
            return None


def setup(bot):
    bot.add_cog(Trigger(bot))
