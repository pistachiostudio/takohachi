from discord.ext import commands
import discord
import random


class Dice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def d(self, ctx):

        #map pool
        map_dice_list = ['Ascent', 'Bind', 'Haven', 'Split', 'Icebox', 'Breeze', 'Fracture']
        map_dice = random.choice(map_dice_list)

        await ctx.send(f"{map_dice}")


def setup(bot):
    bot.add_cog(Dice(bot))
