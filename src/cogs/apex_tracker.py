import logging
import os
from datetime import datetime, timedelta, timezone

import discord
import requests
from discord import app_commands
from discord.ext import commands

from libs.logging import DiscordBotHandler

LOG_TEXT_CHANNEL_ID = os.environ["LOG_TEXT_CHANNEL_ID"]

logger = logging.getLogger(__name__)


class ApexTracker(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        log_channel = self.bot.get_channel(int(LOG_TEXT_CHANNEL_ID))
        logger.setLevel(logging.DEBUG)

        handler = DiscordBotHandler(log_channel)
        handler.setLevel(logging.INFO)

        # add ch to logger
        logger.addHandler(handler)

    def __get_rank_zone_rgb(self, rank_zone: str):
        if rank_zone == "Bronze":
            return 122, 89, 47
        elif rank_zone == "Silver":
            return 192, 192, 192
        elif rank_zone == "Gold":
            return 255, 215, 0
        elif rank_zone == "Platinum":
            return 190, 219, 217
        elif rank_zone == "Diamond":
            return 104, 176, 215
        elif rank_zone == "Master":
            return 135, 83, 186
        elif rank_zone == "Apex Predator":
            return 255, 0, 0

    @app_commands.command(name="apexrank", description="Apex Legendsのランクを取得します。")
    @app_commands.describe(platform="プラットフォームを選択してください", user_id="ユーザーIDを入力してください")
    @app_commands.choices(
        platform=[
            discord.app_commands.Choice(name="Origin & Steam(PC)", value="origin"),
            discord.app_commands.Choice(name="Xbox", value="xbl"),
            discord.app_commands.Choice(name="Play Station", value="psn"),
        ]
    )
    async def apexrank(self, interaction: discord.Interaction, platform: str, user_id: str):
        # interactionは3秒以内にレスポンスしないといけないとエラーになるのでこの処理を入れる。
        await interaction.response.defer()

        url = f"https://public-api.tracker.gg/v2/apex/standard/profile/{platform}/{user_id}"
        trn_api_key = os.environ["TRN_API_KEY"]
        headers = {"TRN-Api-Key": trn_api_key}

        res = requests.get(url, headers=headers)

        if res.status_code != 200:
            logger.error(res.json())
            await interaction.response.send_message(f"ランクポイントの取得に失敗しました...")
            return

        data = res.json()
        segments = data.get("data").get("segments")

        for segment in segments:
            if segment.get("type") == "overview":
                rank_name: str = segment.get("stats").get("rankScore").get("metadata").get("rankName")
                icon_url: str = segment.get("stats").get("rankScore").get("metadata").get("iconUrl")
                rank_point: str = segment.get("stats").get("rankScore").get("displayValue")
                break

        embed = discord.Embed()
        JST = timezone(timedelta(hours=+9), "JST")
        embed.timestamp = datetime.now(JST)

        if rank_name == "Apex Predator":
            rank_zone = rank_name
        else:
            rank_zone = rank_name.split()[0]
        r, g, b = self.__get_rank_zone_rgb(rank_zone)

        embed.color = discord.Color.from_rgb(r, g, b)  # Gold
        embed.set_thumbnail(url=icon_url)
        embed.set_author(
            name=f"{user_id}'s profile",
            url=f"https://apex.tracker.gg/apex/profile/{platform}/{user_id}/overview",
            icon_url="https://github.com/pistachiostudio/takohachi/blob/master/images/apex%20legends.jpg?raw=true",
        )
        embed.description = f"{user_id} の現在のランクポイントを表示します."
        embed.add_field(name="ランクポイント", value=f"{rank_point} point ({rank_name})")

        # interaction.response.deferを使ったのでここはfollowup.sendが必要
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(ApexTracker(bot), guilds=[discord.Object(id=731366036649279518)])
