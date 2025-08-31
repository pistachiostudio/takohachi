import discord

from libs.utils import get_now_timestamp_jst


# 共通で利用するカスタム embed を返します
def get_custum_embed() -> discord.Embed:
    embed = discord.Embed()
    embed.timestamp = get_now_timestamp_jst()

    return embed


def create_embed(
    title: str | None = None,
    description: str | None = None,
    color: discord.Color | None = None,
    thumbnail_url: str | None = None,
    image_url: str | None = None,
    author_name: str | None = None,
    author_url: str | None = None,
    author_icon_url: str | None = None,
    footer_text: str | None = None,
    footer_icon_url: str | None = None,
    fields: list[tuple[str, str, bool]] | None = None,
    timestamp: bool = True,
) -> discord.Embed:
    """
    Discord Embedを作成するヘルパー関数

    Args:
        title: Embedのタイトル
        description: Embedの説明文
        color: Embedの色
        thumbnail_url: サムネイル画像のURL
        image_url: メイン画像のURL
        author_name: 著者名
        author_url: 著者のURL
        author_icon_url: 著者のアイコンURL
        footer_text: フッターテキスト
        footer_icon_url: フッターアイコンURL
        fields: フィールドのリスト [(name, value, inline), ...]
        timestamp: タイムスタンプを追加するか

    Returns:
        discord.Embed: 設定されたEmbed
    """
    embed = discord.Embed()

    if title:
        embed.title = title
    if description:
        embed.description = description
    if color:
        embed.color = color
    if timestamp:
        embed.timestamp = get_now_timestamp_jst()

    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)
    if image_url:
        embed.set_image(url=image_url)

    if author_name:
        embed.set_author(name=author_name, url=author_url, icon_url=author_icon_url)

    if footer_text:
        embed.set_footer(text=footer_text, icon_url=footer_icon_url)

    if fields:
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

    return embed


def create_error_embed(
    error_message: str, title: str = "エラーが発生しました", service_name: str | None = None
) -> discord.Embed:
    """
    エラー用のEmbedを作成するヘルパー関数

    Args:
        error_message: エラーメッセージ
        title: Embedのタイトル
        service_name: サービス名（あれば）

    Returns:
        discord.Embed: エラー用のEmbed
    """
    if service_name:
        title = f"{service_name} - {title}"

    return create_embed(
        title=f"⚠ {title}", description=error_message, color=discord.Color.red(), timestamp=True
    )


def create_success_embed(
    message: str, title: str = "成功", color: discord.Color = discord.Color.green()
) -> discord.Embed:
    """
    成功メッセージ用のEmbedを作成するヘルパー関数

    Args:
        message: 成功メッセージ
        title: Embedのタイトル
        color: Embedの色（デフォルトは緑）

    Returns:
        discord.Embed: 成功用のEmbed
    """
    return create_embed(title=f"✅ {title}", description=message, color=color, timestamp=True)
