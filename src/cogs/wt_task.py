from datetime import datetime, timedelta, timezone

import discord
from discord.ext import commands, tasks

from libs.utils import get_exchange_rate, get_weather, get_what_today


class WTTasks(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.index = 0
        self.bot = bot
        self.printer.start()

    def cog_unload(self):
        self.printer.cancel()

    @tasks.loop(seconds=600.0)
    async def printer(self):
        channel = self.bot.get_channel(int("762575939623452682"))

        # タイムゾーンの生成
        JST = timezone(timedelta(hours=+9), "JST")
        today = datetime.now(JST)

        this_month = today.month
        this_day = today.day
        this_hour = today.hour
        this_minute = today.minute

        if this_hour == 7 and 0 <= this_minute <= 9:
            result = get_what_today(this_month, this_day)

            # 東京地方。citycode一覧 "https://weather.tsukumijima.net/primary_area.xml"
            citycode = 130010
            weather = get_weather(citycode)

            embed = discord.Embed()
            embed.set_footer(text=f"{weather}\n💵USD/JPY = {get_exchange_rate()}")
            embed.color = discord.Color.green()
            embed.title = f"7時です。今日はなんの日？"
            embed.description = f"{this_month}月{this_day}日\n{result}"
            await channel.send(embed=embed)
            print("what today post done :)")

    # デプロイ後Botが完全に起動してからタスクを回す
    @printer.before_loop
    async def before_printer(self):
        print("waiting until bot booting")
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(WTTasks(bot))
