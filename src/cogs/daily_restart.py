import logging
import sys
from datetime import datetime, timedelta, timezone

from discord.ext import commands, tasks

RESTART_HOUR = 4


class DailyRestart(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.checker.start()

    def cog_unload(self):
        self.checker.cancel()

    @tasks.loop(seconds=60.0)
    async def checker(self):
        JST = timezone(timedelta(hours=+9), "JST")
        now = datetime.now(JST)

        if now.hour == RESTART_HOUR and now.minute == 0:
            logging.info(
                f"Scheduled daily restart triggered at {now.isoformat()}. Exiting process."
            )
            await self.bot.close()
            # Railwayのrestart policy(ON_FAILURE)によって自動的に再起動されるよう、
            # 意図的に非ゼロの終了コードでプロセスを終了する。
            sys.exit(1)

    @checker.before_loop
    async def before_checker(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(DailyRestart(bot))
