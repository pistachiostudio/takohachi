import random

import discord
from discord import app_commands
from discord.ext import commands


class HappyNewYear(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="hny",
        description="あけましておめでとうございます！おみくじを引きます。"
    )

    async def hny(
        self,
        interaction: discord.Interaction
    ):
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
        embed.title = "🐰ピスタチオおみくじ 2023🐰"
        embed.description = f"おめでとうございます！\n{interaction.user.mention} さんの2023年の運勢は **{omikuji}** です👍"
        embed.color = discord.Color.dark_green()
        embed.set_footer(text=f"Happy New Year 2023! Love from Pistachio Studio & Gaming❤")
        embed.set_image(url=image_url)
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(
        HappyNewYear(bot),
        guilds = [discord.Object(id=731366036649279518)]
    )
