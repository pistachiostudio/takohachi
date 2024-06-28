import sqlite3

# データベースに接続
conn = sqlite3.connect("data/takohachi.db")

# カーソルを取得
cur = conn.cursor()

# 新しいカラムを追加
cur.execute(
    """
    ALTER TABLE val_puuids
    ADD COLUMN d_uid INTEGER
    """
)


# "yesterday_win"と"yesterday_lose"のカラムに0を設定
# cur.execute(
#    """
#    UPDATE val_puuids
#    SET yesterday_win = 0,
#        yesterday_lose = 0
#    """
# )


# 変更をコミット
conn.commit()

# データベースとの接続を閉じる
conn.close()
