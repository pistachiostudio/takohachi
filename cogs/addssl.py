import gspread
import json
#ServiceAccountCredentials：Googleの各サービスへアクセスできるservice変数を生成。
from oauth2client.service_account import ServiceAccountCredentials
import os
from discord.ext import commands
from typing import Any
import requests
from bs4 import BeautifulSoup


class SSLadd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def addssl(self, ctx, addurl):

        #ちゃんとURLかチェック！
        if f"{addurl}".startswith('http'):

            #URLからHPのタイトルをとってくる
            url = f"{addurl}"
            session = requests.Session()
            session.trust_env = False
            response = requests.get(f"{addurl}")
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.find('title').text

            #環境変数を設定
            TAKO_GSP_JSON = os.environ["TAKOHACHI_JSON"]
            SSLADD_GSP_KEY = os.environ["SSLADD_KEY"]

            #2つのAPIを記述しないとリフレッシュトークンを3600秒毎に発行し続けなければならないです！
            scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

            #認証情報設定
            #ダウンロードしたjsonファイル名をクレデンシャル変数に設定（秘密鍵、Pythonファイルから読み込みしやすい位置に置く）
            addssl_json_keyfile = 'addssl_client_secrets.json'
            credentials = ServiceAccountCredentials.from_json_keyfile_name(addssl_json_keyfile, scope)


            #json_keyfile = 'client_secrets.json'
            #credentials = ServiceAccountCredentials.from_json_keyfile_name(TAKO_GSP_JSON, scope)

            #OAuth2の資格情報を使用してGoogle APIにログインします。
            gc = gspread.authorize(credentials)


            #共有設定したスプレッドシートのシート1を開く
            worksheet = gc.open_by_key(SSLADD_GSP_KEY).sheet1

            # A列とB列にappend。Aはとりあえず空欄。後々はURLからタイトルとってきていれたい
            export_value = [title, url]
            worksheet.append_row(export_value)

            #自分の最初のコマンドに絵文字リアクション
            message = ctx.message
            await message.add_reaction('👍')

        else:
            await ctx.send(f"URLを指定してください！")

def setup(bot):
    bot.add_cog(SSLadd(bot))