import sqlite3
connection=sqlite3.connect("practisce.db")
cursor=connection.cursor()

command="""CREATE TABLE IF NOT EXISTS
ticket(number TEXT PRIMARY KEY,title TEXT,priority TEXT,status TEXT)"""
cursor.execute(command)


cursor.execute("select max(number) from ticket")

k=cursor.fetchall()
for i in k:
    print(i[0])
connection.commit()
connection.close()