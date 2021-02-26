from discord.ext import commands
import discord

class Yobro(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

@commands.command()
async def yo(self, ctx):
    await ctx.send(f"Yo bro, {ctx.author.mention}. How do you do? dude!")
    return

@commands.command()
async def apex(self, ctx):
    await ctx.send(f"{ctx.author.mention} You are LEGENDS!!!")
    return

def setup(bot):
    bot.add_cog(Yobro(bot))