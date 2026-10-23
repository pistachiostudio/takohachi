import os
import uuid
from datetime import datetime, timedelta, timezone

import discord
from discord.ext import commands

from libs import google_drive


class SavaImage(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # botのリアクションは無視する
        if payload.member.bot:
            return
        # 該当の絵文字以外は無視
        if str(payload.emoji) != "<:p01_neko:863117588757872730>":
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

        for attachment in message.attachments:
            embed = discord.Embed()
            # タイムゾーンの生成
            JST = timezone(timedelta(hours=+9), "JST")
            embed.timestamp = datetime.now(JST)
            filename = attachment.filename
            upload_filename = filename
            try:
                content = await attachment.read()

                # filename が デフォルトファイル名の場合はファイル名を変更する
                if filename.split(".")[0] == "image0":
                    uuid_name = self._generate_uuid_filename()
                    upload_filename = uuid_name + "." + filename.split(".")[1]

                # Google Drive へのアップロード処理
                await google_drive.upload_file(
                    upload_filename,
                    content,
                    attachment.content_type or "application/octet-stream",
                    os.environ["DRIVE_FOLDER_ID"],
                )

                embed.color = discord.Color.green()
                embed.set_thumbnail(url=attachment.url)
                embed.set_author(
                    name="殿堂・オブ・ピスタチオ・アニマルズ",
                    url="https://drive.google.com/drive/folders/1Vh0efZjmlXjHYenDT5YyipvLGcEXaY8A?usp=sharing",
                    icon_url="https://user-images.githubusercontent.com/4445606/125683381-65c62bf9-3380-4167-8c69-224ecc86fc11.png",
                )
                embed.description = ":white_check_mark: 保存が完了し、殿堂入りをはたしました。"
                embed.add_field(name="uploaded file name:", value=upload_filename)
                await channel.send(embed=embed)
            except Exception:
                import traceback

                traceback.print_exc()

                embed.color = discord.Color.red()
                embed.set_thumbnail(url=attachment.url)
                embed.set_author(
                    name="殿堂・オブ・ピスタチオ・アニマルズ",
                    url="https://drive.google.com/drive/folders/1Vh0efZjmlXjHYenDT5YyipvLGcEXaY8A?usp=sharing",
                    icon_url="https://user-images.githubusercontent.com/4445606/125683381-65c62bf9-3380-4167-8c69-224ecc86fc11.png",
                )
                embed.description = ":warning: ファイルアップロードに失敗しました"
                embed.add_field(name="file:", value=filename)
                await channel.send(embed=embed)

    def _generate_uuid_filename(self):
        filename = str(uuid.uuid4())
        return filename

    def _get_neko_emoji_count(self, reactions) -> int:
        count = 0
        for reaction in reactions:
            if str(reaction.emoji) == "<:p01_neko:863117588757872730>":
                count = reaction.count
        return count


async def setup(bot: commands.Bot):
    await bot.add_cog(SavaImage(bot))
