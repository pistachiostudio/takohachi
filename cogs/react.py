from discord.ext import commands
import config
import asyncio
import discord

class React(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return                
                                  
                    
        KNGWWORDS = ['神奈川', 'kanagawa', 'Kanagawa', 'KANAGAWA', 'かながわ', 'カナガワ', 'kngw', 'KNGW', 'k.n.g.w', "K.N.G.W"]
    
        # 全NGワードについて存在確認
        for kngw in KNGWWORDS:
            if kngw in message.content:
            # NGワードを発見したらテキストチャンネルに通知
                for reaction in ["🇰", "🇳", "🇬", "🇼", "👀"]:
                    await message.add_reaction(reaction)
                    
                    
                
    #await self.bot.process_commands(message) これがcogでは不要になる！！


def setup(bot):
    bot.add_cog(React(bot))
