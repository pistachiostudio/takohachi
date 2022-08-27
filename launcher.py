import os
from pathlib import Path

import discord
from discord.ext import commands

PREFIX = os.environ["PREFIX"]

bot = commands.Bot(command_prefix=PREFIX, help_command=None)

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

init()

bot.load_extension("cogs.apex_tracker")
bot.load_extension("cogs.commandslist")
bot.load_extension("cogs.spotify")
bot.load_extension("cogs.marimo")
bot.load_extension("cogs.what_today")
bot.load_extension("cogs.addssl")
bot.load_extension("cogs.message_count")
bot.load_extension("cogs.happy_new_year")
bot.load_extension("cogs.card_list")
bot.load_extension("cogs.trigger")
bot.load_extension("cogs.dice")
bot.load_extension("cogs.bath")
bot.load_extension("cogs.ping")
bot.load_extension("cogs.play")
bot.load_extension("cogs.vc_role")

# Productionのみで読み込むcogs
if PREFIX == '!!':
    bot.load_extension("dispander")
    bot.load_extension("cogs.wt_task")
    bot.load_extension("cogs.vcwhite")
    bot.load_extension("cogs.save_image")
    bot.load_extension("cogs.card_count")

bot.run(TOKEN)