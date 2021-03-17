from discord.ext import commands
import config
import asyncio
import discord

class VC_alert(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        VC_ID_01 = self.bot.get_channel(762575797327757322)
        VC_ID_02 = self.bot.get_channel(762576631810228256)
        VC_ID_03 = self.bot.get_channel(780611246155497482)
        VC_ID_04 = self.bot.get_channel(812312211112198144)
        VC_ID_05 = self.bot.get_channel(819874983290339338)

        if after.channel is VC_ID_01 and not None:
            channel_id = 786793644283265046
            text_channel = self.bot.get_channel(channel_id)
            await text_channel.send(f"**{member.name}** が **{after.channel.name}** に入りました。")

        elif after.channel is VC_ID_02 and not None:
            channel_id = 786793644283265046
            text_channel = self.bot.get_channel(channel_id)
            await text_channel.send(f"**{member.name}** が **{after.channel.name}** に入りました。")

        elif after.channel is VC_ID_03 and not None:
            channel_id = 786793644283265046
            text_channel = self.bot.get_channel(channel_id)
            await text_channel.send(f"**{member.name}** が **{after.channel.name}** に入りました。")

        elif after.channel is VC_ID_04 and not None:
            channel_id = 786793644283265046
            text_channel = self.bot.get_channel(channel_id)
            await text_channel.send(f"**{member.name}** が **{after.channel.name}** に入りました。")

        elif after.channel is VC_ID_05 and not None:
            channel_id = 786793644283265046
            text_channel = self.bot.get_channel(channel_id)
            await text_channel.send(f"**{member.name}** が **{after.channel.name}** に入りました。")            

def setup(bot):
    bot.add_cog(VC_alert(bot))