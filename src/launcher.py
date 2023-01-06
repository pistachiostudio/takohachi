import asyncio
import os
from pathlib import Path

import discord
from discord.ext import commands

PREFIX = os.environ["PREFIX"]

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, help_command=None, intents=intents)

# 環境変数からトークンを読み込む
TOKEN = os.environ["TOKEN"]


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


@bot.event
async def on_ready():
    print("Yeah!_bot_is_on_ready")
    await bot.change_presence(activity=discord.Game(name="ピスタチオゲーム部", type=1))
    return


@bot.command()
async def playing(ctx, title):
    client = bot
    game = discord.Game(name=title)
    await client.change_presence(activity=game)

class Takohachi(commands.Bot):
    async def setup_hook(self):
        await self.load_extension('my_extension')

async def main():
    async with bot:

        await bot.load_extension("cogs.apex_tracker")
        await bot.load_extension("cogs.commandslist")
        await bot.load_extension("cogs.spotify")
        await bot.load_extension("cogs.marimo")
        await bot.load_extension("cogs.what_today")
        await bot.load_extension("cogs.addssl")
        await bot.load_extension("cogs.message_count")
        await bot.load_extension("cogs.happy_new_year")
        await bot.load_extension("cogs.card_list")
        await bot.load_extension("cogs.trigger")
        await bot.load_extension("cogs.dice")
        await bot.load_extension("cogs.bath")
        await bot.load_extension("cogs.ping")
        await bot.load_extension("cogs.play")
        await bot.load_extension("cogs.valorant_api")
        # await bot.load_extension("cogs.currency")

        # Productionのみで読み込むcogs
        if PREFIX == '!!':
            await bot.load_extension("cogs.autodelete")
            await bot.load_extension("cogs.wt_task")
            await bot.load_extension("cogs.vcwhite")
            await bot.load_extension("cogs.save_image")
            await bot.load_extension("cogs.card_count")
            await bot.load_extension("cogs.vc_role")

        await bot.start(TOKEN)

init()
asyncio.run(main())
