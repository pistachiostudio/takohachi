from discord.ext import commands
from typing import Any
import discord
from datetime import datetime, timedelta, timezone


class MessageCount(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def count(self, ctx, channel: discord.TextChannel=None):

        channel = channel or ctx.channel
        count = 0
        async for _ in channel.history(limit=None):
            count += 1
            d_count = f"{count:,}"

        embed = discord.Embed()
        JST = timezone(timedelta(hours=+9), "JST")
        embed.timestamp = datetime.now(JST)
        embed.color = discord.Color.greyple()
        embed.description = f"このチャンネルには現在 **{d_count}** 件のメッセージがあります。"
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(MessageCount(bot))