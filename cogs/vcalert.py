from discord.ext import commands
import config
import asyncio
import discord

class VC_alert(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # 誰かがボイスチャンネルに入ったら、テキストチャンネルに通知する。
        if after.channel is not None:
            # 適当なテキストチャンネルを投稿先として使う。
            # テキストチャンネルが存在しないGuildでは失敗する
            text_channel = member.guild.text_channels[3]
            # テキストチャンネルに通知を送信
            await text_channel.send(f"**{member.name}** が **{after.channel.name}** に入りました。")


def setup(bot):
    bot.add_cog(VC_alert(bot))