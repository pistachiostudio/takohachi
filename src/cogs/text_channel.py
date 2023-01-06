import logging

import discord
from discord.ext import commands

from views.button import LinkButton

logger = logging.getLogger(__name__)


class TextChannel(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def top(self, ctx: commands.Context):
        logger.info(ctx.message)
        ch = ctx.channel
        url = ""
        try:
            async for message in ch.history(limit=1, oldest_first=True):
                url = message.jump_url
        except discord.Forbidden as e:
            msg = "メッセージ履歴を読み取る権限がありません!"
            logger.error(msg, exc_info=True)
            await ctx.send(msg)
            raise e
        except discord.HTTPException as e:
            msg = "メッセージ履歴の取得に失敗しました!"
            logger.error(msg, exc_info=True)
            await ctx.send(msg)
            raise e

        await ctx.send("", view=LinkButton("Go to top on this channel", url))


async def setup(bot: commands.Bot):
    await bot.add_cog(TextChannel(bot))

