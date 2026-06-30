import json
import time
import urllib.parse
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# Keywords to ensure the podcasts are actually developer or tech-related
DEV_KEYWORDS = ["developer", "software", "programming", "engineer", "code", "tech", "dev", "devrel", "saas", "developer marketing", "b2b", "gtm", "technical content marketing"]

def scrape_podcasts(page, query):
    results = []
    url = f"https://podcastindex.org/search?q={urllib.parse.quote_plus(query)}"
    try:
        page.goto(url)
        page.wait_for_selector(".result", timeout=10000)
        time.sleep(2) # Give a moment for all results to render
        
        html = page.content()
        soup = BeautifulSoup(html, "html.parser")
        
        for item in soup.find_all("div", class_="result"):
            title_elem = item.find("div", class_="result-title")
            desc_elem = item.find("p", class_="result-description")
            
            if title_elem and title_elem.a:
                title = title_elem.get_text(strip=True)
                # Extract the absolute link
                link = "https://podcastindex.org" + title_elem.a["href"]
                description = desc_elem.get_text(strip=True) if desc_elem else ""
                
                # Filter out completely unrelated podcasts (e.g., chiropractic, detailing, etc.)
                title_lower = title.lower()
                desc_lower = description.lower()
                if not any(kw in title_lower or kw in desc_lower for kw in DEV_KEYWORDS):
                    continue
                
                # Prepend category to the description so it categorizes them visually
                # since update_readme.py expects just title, description, link
                description = f"**[{query.upper()}]** {description}"
                
                results.append({
                    "title": title,
                    "description": description,
                    "link": link
                })
    except Exception as e:
        print(f"Error scraping {query}: {e}")
    return results

def main():
    queries = ["GTM", "developer marketing", "technical content marketing"]
    all_podcasts = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        for q in queries:
            print(f"Fetching podcasts for '{q}'...")
            podcasts = scrape_podcasts(page, q)
            all_podcasts.extend(podcasts)
        browser.close()
        
    # Write to podcastindex.json
    with open("podcastindex.json", "w") as f:
        json.dump(all_podcasts, f, indent=4)
        
    print(f"Saved {len(all_podcasts)} podcasts to podcastindex.json")

if __name__ == "__main__":
    main()