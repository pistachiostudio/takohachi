import logging
import os
from logging.handlers import TimedRotatingFileHandler

import discord
from discord import app_commands
from discord.ext import commands

from settings import GUILD_ID, REBOOT_LOG_CHANNEL_ID

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        TimedRotatingFileHandler("/logs/takohachi.log", when="D", interval=1, backupCount=7),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

TOKEN = os.environ["TOKEN"]
PREFIX = os.environ["PREFIX"]

# コマンド系のいつも読み込むcogs
INITIAL_EXTENSIONS = [
    "cogs.addssl",
    "cogs.bath",
    "cogs.card_list",
    "cogs.currency",
    "cogs.gakigo",
    # "cogs.happy_new_year",
    "cogs.marimo",
    "cogs.message_count",
    "cogs.ping",
    "cogs.purge",
    "cogs.spotify",
    "cogs.text_channel",
    "cogs.trigger",
    "cogs.what_today",
]

# コマンド系じゃないdevで読み込むと競合してややこしいcogs
PRODUCTION_ONLY_EXTENSIONS = [
    "cogs.autodelete",
    "cogs.card_count",
    "cogs.save_image",
    "cogs.vc_role",
    "cogs.vcwhite",
    "cogs.wt_task",
    "cogs.vl_rank_task",
]


class MyBot(commands.Bot):
    def __init__(self):
        # presences(全メンバーのオンライン状態)は使わないので要求しない。
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(
            command_prefix=PREFIX,
            intents=intents,
            help_command=None,
            # スプレッドシートの登録内容・ユーザー名・入力文字列などをそのまま投稿する箇所があるため、
            # @everyone / @here / ロールへの一斉メンションは常に無効にする。
            allowed_mentions=discord.AllowedMentions(everyone=False, roles=False, users=True),
        )
        self.tree.on_error = self.on_app_command_error

    async def setup_hook(self):
        extensions = INITIAL_EXTENSIONS
        if PREFIX == "!!":
            extensions = INITIAL_EXTENSIONS + PRODUCTION_ONLY_EXTENSIONS
        for extension in extensions:
            await self.load_extension(extension)

        # インタラクションをシンクする。ギルドコマンドなので即時反映。
        await self.tree.sync(guild=discord.Object(id=GUILD_ID))

    async def on_ready(self):
        logger.info("Connected!")
        await self.change_presence(activity=discord.Game(name="ピスタチオゲーム部"))
        channel = self.get_channel(REBOOT_LOG_CHANNEL_ID)
        if channel is not None:
            await channel.send("Rebooting... Takohachi is back!")

    async def on_app_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        # 例外の内容(内部情報)は利用者に見せず、ログにだけ残す。
        if isinstance(error, app_commands.CheckFailure):
            message = ":warning: このコマンドを実行する権限がありません。"
        else:
            command = interaction.command.name if interaction.command else "?"
            logger.error("Unhandled error in /%s", command, exc_info=error)
            message = ":warning: エラーが発生しました。"

        try:
            if interaction.response.is_done():
                await interaction.followup.send(message, ephemeral=True)
            else:
                await interaction.response.send_message(message, ephemeral=True)
        except discord.HTTPException:
            logger.exception("Failed to send the error message")


if __name__ == "__main__":
    MyBot().run(TOKEN, log_handler=None)
