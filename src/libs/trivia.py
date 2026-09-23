"""朝の投稿用の雑学を、Geminiで生成しTypeSafeで検証して返すモジュール。"""

import logging
import os
import random
from typing import NamedTuple

from libs import typesafe
from libs.http_client import HTTPClient

logger = logging.getLogger(__name__)

# 主モデルが失敗したら、この順で次のモデルを1回だけ試す。
# 429(クォータ超過)はモデルごと・1分単位の制限なので、同じモデルに再試行しても
# 成功する見込みは薄く、クォータを追加で消費するだけになる。モデルを変えれば
# 別のクォータ枠になるため、503(一時的な過負荷)にも429にも効く。
#
# 2026年9月時点、gemini-3.6/3.7/3.8-flash は新モデル特有の需要過多で503が頻発しており
# (Google公式フォーラムで報告多数)、3.8が落ちていると3.6も道連れで落ちていることがある。
# 3.5-flash-lite は軽量モデルで別のGPU枠のため影響を受けにくく、2.5-flashは実績のある
# 最後の砦として残す。
GEMINI_MODELS = ["gemini-3.8-flash", "gemini-3.5-flash-lite", "gemini-2.5-flash"]

# 検証に通らなかった場合に雑学を作り直す最大回数(初回を含む)
MAX_ATTEMPTS = 3
# Noulの確率(yesである確率)がこの値以上なら「問題あり」として却下する。
# 実際の出力を見ながら調整する想定の初期値。
REJECT_THRESHOLD = 0.5

FALLBACK_MESSAGE = "⚠雑学の取得でエラーが発生したので今日の雑学はなしです。"


class Trivia(NamedTuple):
    text: str
    # 実際に生成できたGeminiのモデル名。生成できなかった(フォールバック文言の)場合はNone。
    model: str | None = None
    # TypeSafe(Jev)の検証を通過した場合のみ設定される「事実誤認がない確率」(0〜1)。
    # 検証のスキップ・失敗時やフォールバック時はNone。
    truth: float | None = None


def format_trivia_section(trivia: Trivia) -> str:
    """投稿用に、雑学の本文とクレジット行(使用モデル・検証済みならJevのスコア付き)を組み立てる。"""
    model = trivia.model or "Gemini"
    credit = f"Powered by {model}"
    if trivia.truth is not None:
        credit += f" / Jev truthfulness score: {trivia.truth:.0%}"
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


async def generate_trivia() -> tuple[str, str]:
    """Gemini APIで雑学を1つ生成する。(本文, 実際に使ったモデル名) を返す。

    GEMINI_MODELS の先頭から順に1回ずつ試し、最初に成功したものを返す。
    retry_transient(libs.http_client)はこのパスには適用していない。同じモデルへの
    多重リトライは、失敗のたびに次のモデルへ切り替えるこの仕組みと二重にかかると、
    短時間に大量のリクエストが飛んでクォータを消費してしまうため(過去に実際に発生した。
    詳細は GEMINI_MODELS の説明を参照)。
    """
    if not GEMINI_MODELS:
        raise ValueError("GEMINI_MODELS が空です")

    last_error: Exception | None = None
    for model in GEMINI_MODELS:
        try:
            return await _generate_with_model(model), model
        except Exception as e:
            last_error = e
            logger.warning("Gemini(%s) failed, trying next model: %s", model, e)
    raise last_error


async def _generate_with_model(model: str) -> str:
    prompt = TRIVIA_PROMPT.format(category=random.choice(TRIVIA_CATEGORIES))
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    res = await HTTPClient().post(
        url,
        headers={
            "x-goog-api-key": os.environ["GEMINI_API_KEY"],
            "Content-Type": "application/json",
        },
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=120,
    )
    candidate = res["candidates"][0]
    if candidate.get("finishReason") == "MAX_TOKENS":
        raise ValueError(f"Geminiの出力がMAX_TOKENSで途切れました({model})")
    # 思考(thought)パートが混ざる場合に備え、本文のテキストだけを連結する。
    parts = candidate["content"]["parts"]
    text = "".join(p.get("text", "") for p in parts if not p.get("thought")).strip()
    if not text:
        raise ValueError(f"Geminiの出力に本文がありません({model})")
    return text


async def check_trivia(trivia: str) -> dict[str, float]:
    """TypeSafeで雑学を検証し、質問IDごとの「問題がある確率」を返す。"""
    answers = await typesafe.system_one(trivia, CHECK_QUESTIONS)
    probabilities = {q: answers[q]["noul"] for q in CHECK_QUESTIONS}
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

    verify = typesafe.is_configured()
    if not verify:
        logger.warning("TYPESAFE_API_KEY is not set; skipping trivia verification")

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            text, model = await generate_trivia()
        except Exception:
            logger.exception("Failed to generate trivia (attempt %d)", attempt)
            continue

        if not verify:
            return Trivia(text, model)

        try:
            probabilities = await check_trivia(text)
        except Exception:
            logger.exception("Trivia verification failed; posting without verification")
            return Trivia(text, model)

        problems = [q for q, p in probabilities.items() if p >= REJECT_THRESHOLD]
        if not problems:
            return Trivia(text, model, truth=1 - probabilities["has_factual_error"])
        logger.warning("Trivia rejected (attempt %d): %s", attempt, ", ".join(problems))

    return Trivia(FALLBACK_MESSAGE)
