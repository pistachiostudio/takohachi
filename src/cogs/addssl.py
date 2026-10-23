import os
import re
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

import discord
import gspread
import httpx
from bs4 import BeautifulSoup
from discord import app_commands
from discord.ext import commands

from settings import GUILD_ID


class SSLAdd(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="addssl", description="怠けたNot SSLを監視しましょう。")
    @app_commands.describe(add_url="監視DBに登録したいURLを記載してください。")
    async def addssl(self, interaction: discord.Interaction, add_url: str):
        # interactionは3秒以内にレスポンスしないといけないとエラーになるのでこの処理を入れる。
        await interaction.response.defer()

        # 最初にaddssl引数がURLかを判断し、URL出ない場合はエラーを返す
        if not add_url.startswith("http"):
            await interaction.followup.send(":warning: URLを指定してください！", ephemeral=True)

        # httpから始まる文字列の場合は処理をすすめる
        else:
            session = httpx.Client()
            session.trust_env = False
            response = httpx.get(add_url)
            soup = BeautifulSoup(response.content, "html.parser")
            # タイトルをゲットし、前後の空白や改行をすべて取る
            # （ナオトインティライミのHPは前後に空白が16個ずつも入っていた！ふざけるな！）
            title = soup.find("title").text.strip()
            # その後中盤に改行やTABが入っている場合は取る
            plain_title = re.sub("\n|\t|", "", title)

            # 環境変数を設定
            SSLADD_GSP_KEY = os.environ["SSLADD_KEY"]

            # サービスアカウントの鍵ファイルで Google API(スプレッドシート / Drive)にログインする
            gc = gspread.service_account(filename="client_secrets.json")

            # 共有設定したスプレッドシートのシート1を開く
            worksheet = gc.open_by_key(SSLADD_GSP_KEY).sheet1

            # //C列に記載するドメインを抽出
            out = urlparse(add_url)
            domain = out.hostname

            # ワークシートのデータが入っている行数ゲットする
            row = worksheet.row_count

            # C列の便宜的ドメインをリストでゲットする
            domain_lists = worksheet.get(f"C3:C{row}")

            # 今回登録したURLの便宜的ドメインが登録されているC列のドメインリストにないかチェック。
            # すでに登録されていた場合はエラーを返す
            for dlist in domain_lists:
                if domain in dlist:
                    await interaction.followup.send("このドメインはすでに登録されています！")
                    break

            else:
                # 新規登録と判断できたらgspに書き込みを行う
                # A, B, C列にappend
                export_value = [plain_title, add_url, domain]
                worksheet.append_row(export_value)

                # その後レスポンスメッセージ
                embed = discord.Embed()
                JST = timezone(timedelta(hours=+9), "JST")
                embed.timestamp = datetime.now(JST)
                embed.color = discord.Color.green()
                embed.description = f"**「{plain_title}」** を監視いたします。\
                    \n\n[SSL Checker](https://ssl-checker.vercel.app/) | \
                    [SSLC Database](https://docs.google.com/spreadsheets/d/1c25pvMyjQ89OBCvB9whCQQLM_BPXKyY7umsj5wmpP2k/edit?usp=sharing)"
                await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(SSLAdd(bot), guilds=[discord.Object(id=GUILD_ID)])
