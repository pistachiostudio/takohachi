import json
import os
import re
from datetime import datetime, timedelta, timezone
from random import randint
from urllib import parse

import httpx
import yfinance as yf

from libs.http_client import HTTPClient, APIError

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


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

    res = httpx.get(
        base_url + parse.quote(uri),
        headers={"User-Agent": user_agent},
    )
    html = res.text
    today_idx = html.index(f'id="{this_month}月{this_day}日"')
    ul_start_idx = html.index("ul", today_idx)
    ul_end_idx = html.index("/ul", ul_start_idx)
    ul = html[ul_start_idx:ul_end_idx].replace("\n", "")
    ul_match_list = re.findall(r"<li>.+?<\/li>", ul)
    ul_match_sub_list = [re.sub("<.+?>", "", s) for s in ul_match_list]
    result = ul_match_sub_list[randint(0, len(ul_match_sub_list) - 1)]
    return result


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


async def get_trivia() -> str:
    """Gemini APIを使用して雑学を取得する。"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": "あなたはあらゆる分野からランダムに興味深い雑学を紹介するエキスパートです。 \
                        以下の分野から毎回ランダムに異なるテーマを選び、約400文字の日本語で雑学を1つ紹介してください。 \
                        対象分野：動植物、生物学、宇宙、地理、歴史、哲学、科学、物理学、化学、数学、言語、文学、芸術、音楽、 \
                        映画、カルチャー、食文化、スポーツ、テクノロジー、心理学、社会学、経済学、建築、医学、人体、民俗学、都市伝説など \
                        紹介する雑学は毎回前回と異なる分野から選んでください。雑学の内容はマニアックであっても構いません。 \
                        冒頭に挨拶や前置きは一切不要です。冒頭に分野を記載することも不要で、本文のみ記載してください。"
                    },
                ]
            }
        ]
    }

    try:
        client = HTTPClient()
        res = await client.post(url, headers=headers, json=payload, timeout=120)
        answer = res["candidates"][0]["content"]["parts"][0]["text"]
        return answer
    except (APIError, Exception):
        return "⚠GeminiのAPIリクエストでエラーが発生したので今日の雑学はなしです。"


def get_stock_price(ticker_symbol: str):
    index = yf.Ticker(ticker_symbol)

    data = index.history(period="2d")
    data_json_with_date = data.to_json(orient="split", date_format="iso")
    data_json = json.loads(data_json_with_date)

    stock_yesterday = data_json["data"][0][3]
    stock_today = data_json["data"][1][3]
    day_before_ratio = round(stock_today - stock_yesterday, 1)

    if day_before_ratio > 0:
        day_before_ratio = f"+{day_before_ratio:,}"
    else:
        day_before_ratio = f"{day_before_ratio:,}"

    return day_before_ratio, stock_today
