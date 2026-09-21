import asyncio
from unittest.mock import AsyncMock, MagicMock

import discord

from views.dic import DicSuggestView, build_message, send_kwargs


def _data(**overrides):
    data = {
        "response": "",
        "title": "",
        "description": "",
        "right_small_image_URL": "",
        "big_image_URL": "",
    }
    data.update(overrides)
    return data


def test_build_message_with_response_is_plain_text():
    message = build_message("gomi", _data(response="燃えるごみは月木"))

    assert message == {"content": "燃えるごみは月木", "embed": None}
    assert send_kwargs(message) == {"content": "燃えるごみは月木"}


def test_build_message_without_response_is_embed():
    message = build_message("gomi", _data(title="ゴミの日", description="月木"))

    embed = message["embed"]
    assert message["content"] is None
    assert embed.title == "ゴミの日"
    assert embed.description.startswith("月木")
    assert embed.footer.text == "Keyword: gomi"
    assert set(send_kwargs(message)) == {"embed"}


def _interaction(user_id):
    interaction = MagicMock(spec=discord.Interaction)
    interaction.user = MagicMock(id=user_id)
    interaction.response = MagicMock()
    interaction.response.defer = AsyncMock()
    interaction.response.send_message = AsyncMock()
    interaction.edit_original_response = AsyncMock()
    interaction.channel = MagicMock()
    interaction.channel.send = AsyncMock()
    interaction.followup = MagicMock()
    interaction.followup.send = AsyncMock()
    return interaction


def _run(coro_fn):
    return asyncio.run(coro_fn())


def test_view_has_a_button_per_suggestion():
    async def scenario():
        view = DicSuggestView(1, ["gomi", "genkai"], AsyncMock())
        return [item.label for item in view.children]

    assert _run(scenario) == ["gomi", "genkai"]


def test_owner_can_press_and_message_is_replaced():
    fetch = AsyncMock(return_value={"content": "結果", "embed": None})

    async def scenario():
        view = DicSuggestView(1, ["gomi"], fetch)
        interaction = _interaction(user_id=1)
        assert await view.interaction_check(interaction)
        await view.children[0].callback(interaction)
        return interaction

    interaction = _run(scenario)

    fetch.assert_awaited_once_with("gomi")
    interaction.edit_original_response.assert_awaited_once_with(
        content="結果", embed=None, view=None
    )


def test_other_users_cannot_press():
    async def scenario():
        view = DicSuggestView(1, ["gomi"], AsyncMock())
        interaction = _interaction(user_id=2)
        allowed = await view.interaction_check(interaction)
        return allowed, interaction

    allowed, interaction = _run(scenario)

    assert not allowed
    interaction.response.send_message.assert_awaited_once()


def test_missing_entry_shows_warning():
    async def scenario():
        view = DicSuggestView(1, ["gomi"], AsyncMock(return_value=None))
        interaction = _interaction(user_id=1)
        await view.children[0].callback(interaction)
        return interaction

    interaction = _run(scenario)

    kwargs = interaction.edit_original_response.await_args.kwargs
    assert "gomi" in kwargs["content"] and kwargs["view"] is None


def test_ephemeral_view_posts_result_publicly_and_replaces_buttons():
    fetch = AsyncMock(return_value={"content": "結果", "embed": None})

    async def scenario():
        view = DicSuggestView(1, ["gomi"], fetch)
        view.ephemeral = True
        interaction = _interaction(user_id=1)
        await view.children[0].callback(interaction)
        return interaction

    interaction = _run(scenario)

    # 結果はチャンネルに公開で送り、非公開メッセージのほうは簡単な表示にする
    interaction.channel.send.assert_awaited_once_with(content="結果")
    interaction.edit_original_response.assert_awaited_once_with(
        content="「gomi」を表示しました。", embed=None, view=None
    )


def test_ephemeral_view_falls_back_to_followup_without_channel():
    fetch = AsyncMock(return_value={"content": "結果", "embed": None})

    async def scenario():
        view = DicSuggestView(1, ["gomi"], fetch)
        view.ephemeral = True
        interaction = _interaction(user_id=1)
        interaction.channel = None
        await view.children[0].callback(interaction)
        return interaction

    interaction = _run(scenario)

    interaction.followup.send.assert_awaited_once_with(content="結果")


def test_ephemeral_view_does_not_publish_a_failed_lookup():
    async def scenario():
        view = DicSuggestView(1, ["gomi"], AsyncMock(return_value=None))
        view.ephemeral = True
        interaction = _interaction(user_id=1)
        await view.children[0].callback(interaction)
        return interaction

    interaction = _run(scenario)

    interaction.channel.send.assert_not_awaited()
    assert (
        "取得できませんでした" in interaction.edit_original_response.await_args.kwargs["content"]
    )
