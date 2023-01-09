import asyncio

import discord
import requests
from discord import app_commands
from discord.ext import commands


class Valo(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="vr",
        description="Valorantのランクなどを表示します。"
    )

    @app_commands.describe(
        name="Valorantのプレイヤー名を入れてください。ex) 植 物、ウィングマン太郎、The Manなど",
        tagline="#以降のタグを入れてください。#は不要です。"
    )

    async def vr(
        self,
        interaction: discord.Interaction,
        name: str,
        tagline: str
    ):

        current_season = "e5a3"

        season_txt = (current_season.replace("e", "Episode ").replace("a", " Act "))

        # interactionは3秒以内にレスポンスしないといけないとエラーになるのでこの処理で15秒は待たせる。
        await interaction.response.defer()
        asyncio.sleep(15)

        # API request
        try:
            rank_url = f"https://api.henrikdev.xyz/valorant/v2/mmr/ap/{name}/{tagline}"
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

            account_url = f"https://api.henrikdev.xyz/valorant/v1/account/{name}/{tagline}"
            res = requests.get(account_url)
            account_json = res.json()


            real_name = account_json['data']['name']
            real_tagline = account_json['data']['tag']
            account_level = account_json['data']['account_level']
            card_image_url = account_json['data']['card']['wide']

        except KeyError:
            embed = discord.Embed()
            embed.color = discord.Color.red()
            embed.title = "<:p01_pepebrim:951023068275421235>:warning: 何かが間違えているかもしれません。"
            embed.description = f'もう一度試してみてください。:pray: '
            await interaction.response.defer()
            await asyncio.sleep(15)
            await interaction.followup.send(
                embed=embed,
                ephemeral=True,
                delete_after=5
            )
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

        # interaction.response.deferを使ったのでここはfollowup.sendが必要
        await interaction.followup.send(embed=embed)
        return


    # Valorantの最新ニュースを取ってくるコマンド
    @app_commands.command(
        name="vnews",
        description="Valorantの最新ニュースを取得します。"
    )

    async def vnews(
        self,
        interaction: discord.Interaction
    ):
        # interactionは3秒以内にレスポンスしないといけないとエラーになるのでこの処理で15秒は待たせる。
        await interaction.response.defer()
        asyncio.sleep(15)

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

        # interaction.response.deferを使ったのでここはfollowup.sendが必要
        await interaction.followup.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(
        Valo(bot),
        guilds = [discord.Object(id=731366036649279518)]
    )
