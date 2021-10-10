from discord.ext import commands
import asyncio
import discord

class Vcwhite(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):

        #通知の対象としたいチャンネルidを入力
        allow_01 = self.bot.get_channel(762575797327757322) #犬
        allow_02 = self.bot.get_channel(762576579507126273) #猫
        allow_03 = self.bot.get_channel(780611246155497482) #亀
        allow_04 = self.bot.get_channel(812312211112198144) #恐竜

        #対象チャンネルかつlengthが1の場合メッセージを送る。
        if after.channel in [allow_01, allow_02, allow_03, allow_04]:
            if before.channel is None and after.channel and len(after.channel.members) == 1:

                #メッセージを送るテキストチャンネルID
                channel_id = 822096585429090324
                text_channel = self.bot.get_channel(channel_id)
                await text_channel.send(f"**{member.display_name}** が **{after.channel.name}** をはじめました！")

        else:
            pass

def setup(bot):
    bot.add_cog(Vcwhite(bot))