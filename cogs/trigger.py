import os
import discord
from discord.ext import commands
from typing import Any
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta, timezone

class Trigger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if message.content.startswith('!!'):

            #環境変数を設定
            DIC_KEY = os.environ["DIC_KEY"]

            #2つのAPIを記述しないとリフレッシュトークンを3600秒毎に発行し続けなければならないです！
            scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

            #認証情報設定
            #ダウンロードしたjsonファイル名をクレデンシャル変数に設定（秘密鍵、Pythonファイルから読み込みしやすい位置に置く）
            addssl_json_keyfile = 'addssl_client_secrets.json'
            credentials = ServiceAccountCredentials.from_json_keyfile_name(addssl_json_keyfile, scope)

            #OAuth2の資格情報を使用してGoogle APIにログインします。
            gc = gspread.authorize(credentials)

            #共有設定したスプレッドシートのtriggerシートを開く
            worksheet = gc.open_by_key(DIC_KEY).worksheet('trigger')

            #A列のtriggerをリストで取得する
            word_list = worksheet.get('A3:C200')

            trigger = message.content.lstrip('!!')
            trigger_cell = worksheet.find(str(trigger),in_column=1,case_sensitive=False)


            if trigger_cell == None:
                return

            else:
                response_cell = worksheet.find(str('response'),in_row=2)
                response_value = worksheet.cell(trigger_cell.row, response_cell.col).value

                title_cell = worksheet.find(str('title'),in_row=2)
                title_value = worksheet.cell(trigger_cell.row, title_cell.col).value

                description_cell = worksheet.find(str('description'),in_row=2)
                description_value = worksheet.cell(trigger_cell.row, description_cell.col).value

                right_small_image_URL_cell = worksheet.find(str('right_small_image_URL'),in_row=2)
                right_small_image_URL_value = worksheet.cell(trigger_cell.row, right_small_image_URL_cell.col).value

                big_image_URL_cell = worksheet.find(str('big_image_URL'),in_row=2)
                big_image_URL_value = worksheet.cell(trigger_cell.row, big_image_URL_cell.col).value

                if response_value is not None:
                    await message.channel.send(f'{response_value}')

                else:
                    embed = discord.Embed()
                    JST = timezone(timedelta(hours=+9), "JST")
                    embed.timestamp = datetime.now(JST)
                    if title_value is not None:
                        embed.title = f"{title_value}"
                    if description_value is not None:
                        embed.description = f'{description_value}\n\n[>>>Check & edit trigger database](https://docs.google.com/spreadsheets/d/15QCsHsmtZAs1FtiCplLmybU80WyxWw4C7G6ESf2b9f4/edit#gid=1264027664&range=A1)'
                    if right_small_image_URL_value is not None:
                        embed.set_thumbnail(url=f"{right_small_image_URL_value}")
                    if big_image_URL_value is not None:
                        embed.set_image(url=f"{big_image_URL_value}")
                    embed.color = discord.Color.dark_blue()
                    await message.channel.send(embed=embed)
                    return



def setup(bot):
    bot.add_cog(Trigger(bot))