import asyncio
import logging
import random

import discord
from discord.ext import commands, tasks

from libs.trivia import format_trivia_section, get_trivia
from libs.utils import get_stock_price, get_weather, get_what_today, now_jst

logger = logging.getLogger(__name__)

CHANNEL_ID = 762575939623452682
# 天気を出す地域。citycode一覧 "https://weather.tsukumijima.net/primary_area.xml"
WEATHER_CITY_CODES = ["130010", "060010"]  # 東京, 山形
GOOD_MORNINGS = ["おざし。", "おざす。", "お。", "おはようございます。"]
# (ticker_symbol, 表示名, 単位, アイコン)
MARKET_DATA = [
    ("USDJPY=X", "USD/JPY", "円", ":moneybag:"),
    ("^N225", "日経225", "円", ":flag_jp:"),
    ("^GSPC", "S&P500", "pt", ":flag_us:"),
    ("^IXIC", "NASDAQ", "pt", ":flag_us:"),
    ("3399.T", "丸千代山岡家", "円", ":ramen:"),
    ("9023.T", "東京地下鉄", "円", ":metro:"),
]


async def market_text() -> str:
    lines = []
    for ticker, name, unit, icon in MARKET_DATA:
        try:
            day_before_ratio, stock_today = await asyncio.to_thread(get_stock_price, ticker)
            lines.append(
                f"- {icon} **{name}:** {round(stock_today, 1):,}{unit} ({day_before_ratio})"
            )
        except Exception:
            logger.exception("Failed to get stock price for ticker: %s", ticker)
            lines.append(f"- {icon} **{name}:** データ取得失敗")
        # APIリクエスト制限回避のために遅延を入れる
        await asyncio.sleep(0.5)
    return "\n".join(lines) + "\n※()内は前日比。"


class WTTasks(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.printer.start()

    def cog_unload(self):
        self.printer.cancel()

    @tasks.loop(seconds=600.0)
    async def printer(self):
        today = now_jst()
        if not (today.hour == 7 and today.minute <= 9):
            return

        try:
            what_today = await asyncio.to_thread(get_what_today, today.month, today.day)
            weathers = [await asyncio.to_thread(get_weather, code) for code in WEATHER_CITY_CODES]
            # Geminiで雑学を生成し、TypeSafeで検証して取得
            trivia_section = format_trivia_section(await get_trivia())

            embed = discord.Embed(
                color=discord.Color(0x00FF00),
                title=f"{random.choice(GOOD_MORNINGS)}{today.month}月{today.day}日 朝の7時です。",
                description=(
                    f"### 💡 今日はなんの日？\n{what_today}\n\n"
                    f"### 📚 今日の雑学\n{trivia_section}\n\n"
                    f"### 💹 相場\n{await market_text()}\n\n"
                    f"### ⛅ 今日の天気\n" + "\n".join(weathers)
                ),
            )
            await self.bot.get_channel(CHANNEL_ID).send(embed=embed)
        except Exception:
            # discord.HTTPExceptionなどtasks.loopの自動リトライ対象外の例外が
            # ここで発生するとループ自体が停止し、二度と朝の投稿が行われなく
            # なるため、ここで捕まえて次回ループを継続させる。
            logger.exception("Failed to post morning summary")

    # デプロイ後Botが完全に起動してからタスクを回す
    @printer.before_loop
    async def before_printer(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(WTTasks(bot))
