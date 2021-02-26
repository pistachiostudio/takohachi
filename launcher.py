from discord.ext import commands
import config
from cogs import tanaka
from cogs import yobro


bot = commands.Bot(command_prefix="!!")

@bot.event
async def on_ready():
    print("on_ready")
    return

@bot.command()
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}') #loads the extension in the "cogs" folder
    await ctx.send(f'Loaded "{extension}"')
    print(f'Loaded "{extension}"')
    return

bot.load_extension("dispander") #diapanderをextensionとして読み込み
bot.load_extension("cogs.tanaka")
bot.load_extension("cogs.yobro")

bot.run(config.TOKEN)