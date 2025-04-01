import random
import time
from datetime import datetime, timedelta, timezone

import discord
from discord.ext import commands, tasks
from yfinance.exceptions import YFRateLimitError

from libs.utils import get_stock_price, get_trivia, get_weather, get_what_today


class WTTasks(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.index = 0
        self.bot = bot
        self.printer.start()

    def cog_unload(self):
        self.printer.cancel()

    @tasks.loop(seconds=600.0)
    async def printer(self):
        channel = self.bot.get_channel(int("762575939623452682"))

        # タイムゾーンの生成
        JST = timezone(timedelta(hours=+9), "JST")
        today = datetime.now(JST)

        this_month = today.month
        this_day = today.day
        this_hour = today.hour
        this_minute = today.minute

        if this_hour == 7 and 0 <= this_minute <= 9:
            result = get_what_today(this_month, this_day)

            # 東京地方の天気を取得。citycode一覧 "https://weather.tsukumijima.net/primary_area.xml"
            citycode = "130010"
            tokyo_weather = get_weather(citycode)

            # 山形の天気を取得。
            citycode = "060010"
            yamagata_weather = get_weather(citycode)

            # Geminiで雑学を取得
            trivia = await get_trivia()
            good_morning = random.choice(["おざし。", "おざす。", "お。", "おはようございます。"])

            # 市場データの設定
            # (ticker_symbol, 表示名, 単位, アイコン)
            market_data = [
                ("USDJPY=X", "USD/JPY", "円", ":moneybag:"),
                ("^N225", "日経225", "円", ":flag_jp:"),
                ("^GSPC", "S&P500", "pt", ":flag_us:"),
                ("^IXIC", "NASDAQ", "pt", ":flag_us:"),
                ("3399.T", "丸千代山岡家", "円", ":ramen:"),
                ("9023.T", "東京地下鉄", "円", ":metro:"),
            ]

            stock_results = {}
            # 各銘柄のデータを取得（リクエスト間に遅延を入れる）
            for ticker, name, unit, icon in market_data:
                try:
                    day_before_ratio, stock_today = get_stock_price(ticker)
                    stock_results[ticker] = (day_before_ratio, stock_today, name, unit, icon)
                    # APIリクエスト制限回避のために遅延を入れる
                    time.sleep(0.5)
                except YFRateLimitError:
                    print(f"Rate limit exceeded for ticker: {ticker}")
                    continue
                except Exception as e:
                    print(f"Failed to get stock price for ticker: {ticker}")
                    print("Error message:", e)
                    continue

            # 市場データのテキスト生成
            market_lines = []
            for ticker, (
                day_before_ratio,
                stock_today,
                name,
                unit,
                icon,
            ) in stock_results.items():
                market_lines.append(
                    f"- {icon} **{name}:** {round(stock_today, 1):,}{unit} ({day_before_ratio})"
                )

            market_text = "\n".join(market_lines) + "\n※()内は前日比。"

            embed = discord.Embed()
            embed.color = discord.Color.green()
            embed.title = f"{good_morning}{this_month}月{this_day}日 朝の7時です。"
            embed.description = f"### 💡 今日はなんの日？\n{result}\n### 📚 今日の雑学\n{trivia}(Powered by [gemini-2.5-pro-exp-03-25](https://ai.google.dev/gemini-api/docs/models?hl=ja#gemini-2.5-pro-exp-03-25))\n### 💹 相場\n{market_text}\n### ⛅ 今日の天気\n{tokyo_weather}\n{yamagata_weather}"  # noqa: E501
            await channel.send(embed=embed)

    # デプロイ後Botが完全に起動してからタスクを回す
    @printer.before_loop
    async def before_printer(self):
        print("waiting until bot booting")
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(WTTasks(bot))
