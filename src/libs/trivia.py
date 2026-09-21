"""朝の投稿用の雑学を、Geminiで生成しTypeSafeで検証して返すモジュール。"""

import logging
import os
import random
from typing import NamedTuple

from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from libs.http_client import APIError, HTTPClient

logger = logging.getLogger(__name__)

GEMINI_MODEL = "gemini-3.8-flash"
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

# 一時的な障害として再試行するHTTPステータス(レート制限・過負荷・一時利用不可)
TRANSIENT_STATUS_CODES = {429, 503, 529}

FALLBACK_MESSAGE = "⚠雑学の取得でエラーが発生したので今日の雑学はなしです。"


class Trivia(NamedTuple):
    text: str
    # TypeSafe(Jev)の検証を通過した場合のみ設定される「事実誤認がない確率」(0〜1)。
    # 検証のスキップ・失敗時やフォールバック時はNone。
    truth: float | None = None


def _is_transient(error: BaseException) -> bool:
    return isinstance(error, APIError) and error.status_code in TRANSIENT_STATUS_CODES


_retry_transient = retry(
    retry=retry_if_exception(_is_transient),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
)


def format_trivia_section(trivia: Trivia) -> str:
    """投稿用に、雑学の本文とクレジット行(検証済みならJevのスコア付き)を組み立てる。"""
    credit = "Powered by [Gemini](https://ai.google.dev/gemini-api/docs/models)"
    if trivia.truth is not None:
        credit += f" / [Jev](https://typesafe.ai) truthfulness score: {trivia.truth:.0%}"
    return f"{trivia.text}\n({credit})"


# 毎回独立した呼び出しでは「前回と違う分野」を守れないため、分野はコード側でランダムに選ぶ。
TRIVIA_CATEGORIES = [
    "動植物", "生物学", "宇宙", "地理", "歴史", "哲学", "科学", "物理学", "化学", "数学",
    "言語", "文学", "芸術", "音楽", "映画", "カルチャー", "食文化", "スポーツ", "テクノロジー",
    "心理学", "社会学", "経済学", "建築", "医学", "人体", "民俗学", "都市伝説",
]  # fmt: skip

TRIVIA_PROMPT = (
    "あなたは、正確さを重んじる雑学の専門家です。\n"
    "今回のテーマ分野は「{category}」です。この分野から、あまり知られていないが興味深い雑学を"
    "1つ選び、約400文字の日本語で紹介してください。\n"
    "条件:\n"
    "- 確実に裏付けのある事実だけを書くこと。数字・年号・固有名詞は確信があるものだけを使い、"
    "不確かな点は書かないこと。\n"
    "- 俗説・都市伝説・諸説ある話は、その旨を本文中で明示すること"
    "(例:「〜と言われている」「俗説だが」)。\n"
    "- マニアックな内容でも構わないが、専門用語には短い説明を添え、誰でも読める言葉で書くこと。\n"
    "- 挨拶・前置き・分野名・見出し・締めの一言は書かず、雑学の本文のみを出力すること。"
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


@_retry_transient
async def generate_trivia() -> str:
    """Gemini APIで雑学を1つ生成する。"""
    prompt = TRIVIA_PROMPT.format(category=random.choice(TRIVIA_CATEGORIES))
    res = await HTTPClient().post(
        GEMINI_API_URL,
        headers={
            "x-goog-api-key": os.environ["GEMINI_API_KEY"],
            "Content-Type": "application/json",
        },
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=120,
    )
    candidate = res["candidates"][0]
    if candidate.get("finishReason") == "MAX_TOKENS":
        raise ValueError("Geminiの出力がMAX_TOKENSで途切れました")
    # 思考(thought)パートが混ざる場合に備え、本文のテキストだけを連結する。
    parts = candidate["content"]["parts"]
    text = "".join(p.get("text", "") for p in parts if not p.get("thought")).strip()
    if not text:
        raise ValueError("Geminiの出力に本文がありません")
    return text


@_retry_transient
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
