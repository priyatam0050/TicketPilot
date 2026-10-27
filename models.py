import csv
from pathlib import Path
class Ticket:
    Allowed_priority={"P1","P2","P3","P4"}

    def __init__(self,number,title,priority="P4",status="Open"):
        self.number=number
        self.title=title
        self.priority=priority
        self.status=status


    @property
    def priority(self):
        return self._priority

    @priority.setter
    def priority(self,value):
        if value.upper() not in self.Allowed_priority:
            raise ValueError(f"priorities must be in {self.Allowed_priority}")
        self._priority=value.upper()
        
    def close(self):
        if self.status=="Closed":
            print(self.number+" is already closed")
        else:
            self.status="Closed"
            print(self.number+" is closed")
    def __str__(self):
        return (f"{self.number} | {self.title} | {self.priority} | {self.status}")
    
class TicketStore:

    columns=["Number","Title","Priority","Status"]
    file=Path(__file__).parent/"ticketdetails.csv"
    Inc_def="INC0000001"

    def __init__(self):
        self.tickets=[]
        if not self.file.exists() or self.file.stat().st_size==0:
            with open(self.file,"w",newline="") as f:
                writer=csv.DictWriter(f,fieldnames=self.columns)
                writer.writeheader()
        else:
            with open(self.file,"r",newline="") as f:
                reader=csv.DictReader(f)
                for i in reader:
                    self.tickets.append(Ticket(i["Number"],i["Title"],i["Priority"],i["Status"]))

    def showall(self):
        if len(self.tickets)==0:
            print("No Tickets found")
            return
        for i in self.tickets:
            print(i)
    def filter_by_priority(self,p):
        Found=False
        for i in self.tickets:
            if i.priority.upper()==p.upper():
                Found=True
                print(i)
        if Found==False:
            print("No Tickets found for Priority "+p)
            
    def close(self,number):
        found=False
        for i in self.tickets:
            if i.number==number:
                found=True
                i.close()
                self.save()
                break
        if found==False:
            print(f"{number} NOT FOUND ")
    
    def getinc(self):
        if(len(self.tickets)==0):
            return self.Inc_def

        inc1=self.tickets[-1].number
        inc1=int(inc1[3:])
        inc1+=1
        inc1=str(inc1)
        inc1=inc1.zfill(7)
        str1="INC"
        str1+=inc1
        return str1
    def create(self,title,priority):
        number=self.getinc()
        t=Ticket(number,title,priority)
        self.tickets.append(t)
        self.save()
        return number



            
               
    def save(self):
        with open(self.file,"w",newline="") as f:
            writer=csv.DictWriter(f,fieldnames=self.columns)
            writer.writeheader()
            for i in self.tickets:
                writer.writerow({"Number":i.number,"Title":i.title,"Priority":i.priority,"Status":i.status})
    
