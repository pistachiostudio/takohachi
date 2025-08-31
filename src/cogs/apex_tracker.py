import logging
import os
from datetime import datetime, timedelta, timezone

import discord
from discord import app_commands
from discord.ext import commands

from settings import GUILD_ID
from libs.http_client import HTTPClient, handle_api_error
from libs.logging import DiscordBotHandler

LOG_TEXT_CHANNEL_ID = os.environ["LOG_TEXT_CHANNEL_ID"]
APEX_LEGENDS_API_BASE_URL = "https://api.mozambiquehe.re"

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
        """
        ランク帯に応じたRGB値を返す
        """
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
    @app_commands.describe(
        platform="プラットフォームを選択してください", user_id="ユーザーIDを入力してください"
    )
    @app_commands.choices(
        platform=[
            discord.app_commands.Choice(name="PC (Origin or Steam)", value="PC"),
            discord.app_commands.Choice(name="PS4 (Playstation 4/5)", value="PS4"),
            discord.app_commands.Choice(name="X1 (Xbox)", value="X1"),
        ]
    )
    async def apexrank(self, interaction: discord.Interaction, platform: str, user_id: str):
        # interactionは3秒以内にレスポンスしないといけないとエラーになるのでこの処理を入れる。
        await interaction.response.defer()

        url = f"{APEX_LEGENDS_API_BASE_URL}/bridge"
        apex_api_key = os.environ["APEX_API_KEY"]
        headers = {"Authorization": apex_api_key}
        params = {"player": user_id, "platform": platform}

        try:
            client = HTTPClient()
            data = await client.get(url, headers=headers, params=params)
        except Exception as e:
            logger.error(f"Failed to fetch Apex rank: {e}")
            await handle_api_error(interaction, e, "Apex Legends API")
            return

        rank = data["global"]["rank"]

        rank_name: str = rank.get("rankName")
        rank_score: int = rank.get("rankScore")
        rank_div: int = rank.get("rankDiv")
        rank_img_url: str = rank.get("rankImg")

        # プレイヤーが上位何%にいるか
        al_stop_percent: float = rank.get("ALStopPercent")
        al_stop_percent_grobal: float = rank.get("ALStopPercentGlobal")

        embed = discord.Embed()
        JST = timezone(timedelta(hours=+9), "JST")
        embed.timestamp = datetime.now(JST)

        r, g, b = self.__get_rank_zone_rgb(rank_name)

        embed.color = discord.Color.from_rgb(r, g, b)  # Gold
        embed.set_thumbnail(url=rank_img_url)
        embed.set_author(
            name=f"{user_id}'s profile (Apex Legends Status)",
            url=f"https://apexlegendsstatus.com/profile/{platform}/{user_id}",
            icon_url="https://github.com/pistachiostudio/takohachi/blob/main/images/apex_legends.jpg?raw=true",
        )
        embed.description = f"{user_id} の現在のランクポイントを表示します."
        embed.add_field(name="", value=f"{rank_score} RP({rank_name} {rank_div})")
        embed.add_field(
            name="",
            value=f"Top {al_stop_percent}% ({platform} only) / Top {al_stop_percent_grobal}% (Global)",
        )

        # interaction.response.deferを使ったのでここはfollowup.sendが必要
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(ApexTracker(bot), guilds=[discord.Object(id=GUILD_ID)])
