from discord.ext import commands
import discord
import config

bot = commands.Bot(command_prefix="!!")

@bot.event
async def on_ready():
    print("on_ready")


bot.load_extension("dispander") #diapanderをextensionとして読み込み
bot.load_extension("cogs.tanaka")
bot.load_extension("cogs.yobro")

bot.run(config.TOKEN, bot=True, reconnect=True)