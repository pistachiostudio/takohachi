from discord.ext import commands
import config
import asyncio
import discord

class Tanaka(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
        # Botからのメッセージには反応しない
        # この判定をしないと無限ループが起きる
            return
        
        DIS_WORDS = ['バカ', 'ばか', 'あほ', '死ね', 'だめ', 'ゴミ']
    
        # 全NGワードについて存在確認
        for dis_word in DIS_WORDS:
            if dis_word in message.content:
            # NGワードを発見したらテキストチャンネルに通知
                await message.channel.send(f"{dis_word}野郎はテメェだ！")
                
    #await self.bot.process_commands(message) これがcogでは不要になる！！


def setup(bot):
    bot.add_cog(Tanaka(bot))