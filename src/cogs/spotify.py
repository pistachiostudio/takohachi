import asyncio
import functools
import os

import discord
import spotipy
from discord import app_commands
from discord.ext import commands

from libs.utils import now_jst
from settings import GUILD_ID

SEARCH_TYPES = {"song": "track", "artist": "artist", "album": "album"}


@functools.cache
def _client() -> spotipy.Spotify:
    credentials = spotipy.oauth2.SpotifyClientCredentials(
        os.environ["SPOTIFY_CLIENT_ID"], os.environ["SPOTIFY_CLIENT_SECRET"]
    )
    return spotipy.Spotify(client_credentials_manager=credentials, language="ja")


def _song_embed(track: dict) -> discord.Embed:
    # 検索結果より詳しい情報(Popularityなど)を取るため、改めて曲情報を取得する
    track = _client().track(track["id"])
    artists = ", ".join(a["name"] for a in track["artists"])
    # NOTE: Spotifyは2024年11月にAudio Features/Analysis APIへの
    # 一般アプリのアクセスを廃止したため、BPM等の分析情報は取得不可。
    embed = discord.Embed(
        title="Spotify song search",
        color=discord.Color.red(),
        timestamp=now_jst(),
        description=(
            f"**Track:** {track['name']}\n**Artist:** {artists}\n"
            f"[Listen this track!]({track['external_urls']['spotify']})"
        ),
    )
    embed.set_thumbnail(url=track["album"]["images"][0]["url"])
    embed.add_field(name="Popularity", value=f"```{track['popularity']}```")
    return embed


def _artist_embed(artist: dict) -> discord.Embed:
    artist = _client().artist(artist["id"])
    embed = discord.Embed(
        title=f"{artist['name']}'s Profile",
        color=discord.Color.green(),
        timestamp=now_jst(),
        description=(
            f"**Popularity:** {artist['popularity']}\n"
            f"**Followers:** {artist['followers']['total']:,}\n"
            f"**Genre:** {', '.join(artist['genres'])}\n"
            f"[Listen this artist!]({artist['external_urls']['spotify']})"
        ),
    )
    if artist["images"]:
        embed.set_image(url=artist["images"][0]["url"])
    return embed


def _album_embed(album: dict) -> discord.Embed:
    artist = album["artists"][0]
    embed = discord.Embed(
        title=album["name"],
        color=discord.Color.greyple(),
        timestamp=now_jst(),
        description=(
            f"**Artist:** [{artist['name']}]({artist['external_urls']['spotify']})\n"
            f"**Release Date:** {album['release_date']}\n"
            f"[Listen this album!]({album['external_urls']['spotify']})"
        ),
    )
    if album["images"]:
        embed.set_image(url=album["images"][0]["url"])
    return embed


EMBED_BUILDERS = {"song": _song_embed, "artist": _artist_embed, "album": _album_embed}


def search_embed(select: str, keyword: str) -> discord.Embed | None:
    """検索して最初の1件をEmbedにする。見つからなければNone。"""
    search_type = SEARCH_TYPES[select]
    result = _client().search(q=keyword, type=search_type, market="JP", limit=1)
    items = result[f"{search_type}s"]["items"]
    return EMBED_BUILDERS[select](items[0]) if items else None


class Spotify(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="spotify", description="Spotifyの曲情報を検索します。")
    @app_commands.describe(select="選択してください。", search="検索ワードを入力してください。")
    @app_commands.choices(
        select=[
            app_commands.Choice(name="Song", value="song"),
            app_commands.Choice(name="Artist", value="artist"),
            app_commands.Choice(name="Album", value="album"),
        ]
    )
    async def sp(self, interaction: discord.Interaction, select: str, search: str):
        # interactionは3秒以内にレスポンスしないといけないとエラーになるのでこの処理を入れる。
        await interaction.response.defer()

        embed = await asyncio.to_thread(search_embed, select, search)
        if embed is None:
            await interaction.followup.send(":warning: 見つかりませんでした。")
            return
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Spotify(bot), guilds=[discord.Object(id=GUILD_ID)])
