"""Google スプレッドシート(gspread)のクライアント。

サービスアカウントの鍵(JSON)は環境変数 CLIENT_SECRET から直接読み込み、
ファイルとしてディスクに書き出さない。
"""

import functools
import json
import os

import gspread


@functools.cache
def get_client() -> gspread.Client:
    """認証済みのクライアントを返す。認証は初回だけ行い、以降は使い回す。"""
    return gspread.service_account_from_dict(json.loads(os.environ["CLIENT_SECRET"]))


def open_first_sheet(key: str) -> gspread.Worksheet:
    """key のスプレッドシートのシート1を開く。"""
    return get_client().open_by_key(key).sheet1
