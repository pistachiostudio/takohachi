import os
from pathlib import Path

import discord
from discord.ext import commands

bot = commands.Bot(command_prefix="!!", help_command=None)

# 環境変数からトークンを読み込む
TOKEN = os.environ["TOKEN"]


def init():
    # GoogleDrive API のクレデンシャル情報を保持したファイルを生成する
    client_secrets = os.environ['CLIENT_SECRET']
    current_path = Path(os.path.realpath(__file__)).parent
    file = current_path / 'client_secrets.json'
    with open(file, 'w') as f:
        f.write(client_secrets)


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


init()

bot.load_extension("dispander")  # diapanderをextensionとして読み込み
# bot.load_extension("cogs.tanaka")
bot.load_extension("cogs.marimo")
# bot.load_extension("cogs.read")
# bot.load_extension("cogs.policezen")
# bot.load_extension("cogs.policehan")
# bot.load_extension("cogs.react")
# bot.load_extension("cogs.yobro")
# bot.load_extension("cogs.vcalert")
bot.load_extension("cogs.vctest")
# bot.load_extension("cogs.greet")
# bot.load_extension("cogs.notify")
bot.load_extension("cogs.what_today")
bot.load_extension("cogs.save_image")
# bot.load_extension("cogs.delete_image")
bot.load_extension("cogs.apex_tracker")
bot.load_extension("cogs.commandslist")
bot.load_extension("cogs.spotify")

bot.run(TOKEN)
