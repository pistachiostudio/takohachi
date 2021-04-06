from discord.ext import commands
import config
import asyncio
import discord

class Zenkaku(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
        # Botからのメッセージには反応しない
        # この判定をしないと無限ループが起きる
            return
        
        ZENWORDS = ['Ａ', 'Ｂ', 'Ｃ', 'Ｄ', 'Ｅ', 'Ｆ', 'Ｇ', 'Ｈ', 'Ｉ', 'Ｊ', 'Ｋ', 'Ｌ', 'Ｍ', 'Ｎ', 'Ｏ', 'Ｐ', 'Ｑ', 'Ｒ', 'Ｓ', 'Ｔ', 'Ｕ', 'Ｖ', 'Ｗ', 'Ｘ', 'Ｙ', 'Ｚ', 'ａ', 'ｂ', 'ｃ', 'ｄ', 'ｅ', 'ｆ', 'ｇ', 'ｈ', 'ｉ', 'ｊ', 'ｋ', 'ｌ', 'ｍ', 'ｎ', 'ｏ', 'ｐ', 'ｑ', 'ｒ', 'ｓ', 'ｔ', 'ｕ', 'ｖ', 'ｗ', 'ｘ', 'ｙ', 'ｚ', '０', '１', '２', '３', '４', '５', '６', '７', '８', '９']
    
        # 全NGワードについて存在確認
        for zenkaku in ZENWORDS:
            if zenkaku in message.content:
            # NGワードを発見したらテキストチャンネルに通知
                for reaction in [":kissing:", ":eyes:",]:
                    await ctx.add_reaction(reaction)
                
    #await self.bot.process_commands(message) これがcogでは不要になる！！


def setup(bot):
    bot.add_cog(Zenkaku(bot))