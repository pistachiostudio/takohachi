import re
from datetime import datetime, timedelta, timezone
from random import randint
from urllib import parse

import httpx
import yfinance as yf
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential
from yfinance.exceptions import YFRateLimitError


def get_now_timestamp_jst() -> datetime:
    JST = timezone(timedelta(hours=+9), "JST")
    return datetime.now(JST)


def get_what_today(this_month: int, this_day: int) -> str:
    """Wikipediaの「今日は何の日」に記載されている情報を取得します。
    複数候補がある場合はランダムに1つ返却します。

    Args:
        this_month (int): 指定月
        this_day (int): 指定日

    Returns:
        str: 今日は何の日の取得結果
    """
    # Wikimedia Foundation User-Agent Policy 準拠の User-Agent
    # 参考: https://foundation.wikimedia.org/wiki/Policy:Wikimedia_Foundation_User-Agent_Policy
    # TODO(zztkm): ここの値はアプリの定数値としてどこかに適切な場所に定義することを検討する
    app_name = "takohachi"
    app_version = "1.0.0"
    app_url = "https://github.com/pistachiostudio/takohachi"
    app_contact = "info@pistachiostudio.net"
    user_agent = f"{app_name}/{app_version} (+{app_url}; {app_contact})"

    base_url = "https://ja.wikipedia.org/wiki/Wikipedia:"
    uri = f"今日は何の日_{this_month}月"

    fallback = f"{this_month}月{this_day}日です。"

    try:
        res = httpx.get(
            base_url + parse.quote(uri),
            headers={"User-Agent": user_agent},
        )
        html = res.text
        today_idx = html.index(f'id="{this_month}月{this_day}日"')
        ul_start_idx = html.index("ul", today_idx)
        ul_end_idx = html.index("/ul", ul_start_idx)
        ul = html[ul_start_idx:ul_end_idx].replace("\n", "")
        ul_match_list = re.findall(r"<li[^>]*>.+?<\/li>", ul)
        ul_match_sub_list = [re.sub("<.+?>", "", s) for s in ul_match_list]
    except (ValueError, httpx.HTTPError) as e:
        print(f"Failed to fetch/parse 'what today' page: {e}")
        return fallback

    if not ul_match_sub_list:
        print("項目が見つかりませんでした")
        return fallback

    return ul_match_sub_list[randint(0, len(ul_match_sub_list) - 1)]


def get_weather(citycode: str):
    url = "https://weather.tsukumijima.net/api/forecast"

    # citycode一覧"https://weather.tsukumijima.net/primary_area.xml"
    params = {"city": citycode}

    res = httpx.get(url, params=params)
    json = res.json()

    # date = json["forecasts"][0]["date"]
    city = json["location"]["city"]
    # body_text = json["description"]["bodyText"]
    weather = json["forecasts"][0]["detail"]["weather"]
    weather = weather.replace("　", "")
    # min_temp = json["forecasts"][0]["temperature"]["min"]["celsius"]
    max_temp = json["forecasts"][0]["temperature"]["max"]["celsius"]
    chanceOfRain_morning = json["forecasts"][0]["chanceOfRain"]["T06_12"]
    chanceOfRain_evening = json["forecasts"][0]["chanceOfRain"]["T12_18"]
    chanceOfRain_night = json["forecasts"][0]["chanceOfRain"]["T18_24"]

    result = f"- {city}: {weather}\n  - ️️️️🌡️ 最高気温: {max_temp} ℃\n  - ☔ 朝: {chanceOfRain_morning} | 昼: {chanceOfRain_evening} | 晩: {chanceOfRain_night}"  # noqa: E501

    return result


def get_exchange_rate():
    # demoに制限が出てくれば、無料のAPIキーを取得する。
    url = "https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=USD&to_currency=JPY&apikey=demo"

    result = httpx.get(url)
    json = result.json()

    usd_jpy = float(json["Realtime Currency Exchange Rate"]["5. Exchange Rate"])
    round_usd_jpy = round(usd_jpy, 2)

    return round_usd_jpy


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

    if day_before_ratio > 0:
        day_before_ratio = f"+{day_before_ratio:,}"
    else:
        day_before_ratio = f"{day_before_ratio:,}"

    return day_before_ratio, stock_today
