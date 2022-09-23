import discord
from discord.ext import commands
import requests


class Valo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def vr(self, ctx, *, user):

        print(user)

        current_season = "e5a2"

        season_txt = (current_season.replace("e", "Episode ").replace("a", " Act "))

        # user name & tagline の入力を検証
        if '#' not in user:
            embed = discord.Embed()
            embed.color = discord.Color.red()
            embed.title = "<:p01_pepebrim:951023068275421235>:warning: Enter NAME and tagline separated by #!"
            embed.description = 'ex): 植 物#help、快楽亭ブラック#三代目、ミスターポーゴ#imoya'
            await ctx.send(embed=embed, delete_after=10)
            message = ctx.message
            await message.delete()
            return

        contents = user.split('#')
        if len(contents) != 2:
            embed = discord.Embed()
            embed.color = discord.Color.red()
            embed.title = "<:p01_pepebrim:951023068275421235>:warning: Invalid input value"
            embed.description = 'ex): 植 物#help、快楽亭ブラック#三代目、ミスターポーゴ#imoya'
            await ctx.send(embed=embed, delete_after=10)
            message = ctx.message
            await message.delete()
            return

        username = contents[0]
        tagline = contents[1]

        # API request
        async with ctx.typing():
            try:
                rank_url = f"https://api.henrikdev.xyz/valorant/v2/mmr/ap/{username}/{tagline}"
                res = requests.get(rank_url)
                json = res.json()

                current_rank = json['data']['current_data']['currenttierpatched']
                rank_image_url = json['data']['current_data']['images']['large']
                ranking_in_tier = json['data']['current_data']['ranking_in_tier']
                elo = json['data']['current_data']['elo']

                current_season_data = json['data']['by_season'][current_season]
                season_games = current_season_data.get('number_of_games', 0)
                season_wins = current_season_data.get('wins', 0)
                season_lose = season_games - season_wins

                account_url = f"https://api.henrikdev.xyz/valorant/v1/account/{username}/{tagline}"
                res = requests.get(account_url)
                account_json = res.json()


                real_name = account_json['data']['name']
                real_tagline = account_json['data']['tag']
                account_level = account_json['data']['account_level']
                card_image_url = account_json['data']['card']['wide']

            except KeyError:
                embed = discord.Embed()
                embed.color = discord.Color.red()
                embed.title = "<:p01_pepebrim:951023068275421235>:warning: Either `username` or `tagline` is wrong..."
                embed.description = f'Check your account & `!!valo` command again:pray: '
                await ctx.send(embed=embed, delete_after=10)
                return

        # Embed
        embed = discord.Embed()
        embed.title = f"{real_name} `#{real_tagline}`"
        embed.color = discord.Color.magenta()
        embed.description = f"{season_txt} competitive results"
        embed.set_thumbnail(url=rank_image_url)
        embed.add_field(name="W/L", value=f"```{season_wins}W/{season_lose}L```")
        embed.add_field(name="Current rank", value=f"```{current_rank} (+{ranking_in_tier} RR)```")
        embed.add_field(name="ELO", value=f"```{elo}```")
        embed.add_field(name="Account Level", value=f"```{account_level}```")
        embed.set_image(url=card_image_url)
        await ctx.send(embed=embed)
        return


    # Valorantの最新ニュースを取ってくるコマンド
    @commands.command()
    async def vnews(self, ctx):

        async with ctx.typing():

            news_url = "https://api.henrikdev.xyz/valorant/v1/website/ja-jp"
            res = requests.get(news_url)
            json = res.json()

            news_01_title = json['data'][0]['title']
            news_01_url = json['data'][0]['url']
            news_01_external = json['data'][0]['external_link']
            news_01_image = json['data'][0]['banner_url']

            news_02_title = json['data'][1]['title']
            news_02_url = json['data'][1]['url']
            news_02_external = json['data'][1]['external_link']

            news_03_title = json['data'][2]['title']
            news_03_url = json['data'][2]['url']
            news_03_external = json['data'][2]['external_link']

            news_04_title = json['data'][3]['title']
            news_04_url = json['data'][3]['url']
            news_04_external = json['data'][3]['external_link']

            if news_01_external != None:
                news_01_url = news_01_external
            if news_02_external != None:
                news_02_url = news_02_external
            if news_03_external != None:
                news_03_url = news_03_external
            if news_01_external != None:
                news_04_url = news_04_external

        # Embed
        embed = discord.Embed()
        embed.title = "Valorant Latest News"
        embed.color = discord.Color.purple()
        embed.description = f"- [{news_01_title}]({news_01_url})\n\n- [{news_02_title}]({news_02_url})\n\n- [{news_03_title}]({news_03_url})\n\n- [{news_04_title}]({news_04_url})"
        embed.set_image(url=news_01_image)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Valo(bot))
