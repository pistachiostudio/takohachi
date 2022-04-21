import re
from datetime import datetime, timedelta, timezone
from random import randint
from urllib import parse
import requests
from discord.ext import commands, tasks
import discord

class WTTasks(commands.Cog):
    def __init__(self, bot):
        self.index = 0
        self.bot = bot
        self.printer.start()

    def cog_unload(self):
        self.printer.cancel()

    @tasks.loop(seconds=600.0)
    async def printer(self):
        channel = self.bot.get_channel(int('762575939623452682'))

        # タイムゾーンの生成
        JST = timezone(timedelta(hours=+9), 'JST')
        today = datetime.now(JST)

        this_month = today.month
        this_day = today.day
        this_hour = today.hour
        this_minute = today.minute

        if this_hour == 7 and 0 <= this_minute <= 9:
            base_url = 'https://ja.wikipedia.org/wiki/Wikipedia:'
            uri = f'今日は何の日_{this_month}月'

            res = requests.get(base_url + parse.quote(uri))
            html = res.text
            today_idx = html.index(f'id="{this_month}月{this_day}日"')
            ul_start_idx = html.index('ul', today_idx)
            ul_end_idx = html.index('/ul', ul_start_idx)
            ul = html[ul_start_idx:ul_end_idx].replace('\n', '')
            ul_match_list = re.findall(r'<li>.+?<\/li>', ul)
            ul_match_sub_list = [re.sub('<.+?>', '', s) for s in ul_match_list]
            result = ul_match_sub_list[randint(0, len(ul_match_sub_list) - 1)]

            embed = discord.Embed()
            JST = timezone(timedelta(hours=+9), "JST")
            embed.timestamp = datetime.now(JST)
            embed.color = discord.Color.green()
            embed.title = f'7時です。今日はなんの日？'
            embed.description = f"{this_month}月{this_day}日\n{result}"
            await channel.send(embed=embed)
            print('what today post done :)')
            return

    #デプロイ後Botが完全に起動してからタスクを回す
    @printer.before_loop
    async def before_printer(self):
        print('waiting until bot booting')
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(WTTasks(bot))
