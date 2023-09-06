import random

import discord
import httpx
from discord import app_commands
from discord.ext import commands


class Dice(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="dice", description="Valorantのマップをランダムに返します。")
    async def d(self, interaction: discord.Interaction):
        # interactionは3秒以内にレスポンスしないといけないとエラーになるのでこの処理を入れる。
        await interaction.response.defer()

        url = "https://valorant-api.com/v1/maps"
        async with httpx.AsyncClient() as client:
            res = await client.get(url)
        json = res.json()

        data = json["data"]

        # 除外したいuuidのリストを作成
        excluded_uuids = [
            "ee613ee9-28b7-4beb-9666-08db13bb2244",  # 射撃場のuuid
            "690b3ed2-4dff-945b-8223-6da834e30d24",  # Districtのuuid
            "12452a9d-48c3-0b02-e7eb-0381c3520404",  # Kasbahのuuid
            "de28aa9b-4cbe-1003-320e-6cb3ec309557"   # Piazzaのuuid
        ]

        data_list = [idx for idx, d in enumerate(data) if d["uuid"] not in excluded_uuids]

        num = random.choice(data_list)

        displayName = data[num]["displayName"]
        listViewIcon = data[num]["listViewIcon"]
        # displayIcon = data[num]['displayIcon']

        embed = discord.Embed()
        embed.title = displayName
        embed.set_image(url=listViewIcon)
        # embed.set_thumbnail(url=displayIcon)
        embed.color = discord.Color.dark_blue()
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Dice(bot), guilds=[discord.Object(id=731366036649279518)])
