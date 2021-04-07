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
        # VoiceChannel未参加
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send('先にボイスチャンネルに参加してください')
        vc = await ctx.author.voice.channel.connect()
        self.voice_clients[ctx.guild.id] = vc
        await message.channel.send('読み上げBotが参加しました')


def setup(bot):
    bot.add_cog(Reading(bot))