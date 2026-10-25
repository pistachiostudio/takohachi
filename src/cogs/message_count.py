import discord
from discord import app_commands
from discord.ext import commands

from libs.utils import now_jst
from settings import GUILD_ID

# 犬～恐竜_txt
ANIMAL_CHANNEL_IDS = [
    762575939623452682,  # 犬
    762576579507126273,  # 猫
    780611197350576200,  # 亀
    812312154371784704,  # 恐竜
]


async def count_messages(channel: discord.abc.Messageable) -> int:
    return sum([1 async for _ in channel.history(limit=None)])


class MessageCount(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="count", description="このチャンネルの現在のメッセージ数を数えます。"
    )
    async def count(self, interaction: discord.Interaction):
        # interactionは3秒以内にレスポンスしないといけないとエラーになるのでこの処理を入れる。
        await interaction.response.defer()

        count = await count_messages(interaction.channel)
        embed = discord.Embed(
            color=discord.Color.greyple(),
            timestamp=now_jst(),
            description=f"このチャンネルには現在 **{count:,}** 件のメッセージがあります。",
        )
        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="countall", description="犬～恐竜_txtの現在のメッセージ数を数えます。"
    )
    async def countall(self, interaction: discord.Interaction):
        # interactionは3秒以内にレスポンスしないといけないとエラーになるのでこの処理を入れる。
        await interaction.response.defer()

        total = 0
        for channel_id in ANIMAL_CHANNEL_IDS:
            total += await count_messages(self.bot.get_channel(channel_id))
        embed = discord.Embed(
            color=discord.Color.blurple(),
            timestamp=now_jst(),
            description=f"犬～恐竜_txtには現在合計 **{total:,}** 件のメッセージがあります。",
        )
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(MessageCount(bot), guilds=[discord.Object(id=GUILD_ID)])
