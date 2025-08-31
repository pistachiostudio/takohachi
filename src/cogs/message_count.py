from datetime import datetime, timedelta, timezone

import discord
from discord import app_commands
from discord.ext import commands

from settings import GUILD_ID


class MessageCount(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="count", description="このチャンネルの現在のメッセージ数を数えます。"
    )
    async def count(
        self,
        interaction: discord.Interaction,
    ):
        # interactionは3秒以内にレスポンスしないといけないとエラーになるのでこの処理を入れる。
        await interaction.response.defer()

        channel = interaction.channel
        count = 0
        async for _ in channel.history(limit=None):
            count += 1
            d_count = f"{count:,}"

        embed = discord.Embed()
        JST = timezone(timedelta(hours=+9), "JST")
        embed.timestamp = datetime.now(JST)
        embed.color = discord.Color.greyple()
        embed.description = f"このチャンネルには現在 **{d_count}** 件のメッセージがあります。"
        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="countall", description="犬～恐竜_txtの現在のメッセージ数を数えます。"
    )
    async def countall(self, interaction: discord.Interaction):
        # interactionは3秒以内にレスポンスしないといけないとエラーになるのでこの処理を入れる。
        await interaction.response.defer()

        inu_id = self.bot.get_channel(762575939623452682)  # 犬
        neko_id = self.bot.get_channel(762576579507126273)  # 猫
        kame_id = self.bot.get_channel(780611197350576200)  # 亀
        kyoryu_id = self.bot.get_channel(812312154371784704)  # 恐竜

        all_counter = 0

        async for _ in inu_id.history(limit=None):
            all_counter += 1

        async for _ in neko_id.history(limit=None):
            all_counter += 1

        async for _ in kame_id.history(limit=None):
            all_counter += 1

        async for _ in kyoryu_id.history(limit=None):
            all_counter += 1

        ttl_count = f"{all_counter:,}"

        embed = discord.Embed()
        JST = timezone(timedelta(hours=+9), "JST")
        embed.timestamp = datetime.now(JST)
        embed.color = discord.Color.blurple()
        embed.description = f"犬～恐竜_txtには現在合計 **{ttl_count}** 件のメッセージがあります。"
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(MessageCount(bot), guilds=[discord.Object(id=GUILD_ID)])
