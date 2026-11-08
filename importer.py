import requests
from schema import TicketIn
from pydantic import ValidationError
import os
from dotenv import load_dotenv
from llm import classify_tickets
import time

load_dotenv()

API_URL=os.getenv("API_URL","https://jsonplaceholder.typicode.com/posts")
LIMIT=int(os.getenv("IMPORT_LIMIT",20))
def fetch_posts():
    response=requests.get(API_URL)
    status_code=response.status_code
    if status_code!=200:
        print(f"API Failed with the code : {status_code}")
        return []
    else:

        return response.json()
    
def get_tickets_from_api():
     data=fetch_posts()
     data=data[:LIMIT]
     result=[]
     if len(data)==0:
         print("Nothing to Import")
     else:
            count=0
            for i in data:
                ticket={}
                try:
                    validticket=TicketIn(title=i["title"],priority="P"+str((i["id"])%4+1))
                    ticket["title"]=validticket.title
                    result_ai=classify_tickets(validticket.title)
                    if result_ai is None:
                        ticket["priority"]=validticket.priority
                        ticket["category"]="Unclassified"
                        ticket["reason"]="AI Unavailable"
                    else:
                        ticket["priority"]=result_ai.priority
                        ticket["category"]=result_ai.category
                        ticket["reason"]=result_ai.reason

                    result.append(ticket)
                    count+=1
                    print(f"Classifying : {count}/{len(data)}")
                    time.sleep(2)
                    
                except ValidationError as e:
                     print(e)
     return result
          
         

if __name__=="__main__":
    data=get_tickets_from_api()
    if len((data))==0:
        print("No Data Recieved")   
    else:
        for i in data:
            print(i)
