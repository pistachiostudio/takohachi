from discord.ext import commands
import config
import asyncio
import discord

class VC_alert(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        
        #省きたいチャンネルidを入力
        not_01 = self.bot.get_channel(762575797327757322)
        not_02 = self.bot.get_channel(762576631810228256)
        not_03 = self.bot.get_channel(780611246155497482)
        not_04 = self.bot.get_channel(812312211112198144)
        not_05 = self.bot.get_channel(819874983290339338)

        #除外チャンネルの場合はreturn
        if after.channel is not_01 or after.channel is not_02 or after.channel is not_03 or after.channel is not_04 or after.channel is not_05:
            return

        else:
            if before.channel is None and after.channel is not None:
                #メッセージを送るテキストチャンネルID
                channel_id = 821804359700185088
                text_channel = self.bot.get_channel(channel_id)
                await text_channel.send(f"**{member.name}** が **{after.channel.name}** に入りました。")

def setup(bot):
    bot.add_cog(VC_alert(bot))