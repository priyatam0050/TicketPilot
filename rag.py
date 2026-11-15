from kb_index import embed_text,get_Collection
from dotenv import load_dotenv
import os
from google import genai
import time

load_dotenv()
model=os.getenv("GEMINI_MODEL")
client =genai.Client()
RAG_INSTRUCTION="""
You are the IT helpdesk assistant for PVP Corp. Answer only using the articles provided below.
After each fact or step, cite the article in square brackets, like [KB0001].
If the articles don’t contain the answer, say you don’t know and suggest raising a ticket. Never guess.
Keep answers short. Use numbered steps where it helps."""

def answer_question(question):

    

    wait=2

    for k in range(3):

        try:
            chunks=search_kb(question)
            if not chunks:
                return {"answer":"KB index not built , Please come back after some time ","sources":[]}
            context=''
            sources=[]
            for i in chunks:
                context+="[" + i["kb_id"] + "]\n" + i["text"] + "\n\n"
                if i["kb_id"] not in sources:
                    sources.append(i["kb_id"])
            ai_input=context+" Question : "+question
            result=client.interactions.create(model=model,system_instruction=RAG_INSTRUCTION,input=ai_input)
            answer=result.output_text
            cited=[]
            for i in sources:
                if "[" + i + "]" in answer:
                    cited.append(i)


            return {"answer":result.output_text,"sources":(cited)}
        except Exception as e:
            print("AI Unavailable Retrying in "+str(wait)+" Seconds.....")
            time.sleep(wait)
            wait=wait*2
    return   {"answer":"AI Unavailable , Please come back after some time ","sources":[]}      




def search_kb(question,n=5):
    query_embedding=embed_text([question],"RETRIEVAL_QUERY")
    collection=get_Collection()
    if collection.count()==0:
        return []
    result=collection.query(query_embedding,n_results=n)
    docs  = result["documents"][0]
    metas = result["metadatas"][0]
    dists = result["distances"][0]  
    final=[]
    for doc,metadata,distance in zip(docs,metas,dists):
        res={}
        res["kb_id"]=metadata["kb_id"]
        res["title"]=metadata["title"]
        res["text"]=doc
        res["distance"]=distance
        final.append(res)
    return final

if __name__=="__main__":



    question=['my vpn shows error 809 at home','internet keeps cutting out in meeting rooms','how long before my password expires','how do I order a new monitor']
    for q in question:
        print("\n" + q)
        result=answer_question(q)
        if result:
            print(result["answer"])
            print(result["sources"])
        else:
            break

    
