import logging
import os
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
            # bot.close()はcog_unload()経由でこのタスク自身をcancelしてしまい、
            # 後続処理が実行されなくなるため使わない。
            # os._exit()はPythonの終了処理(例外伝播やatexit)を一切介さず
            # 即座にプロセスを終了するため、Railwayのrestart policyに
            # 非ゼロ終了コードを確実に渡せる。
            os._exit(1)

    @checker.before_loop
    async def before_checker(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(DailyRestart(bot))
