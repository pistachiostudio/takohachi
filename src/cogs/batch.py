from datetime import datetime, timedelta, timezone, time

import discord
from discord.ext import commands, tasks

from .api import get_trigger_repository
from libs.utils import get_exchange_rate, get_weather, get_what_today

JST = timezone(timedelta(hours=+9), 'JST')


class Batch(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cache_trigger.start()
        self.trigger_repo = get_trigger_repository()

    def cog_unload(self):
        self.cache_trigger.cancel()

    @tasks.loop(time=time(hour=5, tzinfo=JST))
    async def cache_trigger(self):
        data = self.trigger_repo.select_all()

    #デプロイ後Botが完全に起動してからタスクを回す
    @cache_trigger.before_loop
    async def before_batch(self):
        print('waiting until bot booting')
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(Batch(bot))

