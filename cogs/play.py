import discord
from discord import message
from discord.ext import commands
from datetime import datetime, timedelta, timezone
import glob

class Play(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def saisei(self, ctx, dict):
        # mp3を再生する
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(dict), volume=0.2)
        message.guild.voice_client.play(source)


    @commands.command()
    async def play(self, ctx):

        # VCに入ってくる
        if ctx.author.voice and ctx.author.voice.channel:
            finished = False
            vc = ctx.author.voice.channel
            await vc.connect()
        else:
            await ctx.send("⚠ VCに入ってからコマンドを使用してください。")
            return

        global emojis
        emojis = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯', '🇰', '🇱',
                   '🇲', '🇳', '🇴', '🇵', '🇶', '🇷', '🇸', '🇹', '🇺', '🇻', '🇼', '🇽', '🇾', '🇿']

        # mp3フォルダ内のmp3をすべて取得して投稿
        mp3list = glob.glob('mp3/*')
        length = len(mp3list)
        true_list = []
        global mp3_name_list
        mp3_name_list = []
        for i in range(length):
            remove_prefix = mp3list[i].removeprefix('mp3\\')
            true_list.append(emojis[i] + ' ' + remove_prefix)
            mp3_name_list.append(remove_prefix)
        result = '\n'.join(true_list)
        global message
        message = await ctx.send(result)
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


    # byeコマンドでBotをVCから抜けさせる
    @commands.command()
    async def bye(self, ctx):
        await ctx.guild.voice_client.disconnect()
        await message.delete()

    # VC内の最後の一人が抜けたらBotも一緒に抜ける
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        voice_state = member.guild.voice_client
        if voice_state is None:
            return
        if len(voice_state.channel.members) == 1:
            await message.delete()
            await voice_state.disconnect()


def setup(bot):
    bot.add_cog(Play(bot))