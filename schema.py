from pydantic import BaseModel,ValidationError,field_validator
from typing import Literal
ALLOWED_PRIORITIES=["P1","P2","P3","P4"]
ALLOWED_CATEGORIES=["Network","Access","Hardware","Software","Email"]

class TicketClassification(BaseModel):
    category:Literal["Network","Access","Hardware","Software","Email"]
    priority:Literal["P1","P2","P3","P4"]
    reason:str
    


class TicketIn(BaseModel):
    title:str
    priority:str
    @field_validator("title")
    @classmethod
    def title_check(cls,value):
        value=value.strip()
        if value=="":
            raise ValueError("Title Cannot be empty")
        else:
            return value
    @field_validator("priority")
    @classmethod
    def priority_check(cls,value):
        value=(value.upper()).strip()
        if value not in ALLOWED_PRIORITIES:
            raise ValueError("Priority must be in [P1,P2,P3,P4]")
        else:
            return value
if __name__=="__main__":
    print(TicketClassification.model_json_schema())
    """try:
        ticket=TicketIn(title="",priority="p2")
        print(ticket)
    except ValidationError as e:
        print(e)""" 
    

