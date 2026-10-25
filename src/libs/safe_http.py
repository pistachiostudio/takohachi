"""利用者が入力したURLへ安全にアクセスするためのモジュール(SSRF対策)。

Botの内部ネットワーク(Railwayのプライベートネットワークやクラウドのメタデータ等)へ
アクセスさせないよう、接続先がインターネット上のアドレスであることを確認してから取得する。
リダイレクトは自動では追わず、1回ごとに接続先を検証し直す。
"""

import asyncio
import ipaddress
import re
import socket
from urllib.parse import urlsplit

import httpx
from bs4 import BeautifulSoup

MAX_REDIRECTS = 5
# <title> を探すのに読む最大バイト数。巨大なファイルを全部読み込まないようにする。
MAX_BODY_BYTES = 1024 * 1024
TIMEOUT = 10


class UnsafeURLError(ValueError):
    """アクセスを許可しないURL"""


def _is_public_ip(address: str) -> bool:
    ip = ipaddress.ip_address(address.split("%", 1)[0])
    # ::ffff:127.0.0.1 のような IPv4 射影アドレスは、中の IPv4 で判定する
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
        ip = ip.ipv4_mapped
    return ip.is_global


async def validate_public_url(url: str) -> None:
    """http(s) で、名前解決した全アドレスがインターネット上のものでなければ UnsafeURLError。"""
    try:
        parts = urlsplit(url)
        port = parts.port
    except ValueError as e:
        raise UnsafeURLError(f"URLの形式が正しくありません: {url}") from e
    if parts.scheme not in ("http", "https") or not parts.hostname:
        raise UnsafeURLError(f"http(s) のURLではありません: {url}")
    if parts.username or parts.password:
        raise UnsafeURLError("認証情報を含むURLは使えません")

    port = port or (443 if parts.scheme == "https" else 80)
    try:
        infos = await asyncio.get_running_loop().getaddrinfo(
            parts.hostname, port, type=socket.SOCK_STREAM
        )
    except socket.gaierror as e:
        raise UnsafeURLError(f"ホストが見つかりません: {parts.hostname}") from e
    if not infos or not all(_is_public_ip(info[4][0]) for info in infos):
        raise UnsafeURLError(f"アクセスできないホストです: {parts.hostname}")


async def fetch_title(url: str) -> str | None:
    """URLのページの <title> を返す(見つからなければNone)。"""
    async with httpx.AsyncClient(follow_redirects=False, timeout=TIMEOUT, trust_env=False) as c:
        for _ in range(MAX_REDIRECTS + 1):
            await validate_public_url(url)
            async with c.stream("GET", url) as res:
                if res.is_redirect:
                    url = str(res.url.join(res.headers["location"]))
                    continue
                body = b""
                async for chunk in res.aiter_bytes():
                    body += chunk
                    if len(body) >= MAX_BODY_BYTES:
                        break
            title = BeautifulSoup(body[:MAX_BODY_BYTES], "html.parser").title
            if title is None or not title.get_text(strip=True):
                return None
            # 前後や途中の空白・改行・TABをまとめる
            # (ナオトインティライミのHPは前後に空白が16個ずつも入っていた！ふざけるな！)
            return re.sub(r"\s+", " ", title.get_text()).strip()
    raise UnsafeURLError("リダイレクトが多すぎます")
