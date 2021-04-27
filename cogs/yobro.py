from discord.ext import commands
import config
import asyncio
import discord

class Reading(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def yo(self, ctx):
        await ctx.send(f"Yo bro, {ctx.author.mention}. How do you do? dude!")


    @commands.command()
    async def apex(self, ctx):
        await ctx.send(f"{ctx.author.mention} You are LEGENDS!!!")
        

def setup(bot):
    bot.add_cog(Reading(bot))