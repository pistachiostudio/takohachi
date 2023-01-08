from datetime import datetime, timedelta, timezone

import discord
from discord import app_commands
from discord.ext import commands

from libs.utils import get_what_today


class WhatToday(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name='wt',
        description='今日はなんの日？'
    )

    async def whatToday(
        self,
        interaction: discord.Interaction
    ):

        # タイムゾーンの生成
        JST = timezone(timedelta(hours=+9), 'JST')

        today = datetime.now(JST)

        this_month = today.month
        this_day = today.day

        result = get_what_today(this_month, this_day)

        embed = discord.Embed()
        embed.timestamp = datetime.now(JST)
        embed.color = discord.Color.green()
        embed.title = f'今日はなんの日？'
        embed.description = f"{this_month}月{this_day}日\n{result}"
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(
        WhatToday(bot),
        guilds = [discord.Object(id=731366036649279518)]
    )
