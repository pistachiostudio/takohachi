import asyncio
import logging
import os

import discord
from discord import app_commands
from discord.ext import commands

from libs import dic_search
from settings import GUILD_ID
from views.dic import DicMessage, DicSuggestView, build_message, send_kwargs

from .api import get_trigger_repository

DIC_KEY = os.environ["DIC_KEY"]
PREFIX = os.environ["PREFIX"]

logger = logging.getLogger(__name__)


class Trigger(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.trigger_repo = get_trigger_repository()

    @app_commands.command(name="dic", description="Trigger Commands")
    @app_commands.describe(keyword="キーワードを入力してください。例) genkai, 徳井病, gomi など")
    async def trigger(self, interaction: discord.Interaction, keyword: str):
        # interactionは3秒以内にレスポンスしないといけないとエラーになるのでこの処理で待たせる。
        await interaction.response.defer()

        trigger: str = keyword
        data = self.trigger_repo.select(trigger)

        if data:
            await interaction.followup.send(**send_kwargs(build_message(keyword, data)))
            return

        not_found = f":warning: 「{trigger}」は登録されていません。"
        suggestions = await self._suggest(trigger)
        if not suggestions:
            await interaction.followup.send(not_found)
            return

        # 完全一致しなかった場合は、Jevが選んだ候補を、本人にだけ見えるボタンで提示する。
        # 最初に公開で出した「考え中」の表示は、非公開のメッセージに切り替えられない
        # 可能性があるため、いったん消してから送る。
        try:
            await interaction.delete_original_response()
        except discord.HTTPException:
            logger.exception("Failed to delete the deferred dic response")
        view = DicSuggestView(interaction.user.id, suggestions, self._fetch)
        try:
            message = await interaction.followup.send(
                f"{not_found}\nもしかして…", view=view, ephemeral=True, wait=True
            )
        except discord.HTTPException:
            # 「考え中」を消したあとに送れなかった場合は、何も残らないことがないよう警告を返す。
            logger.exception("Failed to send the dic suggestions")
            await interaction.followup.send(not_found)
            return
        view.message = message
        # 実際に非公開になったかで、ボタンを押したあとの動きを切り替える(公開になった場合は
        # そのメッセージを結果に置き換える)。
        view.ephemeral = bool(message.flags.ephemeral)
        logger.info("dic suggestions sent (ephemeral=%s)", view.ephemeral)

    async def _suggest(self, keyword: str) -> list[str]:
        try:
            entries = await asyncio.to_thread(self.trigger_repo.list_entries)
        except Exception:
            logger.exception("Failed to load dic entries for fuzzy search")
            return []
        return await dic_search.suggest(keyword, entries)

    async def _fetch(self, keyword: str) -> DicMessage | None:
        data = await asyncio.to_thread(self.trigger_repo.select, keyword)
        return build_message(keyword, data) if data else None

    @trigger.autocomplete("keyword")
    async def trigger_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        keywords = self.trigger_repo.list_triggers()
        matched = [k for k in keywords if current.lower() in k.lower()]
        return [app_commands.Choice(name=k, value=k) for k in matched[:25]]


async def setup(bot: commands.Bot):
    await bot.add_cog(Trigger(bot), guilds=[discord.Object(id=GUILD_ID)])
