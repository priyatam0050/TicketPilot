import asyncio,time,httpx

def normal():
    start=time.perf_counter()
    response=httpx.get("https://jsonplaceholder.typicode.com/posts")
    print(len(response.json()))
    
    response=httpx.get("https://jsonplaceholder.typicode.com/users")
    print(len(response.json()))
   
    response=httpx.get("https://jsonplaceholder.typicode.com/comments")
    print(len(response.json()))
    
    print(f"{time.perf_counter()-start:.2f} Seconds")


async def fetch_value(url):
    async with httpx.AsyncClient() as client:
        response=await client.get(url)
    print(len(response.json()))
async def trigger():
     start=time.perf_counter()
     result=await asyncio.gather(
     fetch_value("https://jsonplaceholder.typicode.com/posts"),
     fetch_value("https://jsonplaceholder.typicode.com/users"),
     fetch_value("https://jsonplaceholder.typicode.com/comments"),
    )
     print(f"{time.perf_counter()- start:.2f} seconds")
    
    
if __name__=="__main__":
    normal()
    asyncio.run(trigger())
