from bs4 import BeautifulSoup
import json
from retry import get_with_backoff

try:
    from fetchers.utils.user_agents import get_random_user_agent
except ModuleNotFoundError:
    from utils.user_agents import get_random_user_agent

def fetch_podcasts():
    url = "https://transistor.fm/dev-podcasts/"
    headers = {"User-Agent": get_random_user_agent()}
    response = get_with_backoff(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')

    podcasts = []
    
    # Find all divs with class 'site-content'
    for content_div in soup.find_all('div', class_='site-content'):
        h2 = content_div.find('h2')
        if h2:
            title = h2.get_text(strip=True)
            # The next paragraphs contain description and link
            paragraphs = content_div.find_all('p')
            if paragraphs:
                description = paragraphs[0].get_text(strip=True)
                
                link = ""
                # Look for a link in the second paragraph
                if len(paragraphs) > 1:
                    a_tag = paragraphs[1].find('a')
                    if a_tag:
                        link = a_tag['href']
                        
                podcasts.append({
                    'title': title,
                    'description': description,
                    'link': link
                })
                
    return podcasts

if __name__ == "__main__":
    podcasts = fetch_podcasts()
    import os
    os.makedirs('data', exist_ok=True)
    with open('data/transistor.json', 'w') as f:
        json.dump(podcasts, f, indent=4)
    print(f"Saved {len(podcasts)} podcasts to transistor.json")