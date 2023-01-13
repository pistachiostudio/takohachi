import logging

import discord
from discord import app_commands
from discord.ext import commands

from views.button import LinkButton

logger = logging.getLogger(__name__)


class TextChannel(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="top",
        description="チャンネルの一番上にジャンプするボタンを表示します。"
    )
    async def top(
        self,
        interaction: discord.Interaction
    ):

        logger.info(interaction.message)
        ch = interaction.channel
        url = ""
        try:
            async for message in ch.history(limit=1, oldest_first=True):
                url = message.jump_url
        except discord.Forbidden as e:
            msg = "メッセージ履歴を読み取る権限がありません!"
            logger.error(msg, exc_info=True)
            await interaction.response.send_message(msg)
            raise e
        except discord.HTTPException as e:
            msg = "メッセージ履歴の取得に失敗しました!"
            logger.error(msg, exc_info=True)
            await interaction.response.send_message(msg)
            raise e

        await interaction.response.send_message(
            "",
            view=LinkButton("Go to top on this channel", url),
            ephemeral=True
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(
        TextChannel(bot),
        guilds = [discord.Object(id=731366036649279518)]
    )
