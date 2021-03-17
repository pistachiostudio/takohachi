from discord.ext import commands
# 以下2点のimportも、launcher.pyから持ってくること
import discord
import asyncio

class Greet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    
    @commands.command()  # ★変更点1: bot -> commandsに修正
    async def bobobob(self, ctx):  # ★変更点2: self引数を追加する
        # 待機するメッセージのチェック関数
        def check_message_author(msg):
            return msg.author is ctx.author
            
        # あいさつする既存の処理
        await ctx.send(f"こんにちは、{ctx.author.name}さん。")
        await ctx.send("ご気分はいかがでしょうか？")
        try:
            # チェック関数に合格するようなメッセージを待つ
            # ★変更点3: bot -> self.botに修正
            msg = await self.bot.wait_for('message', check=check_message_author, timeout=10)
        except asyncio.TimeoutError:
            await ctx.send("タイムアウトしました。")
            return
        # 受け取ったメッセージの内容を使って返信
        embed = discord.Embed()
        embed.color = discord.Color.blue()
        embed.description = "あなたの気分を把握しました。"
        embed.add_field(name="あなたの気分", value=msg.content)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Greet(bot))