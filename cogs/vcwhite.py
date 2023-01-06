import os

from discord.ext import commands


class Vcwhite(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):

        #通知の対象としたいチャンネルidを入力
        INU_VC_ID = self.bot.get_channel(int(os.environ["INU_VC_ID"])) #犬
        NEKO_VC_ID = self.bot.get_channel(int(os.environ["NEKO_VC_ID"])) #猫
        KAME_VC_ID = self.bot.get_channel(int(os.environ["KAME_VC_ID"])) #亀
        KYORYU_VC_ID = self.bot.get_channel(int(os.environ["KYORYU_VC_ID"])) #恐竜

        #対象チャンネルかつlengthが1の場合メッセージを送る。
        if after.channel in [INU_VC_ID, NEKO_VC_ID, KAME_VC_ID, KYORYU_VC_ID]:
            if before.channel is None and after.channel and len(after.channel.members) == 1:

                #メッセージを送るテキストチャンネルID
                channel_id = 822096585429090324
                text_channel = self.bot.get_channel(channel_id)
                await text_channel.send(f"**{member.display_name}** が **{after.channel.name}** をはじめました！")

        else:
            pass

async def setup(bot: commands.Bot):
    await bot.add_cog(Vcwhite(bot))