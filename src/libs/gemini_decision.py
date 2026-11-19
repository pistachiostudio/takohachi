"""Gemini Decisions API(判定モデル)の共通呼び出し。

文章を生成せず、質問ごとの確率だけを返すモデル。Yes/No(noul)・選択式(choice)などを
1リクエストでまとめて評価できる。
"""

import os

from libs.http_client import HTTPClient, retry_transient

DECISIONS_API_URL = "https://generativelanguage.googleapis.com/v1beta/decisions"
DECISION_MODEL = "gemini-decision-1"


def is_configured() -> bool:
    """GEMINI_API_KEY が設定されているか。"""
    return bool(os.getenv("GEMINI_API_KEY"))


@retry_transient
async def decide(input: str, questions: dict, timeout: float = 30) -> dict[str, dict]:
    """inputに対して質問群を評価し、質問IDごとの回答(answers)を返す。

    noulの確率は0.01〜0.99に丸められて返る(0や1にはならない)。
    429/503/529 は一時障害として指数バックオフで再試行する。
    """
    res = await HTTPClient().post(
        DECISIONS_API_URL,
        headers={
            "x-goog-api-key": os.environ["GEMINI_API_KEY"],
            "Content-Type": "application/json",
        },
        json={"model": DECISION_MODEL, "input": input, "questions": questions},
        timeout=timeout,
    )
    return res["answers"]
