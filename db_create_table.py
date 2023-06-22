import sqlite3

# データベースに接続
conn = sqlite3.connect('data/takohachi.db')

# カーソルを取得
cur = conn.cursor()

# 新しいテーブルを作成
cur.execute('''
    CREATE TABLE val_puuids (
        puuid TEXT,
        region TEXT,
        name TEXT,
        tag TEXT,
        yesterday_elo INTEGER
    )
''')

# 変更をコミット
conn.commit()

# データベースとの接続を閉じる
conn.close()
