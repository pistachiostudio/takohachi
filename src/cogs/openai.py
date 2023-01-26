import os

import aiohttp
import discord
import openai_async as openai
from discord import app_commands
from discord.ext import commands

from libs.utils import get_exchange_rate


class Openai(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="gpt",
        description="ChatGPTに質問をしましょう！"
    )
    @app_commands.describe(
        key="ChatGPTに質問をどうぞ！"
    )
    async def openai(
        self,
        interaction: discord.Interaction,
        key: str
    ):

        await interaction.response.defer()

        openai.api_key = os.getenv("OPENAI_API_KEY")

        response = await openai.complete(
            openai.api_key,
            timeout=60,
            payload={
                "model": "text-davinci-003",
                "prompt": key,
                "max_tokens": 1000,
                "temperature": 0.7,
            },
        )

        answer = response.json()["choices"][0]["text"].strip()
        tokens = response.json()['usage']['total_tokens']
        cost = round(tokens*0.00002*get_exchange_rate(), 3)
        print(tokens)
        print(get_exchange_rate())

        embed = discord.Embed()
        embed.title = f"Q. {key}"
        embed.description = answer
        embed.color = discord.Color.dark_green()
        embed.set_footer(text=f"💸この質問の料金は {cost}円 でした。")

        await interaction.followup.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(
        Openai(bot),
        guilds = [discord.Object(id=731366036649279518)]
    )
