import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from libs import dic_search


def _entry(trigger, alias01="", alias02="", title="", description=""):
    return {
        "trigger": trigger,
        "alias01": alias01,
        "alias02": alias02,
        "title": title,
        "description": description,
    }


def _answers(**probabilities):
    return {dic_search.QUESTION_ID: {"type": "choice", "probabilities": probabilities}}


@pytest.fixture(autouse=True)
def _key(monkeypatch):
    monkeypatch.setenv("TYPESAFE_API_KEY", "test-typesafe")


def _suggest(query, entries, answers=None, error=None):
    mock = AsyncMock(return_value=answers, side_effect=error)
    with patch("libs.dic_search.typesafe.system_one", new=mock):
        return asyncio.run(dic_search.suggest(query, entries)), mock


def test_build_question_describes_each_entry():
    entries = [
        _entry("gomi", alias01="ごみ", title="ゴミの日", description="a" * 300),
        _entry("genkai"),
    ]

    question = dic_search.build_question(entries)
    criteria = question["criteria"]

    assert question["type"] == "choice"
    assert list(criteria) == ["gomi", "genkai", dic_search.NONE_OPTION]
    assert criteria["gomi"].startswith("別名: ごみ / タイトル: ゴミの日 / 説明: ")
    assert criteria["gomi"].count("a") == dic_search.DESCRIPTION_CHARS
    assert criteria["genkai"] is None


def test_build_question_dedupes_and_caps_options():
    entries = [_entry("dup", title="first"), _entry("dup", title="second")]
    assert "first" in dic_search.build_question(entries)["criteria"]["dup"]

    many = [_entry(f"t{i}") for i in range(dic_search.MAX_ENTRIES + 10)]
    criteria = dic_search.build_question(many)["criteria"]
    assert len(criteria) == dic_search.MAX_ENTRIES + 1  # 選択肢 + 「該当なし」


def test_suggest_returns_top_candidates_in_order():
    entries = [_entry("gomi"), _entry("genkai"), _entry("徳井病"), _entry("other")]
    answers = _answers(gomi=0.6, genkai=0.2, 徳井病=0.1, other=0.02, **{"__none__": 0.08})

    result, _ = _suggest("ごみ捨て", entries, answers)

    assert result == ["gomi", "genkai", "徳井病"]


def test_suggest_returns_nothing_when_none_is_very_likely():
    entries = [_entry("gomi")]
    answers = _answers(gomi=0.03, **{"__none__": 0.97})

    result, _ = _suggest("ぜんぜん関係ない", entries, answers)

    assert result == []


def test_suggest_keeps_plausible_candidate_even_if_none_is_leading():
    # 実APIで「宴会いつ？」がこの分布になった。確認ボタンで出すので候補を残す。
    entries = [_entry("nomikai", alias01="飲み会")]
    answers = _answers(nomikai=0.31, **{"__none__": 0.66})

    result, _ = _suggest("宴会いつ？", entries, answers)

    assert result == ["nomikai"]


def test_suggest_skips_without_key_or_entries(monkeypatch):
    result, mock = _suggest("x", [])
    assert result == [] and mock.await_count == 0

    monkeypatch.delenv("TYPESAFE_API_KEY")
    result, mock = _suggest("x", [_entry("gomi")])
    assert result == [] and mock.await_count == 0


def test_suggest_falls_back_to_empty_on_error():
    result, _ = _suggest("x", [_entry("gomi")], error=RuntimeError("down"))

    assert result == []
