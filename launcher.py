from discord.ext import commands
import config
import asyncio

bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
    print ("on_ready")

@bot.event
async def on_message(message):
    if message.author == bot.user:
         return

    if "Bot" in message.content:
        await message.channel.send("はーい、Botです")

    await bot.process_commands(message)

@bot.command()
async def hello(ctx):
    
    def check_message_author(msg):
        return msg.author is ctx.author
    
    await ctx.send(f" こんにちは、{ctx.author.name} さん。")
    await ctx.send(f"気分はどうですか？")

    try:
        msg = await bot.wait_for('message', check=check_message_author, timeout=10)
    except asyncio.TimeoutError:
        await ctx.send("タイムアウトしました。")
        return

    await ctx.send(f"「{msg.content}」という気分なんだ。")


bot.run(config.TOKEN)