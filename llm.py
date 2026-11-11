import os
import time
from dotenv import load_dotenv
from google import genai
from schema import TicketClassification
from pydantic import ValidationError
from models import TicketStore
import json
load_dotenv()
name=os.getenv("GEMINI_MODEL")
ticket=TicketStore()
client=genai.Client()
SIMILAR_TOOL={

     "type":"function",
     "name":"similar_tickets",
     "description":"find open tickets whose title contains only one keyword use it to spot dupicates or many users hit by the same issue and also Copy the word exactly as it is spelled in the ticket title, e.g. wifi, not Wi-Fi.",
     "parameters":{
         "type":"object",
         "required":["keyword"],
         "properties":{
             "keyword":{
                 "type":"string",
                 "description": "one keyword from the ticket, e.g. VPN,outlook"
             }
         }
     },
}
SYSTEM_INSTRUCTION = """
You are an IT service desk analyst who classifies incident tickets.

CATEGORIES (use only these):
- Network: VPN, Wi-Fi, internet, DNS, firewall, connectivity
- Access: accounts, permissions, passwords, SSO, MFA, onboarding and offboarding, security alerts on accounts
- Hardware: laptops, printers, monitors, physical devices
- Software: applications, servers, databases, pipelines, payment systems
- Email: Outlook mailboxes, email signatures, distribution lists, bounces, quotas, spam filters

CATEGORY RULES (check in this order):
1. If a physical part is broken, swollen or jamming, it is Hardware.
2. If connectivity drops (Wi-Fi, VPN, DNS, firewall), it is Network, whatever app fails on top.
3. Login, SSO, MFA, credentials or permission denied (403) is Access, even inside Outlook, GitHub or AWS.
4. A running service that crashes, has bugs or database/code errors is Software.
5. Email is only for message delivery: bounces, quotas, distribution lists, spam filters, signatures.

PRIORITY:
- P1: many users or a whole team blocked, business-critical, or a safety hazard
- P2: a single user blocked, or a team partly affected
- P3: an issue with a workaround, or a request with a near deadline
- P4: a request or minor issue, no business impact

TOOLS:
-Before classifying, call similar_tickets with one key word from the ticket.
-If 3 or more open similar tickets exist, it’s likely an outage → P1.
-If an almost identical ticket exists, mention it as a possible duplicate in the reason (with its number).

EXAMPLES:
Ticket: Outlook won't open, MFA prompt never arrives on phone
Answer: Category : Access,Priority: P2

Ticket: Zoom cuts out whenever I enter Conference Room B
Answer: Category : Network,Priority: P3

Ticket: Git push rejected: Permission denied (publickey)
Answer: Category : Access,Priority: P3

Ticket: Campaign email bounces back with error 552: quota exceeded
Answer: Category : Email,Priority: P2


"""

tickets = {
    # Rule 1: Physical / Transit Layer First
    "Monitor flickering and disconnecting when the display cable is lightly bumped": [
        "Hardware",
        "P3",
    ],
    "Warehouse barcode scanner won't charge or turn on after dropping from forklift": [
        "Hardware",
        "P2",
    ],
    "Teams video feeds pixelated and lagging across all branch offices due to 40% packet loss": [
        "Network",
        "P1",
    ],
    "Cannot reach Jira or confluence servers; internal corporate DNS resolving to 0.0.0.0": [
        "Network",
        "P1",
    ],
    # Rule 2: Identity & Permissions Over Surface Apps
    "Okta push notifications failing with 'Device out of compliance' on user's new phone": [
        "Access",
        "P2",
    ],
    "Sales representative unable to view North America pipeline due to missing Salesforce role permission": [
        "Access",
        "P3",
    ],
    "Temporary contractor locked out of AWS production console after entering wrong passphrase 3 times": [
        "Access",
        "P2",
    ],
    # Rule 3: Application & Mail Separation
    "Inventory checkout endpoint throwing 502 Bad Gateway under peak traffic spike": [
        "Software",
        "P1",
    ],
    "Billing report generator crashing with 'NullPointerException' on records containing special characters": [
        "Software",
        "P3",
    ],
    "External vendor invoices quarantined by spam filter due to failed SPF and DKIM checks": [
        "Email",
        "P2",
    ],
    "All emails to engineering-leads distribution list bouncing back with 'User unknown' error": [
        "Email",
        "P3",
    ],
}
def summarize_ticket(title):
    prompt="You are an IT service desk analyst. Summarise this ticket in one short line: "
    title=prompt+title
    interaction=client.interactions.create(model=name,input=title)
    return interaction.output_text

def classify_tickets(title):
    wait=2
    for i in range(3):
        try:
            interaction=client.interactions.create(model=name,system_instruction=SYSTEM_INSTRUCTION,input=title,response_format={"type": "text", "mime_type": "application/json", "schema": TicketClassification.model_json_schema()})
            result=interaction.output_text
            ai_result=TicketClassification.model_validate_json(result)
            return ai_result
        except ValidationError:
             print(result)
             return None
        except Exception as e:
            print(f"AI error .... Retrying in {wait}s...")
            time.sleep(wait)
            wait=wait*2
    print("AI Unavailable after 3 tries")
    return None
def classify_tickets_with_tools(title):

    wait=2
    for i in range(3):
        try:
            flag_tool=False
            #print("Classifying...")
            interaction=client.interactions.create(model=name,system_instruction=SYSTEM_INSTRUCTION,input=title,tools=[SIMILAR_TOOL])
            for i in interaction.steps:
                if i.type=="function_call":
                    if i.name=="similar_tickets":
                        flag_tool=True
                        sim_ticket=json.dumps(ticket.similar_tickets(i.arguments["keyword"]))
                        tool_reply=[{
                            "type": "function_result",
                            "name": i.name,
                            "call_id": i.id,
                            "result":  [{"type": "text", "text": sim_ticket}]
                        }]
                        print(f"Checking similar tickets with the keyword : "+i.arguments["keyword"])
                        final=client.interactions.create(model=name,system_instruction=SYSTEM_INSTRUCTION,previous_interaction_id=interaction.id,input=tool_reply,response_format={"type": "text", "mime_type": "application/json", "schema": TicketClassification.model_json_schema()})
                        result=final.output_text
                        ai_result=TicketClassification.model_validate_json(result)
                        return ai_result
            if flag_tool==False:
                    interaction=client.interactions.create(model=name,system_instruction=SYSTEM_INSTRUCTION,input=title,response_format={"type": "text", "mime_type": "application/json", "schema": TicketClassification.model_json_schema()})
                    result=interaction.output_text
                    ai_result=TicketClassification.model_validate_json(result)
                    return ai_result
        except ValidationError:
            return None
        except Exception as e:
            print(f"AI error .... Retrying in {wait}s...")
            time.sleep(wait)
            wait=wait*2
    print("AI Unavailable after 3 tries")
    return None

                
        

       

if __name__=="__main__":
    count=0
    print(classify_tickets_with_tools("wifi  issue"))
    """
    for i in tickets:
        #sum_title=summarize_ticket(i)
        result=classify_tickets(i)
        if result is None:
            print("Invalid Reply")
            time.sleep(2) 
            continue
        if result.category==tickets[i][0] and result.priority==tickets[i][1]:
            count+=1
        else:
            print(f"{i}\nExpected Result : {tickets[i][0]} | {tickets[i][1]}\nAI Result : {result.category}| {result.priority}\nReason:{result.reason}")  
        time.sleep(2) 
        
    print(f"Accuracy : {count}/{len(tickets)}")"""
        
        
