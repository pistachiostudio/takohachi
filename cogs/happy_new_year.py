import random

import discord
from discord.ext import commands

class HappyNewYear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def happy_new_year(self, ctx):
        #おみくじ！
        omikuji_list = ['大吉🎯', '中吉🐬', '小吉🍓', '末吉🍦', '吉🍨', '凶👾', '大凶💀']
        omikuji = random.choice(omikuji_list)

        # 画像URL
        # https://www.fg-a.com/newyearclipart-2.html
        image_url_list = [
            "https://www.fg-a.com/new-year/animated-fireworks.gif",
            "https://www.fg-a.com/new-year/newyear-0013.gif",
            "https://www.fg-a.com/new-year/happy-new-year-webmaster.jpg",
            "https://www.fg-a.com/new-year/animated-fireworks-2.gif",
            "https://www.fg-a.com/new-year/2019-happy-new-year-3d-animation.gif",
            "https://www.fg-a.com/new-year/2022-happy-new-year-animated.gif",
            "https://www.fg-a.com/new-year/party-celebrate.jpg",
            "https://www.fg-a.com/new-year/happy-new-year-on-black.gif",
            "https://www.fg-a.com/new-year/happy-new-year-balloons-b.gif",
            "https://www.fg-a.com/new-year/2020-happy-new-year-purple-clipart.jpg",
            "https://www.fg-a.com/new-year/2022-happy-new-year-celebrating.jpg",
            "https://www.fg-a.com/new-year/happy-new-year-fireworks.gif",
            "https://www.fg-a.com/new-year/new-year-star-animation.gif",
            "https://www.fg-a.com/new-year/dance-happy-new-year.jpg",
            "https://www.fg-a.com/new-year/new-year-clock-balloons.jpg",
            "https://www.fg-a.com/new-year/friends-new-year-celebration.jpg",
            "https://www.fg-a.com/new-year/2019-happy-new-year-baby-new-year.jpg",
            "https://www.fg-a.com/new-year/2021-happy-new-year-animated-fireworks.gif"
        ]
        image_url = random.choice(image_url_list)

        #embed
        embed = discord.Embed()
        embed.color = discord.Color.dark_green()
        embed.set_footer(text=f"おみくじ: {omikuji}")
        # embed.set_thumbnail(url=image_url)
        await ctx.send(embed=embed)
        await ctx.send(image_url)


def setup(bot):
    bot.add_cog(HappyNewYear(bot))
