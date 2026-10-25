import os

import discord
from discord.ext import commands

# 通知を送るテキストチャンネル
NOTIFY_CHANNEL_ID = 822096585429090324


class Vcwhite(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # 通知の対象とするVC(犬・猫・亀・恐竜)
        self.vc_ids = {
            int(os.environ[name])
            for name in ("INU_VC_ID", "NEKO_VC_ID", "KAME_VC_ID", "KYORYU_VC_ID")
        }

    @commands.Cog.listener()
    async def on_voice_state_update(
        self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState
    ):
        # 誰もいない対象のVCに、どこにも入っていなかった人が最初に入ったときだけ通知する
        if before.channel is not None or after.channel is None:
            return
        if after.channel.id not in self.vc_ids or len(after.channel.members) != 1:
            return

        await self.bot.get_channel(NOTIFY_CHANNEL_ID).send(
            f"**{discord.utils.escape_markdown(member.display_name)}** が "
            f"**{after.channel.name}** をはじめました！"
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Vcwhite(bot))
