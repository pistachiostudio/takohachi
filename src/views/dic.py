from collections.abc import Awaitable, Callable

import discord

# Discordに送る/編集するメッセージの中身。使わない側はNone。
DicMessage = dict[str, str | discord.Embed | None]

DB_URL = "https://docs.google.com/spreadsheets/d/15QCsHsmtZAs1FtiCplLmybU80WyxWw4C7G6ESf2b9f4/edit#gid=1264027664&range=A1"  # noqa: E501


def build_message(keyword: str, data: dict[str, str]) -> DicMessage:
    """`/dic` の検索結果(スプレッドシートの1行)を、Discordのメッセージにする。"""
    if data["response"]:
        return {"content": f"{data['response']}", "embed": None}

    embed = discord.Embed()
    embed.set_footer(text=f"Keyword: {keyword}")
    if data["title"]:
        embed.title = f"{data['title']}"
    if data["description"]:
        embed.description = f"{data['description']}\n\n[Check DB]({DB_URL})"
    if data["right_small_image_URL"]:
        embed.set_thumbnail(url=f"{data['right_small_image_URL']}")
    if data["big_image_URL"]:
        embed.set_image(url=f"{data['big_image_URL']}")
    embed.color = discord.Color.dark_blue()
    return {"content": None, "embed": embed}


def send_kwargs(message: DicMessage) -> dict[str, str | discord.Embed]:
    """followup.send に渡せるよう、Noneの項目を除く。"""
    return {k: v for k, v in message.items() if v is not None}


class DicSuggestView(discord.ui.View):
    """`/dic` の「もしかして」ボタン。押すとそのメッセージが検索結果に置き換わる。"""

    def __init__(
        self,
        owner_id: int,
        keywords: list[str],
        fetch: Callable[[str], Awaitable[DicMessage | None]],
    ):
        super().__init__(timeout=180)
        self.owner_id = owner_id
        self.fetch = fetch
        self.message: discord.Message | None = None
        # このメッセージが本人にだけ見える(ephemeral)か。送信後に呼び出し側が実際の状態を設定する。
        self.ephemeral = False
        for keyword in keywords:
            # ボタンのラベルは80文字まで。
            button = discord.ui.Button(label=keyword[:80], style=discord.ButtonStyle.primary)
            button.callback = self._make_callback(keyword)
            self.add_item(button)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message(
                "このボタンは、コマンドを実行した本人だけが押せます。", ephemeral=True
            )
            return False
        return True

    def _make_callback(self, keyword: str):
        async def callback(interaction: discord.Interaction):
            await interaction.response.defer()
            message = await self.fetch(keyword)
            if message is None:
                await interaction.edit_original_response(
                    content=f":warning: 「{keyword}」を取得できませんでした。",
                    embed=None,
                    view=None,
                )
            elif self.ephemeral:
                # 非公開メッセージを編集しても本人にしか見えないので、結果はチャンネルに公開で送り、
                # ボタン付きのメッセージは簡単な表示に置き換える。
                channel = interaction.channel
                if channel is not None:
                    await channel.send(**send_kwargs(message))
                else:
                    await interaction.followup.send(**send_kwargs(message))
                await interaction.edit_original_response(
                    content=f"「{keyword}」を表示しました。", embed=None, view=None
                )
            else:
                # send_kwargs は使わない。編集ではNoneが「その項目を消す」意味になるため、
                # content=None を渡して「もしかして…」の文言を消し、embedだけの表示に置き換える。
                await interaction.edit_original_response(**message, view=None)
            self.stop()

        return callback

    async def on_timeout(self):
        # 押されないまま時間が経ったら、ボタンを外す。
        if self.message is not None:
            try:
                await self.message.edit(view=None)
            except discord.HTTPException:
                pass
