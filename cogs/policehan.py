from discord.ext import commands
import config
import asyncio
import discord

class Hankaku(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
        # Botからのメッセージには反応しない
        # この判定をしないと無限ループが起きる
            return
        
        HANWORDS = ['ｦ', 'ｧ', 'ｨ', 'ｩ', 'ｪ', 'ｫ', 'ｬ', 'ｭ', 'ｮ', 'ｯ', 'ｰ', 'ｱ', 'ｲ', 'ｳ', 'ｴ', 'ｵ', 'ｶ', 'ｷ', 'ｸ', 'ｹ', 'ｺ', 'ｻ', 'ｼ', 'ｽ', 'ｾ', 'ｿ', 'ﾀ', 'ﾁ', 'ﾂ', 'ﾃ', 'ﾄ', 'ﾅ', 'ﾆ', 'ﾇ', 'ﾈ', 'ﾉ', 'ﾊ', 'ﾋ', 'ﾌ', 'ﾍ', 'ﾎ', 'ﾏ', 'ﾐ', 'ﾑ', 'ﾒ', 'ﾓ', 'ﾔ', 'ﾕ', 'ﾖ', 'ﾗ', 'ﾘ', 'ﾙ', 'ﾚ', 'ﾛ', 'ﾜ', 'ﾝ', 'ﾞ', 'ﾟ']
    
        # 全NGワードについて存在確認
        for hankaku in HANWORDS:
            if hankaku in message.content:
            # NGワードを発見したらテキストチャンネルに通知
                for reaction in ["a:p00_siren:801424753419354133", ":p01_text_han:828978524596731937", ":p01_text_kaku:828979073694040084", ":p01_text_ch4:808200593813274644", ":p01_text_ch13:808515343957098496", "👀"]:
                    await message.add_reaction(reaction)
                   
                
        GOMIWORDS = ['gomi', 'GOMI', 'Gomi', 'ごみ', 'ゴミ', '53', '５３']
    
        # 全NGワードについて存在確認
        for gomi in GOMIWORDS:
            if gomi in message.content:
            # NGワードを発見したらテキストチャンネルに通知
                for reaction in ["a:p00_gomi:802176598756425779", "👀"]:
                    await message.add_reaction(reaction)
                    
                    
        KNGWWORDS = ['神奈川', 'kanagawa', 'Kanagawa', 'KANAGAWA', 'かながわ', 'カナガワ', 'kngw', 'KNGW', 'k.n.g.w', "K.N.G.W"]
    
        # 全NGワードについて存在確認
        for kngw in KNGWWORDS:
            if kngw in message.content:
            # NGワードを発見したらテキストチャンネルに通知
                for reaction in ["🇰", "🇳", "🇬", "🇼", "👀"]:
                    await message.add_reaction(reaction)
                    
                    
                
    #await self.bot.process_commands(message) これがcogでは不要になる！！


def setup(bot):
    bot.add_cog(Hankaku(bot))
