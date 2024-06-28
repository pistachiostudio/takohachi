import sqlite3

# データベースへの接続
conn = sqlite3.connect("data/takohachi.db")
cur = conn.cursor()

# すべてのレコードを削除する
cur.execute("DELETE FROM val_puuids")

# 変更をコミット
conn.commit()
conn.close()

print("すべてのレコードが削除されました。")
