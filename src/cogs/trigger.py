import os

import discord
from discord import app_commands
from discord.ext import commands

from .api import get_trigger_repository

DIC_KEY = os.environ["DIC_KEY"]
PREFIX = os.environ["PREFIX"]


class Trigger(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.trigger_repo = get_trigger_repository()

    @app_commands.command(
        name="dic",
        description="Trigger Commands"
    )
    @app_commands.describe(
        keyword="キーワードを入力してください。例) genkai, 徳井病, gomi など"
    )
    async def trigger(
        self,
        interaction: discord.Interaction,
        keyword: str
    ):

        # interactionは3秒以内にレスポンスしないといけないとエラーになるのでこの処理で待たせる。
        await interaction.response.defer()

        trigger: str = keyword
        data = self.trigger_repo.select(trigger)

        if not data:
            await interaction.followup.send(f":warning: 「{trigger}」は登録されていません。")
            return
        else:
            if data["response"]:
                await interaction.followup.send(f'{data["response"]}')
            else:
                embed = discord.Embed()
                embed.set_footer(text=f"Keyword: {keyword}")
                if data["title"]:
                    embed.title = f'{data["title"]}'
                if data["description"]:
                    embed.description = f'{data["description"]}\n\n[Check DB](https://docs.google.com/spreadsheets/d/15QCsHsmtZAs1FtiCplLmybU80WyxWw4C7G6ESf2b9f4/edit#gid=1264027664&range=A1)'
                if data["right_small_image_URL"]:
                    embed.set_thumbnail(url=f'{data["right_small_image_URL"]}')
                if data["big_image_URL"]:
                    embed.set_image(url=f'{data["big_image_URL"]}')
                embed.color = discord.Color.dark_blue()
                await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(
        Trigger(bot),
        guilds = [discord.Object(id=731366036649279518)]
    )