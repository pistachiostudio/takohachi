from discord.ext import commands
import discord
from datetime import datetime, timedelta, timezone


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
    
        embed = discord.Embed()
        embed.set_thumbnail(url='https://raw.githubusercontent.com/pistachiostudio/takohachi/master/images/icon_tako_hachi_BG_less.png')
        embed.title = "takohachi commands help"
        embed.color = discord.Color.blue()
        embed.description = "Prefix は `!!` です。\n[View more info on GitHub](https://github.com/pistachiostudio/takohachi/blob/master/mannual.md)\n\n**mt**\n```まりもたいむ！```\n\n**whatToday**\n```今日はなんの日？```\n\n**apexrank <A> <B>**\n```APEXのランクポイントを表示します。\nA = origin or psn or xbl\nB = YourID```\n\n**sp <SEARCH>**\n```Spotifyの曲情報をゲットします。```\n\n**spartist <ARTIST>**\n```Spotifyのアーティスト情報をゲットします。```\n\n**addssl <URL>**\n```SSL Checkerのデータベースに新しい監視URLを登録します。```\n[SSL Checker](https://ssl-checker.vercel.app) ? [SSLC database](https://docs.google.com/spreadsheets/d/1c25pvMyjQ89OBCvB9whCQQLM_BPXKyY7umsj5wmpP2k/edit?usp=sharing)"

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Help(bot))