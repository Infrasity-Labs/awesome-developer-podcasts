import json
import time
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

def scrape_podcasts(query):
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        # Navigate to search page
        url = f"https://podcastindex.org/search?q={query.replace(' ', '+')}"
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
        finally:
            browser.close()
    return results

def main():
    queries = ["GTM", "developer marketing", "technical content marketing"]
    all_podcasts = []
    
    for q in queries:
        print(f"Fetching podcasts for '{q}'...")
        podcasts = scrape_podcasts(q)
        all_podcasts.extend(podcasts)
        
    # Write to podcastindex.json
    with open("podcastindex.json", "w") as f:
        json.dump(all_podcasts, f, indent=4)
        
    print(f"Saved {len(all_podcasts)} podcasts to podcastindex.json")

if __name__ == "__main__":
    main()
