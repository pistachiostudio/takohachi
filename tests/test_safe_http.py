import asyncio
import socket
from unittest.mock import patch

import pytest

from libs import safe_http


def _resolve_to(*addresses):
    async def getaddrinfo(host, port, type=0):
        return [(socket.AF_INET, socket.SOCK_STREAM, 0, "", (a, port)) for a in addresses]

    return getaddrinfo


def _validate(url, *addresses):
    async def run():
        loop = asyncio.get_running_loop()
        with patch.object(loop, "getaddrinfo", _resolve_to(*addresses)):
            await safe_http.validate_public_url(url)

    asyncio.run(run())


def test_public_address_is_allowed():
    _validate("https://example.com/path", "93.184.216.34")


@pytest.mark.parametrize(
    "address",
    [
        "127.0.0.1",  # loopback
        "10.0.0.5",  # private
        "192.168.1.1",  # private
        "169.254.169.254",  # クラウドのメタデータ
        "0.0.0.0",
        "::1",
        "fd12:3456::1",  # Railway のプライベートネットワーク(ULA)
        "::ffff:127.0.0.1",  # IPv4 射影
    ],
)
def test_internal_addresses_are_rejected(address):
    with pytest.raises(safe_http.UnsafeURLError):
        _validate("http://internal.example/", address)


def test_rejected_if_any_resolved_address_is_internal():
    with pytest.raises(safe_http.UnsafeURLError):
        _validate("http://mixed.example/", "93.184.216.34", "127.0.0.1")


@pytest.mark.parametrize(
    "url",
    [
        "file:///etc/passwd",
        "ftp://example.com/",
        "httpx://example.com/",
        "http://user:pass@example.com/",
        "http://example.com:99999/",
        "not a url",
    ],
)
def test_invalid_urls_are_rejected(url):
    with pytest.raises(safe_http.UnsafeURLError):
        _validate(url, "93.184.216.34")
