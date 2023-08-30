import sqlite3

conn = sqlite3.connect('data/takohachi.db')
cursor = conn.cursor()

# yesterday_win と yesterday_lose の値を0に更新
update_query = "UPDATE val_puuids SET yesterday_win = 0, yesterday_lose = 0"
cursor.execute(update_query)

conn.commit()
conn.close()
