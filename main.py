
from models import TicketStore
store=TicketStore()
flag=True

pr=["P1","P2","P3","P4"]
while(flag):
   
    print("Choose any of the below Option")

    print("1. Create")

    print("2. view list")

    print("3. filter by priority")

    print("4. Close")

    print("5. Quit")
    
    in1=input()

    if in1=="1":
        print("To Create a Incident we need few details :")
        print("Please enter Title")
        title=input().strip()
        while title=='':
            print("Please enter a valid Title")
            title=input().strip()
                
        print("Please enter Priority of the ticket")
        while True:
            try:
                priority=(input()).upper()
                number=store.create(title,priority)
                print(number+" Created Succesfully")
                break
            except ValueError:
                print("Please Enter Valid priority from below list")
                for i in pr:
                    print(i)

    elif in1=="2":
       store.showall()

    elif in1=="3":
        print("Enter priorty whcih you want to filter by")
        filter_priority=(input())
        store.filter_by_priority(filter_priority)

    elif in1=="4":
       print("Please Enter the Ticket Number you want to Close")
       ticket=input().strip().upper()
       store.close(ticket)

    elif in1=="5":
        flag=False
    
    else:
        print("Invalid Input Please choose only from Given Options")

    