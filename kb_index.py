from kb_loader import load_articles
import os
from dotenv import load_dotenv
from google import genai
import chromadb
from pathlib import Path


load_dotenv()
EMBED_MODEL=os.getenv("EMBED_MODEL")
client=genai.Client()

def chunk_articles():
    articles=load_articles()
    chunks=[]
    for i in articles:
        text=i["text"].split("\n## ")
        count=1
        for k in text[1:]:
            chunk_art={}
            chunk_art["kb_id"]=i["id"]
            chunk_art["title"]=i["title"]
            chunk_art["id"]=i["id"]+"-"+str(count)
            chunk_art["text"]=i["title"]+"\n"+k.strip()
            count+=1
            chunks.append(chunk_art)
    
    return chunks
def embed_text(content,tasks):
     result=client.models.embed_content(model=EMBED_MODEL,contents=content,config={"task_type":tasks}).embeddings
     embedding=[]
     for j in result:
        embedding.append(j.values)
     return embedding
def similarity(a,b):
    total=0
    for i,j in zip(a,b):
        total+=i*j
    return total


def build_index():
    chunks=chunk_articles()
    texts=[]
    ids=[]
    metadatas=[]
    for i in chunks:
        ids.append(i["id"])
        texts.append(i["text"])
        meta_data={
            "kb_id":i["kb_id"],
            "title":i["title"]
        }
        metadatas.append(meta_data)

    vectors=embed_text(texts,"RETRIEVAL_DOCUMENT")

    ch=chromadb.PersistentClient(path=str(Path(__file__).parent/"chroma_db"))
    collection=ch.get_or_create_collection(name="kb_chunks")
    collection.upsert(ids=ids,documents=texts,embeddings=vectors,metadatas=metadatas)
    print(collection.count())


    
if __name__=="__main__":
    build_index()
    
""" k=["wifi not working","unable to connect to wifi","printer paper jam","I can't get online"]
    result=embed_text(k,"SEMANTIC_SIMILARITY")
    print(len(result))
    print(len(result[0]))
    print(result[0][:5])
    print(f"{k[1]} vs {k[2]} {similarity(result[1],result[2])}") 
    print(f"{k[0]} vs {k[1]} {similarity(result[0],result[1])}")
    print(f"{k[0]} vs {k[2]} {similarity(result[0],result[2])}")
    print(f"{k[2]} vs {k[3]} {similarity(result[2],result[3])}")
    print(f"{k[0]} vs {k[3]} {similarity(result[0],result[3])}") """

