from bs4 import BeautifulSoup
import json
import urllib.parse
from retry import get_with_backoff

def fetch_syntax_episodes():
    url = "https://syntax.fm"
    # Added a generic user agent just in case
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = get_with_backoff(url, headers=headers, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')

    episodes = []
    
    # Scrape the first 5 pages to get the 50 most recent episodes
    for page in range(1, 6):
        page_url = f"{url}/shows?page={page}"
        print(f"Fetching {page_url}...")
        
        response = get_with_backoff(page_url, headers=headers, timeout=10)
        if response.status_code != 200:
            break
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Each episode is an 'a' tag with href containing '/show/'
        for a_tag in soup.find_all('a'):
            href = a_tag.get('href', '')
            if '/show/' in href:
                title_tag = a_tag.find(class_='show-title')
                desc_tag = a_tag.find('p', class_='description')
                
                if title_tag and desc_tag:
                    title = title_tag.get_text(strip=True)
                    raw_desc = desc_tag.get_text(strip=True)
                    
                    # Cleanup trailing '#' sometimes left from UI elements
                    if raw_desc.endswith('#'):
                        raw_desc = raw_desc[:-1].strip()
                    
                    link = urllib.parse.urljoin(url, href)
                    
                    # Tag it explicitly so it falls under the existing vertical
                    description = f"**[Software Engineering & Development]** {raw_desc}"
                    
                    episodes.append({
                        'title': title,
                        'description': description,
                        'link': link
                    })
                
    # Remove duplicates if any (due to multiple links)
    unique_episodes = list({p['title']: p for p in episodes}.values())
    return unique_episodes

if __name__ == "__main__":
    episodes = fetch_syntax_episodes()
    import os
    os.makedirs('data', exist_ok=True)
    with open('data/syntax.json', 'w') as f:
        json.dump(episodes, f, indent=4)
    print(f"Saved {len(episodes)} episodes to syntax.json")
