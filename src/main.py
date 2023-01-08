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
            "cogs.slash",
            "cogs.ping",
            "cogs.marimo"
        ]

    async def setup_hook(self):
        for extension in self.initial_extensions:
            await self.load_extension(extension)

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
