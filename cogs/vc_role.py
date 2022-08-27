import os

from discord.ext import commands
import discord

class VcRole(commands.Cog):
    def __init__(self, bot):
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

        channel = before.channel or after.channel

        #犬VC
        if channel.id == INU_VC_ID:
            if before.channel is None and after.channel is not None:
                role_inu = discord.utils.get(member.guild.roles, id=IN_INU_ROLE)
                await member.add_roles(role_inu)
                role_mood = discord.utils.get(member.guild.roles, id=IN_THE_MOOD_ROLE)
                await member.add_roles(role_mood)

            elif before.channel is not None and after.channel is None:
                role_inu = discord.utils.get(member.guild.roles, id=IN_INU_ROLE)
                await member.remove_roles(role_inu)
                role_neko = discord.utils.get(member.guild.roles, id=IN_NEKO_ROLE)
                await member.remove_roles(role_neko)
                role_kame = discord.utils.get(member.guild.roles, id=IN_KAME_ROLE)
                await member.remove_roles(role_kame)
                role_kyoryu = discord.utils.get(member.guild.roles, id=IN_KYORYU_ROLE)
                await member.remove_roles(role_kyoryu)
                role_mood = discord.utils.get(member.guild.roles, id=IN_THE_MOOD_ROLE)
                await member.remove_roles(role_mood)
                return

        #猫VC
        elif channel.id == NEKO_VC_ID:
            if before.channel is None and after.channel is not None:
                role_neko = discord.utils.get(member.guild.roles, id=IN_NEKO_ROLE)
                await member.add_roles(role_neko)
                role_mood = discord.utils.get(member.guild.roles, id=IN_THE_MOOD_ROLE)
                await member.add_roles(role_mood)
                return

            elif before.channel is not None and after.channel is None:
                role_inu = discord.utils.get(member.guild.roles, id=IN_INU_ROLE)
                await member.remove_roles(role_inu)
                role_neko = discord.utils.get(member.guild.roles, id=IN_NEKO_ROLE)
                await member.remove_roles(role_neko)
                role_kame = discord.utils.get(member.guild.roles, id=IN_KAME_ROLE)
                await member.remove_roles(role_kame)
                role_kyoryu = discord.utils.get(member.guild.roles, id=IN_KYORYU_ROLE)
                await member.remove_roles(role_kyoryu)
                role_mood = discord.utils.get(member.guild.roles, id=IN_THE_MOOD_ROLE)
                await member.remove_roles(role_mood)
                return

        #亀VC
        elif channel.id == KAME_VC_ID:
            if before.channel is None and after.channel is not None:
                role_kame = discord.utils.get(member.guild.roles, id=IN_KAME_ROLE)
                await member.add_roles(role_kame)
                role_mood = discord.utils.get(member.guild.roles, id=IN_THE_MOOD_ROLE)
                await member.add_roles(role_mood)
                return

            elif before.channel is not None and after.channel is None:
                role_inu = discord.utils.get(member.guild.roles, id=IN_INU_ROLE)
                await member.remove_roles(role_inu)
                role_neko = discord.utils.get(member.guild.roles, id=IN_NEKO_ROLE)
                await member.remove_roles(role_neko)
                role_kame = discord.utils.get(member.guild.roles, id=IN_KAME_ROLE)
                await member.remove_roles(role_kame)
                role_kyoryu = discord.utils.get(member.guild.roles, id=IN_KYORYU_ROLE)
                await member.remove_roles(role_kyoryu)
                role_mood = discord.utils.get(member.guild.roles, id=IN_THE_MOOD_ROLE)
                await member.remove_roles(role_mood)
                return

        #恐竜VC
        elif channel.id == KYORYU_VC_ID:
            if before.channel is None and after.channel is not None:
                role_kyoryu = discord.utils.get(member.guild.roles, id=IN_KYORYU_ROLE)
                await member.add_roles(role_kyoryu)
                role_mood = discord.utils.get(member.guild.roles, id=IN_THE_MOOD_ROLE)
                await member.add_roles(role_mood)
                return

            elif before.channel is not None and after.channel is None:
                role_inu = discord.utils.get(member.guild.roles, id=IN_INU_ROLE)
                await member.remove_roles(role_inu)
                role_neko = discord.utils.get(member.guild.roles, id=IN_NEKO_ROLE)
                await member.remove_roles(role_neko)
                role_kame = discord.utils.get(member.guild.roles, id=IN_KAME_ROLE)
                await member.remove_roles(role_kame)
                role_kyoryu = discord.utils.get(member.guild.roles, id=IN_KYORYU_ROLE)
                await member.remove_roles(role_kyoryu)
                role_mood = discord.utils.get(member.guild.roles, id=IN_THE_MOOD_ROLE)
                await member.remove_roles(role_mood)
                return

        else:
            pass

def setup(bot):
    bot.add_cog(VcRole(bot))
