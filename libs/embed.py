import discord

from libs.utils import get_now_timestamp_jst


# 共通で利用するカスタム embed を返します
def get_custum_embed() -> discord.Embed:
    embed = discord.Embed()
    embed.timestamp = get_now_timestamp_jst()

    return embed
