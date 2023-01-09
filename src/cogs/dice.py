import random

import discord
import requests
from discord import app_commands
from discord.ext import commands


class Dice(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="dice",
        description="Valorantのマップをランダムに返します。"
    )

    async def d(
        self,
        interaction: discord.Interaction
    ):

        url = 'https://valorant-api.com/v1/maps'

        res = requests.get(url)
        json = res.json()

        data = json["data"]

        data_len = (len(data))
        data_list = list(range(data_len))

        for range_idx in range(data_len):
            if data[range_idx]['uuid'] == 'ee613ee9-28b7-4beb-9666-08db13bb2244':  # 射撃場のuuid
                break

        data_list.remove(range_idx)
        num = random.choice(data_list)

        displayName = data[num]['displayName']
        listViewIcon = data[num]['listViewIcon']
        # displayIcon = data[num]['displayIcon']

        embed = discord.Embed()
        embed.title = displayName
        embed.set_image(url=listViewIcon)
        # embed.set_thumbnail(url=displayIcon)
        embed.color = discord.Color.dark_blue()
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(
        Dice(bot),
        guilds = [discord.Object(id=731366036649279518)]
    )
