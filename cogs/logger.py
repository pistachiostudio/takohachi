import logging

import discord
from discord import Color
from libs.embed import get_custum_embed
from libs.utils import get_now_timestamp_jst

# https://qiita.com/izmktr/items/77f684f6121c103cc194
# logging handler の独自実装について -> https://nowaai.github.io/posts/logging/

class DiscordBotHandler(logging.Handler):

    def __init__(self, log_channel: discord.TextChannel = None) -> None:
        logging.Handler.__init__(self)
        self.log_channel = log_channel
        self.colors = {
            "DEBUG": Color.blue,
            "INFO": Color.from_rgb(255, 255, 255),
            "WARNING": Color.from_rgb(255, 255, 0),
            "CRITICAL": Color.from_rgb(255, 255, 0),
            "ERROR": Color.red
        }
    
    def set_channel(self, log_channel: discord.TextChannel):
        self.log_channel = log_channel

    async def send_log(self, msg: str):
        await self.log_channel.send(msg)
    
    def emit(self, record):
        try:
            timestamp = get_now_timestamp_jst()
            embed = get_custum_embed()
            embed.color = self.colors[record.levelname]
            level = record.levelname
            logger_name = record.name
            msg = record.getMessage()
            log_body = f"{timestamp} | {level} | {logger_name} | {record.name}:{record.funcName}:{record.lineno} - {msg}"
            embed.add_field(name=record.levelname,
                        value=f"```{log_body}```")
            self.send_log(embed=embed)
        except Exception:
            self.handleError(record)
