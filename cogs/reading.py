from discord.ext import commands
import config
import asyncio
import discord
from discord.channel import VoiceChannel

class Reading(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

voiceChannel: VoiceChannel

    @commands.is_owner()
    @commands.command()
    async def hi(self, ctx):

        global voiceChannel

        voiceChannel = await VoiceChannel.connect(message.author.voice.channel)
        await message.channel.send('読み上げBotが参加しました')

def setup(bot):
    bot.add_cog(Reading(bot))