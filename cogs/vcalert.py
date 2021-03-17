from discord.ext import commands
import config
import asyncio
import discord

class VC_alert(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        VC_ID_01 = self.bot.get_channel(762561932229738509)
        VC_ID_02 = self.bot.get_channel(821760928918798408)
        #VC_ID_03 = self.bot.get_channel()
        #VC_ID_04 = self.bot.get_channel()
        #VC_ID_05 = self.bot.get_channel()

        if after.channel is VC_ID_01 and not None:
            channel_id = 821747117290160189
            text_channel = self.bot.get_channel(channel_id)
            await text_channel.send(f"@here **{member.name}** が **{after.channel.name}** に入りました。")

        elif after.channel is VC_ID_02 and not None:
            channel_id = 821747117290160189
            text_channel = self.bot.get_channel(channel_id)
            await text_channel.send(f"@here **{member.name}** が **{after.channel.name}** に入りました。")

def setup(bot):
    bot.add_cog(VC_alert(bot))