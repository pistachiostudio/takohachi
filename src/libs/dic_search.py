"""`/dic` のあいまい検索: 登録済みの項目から、入力に近いものをJev(TypeSafe)で選ぶ。"""

import logging

from libs import typesafe

logger = logging.getLogger(__name__)

# Choiceの選択肢は最大255個。「該当なし」の分を1つ引く。
MAX_ENTRIES = 254
NONE_OPTION = "__none__"
# 各項目の手がかりとして使う説明文の長さ(長文は送らない)
DESCRIPTION_CHARS = 100
MAX_SUGGESTIONS = 3
# この確率未満の候補は提示しない。
MIN_PROBABILITY = 0.05
# 「該当なし」の確率がこの値以上なら、候補を出さず「登録されていません」に倒す。
# 確認ボタンで提示するため、外れた候補が出るコストより見逃しのコストが大きい。緩めの値にしている。
NONE_THRESHOLD = 0.9

QUESTION_ID = "match"


def _describe(entry: dict[str, str]) -> str | None:
    """Jevに渡す、その項目の手がかり(別名・タイトル・説明文の冒頭)。"""
    parts = []
    aliases = [a for a in (entry.get("alias01", ""), entry.get("alias02", "")) if a]
    if aliases:
        parts.append("別名: " + ", ".join(aliases))
    if entry.get("title"):
        parts.append("タイトル: " + entry["title"])
    if entry.get("description"):
        parts.append("説明: " + entry["description"][:DESCRIPTION_CHARS])
    return " / ".join(parts) or None


def build_question(entries: list[dict[str, str]]) -> dict:
    """登録済みの項目から、Jevに投げるChoice質問を組み立てる。"""
    if len(entries) > MAX_ENTRIES:
        logger.warning("dic entries exceed %d; only the first ones are searched", MAX_ENTRIES)

    criteria: dict[str, str | None] = {}
    for entry in entries[:MAX_ENTRIES]:
        # 同じtriggerが重複していても、先に登録されたほうだけを使う。
        criteria.setdefault(entry["trigger"], _describe(entry))
    criteria[NONE_OPTION] = "どの項目にも該当しない"

    return {
        "type": "choice",
        "instructions": (
            "ユーザーが検索欄に入力した言葉 `query` は、辞書のどの項目を探そうとしていますか？"
            "各選択肢の名前と説明(別名・タイトル・説明文)を手がかりに、最も近い項目を選んでください。"
            f"どれにも当てはまらなければ「{NONE_OPTION}」を選んでください。"
        ),
        "criteria": criteria,
    }


async def suggest(
    query: str, entries: list[dict[str, str]], limit: int = MAX_SUGGESTIONS
) -> list[str]:
    """入力に近い登録済みのtriggerを、確からしい順に最大limit件返す。

    候補がない・TypeSafeが使えない・呼び出しに失敗した場合は空リストを返す
    (呼び出し側は従来どおり「登録されていません」に倒せる)。
    """
    if not entries or not typesafe.is_configured():
        return []

    try:
        answers = await typesafe.system_one(
            {"query": query}, {QUESTION_ID: build_question(entries)}
        )
        probabilities: dict[str, float] = answers[QUESTION_ID]["probabilities"]
    except Exception:
        logger.exception("dic fuzzy search failed")
        return []

    ranked = sorted(
        ((p, k) for k, p in probabilities.items() if k != NONE_OPTION and p >= MIN_PROBABILITY),
        reverse=True,
    )
    none_probability = probabilities.get(NONE_OPTION, 0.0)
    # 確率のしきい値を実データで調整するため、毎回上位の候補を残す。
    logger.info(
        "dic fuzzy search: query=%r none=%.3f top=%s",
        query,
        none_probability,
        ", ".join(f"{k}={p:.3f}" for p, k in ranked[:5]),
    )

    if none_probability >= NONE_THRESHOLD:
        return []
    return [k for _, k in ranked[:limit]]
