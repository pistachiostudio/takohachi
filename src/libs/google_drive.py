"""Google Drive へのファイルアップロード。

サービスアカウントは Drive の保存容量を持たないため、アップロードは
自分の Google アカウントの OAuth(リフレッシュトークン)で行う。
リフレッシュトークンは scripts/get_drive_refresh_token.py で取得する。
"""

import json
import logging
import os
import uuid

import httpx

from libs.http_client import HTTPClient

logger = logging.getLogger(__name__)

TOKEN_URL = "https://oauth2.googleapis.com/token"
UPLOAD_URL = "https://www.googleapis.com/upload/drive/v3/files"


async def get_access_token() -> str:
    """リフレッシュトークンからアクセストークンを取得する。"""
    res = await HTTPClient().post(
        TOKEN_URL,
        data={
            "client_id": os.environ["DRIVE_OAUTH_CLIENT_ID"],
            "client_secret": os.environ["DRIVE_OAUTH_CLIENT_SECRET"],
            "refresh_token": os.environ["DRIVE_OAUTH_REFRESH_TOKEN"],
            "grant_type": "refresh_token",
        },
    )
    return res["access_token"]


async def upload_file(name: str, content: bytes, mime_type: str, folder_id: str) -> dict:
    """content を folder_id のフォルダに name で保存し、作成されたファイルの情報を返す。"""
    access_token = await get_access_token()

    # メタデータと本体を1リクエストで送る multipart/related 形式
    boundary = uuid.uuid4().hex
    metadata = json.dumps({"name": name, "parents": [folder_id]})
    body = (
        (
            f"--{boundary}\r\n"
            "Content-Type: application/json; charset=UTF-8\r\n\r\n"
            f"{metadata}\r\n"
            f"--{boundary}\r\n"
            f"Content-Type: {mime_type}\r\n\r\n"
        ).encode()
        + content
        + f"\r\n--{boundary}--\r\n".encode()
    )

    async with httpx.AsyncClient() as client:
        response = await client.post(
            UPLOAD_URL,
            params={"uploadType": "multipart"},
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": f"multipart/related; boundary={boundary}",
            },
            content=body,
            timeout=60,
        )
    if response.is_error:
        logger.error("Drive upload failed: %s - %s", response.status_code, response.text)
    response.raise_for_status()
    return response.json()
