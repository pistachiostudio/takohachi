import os
import discord
from discord.ext import commands
from datetime import datetime, timedelta, timezone
from typing import Any
import gspread
#ServiceAccountCredentials：Googleの各サービスへアクセスできるservice変数を生成。
from oauth2client.service_account import ServiceAccountCredentials
from discord.ext import commands
import os
from typing import Any
from datetime import datetime, timedelta, timezone


class Dictionary(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def dic(self, ctx,  *, words = 'default'):

        #引数がない場合はreturn
        if words == 'default':
            embed = discord.Embed()
            embed.title = f"ピスタチオゲーム部ディクショナリー"
            JST = timezone(timedelta(hours=+9), "JST")
            embed.timestamp = datetime.now(JST)
            embed.color = discord.Color.dark_gold()
            embed.description = f'`!!dic <word>`で意味を返します。\n[check & edit the dictionary](https://docs.google.com/spreadsheets/d/15QCsHsmtZAs1FtiCplLmybU80WyxWw4C7G6ESf2b9f4/edit?usp=sharing)'
            await ctx.send(embed=embed)
            return

        else:
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

            #共有設定したスプレッドシートのシート1を開く
            worksheet = gc.open_by_key(DIC_KEY).sheet1

            #ワークシートのデータが入っている行数ゲットする
            row = worksheet.row_count

            #A列のwordをリストで取得する
            word_list = worksheet.get(f'A2:C{row}')

            cell = worksheet.find(str(words))

            if cell == None:
                embed = discord.Embed()
                embed.title = f"ピスタチオゲーム部ディクショナリー"
                JST = timezone(timedelta(hours=+9), "JST")
                embed.timestamp = datetime.now(JST)
                embed.color = discord.Color.dark_gold()
                embed.description = f'登録がないようです。\n[check & edit the dictionary](https://docs.google.com/spreadsheets/d/15QCsHsmtZAs1FtiCplLmybU80WyxWw4C7G6ESf2b9f4/edit?usp=sharing)'
                await ctx.send(embed=embed)

            else:
                dic_value = worksheet.cell(cell.row, 3).value
                dic_hiragana = worksheet.cell(cell.row, 2).value

                embed = discord.Embed()
                embed.title = f"{words}: {dic_hiragana}"
                JST = timezone(timedelta(hours=+9), "JST")
                embed.timestamp = datetime.now(JST)
                embed.color = discord.Color.purple()
                embed.description = f'{dic_value}\n\n[check & edit the dictionary](https://docs.google.com/spreadsheets/d/15QCsHsmtZAs1FtiCplLmybU80WyxWw4C7G6ESf2b9f4/edit?usp=sharing)'
                await ctx.send(embed=embed)
                return

def setup(bot):
    bot.add_cog(Dictionary(bot))
