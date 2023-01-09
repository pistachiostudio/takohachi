import glob
from datetime import datetime, timedelta, timezone

import discord
from discord import app_commands, message
from discord.ext import commands


class Play(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="play",
        description="マル秘音楽を再生します。VCに入ってからコマンドを使用してください。"
    )
    async def play(
        self,
        interaction: discord.Interaction
    ):

        # VCに入ってくる
        if interaction.user.voice and interaction.user.voice.channel:
            finished = False
            vc = interaction.user.voice.channel
            await vc.connect()
        else:
            await interaction.response.send_message(
                "⚠ VCに入ってからコマンドを使用してください。",
                ephemeral=True,
                delete_after=10
            )
            return

        global emojis
        emojis = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯', '🇰', '🇱',
                   '🇲', '🇳', '🇴', '🇵', '🇶', '🇷', '🇸', '🇹', '🇺', '🇻', '🇼', '🇽', '🇾', '🇿']

        # mp3フォルダ内のmp3をすべて取得して投稿
        mp3list = sorted(glob.glob('mp3/*'))
        length = len(mp3list)
        true_list = []
        global mp3_name_list
        mp3_name_list = []
        for i in range(length):
            remove_prefix = mp3list[i].removeprefix('mp3/')
            true_list.append(emojis[i] + ' ' + remove_prefix)
            mp3_name_list.append(remove_prefix)
        result = '\n'.join(true_list)

        global message
        await interaction.response.send_message(
            "🎶再生したい曲の絵文字を押してください。\n👋で終了し、BotがVCから切断されます。",
            delete_after=10
        )
        message = await interaction.channel.send(result)
        global message_id
        message_id = str(message.id)

        # 絵文字をつける処理
        for idx in range(length):
            await message.add_reaction(emojis[idx])
        for bye_emoji in ['⏹', '👋']:
            await message.add_reaction(bye_emoji)

    # 再生のところ
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # botのリアクションは無視する
        if payload.member.bot:
            return

        react_msg_id = str(payload.message_id)
        react_emoji = str(payload.emoji)
        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)

        #他のリアクションは無視する
        if react_msg_id == message_id:

            # 停止ボタンの場合はとりあえず止める。
            if react_emoji == '⏹':
                message.guild.voice_client.stop()
                await message.remove_reaction(react_emoji, payload.member)
            elif react_emoji == '👋':
                await message.guild.voice_client.disconnect()
                await message.delete()
            else:
                # 再生中のmp3があれば停止する
                message.guild.voice_client.pause()
                # emojisのindexを取得
                play_idx = emojis.index(react_emoji)
                play_mp3_name = mp3_name_list[play_idx]
                # mp3を再生する
                source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(f"mp3/{play_mp3_name}"), volume=0.2)
                message.guild.voice_client.play(source)
                await message.remove_reaction(react_emoji, payload.member)
    """
    # byeコマンドでBotをVCから抜けさせる
    @commands.command()
    async def bye(self, ctx):
        await ctx.guild.voice_client.disconnect()
        await message.delete()
        await ctx.message.delete()
    """
    # VC内の最後の一人が抜けたらBotも一緒に抜ける
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        voice_state = member.guild.voice_client
        if voice_state is None:
            return
        if len(voice_state.channel.members) == 1:
            await message.delete()
            await voice_state.disconnect()


async def setup(bot: commands.Bot):
    await bot.add_cog(
        Play(bot),
        guilds = [discord.Object(id=731366036649279518)]
    )
