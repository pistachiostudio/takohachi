from discord.ext import commands
import discord
import config

bot = commands.Bot(command_prefix="!!")

@bot.event
async def on_ready():
    print("on_ready")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        # Botからのメッセージには反応しない
        # この判定をしないと無限ループが起きる
        return
    DIS_WORDS = ['バカ', 'ばか', 'あほ', '死ね', 'だめ', 'ゴミ']
    
    # 全NGワードについて存在確認
    for dis_word in DIS_WORDS:
        if dis_word in message.content:
            # NGワードを発見したらテキストチャンネルに通知
            await message.channel.send(f"{dis_word}野郎はテメェだ！")

    if "bot" in message.content:
        await message.channel.send("はーい助六ボットです。")

    await bot.process_commands(message)

@bot.command()
async def yo(ctx):

    def check_message_author(messe):
        return messe.author is ctx.author
    
    await ctx.send(f"Yo bro, {ctx.author.mention}. How do you do? dude!")

    msse=await bot.wait_for('message', check=check_message_author)
    await ctx.send(f"Great! You feel {messe.content}!!")
            
bot.run(config.TOKEN)