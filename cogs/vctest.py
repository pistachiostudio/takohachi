from discord.ext import commands
import config
import asyncio
import discord

class VC_test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        
        #省きたいチャンネルidを入力
        not_01 = self.bot.get_channel(821763859949420615)
        not_02 = self.bot.get_channel(821796392224948244)
        #not_03 = self.bot.get_channel()
        #not_04 = self.bot.get_channel()
        #not_05 = self.bot.get_channel()

        #除外チャンネルの場合はreturn
        if after.channel in [not_01, not_02]:
            return

        else:
            if after.channel and len(after.channel.members) == 1:
                #メッセージを送るテキストチャンネルID
                channel_id = 821747117290160189
                text_channel = self.bot.get_channel(channel_id)
                await text_channel.send(f"**{member.nick}** が **{after.channel.name}** に入りました。")


            if before.channel and len(before.channel.members) == 0:
                #メッセージを送るテキストチャンネルID
                channel_id = 821747117290160189
                text_channel = self.bot.get_channel(channel_id)
                await text_channel.send(f"**{member.nick}** が **{before.channel.name}** に入りました。")

def setup(bot):
    bot.add_cog(VC_test(bot))