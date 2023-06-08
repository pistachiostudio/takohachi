import os
from datetime import datetime, timedelta, timezone

import discord
import spotipy
from discord import app_commands
from discord.ext import commands


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

            # 曲のidをfeatureに渡した
            feature = spo.audio_features(song_id)
            for item in feature:
                loudness = round(item["loudness"], 1)
                key = item["key"]
                bpm = round(item["tempo"], 1)
                time_signature = item["time_signature"]
                danceability = round(item["danceability"] * 100, 1)
                energy = round(item["energy"] * 100, 1)
                acousticness = round(item["acousticness"] * 100, 1)
                liveness = round(item["liveness"] * 100, 1)
                inst = round(item["instrumentalness"] * 100, 1)
                # duration_ms = item["duration_ms"]
                # duration = duration_ms / 60000
                mode = item["mode"]

            # key変換
            keydic = {
                0: "C",
                1: "C#",
                2: "D",
                3: "D#",
                4: "E",
                5: "F",
                6: "F#",
                7: "G",
                8: "G#",
                9: "A",
                10: "A#",
                11: "B",
            }
            keys = keydic[key]

            # mojor, minor変換
            modedic = {0: "Minor", 1: "Major"}
            majmin = modedic[mode]

            # embed
            embed = discord.Embed()
            JST = timezone(timedelta(hours=+9), "JST")
            embed.timestamp = datetime.now(JST)
            embed.title = "Spotify song analyser..."
            embed.color = discord.Color.red()
            embed.description = (
                f"**Track:** {songname}\n**Artist:** {arname}\n[Listen this track!]({trackurl})"
            )
            embed.set_thumbnail(url=imageurl)
            embed.add_field(name="Popularity", value=f"```{popularities}```")
            embed.add_field(name="Key", value=f"```{keys}```")
            embed.add_field(name="Mode", value=f"```{majmin}```")
            embed.add_field(name="BPM", value=f"```{bpm}```")
            embed.add_field(name="TS", value=f"```{time_signature}/4```")
            embed.add_field(name="Loudness", value=f"```{loudness}db```")
            embed.add_field(name="Danceability", value=f"```{danceability}%```")
            embed.add_field(name="Energy", value=f"```{energy}%```")
            embed.add_field(name="Acousticness", value=f"```{acousticness}%```")
            embed.add_field(name="Liveness", value=f"```{liveness}%```")
            embed.add_field(name="Instrumentalness", value=f"```{inst}%```")
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
    await bot.add_cog(Spotify(bot), guilds=[discord.Object(id=731366036649279518)])
