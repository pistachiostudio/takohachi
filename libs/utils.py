from datetime import datetime, timedelta, timezone


def get_now_timestamp_jst() -> datetime:
    JST = timezone(timedelta(hours=+9), "JST")
    return datetime.now(JST)
