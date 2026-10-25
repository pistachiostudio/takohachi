import asyncio
import os

import discord
from discord import app_commands
from discord.ext import commands

from libs import google_sheets
from libs.utils import now_jst
from settings import GUILD_ID

YELLOW_CARD = "<:p05_card_yellow:934125477424140308>"
RED_CARD = "<:p05_card_red:934125543111131187>"
SIREN = "<:p05_siren:801693375043862580>"
RANK_EMOJIS = [":one:", ":two:", ":three:", ":four:", ":five:"]
DATABASE_URL = "https://docs.google.com/spreadsheets/d/1pDagY2BfCXA5ILOy_vXZUa31shsKhL-YpS-beyK12M0/edit?usp=sharing"  # noqa: E501


def get_top_rows() -> list[list[str]]:
    """上位の行(A〜F列: 名前, イエロー, レッド, サイレン, 合計, ユーザーID)を返す。"""
    worksheet = google_sheets.open_first_sheet(os.environ["CARDCOUNT_KEY"])
    return worksheet.get(f"A3:F{2 + len(RANK_EMOJIS)}")


class CardList(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="card", description="警告カードの上位5名を表示します。")
    async def card(self, interaction: discord.Interaction):
        # interactionは3秒以内にレスポンスしないといけないとエラーになるのでこの処理を入れる。
        await interaction.response.defer()

        rows = await asyncio.to_thread(get_top_rows)
        lines = [
            f"{emoji}<@{row[5]}>:{YELLOW_CARD}x{row[1]} {RED_CARD}x{row[2]} {SIREN}x{row[3]}"
            for emoji, row in zip(RANK_EMOJIS, rows)
        ]
        embed = discord.Embed(
            title="Top 5 Radiant",
            color=discord.Color.dark_orange(),
            timestamp=now_jst(),
            description="\n\n".join([*lines, f"[Check database]({DATABASE_URL})"]),
        )
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(CardList(bot), guilds=[discord.Object(id=GUILD_ID)])
