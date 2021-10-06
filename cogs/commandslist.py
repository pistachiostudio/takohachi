from discord.ext import commands
import discord
from datetime import datetime, timedelta, timezone


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
    
        embed = discord.Embed()
        JST = timezone(timedelta(hours=+9), "JST")
        embed.timestamp = datetime.now(JST)
        embed.title = "Tako-Hachi commands help"
        embed.color = discord.Color.blue()
        embed.description = "Prefix は `!!` です。\n[View more info on GitHub](https://github.com/pistachiostudio/takohachi/blob/master/mannual.md)\n\n**mt**\n```まりもたいむ！```\n**whatToday**\n```今日はなんの日？```\n**apexrank A B**\n```APEXのランクポイントを表示します。\nA = origin or psn or xbl\nB = YourID```\n**sp SEARCH**\n```Spotifyの曲情報をゲットします！\nex) !!sp chelmico power```\n**spartist ARTIST**\n```Spotifyのアーティスト情報をゲットします！\nex) !!spartist in the blue shirt```"

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Help(bot))