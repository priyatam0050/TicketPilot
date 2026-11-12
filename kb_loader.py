from pathlib import Path

kb_folder=Path(__file__).parent/"KB"


def load_articles():
    kb_folder_list=(sorted(kb_folder.glob("*.md")))
    kb_articles=[]
    
    for i in kb_folder_list:
        article={}
        text=i.read_text(encoding="utf-8")
        article["id"]=i.stem
        article["text"]=text
        lines = text.splitlines()
        article["title"]=lines[0].split("#")[1].strip()
        kb_articles.append(article)

   
    return kb_articles

if __name__=="__main__":
    kb_articles=load_articles()
  
    print(f"{len(kb_articles)} KB Articles loaded :\n")
    for i in kb_articles:
       
        print(f"{i["id"]} | {i["title"]}")
