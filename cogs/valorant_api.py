import asyncio

import discord
from discord.ext import commands
import requests


class Valo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def vr(self, ctx):

        current_season = "e5a2"
        channel = ctx.channel
        takohachi_id = '813757574058213376'

        season_txt = (current_season.replace("e", "Episode ").replace("a", " Act "))

        # Usernameを取得
        embed = discord.Embed()
        embed.color = discord.Color.gold()
        embed.title = "<:p01_pepebrim:951023068275421235> ENTER YOUR VALORANT NAME WITHOUT TAGLINE..."
        embed.description = "ex): 植 物、快楽亭ブラック、ミスターポーゴ"
        username_msg = await ctx.send(embed=embed, delete_after=60)

        try:
            def check(m):
                return m.channel == channel and m.author.id != takohachi_id

            username_waiter = await self.bot.wait_for('message', check=check, timeout=60)
            username = username_waiter.content
            await username_waiter.delete()
            await username_msg.delete()

        # asyncio.TimeoutError が発生したらここに飛ぶ
        except asyncio.TimeoutError:
            embed = discord.Embed()
            embed.color = discord.Color.red()
            embed.title = "<:p01_pepebrim:951023068275421235>:warning: Timeout..."
            embed.description = f'`!!valo` command again'
            await ctx.send(embed=embed, delete_after=10)
            message = ctx.message
            await message.delete()
            return

        # taglineを取得
        embed = discord.Embed()
        embed.color = discord.Color.blue()
        embed.title = "<:p01_pepeyoru:951023518068387880> ENTER YOUR TAGLINE WITHOUT #"
        embed.description = "ex) help、三代目、imoya"
        tagline_msg = await ctx.send(embed=embed, delete_after=60)

        try:
            def check(m):
                return m.channel == channel and m.author.id != takohachi_id

            tagline_waiter = await self.bot.wait_for('message', check=check, timeout=60)
            tagline = tagline_waiter.content
            tagline = tagline.replace("#", "")
            await tagline_waiter.delete()
            await tagline_msg.delete()

        # asyncio.TimeoutError が発生したらここに飛ぶ
        except asyncio.TimeoutError:
            embed = discord.Embed()
            embed.color = discord.Color.red()
            embed.title = "<:p01_pepebrim:951023068275421235>:warning: Timeout..."
            embed.description = f'`!!valo` command again'
            await ctx.send(embed=embed, delete_after=10)
            await message.delete()
            return

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
                season_games = json['data']['by_season'][current_season]['number_of_games']
                season_wins = json['data']['by_season'][current_season]['wins']
                season_lose = int(season_games) - int(season_wins)

                account_url = f"https://api.henrikdev.xyz/valorant/v1/account/{username}/{tagline}"
                res = requests.get(account_url)
                account_json = res.json()

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
            embed.title = f"{username} `#{tagline}`"
            embed.color = discord.Color.magenta()
            embed.description = f"{season_txt} competitive results"
            embed.set_thumbnail(url=rank_image_url)
            embed.add_field(name="W/L", value=f"```{season_wins}W/{season_lose}L```")
            embed.add_field(name="Current rank", value=f"```{current_rank} (+{ranking_in_tier} RR)```")
            embed.add_field(name="ELO", value=f"```{elo}```")
            embed.add_field(name="Account Level", value=f"```{account_level}```")
            embed.set_image(url=card_image_url)
            await ctx.send(embed=embed)


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
