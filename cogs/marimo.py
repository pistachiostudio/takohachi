from discord.ext import commands
import datetime
from datetime import timedelta


class Marimo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def mt(self, ctx):
        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4)))
        JST = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=+9)))
        marimo_time = f"{now.month}/{now.day} {now.hour}:{now.minute:02}"
        japan_time = f"{JST.month}/{JST.day} {JST.hour}:{JST.minute:02}"
        await ctx.send(f"marimo time = **{marimo_time}**\n(In Japan = {japan_time})")


def setup(bot):
    bot.add_cog(Marimo(bot))
