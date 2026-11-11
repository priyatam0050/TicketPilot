from pathlib import Path
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

class Ticket:
    Allowed_priority=["P1","P2","P3","P4"]

    def __init__(self,number,title,priority="P4",status="Open",category="",reason=""):
        self.number=number
        self.title=title
        self.priority=priority
        self.status=status
        self.category=category
        self.reason=reason

    @property
    def priority(self):
        return self._priority

    @priority.setter
    def priority(self,value):
        if value.upper() not in self.Allowed_priority:
            raise ValueError(f"priorities must be in {",".join(self.Allowed_priority)}")
        self._priority=value.upper()
        
    def close(self):
        if self.status=="Closed":
            print(self.number+" is already closed")
        else:
            self.status="Closed"
            print(self.number+" is closed")
    def __str__(self):
        return (f"{self.number} | {self.title} | {self.priority} | {self.status} | {self.category}")
    
class TicketStore:

    Inc_def="INC0000001"

    def __init__(self):
        connection=sqlite3.connect(Path(__file__).parent/(os.getenv("DB_NAME","ticketpilot.db")))
        cursor=connection.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS ticket(number TEXT PRIMARY KEY,title TEXT,priority TEXT,status TEXT,category Text,reason Text)""")
        connection.commit()

        self.connection=connection
         
    def showall(self):
        cursor=self.connection.cursor()
        cursor.execute("SELECT * from ticket order by number")
        ticket=cursor.fetchall()
        if len(ticket)==0:
            print("No Tickets found")
            return
        for i in ticket:
            
            ticket_instance=Ticket(i[0],i[1],i[2],i[3],i[4],i[5])
            print(ticket_instance)

    def filter_by_priority(self,p):
  
        cursor=self.connection.cursor()
        cursor.execute("select * from ticket where priority=? order by number",(p.upper(),))
        tickets=cursor.fetchall()
        if len(tickets)==0:
            print("No Tickets found for Priority "+p)
            return 
        for i in tickets:
            ticket_instance=Ticket(i[0],i[1],i[2],i[3],i[4],i[5])
            print(ticket_instance)

            
    def close(self,number):

        cursor=self.connection.cursor()
        cursor.execute("select status from ticket where number=?",(number,))
        ticket=cursor.fetchall()
        if len(ticket)==0:
            print(f"{number} NOT FOUND ")
            return 
        
        ticket_status=ticket[0][0]
        
        if ticket_status=="Closed":
            print(str(number)+" is already Closed")
            return 
        cursor.execute("UPDATE ticket SET status='Closed' where number=?",(number,))
        self.connection.commit()
        print(str(number) +" is Closed")

       
    
    def getinc(self):
        cursor=self.connection.cursor()
        cursor.execute("select count(*) from ticket")
        count=cursor.fetchall()[0][0]
       
        if count==0:
            return self.Inc_def
        cursor.execute("select max(number) from ticket")
        ticket=cursor.fetchall()
        
        inc1=ticket[0][0]
        
        inc1=int(inc1[3:])
        inc1+=1
        inc1=str(inc1)
        inc1=inc1.zfill(7)
        str1="INC"
        str1+=inc1
        return str1
    def quit(self):
        self.connection.close()
        return
        
    def create(self,title,priority,category="",reason=""):
        number=self.getinc()
        t=Ticket(number,title,priority,category=category,reason=reason)
        cursor=self.connection.cursor()
        cursor.execute("INSERT INTO ticket(number,title,priority,status,category,reason) VALUES(?,?,?,?,?,?)",(t.number,t.title,t.priority,t.status,t.category,t.reason))
        self.connection.commit()

        return number
    def report(self):
        cursor=self.connection.cursor()
        cursor.execute("select count(*) from ticket")
       
        count=cursor.fetchall()[0][0]
        if count==0:
            print("No Tickets to report")
            return

        cursor.execute("select priority,COUNT(*) from ticket GROUP BY priority ORDER BY priority")
        print("--- Tickets by priority ---")
        ticket=cursor.fetchall()
        for i in ticket:
            print(f"{i[0]} : {i[1]}")

        
        cursor.execute("select status,COUNT(*) from ticket GROUP BY status ORDER BY status")
        print("--- Tickets by Status ---")
        ticket=cursor.fetchall()
        for i in ticket:
            print(f"{i[0]} : {i[1]}")
        

        cursor.execute("select category,COUNT(*) from ticket GROUP BY category ORDER BY category")
        print("--- Tickets by Category ---")
        ticket=cursor.fetchall()
        for i in ticket:
            print(f"{i[0]} : {i[1]}")
        print("Total Tickets : "+str(count))

    def search(self,keyword):
        cursor=self.connection.cursor()
        keyword="%"+keyword+"%"
        cursor.execute("select * from ticket where title LIKE ? order by number",(keyword,))
        ticket=cursor.fetchall()
        if len(ticket)==0:
            print("No tickets Found with the given keyword")
            return
        for i in ticket:
            ticket_instance=Ticket(i[0],i[1],i[2],i[3],i[4],i[5])
            print(ticket_instance)
    def similar_tickets(self,keyword):
        cursor=self.connection.cursor()
        keyword="%"+keyword+"%"
        cursor.execute("SELECT * FROM TICKET WHERE TITLE LIKE ? AND STATUS = 'Open' ORDER BY NUMBER LIMIT 5",(keyword,))  
        tickets=cursor.fetchall()
        tic=[]
        for i in tickets:
            tic1={}
            tic1["number"]=i[0]
            tic1["title"]=i[1]
            tic1["priority"]=i[2]
            tic1["status"]=i[3]
            tic1["category"]=i[4]
            tic1["reason"]=i[5]
            tic.append(tic1)
        return tic
if __name__=="__main__":
    k= TicketStore()
    print(k.similar_tickets("ZZZZZ"))