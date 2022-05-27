from discord.ext import commands
import discord
import random


class Dice(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def d(self, ctx):

        #map pool
        map_dice_list = ['Ascent', 'Bind', 'Haven', 'Split', 'Icebox', 'Breeze', 'Fracture']
        map_dice = random.choice(map_dice_list)

        await ctx.send(f"{map_dice}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Dice(bot))
