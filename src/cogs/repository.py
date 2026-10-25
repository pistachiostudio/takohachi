import functools
import os
import time

import gspread

from libs import google_sheets

DIC_KEY = os.environ["DIC_KEY"]

# 一覧(オートコンプリート・あいまい検索用)のキャッシュ期間。追加した項目が反映されるまでの最大遅延。
ROWS_CACHE_TTL_SECONDS = 300

# select() が返す列
RESULT_COLUMNS = ["response", "title", "description", "right_small_image_URL", "big_image_URL"]
# あいまい検索の手がかりとして list_entries() が返す列
ENTRY_COLUMNS = ["trigger", "alias01", "alias02", "title", "description"]
# select() で検索対象にする列(この順で探す)
TRIGGER_COLUMNS = ["trigger", "alias01", "alias02"]


class TriggerRepository:
    def __init__(self, gc: gspread.Client):
        # 共有設定したスプレッドシートのtriggerシートを開く
        self.worksheet = gc.open_by_key(DIC_KEY).worksheet("trigger")

        # ヘッダー行をスプレッドシートから取得
        self.header_list: list[str] = self.worksheet.row_values(2)

        self._rows_cache: list[list[str]] | None = None
        self._rows_cached_at = 0.0

    def select(self, trigger: str) -> dict[str, str] | None:
        """trigger(または別名)に一致する行を、RESULT_COLUMNS の辞書で返します。"""
        row_num = self._find_trigger_row_number(trigger)
        if not row_num:
            return None
        return self._pick(self.worksheet.row_values(row_num), RESULT_COLUMNS)

    def list_triggers(self) -> list[str]:
        """登録されている trigger の値を一覧で返します(空文字は除く)。"""
        return [e["trigger"] for e in self.list_entries()]

    def list_entries(self) -> list[dict[str, str]]:
        """あいまい検索の手がかりとして、登録済みの各項目を ENTRY_COLUMNS の辞書で返します。
        (trigger が空の行は除く)
        """
        if "trigger" not in self.header_list:
            return []
        entries = (self._pick(row, ENTRY_COLUMNS) for row in self._get_rows())
        return [e for e in entries if e["trigger"]]

    def _pick(self, row: list[str], columns: list[str]) -> dict[str, str]:
        """行から指定した列の値を取り出す。ヘッダーにない列や、値が足りない列は空文字にする。"""
        values = dict(zip(self.header_list, row))
        return {name: values.get(name, "") for name in columns}

    def _get_rows(self) -> list[list[str]]:
        """データ行(3行目以降)を返します。Sheets APIの呼び出しを減らすため一定時間キャッシュします。"""
        now = time.monotonic()
        if self._rows_cache is None or now - self._rows_cached_at >= ROWS_CACHE_TTL_SECONDS:
            self._rows_cache = self.worksheet.get_all_values()[2:]
            self._rows_cached_at = now
        return self._rows_cache

    def _find_trigger_row_number(self, trigger: str) -> int | None:
        """trigger が含まれている行番号を返します。"""
        for column in TRIGGER_COLUMNS:
            if column not in self.header_list:
                continue
            # gspread の find(in_column=...) は 1-based のためインデックスを +1 する
            cell = self.worksheet.find(
                trigger, in_column=self.header_list.index(column) + 1, case_sensitive=False
            )
            if cell:
                return cell.row
        return None


@functools.cache
def get_trigger_repository() -> TriggerRepository:
    """/dic と gakigo で同じリポジトリ(シートへの接続・キャッシュ)を共有する。"""
    return TriggerRepository(google_sheets.get_client())
