import gspread
#ServiceAccountCredentials：Googleの各サービスへアクセスできるservice変数を生成。
from oauth2client.service_account import ServiceAccountCredentials
import os
from discord.ext import commands
from typing import Any
import requests
from bs4 import BeautifulSoup
import re
import discord
from datetime import datetime, timedelta, timezone


class SSLAdd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def addssl(self, ctx, addurl):

        #最初にaddssl引数がURLかを判断し、URL出ない場合はエラーを返す
        if not f"{addurl}".startswith('http'):
            await ctx.send(f"URLを指定してください！")

        #httpから始まる文字列の場合は処理をすすめる
        else:
            url = f"{addurl}"
            session = requests.Session()
            session.trust_env = False
            response = requests.get(f"{addurl}")
            soup = BeautifulSoup(response.content, 'html.parser')
            #タイトルをゲットし、前後の空白や改行をすべて取る（ナオトインティライミのHPは前後に空白が16個ずつも入っていた！ふざけるな！）
            title = soup.find('title').text.strip()
            #その後中盤に改行やTABが入っている場合は取る
            plain_title = re.sub('\n|\t|', '', title)

            #環境変数を設定
            TAKO_GSP_JSON = os.environ["TAKOHACHI_JSON"]
            SSLADD_GSP_KEY = os.environ["SSLADD_KEY"]

            #2つのAPIを記述しないとリフレッシュトークンを3600秒毎に発行し続けなければならないです！
            scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

            #認証情報設定
            #ダウンロードしたjsonファイル名をクレデンシャル変数に設定（秘密鍵、Pythonファイルから読み込みしやすい位置に置く）
            addssl_json_keyfile = 'addssl_client_secrets.json'
            credentials = ServiceAccountCredentials.from_json_keyfile_name(addssl_json_keyfile, scope)

            #OAuth2の資格情報を使用してGoogle APIにログインします。
            gc = gspread.authorize(credentials)

            #共有設定したスプレッドシートのシート1を開く
            worksheet = gc.open_by_key(SSLADD_GSP_KEY).sheet1

            #登録のURLの末尾に/が入っている場合はそれを削除したURL(完全一致判定のため)
            #not_slash_url = addurl.rstrip('/')

            #//以降の文字列を抽出(便宜的にこれをドメインとする)
            target = '//'
            idx = addurl.find(target)
            domain = addurl[idx+len(target):].rstrip('/')

            #ワークシートのデータが入っている行数ゲットする
            row = worksheet.row_count

            #C列の便宜的ドメインをリストでゲットする
            domain_lists = worksheet.get(f'C3:C{row}')

            #今回登録したURLの便宜的ドメインが登録されているC列のドメインリストにないかチェック。すでに登録されていた場合はエラーを返す
            for l in domain_lists:
                if domain in l:
                    await ctx.send('すでに登録されています！')
                    break;

            else:
                #新規登録と判断できたらgspに書き込みを行う
                # A, B, C列にappend
                export_value = [plain_title, addurl, domain]
                worksheet.append_row(export_value)

                #自分の最初のコマンドに絵文字リアクション
                message = ctx.message
                await message.add_reaction('✅')

                #その後レスポンスメッセージ
                embed = discord.Embed()
                JST = timezone(timedelta(hours=+9), "JST")
                embed.timestamp = datetime.now(JST)
                embed.color = discord.Color.green()
                embed.description = f"**「{plain_title}」** を監視いたします。\n\n[SSL Checker](https://ssl-checker.vercel.app/) | [SSLC Database](https://docs.google.com/spreadsheets/d/1c25pvMyjQ89OBCvB9whCQQLM_BPXKyY7umsj5wmpP2k/edit?usp=sharing)"
                await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(SSLAdd(bot))