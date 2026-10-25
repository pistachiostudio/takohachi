import asyncio

import discord
from discord import app_commands
from discord.ext import commands

from libs.utils import get_what_today, now_jst
from settings import GUILD_ID


class WhatToday(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="wt", description="今日はなんの日？")
    async def whatToday(self, interaction: discord.Interaction):
        # interactionは3秒以内にレスポンスしないといけないとエラーになるのでこの処理を入れる。
        await interaction.response.defer()

        today = now_jst()
        result = await asyncio.to_thread(get_what_today, today.month, today.day)
        embed = discord.Embed(
            title="今日はなんの日？",
            color=discord.Color.green(),
            timestamp=today,
            description=f"{today.month}月{today.day}日\n{result}",
        )
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(WhatToday(bot), guilds=[discord.Object(id=GUILD_ID)])
