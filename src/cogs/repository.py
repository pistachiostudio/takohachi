import os
from pathlib import Path
from typing import Dict, List, Optional

import gspread
from oauth2client.service_account import ServiceAccountCredentials

DIC_KEY = os.environ["DIC_KEY"]


class TriggerRepository:
    def __init__(self, addssl_json_keyfile: Path):
        # 2つのAPIを記述しないとリフレッシュトークンを3600秒毎に発行し続けなければならないです！
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        # 認証情報設定
        credentials = ServiceAccountCredentials.from_json_keyfile_name(addssl_json_keyfile, scope)
        # OAuth2の資格情報を使用してGoogle APIにログインします。
        self.gc = gspread.authorize(credentials)
        # 共有設定したスプレッドシートのtriggerシートを開く
        self.worksheet = self.gc.open_by_key(DIC_KEY).worksheet("trigger")

        # ヘッダー行をスプレッドシートから取得
        self.header_list: List[str] = self.worksheet.row_values(2)

    def select(self, trigger: str) -> Optional[Dict[str, str]]:
        # trigger 文字列が含まれる列番号を取得
        row_num = self._find_trigger_row_number(trigger, self.header_list)

        if not row_num:
            return None
        else:
            # トリガー行データをスプレッドシートから取得
            trigger_value_list: List[str] = self.worksheet.row_values(row_num)
            pad_len = len(self.header_list) - len(trigger_value_list)
            pad_list = ["" for _ in range(pad_len)]
            trigger_value_list.extend(pad_list)

            # 取得対象のカラム名リスト
            colomn_names = [
                "response",
                "title",
                "description",
                "right_small_image_URL",
                "big_image_URL",
            ]

            # 返却値を格納する辞書
            embed_dict: Dict[str, str] = {}

            for col_name in colomn_names:
                col_index = self._get_index(self.header_list, col_name)
                if col_index is None:
                    value = ""
                else:
                    value = trigger_value_list[col_index]
                embed_dict[col_name] = value

            return embed_dict

    def list_triggers(self) -> List[str]:
        """登録されている trigger の値を一覧で返します。
        Returns:
            List[str]: 登録済みキーワードの一覧(空文字は除く)
        """
        col_index = self._get_index(self.header_list, "trigger")
        if col_index is None:
            return []

        all_values = self.worksheet.get_all_values()
        return [row[col_index] for row in all_values[2:] if col_index < len(row) and row[col_index]]

    def _get_index(self, target: List[str], value: str) -> Optional[int]:
        """value が target の何番目かを取得する関数です。value が存在しない場合は None を返します。
        Args:
            target (List[str]): index を調べたい対象のリスト
            value (str): index を取得する対象文字列
        Returns:
            Optional[int]: 存在すれば index(int) を返し、存在しなければ None を返します。
        """
        try:
            index = target.index(value)
            return index
        except ValueError:
            return None

    def _find_trigger_row_number(self, trigger: str, header_list: List[str]) -> Optional[int]:
        """triggerが含まれている行番号を返します
        Args:
            trigger (str): trigger
            header_list (List[str]): trigger db のヘッダーリスト
        Returns:
            Optional[int]: trigger が含まれている行番号
        """
        trigger_columns = ["trigger", "alias01", "alias02"]
        for trigger_column in trigger_columns:
            index = self._get_index(header_list, trigger_column)
            if index is None:
                # header_list に trigger_column が存在しない場合
                continue
            else:
                # gspread の find(in_column=...) は 1-based のためインデックスを +1 する
                trigger_cell = self.worksheet.find(trigger, in_column=index + 1, case_sensitive=False)
                if not trigger_cell:
                    # trigger column に trigger が存在しない場合
                    continue
                else:
                    return trigger_cell.row
