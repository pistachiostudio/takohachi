import asyncio
import logging
import os
from urllib.parse import urlsplit

import discord
import httpx
from discord import app_commands
from discord.ext import commands

from libs import google_sheets
from libs.safe_http import UnsafeURLError, fetch_title
from libs.utils import now_jst
from settings import GUILD_ID

logger = logging.getLogger(__name__)

SSLC_DATABASE_URL = "https://docs.google.com/spreadsheets/d/1c25pvMyjQ89OBCvB9whCQQLM_BPXKyY7umsj5wmpP2k/edit?usp=sharing"  # noqa: E501


def _register(url: str, title: str, domain: str) -> bool:
    """スプレッドシートに登録する。C列(3行目以降)にドメインが登録済みならFalse。"""
    worksheet = google_sheets.open_first_sheet(os.environ["SSLADD_KEY"])
    if domain in worksheet.col_values(3)[2:]:
        return False
    # A, B, C列にappend。RAW(既定)で書くので、タイトルが数式として解釈されることはない。
    worksheet.append_row([title, url, domain])
    return True


class SSLAdd(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="addssl", description="怠けたNot SSLを監視しましょう。")
    @app_commands.describe(add_url="監視DBに登録したいURLを記載してください。")
    async def addssl(self, interaction: discord.Interaction, add_url: str):
        # interactionは3秒以内にレスポンスしないといけないとエラーになるのでこの処理を入れる。
        await interaction.response.defer()

        try:
            title = await fetch_title(add_url)
        except UnsafeURLError as e:
            await interaction.followup.send(f":warning: {e}")
            return
        except httpx.HTTPError:
            logger.warning("addssl: failed to fetch %s", add_url, exc_info=True)
            await interaction.followup.send(":warning: ページを取得できませんでした。")
            return
        if title is None:
            await interaction.followup.send(":warning: ページのタイトルが見つかりませんでした。")
            return

        domain = urlsplit(add_url).hostname
        if not await asyncio.to_thread(_register, add_url, title[:200], domain):
            await interaction.followup.send("このドメインはすでに登録されています！")
            return

        embed = discord.Embed(
            color=discord.Color.green(),
            timestamp=now_jst(),
            description=(
                f"**「{discord.utils.escape_markdown(title[:200])}」** を監視いたします。\n\n"
                f"[SSL Checker](https://ssl-checker.vercel.app/) | "
                f"[SSLC Database]({SSLC_DATABASE_URL})"
            ),
        )
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(SSLAdd(bot), guilds=[discord.Object(id=GUILD_ID)])
