import os
from datetime import datetime, timedelta, timezone

import discord
from discord.ext import commands

from .api import get_trigger_repository

DIC_KEY = os.environ["DIC_KEY"]
PREFIX = os.environ["PREFIX"]


class Trigger(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.trigger_repo = get_trigger_repository()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if not message.content.startswith(PREFIX):
            return

        trigger: str = message.content.lstrip(PREFIX)
        data = self.trigger_repo.select(trigger)

        if not data:
            return
        else:
            if data["response"]:
                await message.channel.send(f'{data["response"]}')
            else:
                embed = discord.Embed()
                JST = timezone(timedelta(hours=+9), "JST")
                embed.timestamp = datetime.now(JST)
                if data["title"]:
                    embed.title = f'{data["title"]}'
                if data["description"]:
                    embed.description = f'{data["description"]}\n\n[Check DB](https://docs.google.com/spreadsheets/d/15QCsHsmtZAs1FtiCplLmybU80WyxWw4C7G6ESf2b9f4/edit#gid=1264027664&range=A1)'
                if data["right_small_image_URL"]:
                    embed.set_thumbnail(url=f'{data["right_small_image_URL"]}')
                if data["big_image_URL"]:
                    embed.set_image(url=f'{data["big_image_URL"]}')
                embed.color = discord.Color.dark_blue()
                await message.channel.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Trigger(bot))

