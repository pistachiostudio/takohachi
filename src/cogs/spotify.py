import os
from datetime import datetime, timedelta, timezone

import discord
import spotipy
from discord import app_commands
from discord.ext import commands

from settings import GUILD_ID


class Spotify(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="spotify",
        description="Spotifyの曲情報を検索します。",
    )
    @app_commands.describe(select="選択してください。", search="検索ワードを入力してください。")
    @app_commands.choices(
        select=[
            discord.app_commands.Choice(name="Song", value="song"),
            discord.app_commands.Choice(name="Artist", value="artist"),
            discord.app_commands.Choice(name="Album", value="album"),
        ]
    )
    async def sp(self, interaction: discord.Interaction, select: str, search: str):
        # interactionは3秒以内にレスポンスしないといけないとエラーになるのでこの処理を入れる。
        await interaction.response.defer()

        # arguments = ' '.join(args)
        arguments = search

        # 起動
        client_id = os.environ["SPOTIFY_CLIENT_ID"]
        client_secret = os.environ["SPOTIFY_CLIENT_SECRET"]
        client_credentials_manager = spotipy.oauth2.SpotifyClientCredentials(
            client_id, client_secret
        )
        spo = spotipy.Spotify(
            client_credentials_manager=client_credentials_manager, language="ja"
        )

        # Songの検索の場合
        if select == "song":
            # searchから曲名を取る
            searchtrack = spo.search(q=f"{arguments}", type="track", market="JP", limit=1)
            for idx, track in enumerate(searchtrack["tracks"]["items"]):
                songname = track["name"]

            # searchから曲のidを取る
            for track in searchtrack["tracks"]["items"]:
                song_id = track["id"]

            # アーティスト情報
            trackinfo = spo.track(song_id)
            arname = [d.get("name") for d in trackinfo["artists"]]
            arname = ", ".join(arname)

            # ジャケ
            track = trackinfo["album"]["images"][0]
            imageurl = track["url"]

            # Popularity
            for track in trackinfo["artists"]:
                popularities = trackinfo["popularity"]

            # track url
            trackurl = trackinfo["external_urls"]["spotify"]

            # embed
            # NOTE: Spotifyは2024年11月にAudio Features/Analysis APIへの
            # 一般アプリのアクセスを廃止したため、BPM等の分析情報は取得不可。
            embed = discord.Embed()
            JST = timezone(timedelta(hours=+9), "JST")
            embed.timestamp = datetime.now(JST)
            embed.title = "Spotify song search"
            embed.color = discord.Color.red()
            embed.description = (
                f"**Track:** {songname}\n**Artist:** {arname}\n[Listen this track!]({trackurl})"
            )
            embed.set_thumbnail(url=imageurl)
            embed.add_field(name="Popularity", value=f"```{popularities}```")
            await interaction.followup.send(embed=embed)

        # Artistの検索の場合
        elif select == "artist":
            # 検索ワード
            searchartist = spo.search(q=f"{arguments}", type="artist", market="JP", limit=1)

            # searchからアーティスト名を取る
            for idx, track in enumerate(searchartist["artists"]["items"]):
                artistname = track["name"]

            # searchからアーティストidを取る
            for track in searchartist["artists"]["items"]:
                artist_id = track["id"]

            # ジャンルをすべて取る
            artistinfo = spo.artist(artist_id)
            artistgenre = artistinfo["genres"]
            argenre = ", ".join(artistgenre)

            # アー写の一番でかいやつ
            track = artistinfo["images"][0]
            imgurl = track["url"]

            # フォロワー
            follower = "{:,}".format(artistinfo["followers"]["total"])

            # Popularity
            artistpopularity = artistinfo["popularity"]

            # artist url
            artisturl = artistinfo["external_urls"]["spotify"]

            # artist embed
            embed = discord.Embed()
            JST = timezone(timedelta(hours=+9), "JST")
            embed.timestamp = datetime.now(JST)
            embed.title = f"{artistname}'s Profile"
            embed.color = discord.Color.green()
            embed.description = f"**Popularity:** {artistpopularity}\n**Followers:** {follower}\n\
                **Genre:** {argenre}\n[Listen this artist!]({artisturl})"
            embed.set_image(url=imgurl)
            await interaction.followup.send(embed=embed)

        # Albumの検索の場合
        elif select == "album":
            # 検索ワード
            searchalbum = spo.search(q=f"{arguments}", type="album", market="JP", limit=1)

            # 諸々情報取得
            album_title = searchalbum["albums"]["items"][0]["name"]
            album_release_date = searchalbum["albums"]["items"][0]["release_date"]
            album_artist_name = searchalbum["albums"]["items"][0]["artists"][0]["name"]
            album_artist_url = searchalbum["albums"]["items"][0]["artists"][0]["external_urls"][
                "spotify"
            ]
            album_url = searchalbum["albums"]["items"][0]["external_urls"]["spotify"]
            album_image = searchalbum["albums"]["items"][0]["images"][0]["url"]

            # album embed
            embed = discord.Embed()
            JST = timezone(timedelta(hours=+9), "JST")
            embed.timestamp = datetime.now(JST)
            embed.title = f"{album_title}"
            embed.color = discord.Color.greyple()
            embed.description = f"**Artist:** [{album_artist_name}]({album_artist_url})\n\
                **Release Date:** {album_release_date}\n[Listen this album!]({album_url})"
            embed.set_image(url=album_image)
            await interaction.followup.send(embed=embed)

        else:
            await interaction.followup.send("Error")
            return


async def setup(bot: commands.Bot):
    await bot.add_cog(Spotify(bot), guilds=[discord.Object(id=GUILD_ID)])
