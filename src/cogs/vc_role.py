import os

import discord
from discord.ext import commands

IN_THE_MOOD_ROLE = 811959216268509204


class VcRole(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # VCのID → そのVCにいる間だけ付けるロールのID(犬・猫・亀・恐竜)
        self.vc_roles = {
            int(os.environ["INU_VC_ID"]): 811809875285114911,
            int(os.environ["NEKO_VC_ID"]): 811809725741924363,
            int(os.environ["KAME_VC_ID"]): 811803298155200562,
            int(os.environ["KYORYU_VC_ID"]): 812313393020010496,
        }

    @commands.Cog.listener()
    async def on_voice_state_update(
        self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState
    ):
        if before.channel == after.channel:
            return

        roles = member.guild.get_role
        mood = roles(IN_THE_MOOD_ROLE)
        vc_roles = [roles(role_id) for role_id in self.vc_roles.values()]
        new_role_id = self.vc_roles.get(after.channel.id) if after.channel else None

        # VCから出た場合: とにかくロールを外して終わり
        if after.channel is None:
            await member.remove_roles(*vc_roles, mood)
        # どこにも入ってない状態から対象のVCに入った場合
        elif before.channel is None and new_role_id:
            await member.add_roles(roles(new_role_id), mood)
        # VCから対象のVCへ移動した場合 (IN_THE_MOOD_ROLEはそのままにする)
        elif new_role_id:
            await member.remove_roles(*vc_roles)
            await member.add_roles(roles(new_role_id))


async def setup(bot: commands.Bot):
    await bot.add_cog(VcRole(bot))
