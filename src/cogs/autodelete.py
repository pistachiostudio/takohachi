import logging
from datetime import UTC, datetime, timedelta

from discord.ext import commands, tasks

logger = logging.getLogger(__name__)

# チャンネルIDと削除するまでの時間(秒)。例えば1時間で削除する場合は3600。
CHANNEL_TTLS = {
    762575939623452682: 43200,  # 犬
    762576579507126273: 43200,  # 猫
    780611197350576200: 43200,  # 亀
    812312154371784704: 43200,  # 恐竜
    811819005987913790: 600,  # 沈黙の犬
    811810485929639976: 600,  # 沈黙の猫
    811804248299143209: 600,  # 沈黙の亀
    1033285774503841862: 600,  # 沈黙の恐竜
    924924594706583562: 86400,  # 茂林塾
    923469139597721610: 86400,  # moderator
}


class AutoDelete(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.printer.start()

    def cog_unload(self):
        self.printer.cancel()

    @tasks.loop(seconds=600.0)
    async def printer(self):
        logger.info("Message purge task is running.")
        now = datetime.now(UTC)

        for channel_id, ttl in CHANNEL_TTLS.items():
            try:
                channel = self.bot.get_channel(channel_id)
                if channel is None:
                    logger.warning("Channel not found, skipping: %s", channel_id)
                    continue

                # 指定した時間より前の、ピン留めされていないメッセージを削除する。
                # 溜まっていても1回に見るのは100件までにして、残りは次回以降に回す。
                deleted = await channel.purge(
                    limit=100,
                    before=now - timedelta(seconds=ttl),
                    check=lambda message: not message.pinned,
                )
                logger.info("Purged %d messages in %s", len(deleted), channel.name)
            except Exception:
                # discord.HTTPException(Discord側の一時的な503等)はtasks.loopの
                # 自動リトライ対象外で、ここで捕まえないとループ自体が停止し、
                # 二度と自動削除が動かなくなる。1チャンネルの失敗で全体を
                # 止めないためにもチャンネル単位でcatchする。
                logger.exception("Failed to purge messages in channel %s", channel_id)

        logger.info("Message purge task is finished.")

    # デプロイ後Botが完全に起動してからタスクを回す
    @printer.before_loop
    async def before_printer(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(AutoDelete(bot))
