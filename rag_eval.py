from rag import search_kb,answer_question
import time
TESTS = [
    # =========================================================================
    # GROUP 1: CLEAR (14 tests - covering KB0001 to KB0020)
    # =========================================================================
    {
        "question": "my laptop keeps losing internet when I walk between desks or to a meeting room",
        "expected": "KB0003",  # Wi-Fi keeps dropping in the office
    },
    {
        "question": "got a client visiting tomorrow, how do I get them on our guest network?",
        "expected": "KB0004",  # Guest Wi-Fi for visitors
    },
    {
        "question": "what's the service desk phone extension and how many characters does my password need?",
        "expected": "KB0008",  # Password rules and expiry
    },
    {
        "question": "I typed my password wrong too many times and now it says I'm blocked from signing in",
        "expected": "KB0009",  # Account locked out (Close call vs KB0007/KB0010)
    },
    {
        "question": "I upgraded my iPhone over the weekend and now I can't approve my login prompts",
        "expected": "KB0002",  # Set up MFA on a new phone (Close call vs KB0007/KB0009)
    },
    {
        "question": "completely blanked on my login password, how do I reset it myself?",
        "expected": "KB0007",  # Reset a forgotten password (Close call vs KB0009/KB0010)
    },
    {
        "question": "I need permission to open the Finance shared folder on the network drive",
        "expected": "KB0011",  # Request shared drive access
    },
    {
        "question": "we have a new developer starting next Monday, how do I get their login and laptop provisioned?",
        "expected": "KB0012",  # New joiner account setup
    },
    {
        "question": "a contractor on my team is leaving this Friday, how do we revoke their access?",
        "expected": "KB0013",  # Access removal for leavers
    },
    {
        "question": "I pressed the power button on my laptop this morning and the screen stays completely black",
        "expected": "KB0014",  # Laptop won't turn on
    },
    {
        "question": "how do I connect my laptop to the 3rd floor color printer?",
        "expected": "KB0016",  # Add an office printer
    },
    {
        "question": "I plugged my laptop into the desk dock via USB-C and my external screen says no signal",
        "expected": "KB0017",  # Monitor not detected
    },
    {
        "question": "my trackpad is pushing up and the bottom of my laptop case looks curved or bulging",
        "expected": "KB0019",  # Swollen battery (safety)
    },
    {
        "question": "where do I download approved tools like Notepad++ or Postman without admin rights?",
        "expected": "KB0020",  # Install from the company software store
    },

    # =========================================================================
    # GROUP 2: VAGUE (3 tests - scoped to KB0001 to KB0020)
    # =========================================================================
    {
        "question": "vpn not working",
        "expected": "KB0001",  # Best fit: troubleshooting VPN connection failure (vs KB0002 first-time setup)
    },
    {
        "question": "printer broken",
        "expected": "KB0015",  # Best fit: Printer paper jam (vs KB0016 adding a printer)
    },
    {
        "question": "can't sign in",
        "expected": "KB0009",  # Best fit: Account locked out (close call with KB0007/KB0010)
    },

    # =========================================================================
    # GROUP 3: NOT IN THE KB (3 tests)
    # =========================================================================
    {
        "question": "how do I claim travel expenses and cab receipts from my client visit?",
        "expected": None,
    },
    {
        "question": "how many days of casual or sick leave do I have left this year?",
        "expected": None,
    },
    {
        "question": "my office parking badge isn't opening the basement boom barrier",
        "expected": None,
    },
]
if __name__=="__main__":
   counter=0
   retrieval_ok=0
   answer_ok=0
   refusal_ok=0
   total_unanswer=0
   total_answer=0
   for i in TESTS:
      question=i["question"]
      expecetd=i["expected"]
      result_kb_id=[]
      result=search_kb(question)
      answer=answer_question(question)
      
      for j in result:
         result_kb_id.append(j["kb_id"])
      if expecetd is None:
         total_unanswer+=1
         if len(answer["sources"])==0:
            refusal_ok+=1
            time.sleep(3)
            continue
         else:
            print(f"MISS : {question} , Expected : {expecetd} , AI ANSWER : {answer["answer"]}")
            time.sleep(3)
            continue
      else:
        total_answer+=1
         
      
      if expecetd in result_kb_id:
         retrieval_ok+=1
      else:
         print(f"MISS : {question} , Expected : {expecetd} , AI ANSWER : {answer["answer"]}")
         time.sleep(3)
         continue
         
      if expecetd in answer["sources"]:
         answer_ok+=1
      else:
         print(f"MISS : {question} , Expected : {expecetd} , AI ANSWER : {answer["answer"]}")
      
      time.sleep(3)
   print(f"Retrieval : {retrieval_ok}/{total_answer} \n Answers : {answer_ok}/{total_answer} \n Refusals : {refusal_ok}/{total_unanswer}")

