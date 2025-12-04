import os
os.system('sqlite3 db/filmdb.db < sql/filmdb.sql')
print("数据库生成成功：filmdb.db")