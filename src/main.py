import logging
import os
from logging.handlers import TimedRotatingFileHandler

import discord
from discord.ext import commands

from settings import ADD_SSL_CLIENT_SECRETS_PATH, CLIENT_SECRETS_PATH

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        TimedRotatingFileHandler(
            "/logs/takohachi.log",
            when="D",
            interval=1,
            backupCount=7,
        )
    ],
)

TOKEN = os.environ["TOKEN"]
PREFIX = os.environ["PREFIX"]
guild_id = 731366036649279518
reboot_log_channel_id = 901373361618296862


def init():
    # GoogleDrive API のクレデンシャル情報を保持したファイルを生成する
    client_secrets = os.environ["CLIENT_SECRET"]
    with open(CLIENT_SECRETS_PATH, "w") as f:
        f.write(client_secrets)

    # addssl用のjsonファイルを生成
    addssl_client_secrets = os.environ["TAKOHACHI_JSON"]
    with open(ADD_SSL_CLIENT_SECRETS_PATH, "w") as f:
        f.write(addssl_client_secrets)


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=PREFIX, intents=discord.Intents.all(), help_command=None)

        # コマンド系のいつも読み込むcogs
        self.initial_extensions = [
            "cogs.addssl",
            "cogs.apex_tracker",
            "cogs.bath",
            "cogs.card_list",
            "cogs.currency",
            "cogs.dice",
            "cogs.gakigo",
            # "cogs.happy_new_year",
            "cogs.marimo",
            "cogs.message_count",
            "cogs.openai",
            "cogs.ping",
            "cogs.purge",
            "cogs.spotify",
            "cogs.text_channel",
            "cogs.trigger",
            "cogs.valorant_api",
            "cogs.what_today",
        ]

        # コマンド系じゃないdevで読み込むと競合してややこしいcogs
        self.initial_extensions_only_production = [
            "cogs.autodelete",
            "cogs.card_count",
            "cogs.save_image",
            "cogs.vc_role",
            "cogs.vcwhite",
            "cogs.wt_task",
            "cogs.vl_rank_task",
        ]

    async def setup_hook(self):
        for extension in self.initial_extensions:
            await self.load_extension(extension)

        if PREFIX == "!!":
            for production_extension in self.initial_extensions_only_production:
                await self.load_extension(production_extension)

        # インタラクションをシンクする。ギルドコマンドなので即時反映。
        await bot.tree.sync(guild=discord.Object(id=guild_id))

    async def close(self):
        await super().close()
        await self.session.close()

    async def on_ready(self):
        print("Connected!")
        await bot.change_presence(activity=discord.Game(name="ピスタチオゲーム部", type=1))
        channel = bot.get_channel(reboot_log_channel_id)
        await channel.send("Rebooting... Takohachi is back!")
        return


init()
bot = MyBot()
bot.run(TOKEN)
