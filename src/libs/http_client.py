"""
HTTPクライアント関連の共通処理を提供するモジュール
"""

import logging

import httpx
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class APIError(Exception):
    """API関連のエラーの基底クラス"""

    def __init__(
        self, message: str, status_code: int | None = None, response: dict | None = None
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class HTTPClient:
    """共通のHTTPクライアント

    失敗はすべて APIError に変換して返す。ここでは再試行しない
    (一時障害の再試行が必要な呼び出し側は retry_transient を使う)。
    """

    DEFAULT_TIMEOUT = 30.0

    def __init__(self, base_url: str | None = None, headers: dict[str, str] | None = None):
        self.base_url = base_url
        self.headers = headers or {}

    async def get(
        self,
        url: str,
        params: dict | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> dict:
        """GET リクエストを送信"""
        return await self._request("GET", url, headers, timeout, params=params)

    async def post(
        self,
        url: str,
        json: dict | None = None,
        data: dict | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> dict:
        """POST リクエストを送信"""
        return await self._request("POST", url, headers, timeout, json=json, data=data)

    async def _request(
        self,
        method: str,
        url: str,
        headers: dict[str, str] | None,
        timeout: float | None,
        **kwargs,
    ) -> dict:
        full_url = f"{self.base_url}{url}" if self.base_url else url
        request_headers = {**self.headers, **(headers or {})}
        timeout = timeout or self.DEFAULT_TIMEOUT

        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method, full_url, headers=request_headers, timeout=timeout, **kwargs
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                status = e.response.status_code
                logger.error("HTTP error occurred: %s - %s", status, e.response.text[:1000])
                raise APIError(
                    f"API request failed with status {status}",
                    status_code=status,
                    response=_json_or_none(e.response),
                ) from e
            except httpx.TimeoutException as e:
                logger.error("Request timeout: %s", e)
                raise APIError(f"Request timed out after {timeout} seconds") from e
            except Exception as e:
                logger.error("Unexpected error: %s", e)
                raise APIError(f"Unexpected error occurred: {e}") from e


def _json_or_none(response: httpx.Response) -> dict | None:
    """エラー応答の本文がJSONならdictで、そうでなければNoneを返す。"""
    try:
        return response.json()
    except ValueError:
        return None


# 一時的な障害として再試行するHTTPステータス(レート制限・過負荷・一時利用不可)
TRANSIENT_STATUS_CODES = {429, 503, 529}


def _is_transient(error: BaseException) -> bool:
    return isinstance(error, APIError) and error.status_code in TRANSIENT_STATUS_CODES


# 一時障害(TRANSIENT_STATUS_CODES)のときだけ、指数バックオフで最大3回まで再試行するデコレータ。
retry_transient = retry(
    retry=retry_if_exception(_is_transient),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
)
