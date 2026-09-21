import asyncio
from unittest.mock import AsyncMock, patch

import pytest
from tenacity import wait_none

from libs import trivia, typesafe
from libs.http_client import APIError


def _noul(**values):
    """CHECK_QUESTIONS 全項目分のTypeSafeレスポンスを作る。指定のない項目は0.0(問題なし)。"""
    return {
        "answers": {
            q: {"type": "noul", "noul": values.get(q, 0.0)} for q in trivia.CHECK_QUESTIONS
        }
    }


def _gemini(text="雑学です。", finish_reason="STOP"):
    return {
        "candidates": [{"content": {"parts": [{"text": text}]}, "finishReason": finish_reason}]
    }


@pytest.fixture(autouse=True)
def _keys(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini")
    monkeypatch.setenv("TYPESAFE_API_KEY", "test-typesafe")


def _run(post_side_effect):
    with patch("libs.trivia.HTTPClient.post", new=AsyncMock(side_effect=post_side_effect)) as m:
        return asyncio.run(trivia.get_trivia()), m


def test_returns_trivia_when_verification_passes():
    result, post = _run([_gemini("良い雑学"), _noul()])

    assert result == trivia.Trivia("良い雑学", truth=1.0)
    assert post.await_count == 2


def test_regenerates_when_rejected():
    result, post = _run(
        [
            _gemini("誤りのある雑学"),
            _noul(has_factual_error=0.9),
            _gemini("直った雑学"),
            _noul(),
        ]
    )

    assert result == trivia.Trivia("直った雑学", truth=1.0)
    assert post.await_count == 4


def test_fallback_after_max_attempts():
    responses = []
    for _ in range(trivia.MAX_ATTEMPTS):
        responses += [_gemini(), _noul(has_preamble=0.8)]

    result, _ = _run(responses)

    assert result == trivia.Trivia(trivia.FALLBACK_MESSAGE)


def test_posts_unverified_when_typesafe_fails():
    result, _ = _run([_gemini("未検証の雑学"), RuntimeError("typesafe down")])

    assert result == trivia.Trivia("未検証の雑学")


def test_skips_verification_without_typesafe_key(monkeypatch):
    monkeypatch.delenv("TYPESAFE_API_KEY")

    result, post = _run([_gemini("雑学")])

    assert result == trivia.Trivia("雑学")
    assert post.await_count == 1


def test_truncated_output_is_retried():
    result, _ = _run(
        [_gemini("途中で", finish_reason="MAX_TOKENS"), _gemini("完全な雑学"), _noul()]
    )

    assert result == trivia.Trivia("完全な雑学", truth=1.0)


def test_fallback_without_gemini_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY")

    result, post = _run([])

    assert result == trivia.Trivia(trivia.FALLBACK_MESSAGE)
    assert post.await_count == 0


def test_truth_is_inverse_of_factual_error_probability():
    result, _ = _run([_gemini("雑学"), _noul(has_factual_error=0.2)])

    assert result.truth is not None
    assert result.truth == pytest.approx(0.8)


def test_low_truth_is_still_accepted():
    # 却下閾値未満なら採用し、スコアはそのまま(隠さず)返す
    result, _ = _run([_gemini("雑学"), _noul(has_factual_error=0.45)])

    assert result.text == "雑学"
    assert result.truth == pytest.approx(0.55)


def test_format_section_with_score():
    text = trivia.format_trivia_section(trivia.Trivia("本文", truth=0.97))

    assert text.startswith("本文\n(Powered by [Gemini]")
    assert "truthfulness score: 97%" in text


def test_format_section_without_score():
    text = trivia.format_trivia_section(trivia.Trivia("本文"))

    assert "Powered by [Gemini]" in text
    assert "truthfulness score" not in text
    assert "Trivia(" not in text


def test_transient_typesafe_error_is_retried(monkeypatch):
    monkeypatch.setattr(typesafe.system_one.retry, "wait", wait_none())

    result, post = _run([_gemini("雑学"), APIError("overloaded", status_code=529), _noul()])

    assert result == trivia.Trivia("雑学", truth=1.0)
    assert post.await_count == 3


def test_non_transient_error_is_not_retried(monkeypatch):
    monkeypatch.setattr(typesafe.system_one.retry, "wait", wait_none())

    result, post = _run([_gemini("雑学"), APIError("unauthorized", status_code=401)])

    assert result == trivia.Trivia("雑学")
    assert post.await_count == 2


def test_thought_parts_are_excluded():
    response = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"text": "思考の内容", "thought": True},
                        {"text": "本文です。"},
                    ]
                },
                "finishReason": "STOP",
            }
        ]
    }

    result, _ = _run([response, _noul()])

    assert result.text == "本文です。"


def test_empty_body_is_retried():
    empty = {"candidates": [{"content": {"parts": [{"text": "思考", "thought": True}]}}]}

    result, _ = _run([empty, _gemini("本文"), _noul()])

    assert result.text == "本文"


def test_prompt_uses_randomly_chosen_category():
    with patch("libs.trivia.random.choice", return_value="宇宙"):
        _, post = _run([_gemini("雑学"), _noul()])

    sent = post.await_args_list[0].kwargs["json"]["contents"][0]["parts"][0]["text"]
    assert "「宇宙」" in sent
    assert "{category}" not in sent


def test_every_category_fills_the_prompt():
    for category in trivia.TRIVIA_CATEGORIES:
        assert f"「{category}」" in trivia.TRIVIA_PROMPT.format(category=category)
