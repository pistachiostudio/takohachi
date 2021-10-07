from discord.ext import commands
import asyncio
import discord

class Vcwhite(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):

        #省きたいチャンネルidを入力
        not_01 = self.bot.get_channel(762575797327757322) #犬
        not_02 = self.bot.get_channel(780611246155497482) #猫
        not_03 = self.bot.get_channel(780611246155497482) #亀
        not_04 = self.bot.get_channel(812312211112198144) #恐竜
        
        #除外チャンネルの場合はreturn
        if after.channel not in [not_01, not_02, not_03, not_04]:
            pass

        elif before.channel is None and after.channel and len(after.channel.members) == 1:
                #メッセージを送るテキストチャンネルID
                channel_id = 822096585429090324
                text_channel = self.bot.get_channel(channel_id)
                await text_channel.send(f"**{member.display_name}** が **{after.channel.name}** をはじめました。")

def setup(bot):
    bot.add_cog(Vcwhite(bot))