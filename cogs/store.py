from discord.ext import commands
from datetime import timedelta
from libs.shop import Auth, get_data, get_skins, get_night_market


class Store(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def shop(self, ctx):

        username = 'YOUR RIOT ID HERE'
        password = 'YOUR RIOT PASS HERE'
        region = 'ap' #put your region

        auth = Auth({ "username": username, "password": password })
        user_id, headers, _ = auth.authenticate()

        skins_data, bundles_data, weapons_data, offers_data = get_data(user_id, headers, region)

        #get_bundles(skins_data, bundles_data, weapons_data)
        skin_list = get_skins(skins_data, weapons_data, offers_data)
        nm_skin_list = get_night_market(skins_data, weapons_data)
        answer = f'{ctx.author.mention}\n> {skin_list[0]}\n> {skin_list[1]}\n> {skin_list[2]}\n> {skin_list[3]}'
        await ctx.send(answer)

def setup(bot):
    bot.add_cog(Store(bot))
