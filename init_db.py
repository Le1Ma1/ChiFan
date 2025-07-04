import sqlite3

DB_PATH = 'chifan.db'
SQL_PATH = 'app/migrations/001_init.sql'

with open(SQL_PATH, 'r', encoding='utf-8') as f:
    sql = f.read()

conn = sqlite3.connect(DB_PATH)
conn.executescript(sql)
conn.close()

print('✅ 資料庫初始化完成，chifan.db 已建立必要表格！')
