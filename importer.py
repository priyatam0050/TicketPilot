import requests
from schema import TicketIn
from pydantic import ValidationError
import os
from dotenv import load_dotenv

load_dotenv()

API_URL=os.getenv("API_URL")
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
     result=[]
     if len(data)==0:
         print("Nothing to Import")
     else:
            for i in data:
                ticket={}
                try:
                    validticket=TicketIn(title=i["title"],priority="P"+str((i["id"])%4+1))
                    ticket["title"]=validticket.title
                    ticket["priority"]=validticket.priority
                    result.append(ticket)
                    
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
