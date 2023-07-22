import sqlite3

puuid_input = input("削除するPUUIDを入力してください。")

conn = sqlite3.connect("data/takohachi.db")

cur = conn.cursor()

cur.execute(
    """
    DELETE FROM val_puuids
    WHERE puuid = ?
""",
    (puuid_input,),
)

conn.commit()
conn.close()

print("done!")
