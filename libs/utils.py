import re
from random import randint
from urllib import parse
import requests
from datetime import datetime, timedelta, timezone


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
    base_url = 'https://ja.wikipedia.org/wiki/Wikipedia:'
    uri = f'今日は何の日_{this_month}月'

    res = requests.get(base_url + parse.quote(uri))
    html = res.text
    today_idx = html.index(f'id="{this_month}月{this_day}日"')
    ul_start_idx = html.index('ul', today_idx)
    ul_end_idx = html.index('/ul', ul_start_idx)
    ul = html[ul_start_idx:ul_end_idx].replace('\n', '')
    ul_match_list = re.findall(r'<li>.+?<\/li>', ul)
    ul_match_sub_list = [re.sub('<.+?>', '', s) for s in ul_match_list]
    result = ul_match_sub_list[randint(0, len(ul_match_sub_list) - 1)]
    return result