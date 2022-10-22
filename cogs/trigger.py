import os
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

import discord
import gspread
from discord.ext import commands
from oauth2client.service_account import ServiceAccountCredentials

DIC_KEY = os.environ["DIC_KEY"]
PREFIX = os.environ["PREFIX"]

class Trigger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.worksheet = None

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if not message.content.startswith(PREFIX):
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
        self.worksheet = gc.open_by_key(DIC_KEY).worksheet('trigger')

        # ヘッダー行をスプレッドシートから取得
        header_list: List[str] = self.worksheet.row_values(2)

        trigger: str = message.content.lstrip(PREFIX)
        row_num = self._find_trigger_row_number(trigger, header_list)
        print(row_num)

        if not row_num:
            return
        else:
            # トリガー行データをスプレッドシートから取得
            trigger_value_list: List[str] = self.worksheet.row_values(row_num)

            pad_len = len(header_list) - len(trigger_value_list)
            pad_list = ["" for _ in range(pad_len)]
            trigger_value_list.extend(pad_list)

            # 取得対象のカラム名リスト
            colomn_names = ["response", "title", "description", "right_small_image_URL", "big_image_URL"]

            # メッセージ用の値を格納する辞書
            embed_dict: Dict[str, Optional[str]] = {}

            for col_name in colomn_names:
                col_index = self._get_index(header_list, col_name)
                if col_index is None:
                    value = None
                else:
                    value = trigger_value_list[col_index]
                embed_dict[col_name] = value

            if embed_dict["response"]:
                await message.channel.send(f'{embed_dict["response"]}')
            else:
                embed = discord.Embed()
                JST = timezone(timedelta(hours=+9), "JST")
                embed.timestamp = datetime.now(JST)
                if embed_dict["title"]:
                    embed.title = f'{embed_dict["title"]}'
                if embed_dict["description"]:
                    embed.description = f'{embed_dict["description"]}\n\n[Check DB](https://docs.google.com/spreadsheets/d/15QCsHsmtZAs1FtiCplLmybU80WyxWw4C7G6ESf2b9f4/edit#gid=1264027664&range=A1)'
                if embed_dict["right_small_image_URL"]:
                    embed.set_thumbnail(url=f'{embed_dict["right_small_image_URL"]}')
                if embed_dict["big_image_URL"]:
                    embed.set_image(url=f'{embed_dict["big_image_URL"]}')
                embed.color = discord.Color.dark_blue()
                await message.channel.send(embed=embed)

    def _get_index(self, target: List[str], value: str) -> Optional[int]:
        """value が target の何番目かを取得する関数です。value が存在しない場合は None を返します。
        Args:
            target (List[str]): index を調べたい対象のリスト
            value (str): index を取得する対象文字列
        Returns:
            Optional[int]: 存在すれば index(int) を返し、存在しなければ None を返します。
        """
        try:
            index = target.index(value)
            return index
        except ValueError:
            return None

    def _find_trigger_row_number(self, trigger: str, header_list: List[str]) -> Optional[int]:
        """triggerが含まれている行番号を返します
        Args:
            trigger (str): trigger
            header_list (List[str]): trigger db のヘッダーリスト
        Returns:
            Optional[int]: trigger が含まれている行番号
        """
        trigger_columns = ["trigger", "alias01", "alias02"]
        for trigger_column in trigger_columns:
            index = self._get_index(header_list, trigger_column)
            if not index:
                # header_list に trigger_column が存在しない場合
                continue
            else:
                trigger_cell = self.worksheet.find(trigger, in_column=index, case_sensitive=False)
                if not trigger_cell:
                    # trigger column に trigger が存在しない場合
                    continue
                else:
                    return trigger_cell.row

        return None


def setup(bot):
    bot.add_cog(Trigger(bot))
