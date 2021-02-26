from discord.ext import commands
import config
import asyncio
import discord

class Yobro(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #reload command
    @commands.is_owner()
    @commands.command()
    async def reload(self, ctx, module_name):
        await ctx.send(f"**{module_name}** is reloading")
        try:
            self.bot.reload_extension(module_name)
            await ctx.send(f"Well done!")
        except (commands.errors.ExtensionNotLoaded, commands.errors.ExtensionNotFound,
                commands.errors.NoEntryPointError, commands.errors.ExtensionFailed) as e:
            await ctx.send(f"Reloading failed...\nReason: {e}")
            return


    @commands.command()
    async def yo(self, ctx):
        await ctx.send(f"Yo bro, {ctx.author.mention}. How do you do? dude!")


    @commands.command()
    async def apex(self, ctx):
        await ctx.send(f"{ctx.author.mention} You are LEGENDS!!!")
        

def setup(bot):
    bot.add_cog(Yobro(bot))