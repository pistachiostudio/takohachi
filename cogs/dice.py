from discord.ext import commands
import random
import requests
import discord


class Dice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def d(self, ctx):

        url = 'https://valorant-api.com/v1/maps'

        res = requests.get(url)
        json = res.json()

        data = json["data"]

        data_len: int = int(len(data))
        len_list = list(range(data_len))

        random_num: int = random.choice(len_list)
        uuid = data[random_num]['uuid']

        if uuid == 'ee613ee9-28b7-4beb-9666-08db13bb2244': #射撃場のMap uuid
            no_range_num_list = len_list.remove(random_num)
            new_random_num: int = random.choice(no_range_num_list)
            uuid = data[new_random_num]['uuid']
            displayName = data[new_random_num]['displayName']
            listViewIcon = data[new_random_num]['listViewIcon']
            displayIcon = data[new_random_num]['displayIcon']

        else:
            displayName = data[random_num]['displayName']
            listViewIcon = data[random_num]['listViewIcon']
            displayIcon = data[random_num]['displayIcon']

        embed = discord.Embed()
        embed.title = displayName
        embed.set_image(url=listViewIcon)
        #embed.set_thumbnail(url=displayIcon)
        embed.color = discord.Color.dark_blue()
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Dice(bot))
