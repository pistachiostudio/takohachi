import time
from datetime import datetime, timedelta, timezone

import discord
from discord.ext import commands, tasks


class AutoDelete(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.index = 0
        self.bot = bot
        self.printer.start()

    def cog_unload(self):
        self.printer.cancel()

    @tasks.loop(seconds=600.0)
    async def printer(self):
        channel = self.bot.get_channel(int('780611197350576200'))

        now = int(time.time())

        counter = 0
        async for message in channel.history():
            message_time = int(message.created_at.timestamp())
            if now-message_time > 43200:
                await message.delete()
            counter += 1

    #デプロイ後Botが完全に起動してからタスクを回す
    @printer.before_loop
    async def before_printer(self):
        print('waiting until bot booting')
        await self.bot.wait_until_ready()

async def setup(bot: commands.Bot):
    await bot.add_cog(AutoDelete(bot))
