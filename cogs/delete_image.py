import os

from discord.ext import commands
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive


class DeleteImage(commands.Cog):
    """画像を削除するやつですが、動作しないので調整中です
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_clear_emoji(self, payload):
        print("リアクションクリーパー")
        # botのリアクションは無視する
        if payload.member.bot:
            return
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        # 添付ファイルが存在しない場合は 無視する
        if len(message.attachments) == 0:
            return

        print(message.reactions)
        if str(payload.emoji) == "<:p01_neko:863117588757872730>":
            print("猫のリアクションが削除されました")

            attachment = message.attachments[0]
            try:
                self._delete_img(attachment.filename)
                await channel.send(f"GoogleDriveに保存されている`{attachment.filename}`を削除しました")
            except:
                await channel.send(f"GoogleDriveに保存されている`{attachment.filename}`の削除に失敗しました")

    def _delete_img(self, filename):
        gauth = GoogleAuth()
        gauth.CommandLineAuth()
        drive = GoogleDrive(gauth)

        folder_id = os.environ["DRIVE_FOLDER_ID"]

        file_list = drive.ListFile(
            {'q': f"'{folder_id}' in parents and title contains '{filename}'"}).GetList()

        for file in file_list:
            f = drive.CreateFile({"id": file["id"]})
            f.Trash()


async def setup(bot: commands.Bot):
    await bot.add_cog(DeleteImage(bot))
