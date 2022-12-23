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

    @tasks.loop(seconds=10.0)
    async def printer(self):
        channel_list = ["xxxxxxxxxxxxx", "cccccccccccccccc"]
        for channel_id in channel_list:
            channel = self.bot.get_channel(int(channel_id))
            now = int(time.time())
            counter = 0
            async for message in channel.history(oldest_first=True):
                message_time = int(message.created_at.timestamp())
                if now-message_time > 60:
                    await message.delete()
                counter += 1

    #デプロイ後Botが完全に起動してからタスクを回す
    @printer.before_loop
    async def before_printer(self):
        print('waiting until bot booting')
        await self.bot.wait_until_ready()

async def setup(bot: commands.Bot):
    await bot.add_cog(AutoDelete(bot))
