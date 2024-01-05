import sqlite3

# create database
con = sqlite3.connect("./takohachi.db")
cur = con.cursor()
cur.execute("CREATE TABLE currency(user_id text, user_name text, bonus text, money int)")
con.close()
