"""朝の投稿用の雑学を、Geminiで生成しTypeSafeで検証して返すモジュール。"""

import logging
import os
from typing import NamedTuple

from libs.http_client import HTTPClient

logger = logging.getLogger(__name__)

GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_API_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
)

TYPESAFE_API_URL = "https://api.typesafe.ai/v1/systemone"
TYPESAFE_MODEL = "jev-latest"

# 検証に通らなかった場合に雑学を作り直す最大回数(初回を含む)
MAX_ATTEMPTS = 3
# Noulの確率(yesである確率)がこの値以上なら「問題あり」として却下する。
# 実際の出力を見ながら調整する想定の初期値。
REJECT_THRESHOLD = 0.5

FALLBACK_MESSAGE = "⚠雑学の取得でエラーが発生したので今日の雑学はなしです。"


class Trivia(NamedTuple):
    text: str
    # TypeSafe(Jev)の検証を通過した場合のみ設定される「事実誤認がない確率」(0〜1)。
    # 検証のスキップ・失敗時やフォールバック時はNone。
    truth: float | None = None

    @property
    def verified(self) -> bool:
        return self.truth is not None


TRIVIA_PROMPT = (
    "あなたはあらゆる分野からランダムに興味深い雑学を紹介するエキスパートです。\n"
    "以下の分野から毎回ランダムに異なるテーマを選び、約400文字の日本語で雑学を1つ紹介してください。\n"
    "対象分野：動植物、生物学、宇宙、地理、歴史、哲学、科学、物理学、化学、数学、言語、文学、芸術、音楽、"
    "映画、カルチャー、食文化、スポーツ、テクノロジー、心理学、社会学、経済学、建築、医学、人体、民俗学、"
    "都市伝説など\n"
    "紹介する雑学は毎回前回と異なる分野から選んでください。雑学の内容はマニアックであっても構いません。\n"
    "冒頭に挨拶や前置きは一切不要です。冒頭に分野を記載することも不要で、本文のみ記載してください。"
)

# yes(=1に近い)が「問題あり」を意味するNoul質問。回答は質問IDごとに返る。
CHECK_QUESTIONS = {
    "has_factual_error": {
        "type": "noul",
        "instructions": (
            "この雑学は、事実として誤っている内容、または根拠のない俗説や捏造を"
            "事実であるかのように断定して紹介していますか？"
            "都市伝説や俗説を「そう言われている」「俗説である」と明示して紹介している場合は含みません。"
        ),
        "criteria": {
            "true": "事実として誤っている、または俗説・捏造を事実として断定している",
            "false": "事実として妥当、または俗説であることが明示されている",
        },
    },
    "has_preamble": {
        "type": "noul",
        "instructions": (
            "この文章には、雑学の本文以外の要素(挨拶、前置き、分野名や見出し、"
            "「以下に紹介します」のような案内文、締めの一言など)が含まれていますか？"
        ),
        "criteria": {
            "true": "本文以外の挨拶・前置き・見出し・案内文などを含む",
            "false": "雑学の本文のみで構成されている",
        },
    },
    "is_incomplete": {
        "type": "noul",
        "instructions": "この文章は、途中で途切れていたり、文の途中で終わっていたりしますか？",
        "criteria": {
            "true": "文の途中で終わっている、または内容が未完成",
            "false": "最後まで文章として完結している",
        },
    },
}


async def generate_trivia() -> str:
    """Gemini APIで雑学を1つ生成する。"""
    res = await HTTPClient().post(
        GEMINI_API_URL,
        headers={
            "x-goog-api-key": os.environ["GEMINI_API_KEY"],
            "Content-Type": "application/json",
        },
        json={"contents": [{"parts": [{"text": TRIVIA_PROMPT}]}]},
        timeout=120,
    )
    candidate = res["candidates"][0]
    if candidate.get("finishReason") == "MAX_TOKENS":
        raise ValueError("Geminiの出力がMAX_TOKENSで途切れました")
    return candidate["content"]["parts"][0]["text"].strip()


async def check_trivia(trivia: str) -> dict[str, float]:
    """TypeSafeで雑学を検証し、質問IDごとの「問題がある確率」を返す。"""
    res = await HTTPClient().post(
        TYPESAFE_API_URL,
        headers={"Authorization": f"Bearer {os.environ['TYPESAFE_API_KEY']}"},
        json={"state": trivia, "model": TYPESAFE_MODEL, "questions": CHECK_QUESTIONS},
        timeout=30,
    )
    probabilities = {q: res["answers"][q]["noul"] for q in CHECK_QUESTIONS}
    # 閾値を実データで調整するため、通った場合も含めて毎回確率を残す。
    logger.info(
        "Trivia check: %s (threshold=%.2f) head=%r",
        " ".join(f"{q}={p:.3f}" for q, p in probabilities.items()),
        REJECT_THRESHOLD,
        trivia[:30],
    )
    return probabilities


async def get_trivia() -> Trivia:
    """雑学を返す。取得できなかった場合はフォールバック文言を返す。

    TYPESAFE_API_KEY が未設定、またはTypeSafeの呼び出しに失敗した場合は、
    朝の投稿を止めないため検証をスキップして生成結果をそのまま返す。
    """
    if not os.getenv("GEMINI_API_KEY"):
        logger.error("GEMINI_API_KEY is not set")
        return Trivia(FALLBACK_MESSAGE)

    verify = bool(os.getenv("TYPESAFE_API_KEY"))
    if not verify:
        logger.warning("TYPESAFE_API_KEY is not set; skipping trivia verification")

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            trivia = await generate_trivia()
        except Exception:
            logger.exception("Failed to generate trivia (attempt %d)", attempt)
            continue

        if not verify:
            return Trivia(trivia)

        try:
            probabilities = await check_trivia(trivia)
        except Exception:
            logger.exception("Trivia verification failed; posting without verification")
            return Trivia(trivia)

        problems = [q for q, p in probabilities.items() if p >= REJECT_THRESHOLD]
        if not problems:
            return Trivia(trivia, truth=1 - probabilities["has_factual_error"])
        logger.warning("Trivia rejected (attempt %d): %s", attempt, ", ".join(problems))

    return Trivia(FALLBACK_MESSAGE)
