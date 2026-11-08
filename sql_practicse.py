import sqlite3
connection=sqlite3.connect("ticketpilot.db")
cursor=connection.cursor()

cursor.execute("UPDATE ticket SET category = 'Unclassified' WHERE category IS NULL;")
print(cursor.rowcount)
connection.commit()
connection.close()