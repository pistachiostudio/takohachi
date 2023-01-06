from datetime import datetime, timedelta, timezone

import discord
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):

        embed = discord.Embed()
        embed.set_thumbnail(url='https://raw.githubusercontent.com/pistachiostudio/takohachi/master/images/icon_tako_hachi_BG_less.png')
        embed.title = "Takohachi commands help"
        embed.color = discord.Color.blue()
        embed.description = """

**Main Commands**
!!addssl [URL]
!!apedxrank [PLATFORM] [YOUR ID]
!!b
!!card
!!cardall
!!count
!!countall
!!d
!!help
!!mt
!!ping
!!play
!!sp [SEARCH WORDS]
!!spartist [ARTIST WORDS]
!!top
!!vr [VALORANT NAME]#[TAGLINE]
!!vrnews
!!whatToday
[More info](https://github.com/pistachiostudio/takohachi/blob/master/src/cogs/README.md)

**User Create Commands**
[See here](https://docs.google.com/spreadsheets/d/15QCsHsmtZAs1FtiCplLmybU80WyxWw4C7G6ESf2b9f4/edit#gid=1264027664&range=A1)
"""

        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))