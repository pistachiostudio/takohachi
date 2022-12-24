import time

from discord.ext import commands, tasks


class AutoDelete(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.index = 0
        self.bot = bot
        self.printer.start()

    def cog_unload(self):
        self.printer.cancel()

    @tasks.loop(seconds=300.0)
    async def printer(self):

        # チャンネルIDと削除する時間(秒)を指定。例えば1時間ごとに削除する場合は3600。
        channel_list = {
            762575939623452682: 43200, # 犬
            762576579507126273: 43200, # 猫
            780611197350576200: 43200, # 亀
            812312154371784704: 43200, # 恐竜
            811819005987913790: 600, # 沈黙の犬
            811810485929639976: 600, # 沈黙の猫
            811804248299143209: 600, # 沈黙の亀
            1033285774503841862: 600, # 沈黙の恐竜
            924924594706583562: 86400 # 茂林塾
        }
        # UNIX時間の現在時刻を取得
        now = int(time.time())
        print("----------")
        print("\033[32m"+f"🔨task is running."+"\033[0m")

        # 辞書のキーをループで回していく。キーはチャンネルID
        for channel_id in channel_list.keys():
            # チャンネルを取得
            channel = self.bot.get_channel(int(channel_id))

            # チャンネルのメッセージを古い順に取得
            async for message in channel.history(oldest_first=True):
                # メッセージの投稿時間をUNIX時間に変換
                message_time = int(message.created_at.timestamp())
                # メッセージがピン留めされているかどうかを確認
                isPinned = message.pinned
                # 現在時間からメッセージの投稿時間を引いて、指定した時間よりも古いかどうかを確認
                if now - message_time > channel_list[channel_id]:
                    # ピン留めされているメッセージは削除しない！
                    if isPinned == False:
                        await message.delete()
                        print(f"  🗑deleted message in {channel.name}")

        print("\033[31m"+f"💦task is finished.({int(time.time())-now}sec)"+"\033[0m")

    # デプロイ後Botが完全に起動してからタスクを回す
    @printer.before_loop
    async def before_printer(self):
        print("waiting until bot booting")
        await self.bot.wait_until_ready()

async def setup(bot: commands.Bot):
    await bot.add_cog(AutoDelete(bot))
