from datetime import datetime, timedelta, timezone

import discord


# 共通で利用するカスタム embed を返します
def get_custum_embed() -> discord.Embed:
    embed = discord.Embed()
    JST = timezone(timedelta(hours=+9), "JST")
    embed.timestamp = datetime.now(JST)

    return embed
