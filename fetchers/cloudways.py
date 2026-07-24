import json
import re
from bs4 import BeautifulSoup
from retry import get_with_backoff

def fetch_cloudways_podcasts():
    # Use archive.org to bypass Cloudflare protection
    url = "http://web.archive.org/web/20230601000000/https://www.cloudways.com/blog/best-coding-podcasts/"
    
    response = get_with_backoff(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    
    podcasts = []
    
    # Categories to skip
    skip_categories = [
        "Podcasts for Beginners & Code Newbies",
        "How to Choose the Right Coding Podcast",
        "Conclusion",
        "Frequently Asked Questions",
        "Why You Should Listen to Podcasts",
        "This website uses cookies"
    ]
    
    skip_mode = False
    current_category = "Software Engineering & Development"
    
    # Cloudways uses H3 for podcast titles, and H2 for categories.
    for element in soup.find_all(['h2', 'h3']):
        text = element.get_text(strip=True)
        if not text:
            continue
            
        if element.name == 'h2':
            if any(skip_cat.lower() in text.lower() for skip_cat in skip_categories):
                skip_mode = True
            else:
                skip_mode = False
                
        elif element.name == 'h3':
            if skip_mode:
                continue
                
            title = text
            title = re.sub(r'^\d+\.\s*', '', title)
            
            desc_text = ""
            link = ""
            
            # Often the link is embedded directly in the h3 title tag
            h3_a_tag = element.find('a')
            if h3_a_tag:
                href = h3_a_tag.get('href', '')
                if "/web/" in href:
                    m = re.search(r'/web/\d+/(.*)', href)
                    if m:
                        link = m.group(1)
                elif href.startswith('http'):
                    link = href
            
            next_node = element.find_next_sibling()
            while next_node and next_node.name not in ['h2', 'h3']:
                if next_node.name == 'p':
                    a_tag = next_node.find('a')
                    if a_tag and not link:
                        href = a_tag.get('href', '')
                        if "/web/" in href:
                            m = re.search(r'/web/\d+/(.*)', href)
                            if m:
                                link = m.group(1)
                        elif href.startswith('http'):
                            link = href
                    desc_text += " " + next_node.get_text(strip=True)
                next_node = next_node.find_next_sibling()
                
            if title and desc_text and link:
                description = f"**[{current_category}]** {desc_text.strip()}"
                
                podcasts.append({
                    'title': title,
                    'description': description,
                    'link': link
                })

    return podcasts

def main():
    print("Fetching Cloudways podcasts via Archive.org...")
    try:
        podcasts = fetch_cloudways_podcasts()
    except Exception as e:
        print(f"Failed to fetch or parse: {e}")
        podcasts = []
        
    import os
    os.makedirs('data', exist_ok=True)
    with open('data/cloudways.json', 'w') as f:
        json.dump(podcasts, f, indent=4)
        
    print(f"Saved {len(podcasts)} podcasts to cloudways.json")

if __name__ == "__main__":
    main()
