from discord.ext import commands


class Bath(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def b(self, ctx):
        before_nick = ctx.author.display_name
        message = ctx.message
        rtn = before_nick.startswith('🛀')

        if rtn is False:
            after_nick = f'🛀{before_nick}'
            await message.author.edit(nick=after_nick)
            await message.delete()
            pass

        if rtn is True:
            after_nick = before_nick.lstrip('🛀')
            await message.author.edit(nick=after_nick)
            await message.delete()
            pass

def setup(bot):
    bot.add_cog(Bath(bot))
