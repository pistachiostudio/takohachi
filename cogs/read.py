from discord.ext import commands
import config
import asyncio
import discord
from discord.channel import VoiceChannel
from typing import Dict

class Voice(commands.Cog):
    def __init__(self, bot: DBot):
        self.bot = bot
        self.voice_clients: Dict[int, discord.VoiceClient] = {}

    @commands.command()
    async def hi(self, ctx: commands.Context):
        # VoiceChannel未参加
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send('先にボイスチャンネルに参加してください')
        vc = await ctx.author.voice.channel.connect()
        self.voice_clients[ctx.guild.id] = vc

    @commands.command()
    async def bye(self, ctx: commands.Context):
        vc = self.voice_clients.get(ctx.guild.id)
        if vc is None:
            return await ctx.send('ボイスチャンネルにまだ未参加です')
        await vc.disconnect()
        del self.voice_clients[ctx.guild.id]

def setup(bot):
    bot.add_cog(Voice(bot))