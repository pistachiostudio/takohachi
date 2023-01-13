import os

import discord
from discord.ext import commands


class VcRole(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):

        INU_VC_ID = int(os.environ["INU_VC_ID"])
        NEKO_VC_ID = int(os.environ["NEKO_VC_ID"])
        KAME_VC_ID = int(os.environ["KAME_VC_ID"])
        KYORYU_VC_ID = int(os.environ["KYORYU_VC_ID"])

        IN_THE_MOOD_ROLE = 811959216268509204
        IN_INU_ROLE = 811809875285114911
        IN_NEKO_ROLE = 811809725741924363
        IN_KAME_ROLE = 811803298155200562
        IN_KYORYU_ROLE = 812313393020010496

        role_mood = discord.utils.get(member.guild.roles, id=IN_THE_MOOD_ROLE)
        role_inu = discord.utils.get(member.guild.roles, id=IN_INU_ROLE)
        role_neko = discord.utils.get(member.guild.roles, id=IN_NEKO_ROLE)
        role_kame = discord.utils.get(member.guild.roles, id=IN_KAME_ROLE)
        role_kyoryu = discord.utils.get(member.guild.roles, id=IN_KYORYU_ROLE)

        # どこにも入ってない状態からVCに入った場合
        if before.channel == None and after.channel != None:
            # 犬VCに入った場合
            if after.channel.id == INU_VC_ID:
                await member.add_roles(role_inu, role_mood)
            # 猫VCに入った場合
            elif after.channel.id == NEKO_VC_ID:
                await member.add_roles(role_neko, role_mood)
            # 亀VCに入った場合
            elif after.channel.id == KAME_VC_ID:
                await member.add_roles(role_kame, role_mood)
            # 恐竜VCに入った場合
            elif after.channel.id == KYORYU_VC_ID:
                await member.add_roles(role_kyoryu, role_mood)
            else:
                pass

        # VCからVCへ移動した場合 (IN_THE_MOOD_ROLEはそのままにする)
        elif before.channel != None and after.channel != None:
            # 移動先が犬VCの場合
            if  after.channel.id == INU_VC_ID:
                # まず絵文字を一旦取ってからロールをつける
                await member.remove_roles(role_inu, role_neko, role_kame, role_kyoryu)
                await member.add_roles(role_inu)
            # 移動先が猫VCの場合
            elif after.channel.id == NEKO_VC_ID:
                # まず絵文字を一旦取ってからロールをつける
                await member.remove_roles(role_inu, role_neko, role_kame, role_kyoryu)
                await member.add_roles(role_neko)
            # 移動先が亀VCの場合
            elif after.channel.id == KAME_VC_ID:
                # まず絵文字を一旦取ってからロールをつける
                await member.remove_roles(role_inu, role_neko, role_kame, role_kyoryu)
                await member.add_roles(role_kame)
            # 移動先が恐竜VCの場合
            elif after.channel.id == KYORYU_VC_ID:
                # まず絵文字を一旦取ってからロールをつける
                await member.remove_roles(role_inu, role_neko, role_kame, role_kyoryu)
                await member.add_roles(role_kyoryu)
            else:
                pass

        # VCから出た場合
        elif before.channel != None and after.channel == None:
            # とにかくロールを外して終わり
            await member.remove_roles(role_inu, role_neko, role_kame, role_kyoryu, role_mood)

        else:
            pass

async def setup(bot: commands.Bot):
    await bot.add_cog(VcRole(bot))