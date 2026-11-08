
from models import TicketStore
from importer import get_tickets_from_api
store=TicketStore()
flag=True
from llm import classify_tickets

pr=["P1","P2","P3","P4"]
while(flag):
   
    print("Choose any of the below Option")

    print("1. Create")

    print("2. view list")

    print("3. filter by priority")

    print("4. Close")

    print("5. Import From API")

    print("6. Report")

    print("7. Search")

    print("8. Quit")
    
    in1=input()

    if in1=="1":
        print("To Create a Incident we need few details :")
        print("Please enter Title")
        title=input().strip()
        while title=='':
            print("Please enter a valid Title")
            title=input().strip()
        print("ASKING AI ...")
        result_ai=classify_tickets(title)
        if result_ai is None:
            print("AI unavailable, default priority P4")
            ai_category="Unclassified"
            ai_priority="P4"
            ai_reason="AI Unavailable"
        else:
            ai_category=result_ai.category
            ai_priority=result_ai.priority
            ai_reason=result_ai.reason
            print(f"AI Suggests Category = {result_ai.category}, Priority = {result_ai.priority} , Reason = {result_ai.reason}")
        

        while True:
            try:
                print("Please enter to accept AI Priority or Type P1-P4 to Overide")
                priority=(input()).upper().strip()
                if priority=='':
                    number=store.create(title,ai_priority,ai_category,ai_reason)
                else:
                     number=store.create(title,priority,ai_category,ai_reason)
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
        ticket=get_tickets_from_api()
        count=0
        if len(ticket)>0:
            for i in ticket:
                title=i["title"]
                priority=i["priority"]
                category=i["category"]
                reason=i["reason"]
                try:
                    number=store.create(title,priority,category,reason)
                    count+=1
                except ValueError as e:
                    print(f"Ticket Creation skipped Beacuse of {e}")
            print(str(count)+" Ticket's created successfully")

    elif in1=='6':
        store.report()
    
    elif in1=='7':
         print("Please enter keyword you want to search")
         title=input().strip()
         while title=='':
            print("Please enter a valid keyword")
            title=input().strip()
         store.search(title)

    elif in1=="8":
        store.quit()
        flag=False
        
    else:
        print("Invalid Input Please choose only from Given Options")

    