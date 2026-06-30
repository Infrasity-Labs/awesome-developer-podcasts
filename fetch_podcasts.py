import requests
from bs4 import BeautifulSoup

def fetch_podcasts():
    url = "https://transistor.fm/dev-podcasts/"
    response = requests.get(url, timeout=10)
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
                        link = a_tag.get('href', '')
                        
                podcasts.append({
                    'title': title,
                    'description': description,
                    'link': link
                })
                
    return podcasts

if __name__ == "__main__":
    podcasts = fetch_podcasts()
    print(f"Found {len(podcasts)} podcasts:")
    for podcast in podcasts:
        print(f"\nTitle: {podcast['title']}")
        print(f"Description: {podcast['description']}")
        print(f"Link: {podcast['link']}")
