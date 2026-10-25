import asyncio
import os

import discord
from discord.ext import commands

from libs import google_sheets

# 絵文字 → カウントする列(A: 名前, B: イエロー, C: レッド, D: サイレン, E: 合計, F: ユーザーID)
YELLOW_COL, RED_COL, SIREN_COL = 2, 3, 4
CARD_COLUMNS = {
    "<:p05_card_yellow:934125477424140308>": YELLOW_COL,
    "<a:p00_card_yellow:934125609544745030>": YELLOW_COL,
    "<:p05_card_red:934125543111131187>": RED_COL,
    "<a:p00_card_red:934125658529988648>": RED_COL,
    "<a:p00_siren:801424753419354133>": SIREN_COL,
    "<a:p00_sirenblue:802091428057579521>": SIREN_COL,
    "<a:p00_sirenpurple:805201572111974401>": SIREN_COL,
    "<:p05_siren:801693375043862580>": SIREN_COL,
}


def count_card(author_name: str, user_id: int, column: int) -> None:
    """author_name の行の column を1増やす(未登録なら行を追加する)。E列の合計で降順に並べ直す。"""
    worksheet = google_sheets.open_first_sheet(os.environ["CARDCOUNT_KEY"])
    cell = worksheet.find(author_name)

    if cell is None:
        counts = [1 if col == column else 0 for col in (YELLOW_COL, RED_COL, SIREN_COL)]
        # RAW(既定)で書くので、ユーザー名が数式として解釈されることはない。
        worksheet.append_row([author_name, *counts])
        row = worksheet.find(author_name).row
        worksheet.update_cell(row, 5, f"=SUM(B{row}:D{row})")
        worksheet.update_cell(row, 6, str(user_id))
    else:
        # 名前の列(cell.col)から数えて、カードの種類ぶん右の列をカウントアップ
        col = cell.col + column - 1
        worksheet.update_cell(cell.row, col, int(worksheet.cell(cell.row, col).value) + 1)

    # E列のTTLを降順でソートする
    worksheet.sort((5, "des"))


class CardCount(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        # botのリアクションとサーバー外(DM)のリアクションは無視する
        if payload.member is None or payload.member.bot:
            return
        column = CARD_COLUMNS.get(str(payload.emoji))
        if column is None:
            return

        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        await asyncio.to_thread(count_card, str(message.author), message.author.id, column)


async def setup(bot: commands.Bot):
    await bot.add_cog(CardCount(bot))
