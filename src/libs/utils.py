import os
import re
from datetime import datetime, timedelta, timezone
from random import randint
from urllib import parse

import httpx
import requests
import tenacity


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
    base_url = "https://ja.wikipedia.org/wiki/Wikipedia:"
    uri = f"今日は何の日_{this_month}月"

    res = requests.get(base_url + parse.quote(uri))
    html = res.text
    today_idx = html.index(f'id="{this_month}月{this_day}日"')
    ul_start_idx = html.index("ul", today_idx)
    ul_end_idx = html.index("/ul", ul_start_idx)
    ul = html[ul_start_idx:ul_end_idx].replace("\n", "")
    ul_match_list = re.findall(r"<li>.+?<\/li>", ul)
    ul_match_sub_list = [re.sub("<.+?>", "", s) for s in ul_match_list]
    result = ul_match_sub_list[randint(0, len(ul_match_sub_list) - 1)]
    return result


def get_weather(citycode: int):
    url = "https://weather.tsukumijima.net/api/forecast"

    # citycode一覧"https://weather.tsukumijima.net/primary_area.xml"
    params = {"city": citycode}

    res = requests.get(url, params=params)
    json = res.json()

    # date = json["forecasts"][0]["date"]
    district = json["location"]["district"]
    # body_text = json["description"]["bodyText"]
    weather = json["forecasts"][0]["detail"]["weather"]
    weather = weather.replace("　", "")
    # min_temp = json["forecasts"][0]["temperature"]["min"]["celsius"]
    # max_temp = json["forecasts"][0]["temperature"]["max"]["celsius"]
    chanceOfRain_morning = json["forecasts"][0]["chanceOfRain"]["T06_12"]
    chanceOfRain_evening = json["forecasts"][0]["chanceOfRain"]["T12_18"]
    chanceOfRain_night = json["forecasts"][0]["chanceOfRain"]["T18_24"]

    result = f"{district}: {weather}\n☔ 朝: {chanceOfRain_morning} | 昼: {chanceOfRain_evening} | 晩: {chanceOfRain_night}"

    return result


def get_exchange_rate():
    # demoに制限が出てくれば、無料のAPIキーを取得する。
    url = "https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=USD&to_currency=JPY&apikey=demo"

    result = requests.get(url)
    json = result.json()

    usd_jpy = float(json["Realtime Currency Exchange Rate"]["5. Exchange Rate"])
    round_usd_jpy = round(usd_jpy, 2)

    return round_usd_jpy


async def get_trivia() -> str:
    endpoint = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f'Bearer {os.getenv("OPENAI_API_KEY")}',
    }

    payload = {
        "model": "gpt-4-1106-preview",
        "messages": [
            {"role": "system", "content": "あなたはこの世の森羅万象を知り尽くした天才です。"},
            {
                "role": "user",
                "content": "雑学を一つ教えてください。内容は、この世の森羅万象を対象に動物、昆虫、その他の生物、\
                    科学、物理、音楽、文学、カルチャーなどなど、何でも良いです。難しい話ももちろんOKです。\
                    文字数はだいたい日本語で200文字程度にしてください。",
            },
        ],
        "max_tokens": 1000,
    }

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(3),
        retry=tenacity.retry_if_exception_type(httpx.HTTPError),
    )
    async def fetch_data():
        async with httpx.AsyncClient() as client:
            res = await client.post(endpoint, headers=headers, json=payload, timeout=120)

        if res.status_code != 200:
            raise httpx.HTTPError("Non-200 response from OpenAI API")
        return res

    try:
        res = await fetch_data()
    except tenacity.RetryError:
        return "⚠OpenAIのAPIリクエストでエラーが発生したので今日の雑学はなしです。"

    json = res.json()
    answer = json["choices"][0]["message"]["content"]
    return answer
