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
        embed.description = "Prefix は `!!` です。"

        embed.add_field(name="apexrank A B",
                        value="```APEXのランクポイントを表示します。\nA = origin or psn or xbl\nB = YourID```")

        embed.add_field(name="mt",
                        value="```まりもタイム```")

        embed.add_field(name="whatToday",
                        value="```今日は何の日？```")

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))