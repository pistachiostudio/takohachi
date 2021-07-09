import asyncio
import datetime
import re
from datetime import datetime, timedelta, timezone
from random import randint
from urllib import parse

import discord
import requests
from discord.ext import commands


class WhatToday(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def whatToday(self, ctx):
        # タイムゾーンの生成
        JST = timezone(timedelta(hours=+9), 'JST')

        today = datetime.now(JST)

        this_month = today.month
        this_day = today.day

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

        await ctx.send(result)


def setup(bot):
    bot.add_cog(WhatToday(bot))
