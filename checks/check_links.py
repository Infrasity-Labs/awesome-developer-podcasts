import json
import glob
import asyncio
import aiohttp
import time
import os
import re

def get_known_links(readme_path="README.md"):
    if not os.path.exists(readme_path):
        return set()
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()
    # Extract links in markdown format
    links = re.findall(r'\[.*?\]\((https?://[^\s)]+)\)', content)
    return set(links)

async def check_link(session, url, sem):
    if not url:
        return False
    async with sem:
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            timeout = aiohttp.ClientTimeout(total=10)
            async with session.head(url, timeout=timeout, allow_redirects=True, headers=headers) as response:
                if response.status < 400:
                    return True
                # If HEAD fails or gives Forbidden/Method Not Allowed, try GET
                if response.status in (405, 403, 429):
                    async with session.get(url, timeout=timeout, allow_redirects=True, headers=headers) as get_resp:
                        return get_resp.status < 400
                return False
        except Exception as e:
            return False

async def process_file(filepath, session, sem, known_links):
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            podcasts = json.load(f)
        except json.JSONDecodeError:
            print(f"Failed to parse {filepath}")
            return
            
    if not podcasts:
        return
        
    valid_podcasts = []
    tasks = []
    podcasts_to_check = []
    
    for p in podcasts:
        url = p.get('link', '')
        if not url:
            continue
            
        if url in known_links:
            valid_podcasts.append(p)
        else:
            podcasts_to_check.append(p)
            tasks.append(check_link(session, url, sem))
            
    print(f"{filepath}: Skipped checking {len(valid_podcasts)} already known links. Checking {len(podcasts_to_check)} new links...")
    
    if tasks:
        results = await asyncio.gather(*tasks)
        for p, is_valid in zip(podcasts_to_check, results):
            if is_valid:
                valid_podcasts.append(p)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(valid_podcasts, f, indent=4)
        
    print(f"{filepath}: Kept {len(valid_podcasts)} out of {len(podcasts)} podcasts.")

async def main():
    known_links = get_known_links()
    files = glob.glob("data/*.json")
    # Limit concurrent requests to 20 to avoid getting rate-limited
    sem = asyncio.Semaphore(20) 
    
    connector = aiohttp.TCPConnector(limit=20)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [process_file(f, session, sem, known_links) for f in files]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    print(f"Link checking completed in {time.time() - start:.2f} seconds.")
