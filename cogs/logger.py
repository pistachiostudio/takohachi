import logging
import os
from datetime import datetime, timedelta, timezone
from io import StringIO

import discord
import requests
from discord import channel
from discord.ext import commands
from libs import embed

from ..libs.embed import get_custum_embed

# https://qiita.com/izmktr/items/77f684f6121c103cc194
# logging handler の独自実装について -> https://nowaai.github.io/posts/logging/

class DiscordHandler(logging.Handler):

    def __init__(self, log_channel: discord.TextChannel) -> None:
        print()
        self.log_channel = log_channel
    
    def emit(self, record):
        try:
            print(record)
            embed = get_custum_embed()
        except Exception:
            self.handleError(record)

class TakohachiLogger(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.log_channel: discord.TextChannel = self.bot.get_channel(os.environ["LOG_CHANNEL_ID"])

    @commands.command()
    async def snapshot(self, ctx):
        await ctx.message.delete()

        messages = []
        for message in ctx.history(limit=100):
            messages.append(message)
        numbers = "\n".join(
            f"{message.author}: {message.clean_content}" for message in messages
        )

        JST = timezone(timedelta(hours=+9), "JST")
        timestamp = datetime.now(JST)
        with StringIO(numbers) as f:
            file = discord.File(f, f"snapshot-{timestamp}.log")
            await self.log_channel.send(file)

    async def info(self, msg) -> None:
        await self.log_channel.send(msg)



class ApexTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def __get_rank_zone_rgb(self, rank_zone: str):
        if rank_zone == "Bronze":
            return 122, 89, 47
        elif rank_zone == "Silver":
            return 192, 192, 192
        elif rank_zone == "Gold":
            return 255, 215, 0
        elif rank_zone == "Platinum":
            return 190, 219, 217
        elif rank_zone == "Diamond":
            return 104, 176, 215
        elif rank_zone == "Master":
            return 135, 83, 186
        elif rank_zone == "Apex Predator":
            return 255, 0, 0

    @commands.command()
    async def apexrank(self, ctx, platform, user_id):
        url = f"https://public-api.tracker.gg/v2/apex/standard/profile/{platform}/{user_id}"
        trn_api_key = os.environ["TRN_API_KEY"]
        headers = {"TRN-Api-Key": trn_api_key}

        res = requests.get(url, headers=headers)

        if res.status_code != 200:
            await ctx.send(f"ランクポイントの取得に失敗しました...")
            return

        data = res.json()
        segments = data.get("data").get("segments")

        for segment in segments:
            if segment.get("type") == "overview":
                rank_name: str = segment.get("stats").get(
                    "rankScore").get("metadata").get("rankName")
                icon_url: str = segment.get("stats").get(
                    "rankScore").get("metadata").get("iconUrl")
                rank_point: str = segment.get("stats").get(
                    "rankScore").get("displayValue")
                break

        embed = discord.Embed()
        JST = timezone(timedelta(hours=+9), "JST")
        embed.timestamp = datetime.now(JST)

        if rank_name == "Apex Predator":
            rank_zone = rank_name
        else:
            rank_zone = rank_name.split()[0]
        r, g, b = self.__get_rank_zone_rgb(rank_zone)

        embed.color = discord.Color.from_rgb(r, g, b)  # Gold
        embed.set_thumbnail(url=icon_url)
        embed.set_author(name=f"{user_id}'s profile",
                         url=f"https://apex.tracker.gg/apex/profile/{platform}/{user_id}/overview",
                         icon_url="https://github.com/pistachiostudio/takohachi/blob/master/images/apex%20legends.jpg?raw=true")
        embed.description = f"{user_id} の現在のランクポイントを表示します."
        embed.add_field(name="ランクポイント",
                        value=f"{rank_point} point ({rank_name})")
        await ctx.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(ApexTracker(bot))
