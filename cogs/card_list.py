import os
from datetime import datetime, timedelta, timezone
from distutils.command.build_scripts import first_line_re
from typing import List

import discord
import gspread
from discord.ext import commands
#ServiceAccountCredentials：Googleの各サービスへアクセスできるservice変数を生成。
from oauth2client.service_account import ServiceAccountCredentials


class CardList(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def card(self, ctx):

        yellow_card = "<:p05_card_yellow:934125477424140308>"
        red_card = "<:p05_card_red:934125543111131187>"
        siren_emoji = "<:p05_siren:801693375043862580>"
        database_url = "[Check database](https://docs.google.com/spreadsheets/d/1pDagY2BfCXA5ILOy_vXZUa31shsKhL-YpS-beyK12M0/edit?usp=sharing)"

        #環境変数を設定
        CARDCOUNT_KEY = os.environ["CARDCOUNT_KEY"]

        #2つのAPIを記述しないとリフレッシュトークンを3600秒毎に発行し続けなければならないです！
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

        #認証情報設定
        #ダウンロードしたjsonファイル名をクレデンシャル変数に設定（秘密鍵、Pythonファイルから読み込みしやすい位置に置く）
        addssl_json_keyfile = 'addssl_client_secrets.json'
        credentials = ServiceAccountCredentials.from_json_keyfile_name(addssl_json_keyfile, scope)

        #OAuth2の資格情報を使用してGoogle APIにログインします。
        gc = gspread.authorize(credentials)

        #共有設定したスプレッドシートのシート1を開く
        worksheet = gc.open_by_key(CARDCOUNT_KEY).sheet1

        #ワークシートのデータが入っている行数ゲットする
        row = worksheet.row_count

        #A列のauthor_nameをリストで取得する
        author_lists = worksheet.get(f'A3:F{row}')

        first = f":one:<@{author_lists[0][5]}>:{yellow_card}x{author_lists[0][1]} {red_card}x{author_lists[0][2]} {siren_emoji}x{author_lists[0][3]}"
        second = f":two:<@{author_lists[1][5]}>:{yellow_card}x{author_lists[1][1]} {red_card}x{author_lists[1][2]} {siren_emoji}x{author_lists[1][3]}"
        third = f":three:<@{author_lists[2][5]}>:{yellow_card}x{author_lists[2][1]} {red_card}x{author_lists[2][2]} {siren_emoji}x{author_lists[2][3]}"
        forth = f":four:<@{author_lists[3][5]}>:{yellow_card}x{author_lists[3][1]} {red_card}x{author_lists[3][2]} {siren_emoji}x{author_lists[3][3]}"
        fifth = f":five:<@{author_lists[4][5]}>:{yellow_card}x{author_lists[4][1]} {red_card}x{author_lists[4][2]} {siren_emoji}x{author_lists[4][3]}"

        embed = discord.Embed()
        embed.title = "Top 5 Radiant"
        JST = timezone(timedelta(hours=+9), "JST")
        embed.timestamp = datetime.now(JST)
        embed.color = discord.Color.dark_orange()
        embed.description = f"{first}\n\n{second}\n\n{third}\n\n{forth}\n\n{fifth}\n\n{database_url}"
        await ctx.send(embed=embed)


    @commands.command()
    async def cardall(self, ctx):

        yellow_card = "<:p05_card_yellow:934125477424140308>"
        red_card = "<:p05_card_red:934125543111131187>"
        siren_emoji = "<:p05_siren:801693375043862580>"
        database_url = "[Check database](https://docs.google.com/spreadsheets/d/1pDagY2BfCXA5ILOy_vXZUa31shsKhL-YpS-beyK12M0/edit?usp=sharing)"

        #環境変数を設定
        CARDCOUNT_KEY = os.environ["CARDCOUNT_KEY"]

        #2つのAPIを記述しないとリフレッシュトークンを3600秒毎に発行し続けなければならないです！
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

        #認証情報設定
        #ダウンロードしたjsonファイル名をクレデンシャル変数に設定（秘密鍵、Pythonファイルから読み込みしやすい位置に置く）
        addssl_json_keyfile = 'addssl_client_secrets.json'
        credentials = ServiceAccountCredentials.from_json_keyfile_name(addssl_json_keyfile, scope)

        #OAuth2の資格情報を使用してGoogle APIにログインします。
        gc = gspread.authorize(credentials)

        #共有設定したスプレッドシートのシート1を開く
        worksheet = gc.open_by_key(CARDCOUNT_KEY).sheet1

        #ワークシートのデータが入っている行数ゲットする
        row = worksheet.row_count

        #A列のauthor_nameをリストで取得する
        author_lists = worksheet.get(f'A3:F{row}')

        def converte_text(l: List):
            return f"<@{l[5]}>: {yellow_card}x{l[1]} {red_card}x{l[2]} {siren_emoji}x{l[3]}"

        # 送信するデータ
        body = "\n".join(map(converte_text, author_lists))

        embed = discord.Embed()
        embed.title = "all card list..."
        JST = timezone(timedelta(hours=+9), "JST")
        embed.timestamp = datetime.now(JST)
        embed.color = discord.Color.dark_orange()
        embed.description = f"{body}\n\n{database_url}"
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(CardList(bot))
