import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import discord

from cogs.trigger import Trigger
from views.dic import DicSuggestView

DATA = {
    "response": "燃えるごみは月木",
    "title": "",
    "description": "",
    "right_small_image_URL": "",
    "big_image_URL": "",
}


def _interaction():
    interaction = MagicMock(spec=discord.Interaction)
    interaction.user = MagicMock(id=42)
    interaction.response = MagicMock()
    interaction.response.defer = AsyncMock()
    interaction.followup = MagicMock()
    interaction.followup.send = AsyncMock()
    interaction.delete_original_response = AsyncMock()
    return interaction


def _run_command(repo, keyword, suggestions=None, suggest_error=None):
    """Trigger.trigger を、リポジトリとJevをモックして実行する。"""
    interaction = _interaction()
    suggest = AsyncMock(return_value=suggestions or [], side_effect=suggest_error)

    async def scenario():
        with (
            patch("cogs.trigger.get_trigger_repository", return_value=repo),
            patch("cogs.trigger.dic_search.suggest", new=suggest),
        ):
            cog = Trigger(bot=MagicMock())
            await Trigger.trigger.callback(cog, interaction, keyword)

    asyncio.run(scenario())
    return interaction, suggest


def test_found_sends_result_without_fuzzy_search():
    repo = MagicMock()
    repo.select.return_value = DATA

    interaction, suggest = _run_command(repo, "gomi")

    interaction.response.defer.assert_awaited_once()
    interaction.followup.send.assert_awaited_once_with(content="燃えるごみは月木")
    suggest.assert_not_awaited()


def _run_with_suggestions(ephemeral_flag):
    repo = MagicMock()
    repo.select.return_value = None
    repo.list_entries.return_value = [{"trigger": "gomi"}, {"trigger": "genkai"}]
    sent = MagicMock(spec=discord.WebhookMessage)
    sent.flags = MagicMock(ephemeral=ephemeral_flag)

    async def scenario():
        interaction = _interaction()
        interaction.followup.send.return_value = sent
        with (
            patch("cogs.trigger.get_trigger_repository", return_value=repo),
            patch(
                "cogs.trigger.dic_search.suggest",
                new=AsyncMock(return_value=["gomi", "genkai"]),
            ),
        ):
            cog = Trigger(bot=MagicMock())
            await Trigger.trigger.callback(cog, interaction, "ごみ捨て")
        return interaction

    return asyncio.run(scenario()), sent


def test_not_found_with_suggestions_sends_ephemeral_buttons():
    interaction, sent = _run_with_suggestions(ephemeral_flag=True)

    # 公開の「考え中」を消してから、本人にだけ見える形で送る
    interaction.delete_original_response.assert_awaited_once()
    interaction.followup.send.assert_awaited_once()
    args, kwargs = interaction.followup.send.await_args
    assert "「ごみ捨て」は登録されていません。" in args[0]
    assert "もしかして" in args[0]
    assert kwargs["ephemeral"] is True
    view = kwargs["view"]
    assert isinstance(view, DicSuggestView)
    assert [item.label for item in view.children] == ["gomi", "genkai"]
    assert view.owner_id == 42
    # タイムアウト時にボタンを外せるよう、送信したメッセージを保持している
    assert view.message is sent
    assert view.ephemeral is True


def test_view_falls_back_to_in_place_edit_when_message_is_public():
    # ephemeralを指定しても、Discord側で公開になった場合は、押したら置き換える動きにする
    interaction, _ = _run_with_suggestions(ephemeral_flag=False)

    view = interaction.followup.send.await_args.kwargs["view"]
    assert view.ephemeral is False


def test_not_found_without_suggestions_sends_plain_warning():
    repo = MagicMock()
    repo.select.return_value = None
    repo.list_entries.return_value = []

    interaction, _ = _run_command(repo, "zzz", suggestions=[])

    interaction.followup.send.assert_awaited_once_with(":warning: 「zzz」は登録されていません。")


def test_sheet_error_during_fuzzy_search_falls_back_to_warning():
    repo = MagicMock()
    repo.select.return_value = None
    repo.list_entries.side_effect = RuntimeError("sheets down")

    interaction, suggest = _run_command(repo, "zzz")

    interaction.followup.send.assert_awaited_once_with(":warning: 「zzz」は登録されていません。")
    suggest.assert_not_awaited()


def test_fetch_builds_message_or_returns_none():
    repo = MagicMock()
    repo.select.side_effect = [DATA, None]

    async def scenario():
        with patch("cogs.trigger.get_trigger_repository", return_value=repo):
            cog = Trigger(bot=MagicMock())
            return await cog._fetch("gomi"), await cog._fetch("nothing")

    found, missing = asyncio.run(scenario())

    assert found == {"content": "燃えるごみは月木", "embed": None}
    assert missing is None


def test_send_failure_after_deleting_thinking_message_falls_back_to_warning():
    repo = MagicMock()
    repo.select.return_value = None
    repo.list_entries.return_value = [{"trigger": "gomi"}]
    error = discord.HTTPException(MagicMock(status=500, reason="error"), "boom")

    async def scenario():
        interaction = _interaction()
        interaction.followup.send.side_effect = [error, None]
        with (
            patch("cogs.trigger.get_trigger_repository", return_value=repo),
            patch("cogs.trigger.dic_search.suggest", new=AsyncMock(return_value=["gomi"])),
        ):
            cog = Trigger(bot=MagicMock())
            await Trigger.trigger.callback(cog, interaction, "ごみ捨て")
        return interaction

    interaction = asyncio.run(scenario())

    # 1回目は候補つき(失敗)、2回目は従来の警告。何も残らない状態にはならない
    assert interaction.followup.send.await_count == 2
    assert interaction.followup.send.await_args_list[1].args == (
        ":warning: 「ごみ捨て」は登録されていません。",
    )
