import logging
import os
import re
import uuid

import discord
from discord.ext import commands

from libs import google_drive
from libs.utils import now_jst

logger = logging.getLogger(__name__)

NEKO_EMOJI = "<:p01_neko:863117588757872730>"
# これより大きいファイルは保存しない(メモリにまるごと読み込むため)
MAX_FILE_BYTES = 50 * 1024 * 1024
# multipart のヘッダーにそのまま書くため、type/subtype 形式以外の値は使わない
MIME_TYPE_PATTERN = re.compile(r"[\w.+-]+/[\w.+-]+")
DRIVE_FOLDER_URL = (
    "https://drive.google.com/drive/folders/1Vh0efZjmlXjHYenDT5YyipvLGcEXaY8A?usp=sharing"  # noqa: E501
)
ICON_URL = "https://user-images.githubusercontent.com/4445606/125683381-65c62bf9-3380-4167-8c69-224ecc86fc11.png"  # noqa: E501


def upload_filename(filename: str) -> str:
    """Discordのデフォルト名(image0.png など)の場合は、重複しないようUUIDの名前にする。"""
    stem, dot, ext = filename.partition(".")
    if stem == "image0":
        return f"{uuid.uuid4()}{dot}{ext}"
    return filename


def mime_type(content_type: str | None) -> str:
    base = (content_type or "").split(";", 1)[0].strip()
    return base if MIME_TYPE_PATTERN.fullmatch(base) else "application/octet-stream"


class SaveImage(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        # botのリアクションとサーバー外(DM)のリアクションは無視する
        if payload.member is None or payload.member.bot:
            return
        # 該当の絵文字以外は無視
        if str(payload.emoji) != NEKO_EMOJI:
            return
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        # 添付ファイルがない場合と、すでに誰かが同じ絵文字を付けていた(保存済みの)場合は無視する
        neko = next((r for r in message.reactions if str(r.emoji) == NEKO_EMOJI), None)
        if not message.attachments or (neko is not None and neko.count > 1):
            return

        for attachment in message.attachments:
            embed = discord.Embed(timestamp=now_jst())
            embed.set_thumbnail(url=attachment.url)
            embed.set_author(
                name="殿堂・オブ・ピスタチオ・アニマルズ", url=DRIVE_FOLDER_URL, icon_url=ICON_URL
            )
            try:
                if attachment.size > MAX_FILE_BYTES:
                    raise ValueError(f"file too large: {attachment.size} bytes")
                name = upload_filename(attachment.filename)
                await google_drive.upload_file(
                    name,
                    await attachment.read(),
                    mime_type(attachment.content_type),
                    os.environ["DRIVE_FOLDER_ID"],
                )
                embed.color = discord.Color.green()
                embed.description = ":white_check_mark: 保存が完了し、殿堂入りをはたしました。"
                embed.add_field(name="uploaded file name:", value=name)
            except Exception:
                logger.exception("Failed to save %s", attachment.filename)
                embed.color = discord.Color.red()
                embed.description = ":warning: ファイルアップロードに失敗しました"
                embed.add_field(name="file:", value=attachment.filename)
            await channel.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(SaveImage(bot))
