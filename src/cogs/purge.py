import logging
import time

from discord.ext import commands, tasks


class AutoDelete(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.index = 0
        self.bot = bot
        self.printer.start()

    def cog_unload(self):
        self.printer.cancel()

    @tasks.loop(seconds=600.0)
    async def printer(self):

        logging.info(f"Message purge task is running.")

        # チャンネルIDと削除する時間(秒)を指定。例えば1時間ごとに削除する場合は3600。
        channel_list = {
            762575939623452682: 43200,  # 犬
            762576579507126273: 43200,  # 猫
            780611197350576200: 43200,  # 亀
            812312154371784704: 43200,  # 恐竜
            811819005987913790: 600,  # 沈黙の犬
            811810485929639976: 600,  # 沈黙の猫
            811804248299143209: 600,  # 沈黙の亀
            1033285774503841862: 600,  # 沈黙の恐竜
            924924594706583562: 86400,  # 茂林塾
            1068452228089790464: 1,  # テスト1
            1068453475899424779: 1,  # テスト2
        }

        # UNIX時間の現在時刻を取得
        now = int(time.time())

        # 辞書のキーをループで回していく。キーはチャンネルID
        for channel_id in channel_list.keys():
            # チャンネルを取得
            channel = self.bot.get_channel(channel_id)

            # チャンネルのメッセージを古い順に取得
            purge_count = 0
            pinned_count = 0
            async for message in channel.history(oldest_first=True):
                message_time = int(message.created_at.timestamp())
                if now - message_time > channel_list[channel_id]:
                    purge_count += 1
                    if message.pinned:
                        pinned_count += 1

            #checkを定義
            def is_not_pinned(message):
                return not message.pinned and now - message_time > channel_list[channel_id]

            deleted = await channel.purge(limit=purge_count, check=is_not_pinned)
            logging.info(f'Purged {len(deleted)} messages in {channel.name} (pinned: {pinned_count})')

        logging.info(f"Message purge task is finished.")

    # デプロイ後Botが完全に起動してからタスクを回す
    @printer.before_loop
    async def before_printer(self):
        print("waiting until bot booting")
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(AutoDelete(bot))
