from discord.ext import commands
import config
import asyncio
import discord
from discord.channel import VoiceChannel

class Reading(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hi(self, ctx):
        vc = ctx.author.voice.channel
        await ctx.send(f'失礼します。')
        await vc.connect()

def setup(bot):
    bot.add_cog(Reading(bot))