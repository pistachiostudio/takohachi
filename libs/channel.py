from typing import Optional

import discord
from discord.ext import commands


def get_channels(ctx: commands.Context, names: list[str], channel_type: Optional[discord.ChannelType] = None) -> Optional[list[discord.abc.GuildChannel]]:
    guild = ctx.guild
    if guild is None:
        return None

    channels: list[discord.abc.GuildChannel] = []
    if channel_type is not None:
        for ch in guild.channels:
            if ch.type == channel_type:
                channels.append(ch)
    else:
        channels = guild.channels

    if len(channels) == 0:
        return None

    res :list[discord.abc.GuildChannel] = []
    for ch in channels:
        if ch.name in names:
            res.append[ch]
    
    if len(res) == 0:
        return None

    return res
