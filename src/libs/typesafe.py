"""TypeSafe(System One)APIの共通呼び出し。"""

import os

from libs.http_client import HTTPClient, retry_transient

TYPESAFE_API_URL = "https://api.typesafe.ai/v1/systemone"
TYPESAFE_MODEL = "jev-latest"


def is_configured() -> bool:
    """TYPESAFE_API_KEY が設定されているか。"""
    return bool(os.getenv("TYPESAFE_API_KEY"))


@retry_transient
async def system_one(state, questions: dict, timeout: float = 30) -> dict[str, dict]:
    """stateに対して質問群を評価し、質問IDごとの回答(answers)を返す。

    429/503/529 は一時障害として指数バックオフで再試行する。
    """
    res = await HTTPClient().post(
        TYPESAFE_API_URL,
        headers={"Authorization": f"Bearer {os.environ['TYPESAFE_API_KEY']}"},
        json={"state": state, "model": TYPESAFE_MODEL, "questions": questions},
        timeout=timeout,
    )
    return res["answers"]
