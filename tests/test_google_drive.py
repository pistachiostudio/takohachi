import asyncio
import json
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from libs import google_drive


@pytest.fixture(autouse=True)
def _keys(monkeypatch):
    monkeypatch.setenv("DRIVE_OAUTH_CLIENT_ID", "test-client-id")
    monkeypatch.setenv("DRIVE_OAUTH_CLIENT_SECRET", "test-client-secret")
    monkeypatch.setenv("DRIVE_OAUTH_REFRESH_TOKEN", "test-refresh-token")


def _upload(handler):
    """トークン取得をモックし、アップロードのリクエストを handler で受けて upload_file を実行する。"""
    real_client = httpx.AsyncClient
    token = AsyncMock(return_value={"access_token": "test-access-token"})
    with (
        patch("libs.google_drive.HTTPClient.post", new=token),
        patch(
            "libs.google_drive.httpx.AsyncClient",
            new=lambda: real_client(transport=httpx.MockTransport(handler)),
        ),
    ):
        result = asyncio.run(
            google_drive.upload_file("cat.png", b"\x89PNG", "image/png", "folder-123")
        )
    return result, token


def test_upload_file_sends_metadata_and_content():
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(200, json={"id": "file-1", "name": "cat.png"})

    result, token = _upload(handler)

    assert result == {"id": "file-1", "name": "cat.png"}
    # リフレッシュトークンでアクセストークンを取得している
    assert token.call_args.kwargs["data"] == {
        "client_id": "test-client-id",
        "client_secret": "test-client-secret",
        "refresh_token": "test-refresh-token",
        "grant_type": "refresh_token",
    }

    request = requests[0]
    assert request.url.params["uploadType"] == "multipart"
    assert request.headers["Authorization"] == "Bearer test-access-token"
    boundary = request.headers["Content-Type"].split("boundary=")[1]
    parts = request.content.split(f"--{boundary}".encode())
    # [前置き, メタデータ, 本体, 終端]
    metadata = json.loads(parts[1].split(b"\r\n\r\n", 1)[1])
    assert metadata == {"name": "cat.png", "parents": ["folder-123"]}
    assert parts[2] == b"\r\nContent-Type: image/png\r\n\r\n\x89PNG\r\n"


def test_upload_file_raises_on_error():
    def handler(request):
        return httpx.Response(403, json={"error": {"message": "forbidden"}})

    with pytest.raises(httpx.HTTPStatusError):
        _upload(handler)
