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

    assert result == trivia.Trivia("良い雑学", trivia.GEMINI_MODELS[0], truth=1.0)
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

    assert result == trivia.Trivia("直った雑学", trivia.GEMINI_MODELS[0], truth=1.0)
    assert post.await_count == 4


def test_fallback_after_max_attempts():
    responses = []
    for _ in range(trivia.MAX_ATTEMPTS):
        responses += [_gemini(), _noul(has_preamble=0.8)]

    result, _ = _run(responses)

    assert result == trivia.Trivia(trivia.FALLBACK_MESSAGE)


def test_posts_unverified_when_typesafe_fails():
    result, _ = _run([_gemini("未検証の雑学"), RuntimeError("typesafe down")])

    assert result == trivia.Trivia("未検証の雑学", trivia.GEMINI_MODELS[0])


def test_skips_verification_without_typesafe_key(monkeypatch):
    monkeypatch.delenv("TYPESAFE_API_KEY")

    result, post = _run([_gemini("雑学")])

    assert result == trivia.Trivia("雑学", trivia.GEMINI_MODELS[0])
    assert post.await_count == 1


def test_truncated_output_falls_back_to_next_model():
    # 主モデルがMAX_TOKENSで途切れた場合、同じモデルに再試行せず次のモデルを試す
    result, post = _run(
        [_gemini("途中で", finish_reason="MAX_TOKENS"), _gemini("完全な雑学"), _noul()]
    )

    assert result == trivia.Trivia("完全な雑学", trivia.GEMINI_MODELS[1], truth=1.0)
    assert post.await_count == 3


def test_primary_model_failure_falls_back_within_one_generate_call():
    # 主モデルが503などで失敗しても、get_trivia の外側ループを消費せず
    # generate_trivia の中でフォールバックモデルに切り替わる。
    result, post = _run(
        [APIError("overloaded", status_code=503), _gemini("フォールバックの雑学"), _noul()]
    )

    assert result == trivia.Trivia("フォールバックの雑学", trivia.GEMINI_MODELS[1], truth=1.0)
    assert post.await_count == 3
    urls = [call.args[0] for call in post.await_args_list]
    assert trivia.GEMINI_MODELS[0] in urls[0]
    assert trivia.GEMINI_MODELS[1] in urls[1]


def test_three_models_configured_newest_first():
    # 障害時、より軽量/実績のあるモデルへ段階的にフォールバックする構成になっている
    assert trivia.GEMINI_MODELS == [
        "gemini-3.8-flash",
        "gemini-3.5-flash-lite",
        "gemini-2.5-flash",
    ]


def test_all_models_failing_is_one_outer_attempt():
    # 全モデルが失敗しても、get_trivia の外側ループは1回消費するだけ(多重リトライしない)
    responses = []
    for _ in range(trivia.MAX_ATTEMPTS):
        responses += [APIError("overloaded", status_code=503) for _ in trivia.GEMINI_MODELS]

    result, post = _run(responses)

    assert result == trivia.Trivia(trivia.FALLBACK_MESSAGE)
    assert post.await_count == trivia.MAX_ATTEMPTS * len(trivia.GEMINI_MODELS)


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
    text = trivia.format_trivia_section(trivia.Trivia("本文", "gemini-3.8-flash", truth=0.97))

    assert text == "本文\n(Powered by gemini-3.8-flash / Jev truthfulness score: 97%)"


def test_format_section_without_score():
    text = trivia.format_trivia_section(trivia.Trivia("本文", "gemini-3.8-flash"))

    assert text == "本文\n(Powered by gemini-3.8-flash)"
    assert "Trivia(" not in text


def test_format_section_without_model():
    # フォールバック文言など、モデルが分からない場合は総称の"Gemini"を出す
    text = trivia.format_trivia_section(trivia.Trivia("本文"))

    assert text == "本文\n(Powered by Gemini)"


def test_transient_typesafe_error_is_retried(monkeypatch):
    monkeypatch.setattr(typesafe.system_one.retry, "wait", wait_none())

    result, post = _run([_gemini("雑学"), APIError("overloaded", status_code=529), _noul()])

    assert result == trivia.Trivia("雑学", trivia.GEMINI_MODELS[0], truth=1.0)
    assert post.await_count == 3


def test_non_transient_error_is_not_retried(monkeypatch):
    monkeypatch.setattr(typesafe.system_one.retry, "wait", wait_none())

    result, post = _run([_gemini("雑学"), APIError("unauthorized", status_code=401)])

    assert result == trivia.Trivia("雑学", trivia.GEMINI_MODELS[0])
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


def test_empty_body_falls_back_to_next_model():
    empty = {"candidates": [{"content": {"parts": [{"text": "思考", "thought": True}]}}]}

    result, _ = _run([empty, _gemini("本文"), _noul()])

    assert result.text == "本文"
    assert result.model == trivia.GEMINI_MODELS[1]


def test_prompt_uses_randomly_chosen_category():
    with patch("libs.trivia.random.choice", return_value="宇宙"):
        _, post = _run([_gemini("雑学"), _noul()])

    sent = post.await_args_list[0].kwargs["json"]["contents"][0]["parts"][0]["text"]
    assert "「宇宙」" in sent
    assert "{category}" not in sent


def test_every_category_fills_the_prompt():
    for category in trivia.TRIVIA_CATEGORIES:
        assert f"「{category}」" in trivia.TRIVIA_PROMPT.format(category=category)


def test_empty_model_list_raises_clear_error(monkeypatch):
    monkeypatch.setattr(trivia, "GEMINI_MODELS", [])

    with pytest.raises(ValueError, match="GEMINI_MODELS"):
        asyncio.run(trivia.generate_trivia())
