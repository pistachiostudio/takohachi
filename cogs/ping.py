from discord.ext import commands
import discord


class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):

        latency: float = self.bot.latency
        latency_ms: int = round(latency * 1000)

        await ctx.send(f'Pong! ({latency_ms}ms)')

def setup(bot):
    bot.add_cog(Ping(bot))