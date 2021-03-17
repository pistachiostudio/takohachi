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
        not_01 = self.bot.get_channel(803245850616791040)
        not_02 = self.bot.get_channel(801064070399787028)
        #not_03 = self.bot.get_channel()
        #not_04 = self.bot.get_channel()
        #not_05 = self.bot.get_channel()

        #除外チャンネルの場合はreturn
        if after.channel in [not_01, not_02]:
            return

        else:
            if before.channel is None and after.channel is not None:
                #メッセージを送るテキストチャンネルID
                channel_id = 821804359700185088
                text_channel = self.bot.get_channel(channel_id)
                await text_channel.send(f"**{member.nick}** が **{after.channel.name}** に入りました。")

def setup(bot):
    bot.add_cog(VC_alert(bot))