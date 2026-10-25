import asyncio

import discord
from discord.ext import commands

from views.dic import build_message, send_kwargs

from .repository import get_trigger_repository

NEKO_EMOJI = "<:p01_neko:863117588757872730>"
TRIGGER = "dendou"


class Gakigo(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.trigger_repo = get_trigger_repository()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.content != NEKO_EMOJI:
            return

        data = await asyncio.to_thread(self.trigger_repo.select, TRIGGER)
        if data:
            await message.channel.send(**send_kwargs(build_message(TRIGGER, data)))


async def setup(bot: commands.Bot):
    await bot.add_cog(Gakigo(bot))
