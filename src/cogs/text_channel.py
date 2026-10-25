import logging

import discord
from discord import app_commands
from discord.ext import commands

from settings import GUILD_ID
from views.button import LinkButton

logger = logging.getLogger(__name__)


class TextChannel(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="top", description="チャンネルの一番上にジャンプするボタンを表示します。"
    )
    async def top(self, interaction: discord.Interaction):
        # interactionは3秒以内にレスポンスしないといけないとエラーになるのでこの処理を入れる。
        await interaction.response.defer()

        try:
            first = [m async for m in interaction.channel.history(limit=1, oldest_first=True)]
        except discord.Forbidden:
            logger.exception("No permission to read the channel history")
            await interaction.followup.send("メッセージ履歴を読み取る権限がありません!")
            return
        except discord.HTTPException:
            logger.exception("Failed to read the channel history")
            await interaction.followup.send("メッセージ履歴の取得に失敗しました!")
            return

        if not first:
            await interaction.followup.send("このチャンネルにはまだメッセージがありません。")
            return
        await interaction.followup.send(
            view=LinkButton("Go to top on this channel", first[0].jump_url), ephemeral=True
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(TextChannel(bot), guilds=[discord.Object(id=GUILD_ID)])
