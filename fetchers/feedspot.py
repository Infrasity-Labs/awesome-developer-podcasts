import requests
from bs4 import BeautifulSoup
import json

def fetch_feedspot_podcasts():
    url = "https://podcast.feedspot.com/programming_podcasts/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    
    podcasts = []
    
    # Each podcast is listed with an h3 tag of class 'feed_heading'
    for h3 in soup.find_all('h3', class_='feed_heading'):
        # The title usually starts with a number like "1. ", so we clean it up
        title_text = h3.get_text(strip=True)
        title = title_text.split('.', 1)[-1].strip()
        
        # The details are in the next p tag with class 'trow'
        container = h3.find_next_sibling('p', class_='trow')
        if not container:
            continue
            
        # Description
        desc_span = container.find('span', class_='feed_desc')
        description = desc_span.get_text(strip=True) if desc_span else ""
        if description.endswith("MORE"):
            description = description[:-4].strip()
            
        # Link (Usually an Apple Podcasts link or external link)
        link = ""
        link_tag = container.find('a', class_='eng--item')
        if link_tag and 'href' in link_tag.attrs:
            link = link_tag['href']
            
        podcasts.append({
            'title': title,
            'description': description,
            'link': link
        })
        
    return podcasts

if __name__ == "__main__":
    podcasts = fetch_feedspot_podcasts()
    with open('data/feedspot.json', 'w') as f:
        json.dump(podcasts, f, indent=4)
    print(f"Saved {len(podcasts)} podcasts to feedspot.json")
