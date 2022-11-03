import os
import uuid
from datetime import datetime, timedelta, timezone

import discord
from discord.ext import commands
from oauth2client.service_account import ServiceAccountCredentials
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive


class SavaImage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # botのリアクションは無視する
        if payload.member.bot:
            return
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        # 添付ファイルが存在しない場合は 無視する
        if len(message.attachments) == 0:
            return

        neko_count = self._get_neko_emoji_count(message.reactions)
        # <:p01_neko:863117588757872730> の count が 1より大きい場合は無視する
        if neko_count > 1:
            return

        if str(payload.emoji) == "<:p01_neko:863117588757872730>":
            attachment = message.attachments[0]
            embed = discord.Embed()
            # タイムゾーンの生成
            JST = timezone(timedelta(hours=+9), "JST")
            embed.timestamp = datetime.now(JST)
            try:
                filename = attachment.filename
                upload_filename = filename
                await attachment.save(fp=filename)

                # filename が デフォルトファイル名の場合はファイル名を変更する
                if filename.split(".")[0] == "image0":
                    uuid_name = self._generate_uuid_filename()
                    upload_filename = uuid_name + \
                        "." + filename.split(".")[1]

                # Google Drive へのアップロード処理
                self._upload_img(filename, upload_filename)

                embed.color = discord.Color.green()
                embed.set_thumbnail(url=attachment.url)
                embed.set_author(name="殿堂・オブ・ピスタチオ・アニマルズ",
                                url="https://drive.google.com/drive/folders/1Vh0efZjmlXjHYenDT5YyipvLGcEXaY8A?usp=sharing",
                                icon_url="https://user-images.githubusercontent.com/4445606/125683381-65c62bf9-3380-4167-8c69-224ecc86fc11.png")
                embed.description = ":white_check_mark: 保存が完了し、殿堂入りをはたしました。"
                embed.add_field(name="uploaded file name:",
                                value=upload_filename)
                await channel.send(embed=embed)
            except:
                import traceback
                traceback.print_exc()

                embed.color = discord.Color.red()
                embed.set_thumbnail(url=attachment.url)
                embed.set_author(name="殿堂・オブ・ピスタチオ・アニマルズ",
                                url="https://drive.google.com/drive/folders/1Vh0efZjmlXjHYenDT5YyipvLGcEXaY8A?usp=sharing",
                                icon_url="https://user-images.githubusercontent.com/4445606/125683381-65c62bf9-3380-4167-8c69-224ecc86fc11.png")
                embed.description = ":warning: ファイルアップロードに失敗しました"
                embed.add_field(name="file:", value=filename)
                await channel.send(embed=embed)
            finally:
                os.remove(filename)

    def _upload_img(self, filename, upload_filename):
        scope = ['https://www.googleapis.com/auth/drive']
        json_keyfile = 'client_secrets.json'
        credentials = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
        gauth = GoogleAuth()
        gauth.credentials = credentials
        drive = GoogleDrive(gauth)

        folder_id = os.environ["DRIVE_FOLDER_ID"]

        f = drive.CreateFile(
            {'title': upload_filename, 'parents': [{'kind': 'drive#fileLink', 'id': folder_id}]})
        f.SetContentFile(filename)
        f.Upload()

    def _generate_uuid_filename(self):
        filename = str(uuid.uuid4())
        return filename

    def _get_neko_emoji_count(self, reactions) -> int:
        for reaction in reactions:
            if str(reaction.emoji) == "<:p01_neko:863117588757872730>":
                count = reaction.count
        return count


def setup(bot):
    bot.add_cog(SavaImage(bot))
