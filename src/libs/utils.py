import logging
import random
import re
from datetime import datetime, timedelta, timezone
from urllib import parse

import httpx
import yfinance as yf
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential
from yfinance.exceptions import YFRateLimitError

logger = logging.getLogger(__name__)

JST = timezone(timedelta(hours=+9), "JST")

# Wikimedia Foundation User-Agent Policy 準拠の User-Agent
# 参考: https://foundation.wikimedia.org/wiki/Policy:Wikimedia_Foundation_User-Agent_Policy
USER_AGENT = (
    "takohachi/1.0.0 (+https://github.com/pistachiostudio/takohachi; info@pistachiostudio.net)"
)


def now_jst() -> datetime:
    return datetime.now(JST)


def get_what_today(this_month: int, this_day: int) -> str:
    """Wikipediaの「今日は何の日」に記載されている情報を取得します。
    複数候補がある場合はランダムに1つ返却します。取得できなければ日付だけを返します。
    """
    url = "https://ja.wikipedia.org/wiki/Wikipedia:" + parse.quote(f"今日は何の日_{this_month}月")
    fallback = f"{this_month}月{this_day}日です。"

    try:
        html = httpx.get(url, headers={"User-Agent": USER_AGENT}, timeout=15).text
        today_idx = html.index(f'id="{this_month}月{this_day}日"')
        ul_start_idx = html.index("ul", today_idx)
        ul_end_idx = html.index("/ul", ul_start_idx)
        ul = html[ul_start_idx:ul_end_idx].replace("\n", "")
        items = [re.sub("<.+?>", "", s) for s in re.findall(r"<li[^>]*>.+?<\/li>", ul)]
    except (ValueError, httpx.HTTPError) as e:
        logger.warning("Failed to fetch/parse 'what today' page: %s", e)
        return fallback

    if not items:
        logger.warning("'what today' items not found")
        return fallback
    return random.choice(items)


def get_weather(citycode: str) -> str:
    # citycode一覧 "https://weather.tsukumijima.net/primary_area.xml"
    res = httpx.get(
        "https://weather.tsukumijima.net/api/forecast", params={"city": citycode}, timeout=15
    )
    data = res.json()
    today = data["forecasts"][0]
    city = data["location"]["city"]
    weather = today["detail"]["weather"].replace("　", "")
    max_temp = today["temperature"]["max"]["celsius"]
    rain = today["chanceOfRain"]

    return (
        f"- {city}: {weather}\n  - ️️️️🌡️ 最高気温: {max_temp} ℃\n"
        f"  - ☔ 朝: {rain['T06_12']} | 昼: {rain['T12_18']} | 晩: {rain['T18_24']}"
    )


@retry(
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(YFRateLimitError),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    reraise=True,
)
def get_stock_price(ticker_symbol: str):
    index = yf.Ticker(ticker_symbol)

    # "2d" だと当日分の Close が未確定 (NaN) だったり、行自体が1件しか
    # 返らないことがある（特に日本時間早朝の指数系ティッカーで発生しやすい）。
    # 直近5日分から NaN を除いた末尾2件を使うことで、取得失敗を避ける。
    data = index.history(period="5d")
    closes = data["Close"].dropna()

    if len(closes) < 2:
        raise ValueError(
            f"Not enough valid close prices for {ticker_symbol}: got {len(closes)} row(s)"
        )

    stock_yesterday = closes.iloc[-2]
    stock_today = closes.iloc[-1]
    day_before_ratio = round(stock_today - stock_yesterday, 1)
    sign = "+" if day_before_ratio > 0 else ""
    return f"{sign}{day_before_ratio:,}", stock_today
