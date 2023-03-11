import sqlite3

# delete db record
dbname = "takohachi.db"
con = sqlite3.connect('./data/takohachi.db')
cur = con.cursor() 
cur.execute("DELETE FROM currency WHERE user_id = '978537379923099668'")
con.commit()

