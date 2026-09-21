"""
HTTPクライアント関連の共通処理を提供するモジュール
"""

import logging

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

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
    """共通のHTTPクライアント"""

    DEFAULT_TIMEOUT = 30.0
    DEFAULT_RETRY_ATTEMPTS = 3

    def __init__(self, base_url: str | None = None, headers: dict[str, str] | None = None):
        self.base_url = base_url
        self.headers = headers or {}

    @retry(
        stop=stop_after_attempt(DEFAULT_RETRY_ATTEMPTS),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def get(
        self,
        url: str,
        params: dict | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> dict:
        """GET リクエストを送信"""
        full_url = f"{self.base_url}{url}" if self.base_url else url
        request_headers = {**self.headers, **(headers or {})}
        timeout = timeout or self.DEFAULT_TIMEOUT

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    full_url, params=params, headers=request_headers, timeout=timeout
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
                raise APIError(
                    f"API request failed with status {e.response.status_code}",
                    status_code=e.response.status_code,
                    response=e.response.json() if e.response.text else None,
                )
            except httpx.TimeoutException as e:
                logger.error(f"Request timeout: {e}")
                raise APIError(f"Request timed out after {timeout} seconds")
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                raise APIError(f"Unexpected error occurred: {str(e)}")

    @retry(
        stop=stop_after_attempt(DEFAULT_RETRY_ATTEMPTS),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def post(
        self,
        url: str,
        json: dict | None = None,
        data: dict | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> dict:
        """POST リクエストを送信"""
        full_url = f"{self.base_url}{url}" if self.base_url else url
        request_headers = {**self.headers, **(headers or {})}
        timeout = timeout or self.DEFAULT_TIMEOUT

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    full_url, json=json, data=data, headers=request_headers, timeout=timeout
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
                raise APIError(
                    f"API request failed with status {e.response.status_code}",
                    status_code=e.response.status_code,
                    response=e.response.json() if e.response.text else None,
                )
            except httpx.TimeoutException as e:
                logger.error(f"Request timeout: {e}")
                raise APIError(f"Request timed out after {timeout} seconds")
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                raise APIError(f"Unexpected error occurred: {str(e)}")
