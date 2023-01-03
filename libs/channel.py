from typing import Optional

import discord
from discord.ext import commands

def get_channels(ctx: commands.Context, names: list[str], channel_type: Optional[discord.ChannelType] = None):
    print()
