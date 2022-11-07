import discord
from discord.ext import commands


class Ping(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):

        latency: float = self.bot.latency
        latency_ms: int = round(latency * 1000)

        await ctx.send(f'Pong! ({latency_ms}ms)')

async def setup(bot: commands.Bot):
    await bot.add_cog(Ping(bot))
