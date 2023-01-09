import asyncio
import logging
import os
from pathlib import Path

import discord
from discord.ext import commands

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ["TOKEN"]
PREFIX = os.environ["PREFIX"]
guild_id = 731366036649279518


def init():
    # GoogleDrive API のクレデンシャル情報を保持したファイルを生成する
    client_secrets = os.environ['CLIENT_SECRET']
    current_path = Path(os.path.realpath(__file__)).parent
    file = current_path / 'client_secrets.json'
    with open(file, 'w') as f:
        f.write(client_secrets)

    # addssl用のjsonファイルを生成
    addssl_client_secrets = os.environ['TAKOHACHI_JSON']
    addssl_current_path = Path(os.path.realpath(__file__)).parent
    file = addssl_current_path/ 'addssl_client_secrets.json'
    with open(file, 'w') as f:
        f.write(addssl_client_secrets)


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=PREFIX,
            intents=discord.Intents.all(),
            help_command=None,
        )

        self.initial_extensions = [
            "cogs.ping",
            "cogs.marimo",
            "cogs.addssl",
            "cogs.bath",
            "cogs.card_list",
            "cogs.dice",
            "cogs.message_count",
            "cogs.spotify",
            "cogs.text_channel",
            "cogs.valorant_api",
            "cogs.what_today",
            "cogs.currency",
            "cogs.play",
            "cogs.apex_tracker"
        ]

        self.initial_extensions_only_production = [
            "cogs.autodelete",
            "cogs.card_count",
            "cogs.save_image",
            "cogs.vc_role",
            "cogs.vcwhite",
            "cogs.wt_task"
        ]

    async def setup_hook(self):

        # コマンド系のいつも読み込むcogs
        for extension in self.initial_extensions:
            await self.load_extension(extension)

        # コマンド系じゃないdevで読み込むとややこしいcogs
        if PREFIX == '!!':
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
        return

bot = MyBot()
bot.run(TOKEN)
