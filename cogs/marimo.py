from discord.ext import commands
import datetime
from datetime import timedelta
import discord
import random


class Marimo(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def mt(self, ctx):
        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4)))
        pnow = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=+1)))
        JST = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=+9)))
        marimo_time = f"{now.month}/{now.day} {now.hour}:{now.minute:02}"
        paul_time = f"{pnow.month}/{pnow.day} {pnow.hour}:{pnow.minute:02}"
        japan_time = f"{JST.month}/{JST.day} {JST.hour}:{JST.minute:02}"

        #コマンド自体のチャットを削除する(やっぱりやめた)
        #message = ctx.message
        #await message.delete()

        #slot
        slot_list = ['🍒', '🔔', '🍉', '🍇', '🍋', '🐈', '🐬', '🦕', '🐢', '🐕']
        slot_left = random.choice(slot_list)
        slot_center = random.choice(slot_list)
        slot_right = random.choice(slot_list)

        #おみくじ！
        #omikuji_list = ['大吉🎯', '中吉🐬', '小吉🍓', '末吉🍦', '吉🍨', '凶👾', '大凶💀']
        #omikuji = random.choice(omikuji_list)

        #embed
        embed = discord.Embed()
        embed.color = discord.Color.dark_green()
        embed.set_footer(text=f"mt slot: {slot_left}{slot_center}{slot_right}")
        embed.description = f"marimo time = **{marimo_time}**\npaul time = **{paul_time}**\n(In Japan = {japan_time})"
        await ctx.send(embed=embed)

        if slot_left == slot_center == slot_right:
            await ctx.send(f"🎉Congratulations!! {ctx.author.mention} hits the Jackpot!!🎉")
        else:
            pass

async def setup(bot: commands.Bot):
    await bot.add_cog(Marimo(bot))
