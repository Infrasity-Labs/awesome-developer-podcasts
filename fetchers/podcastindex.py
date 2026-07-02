import json
import time
import urllib.parse
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# Keywords to ensure the podcasts are actually developer or tech-related
DEV_KEYWORDS = ["developer", "software", "programming", "engineer", "code", "tech", "dev", "devrel", "saas", "developer marketing", "b2b", "gtm", "technical content marketing", "developer", "software", "programming", "engineer", "code", "tech", "dev", "devrel", "saas", "developer marketing", "b2b", "gtm", "technical content marketing", "ops", "devops", "sre", "kubernetes", "docker", "infrastructure", "cloud", "aws", "azure", "gcp", "ai", "machine learning", "artificial intelligence", "data science", "neural", "security", "cybersecurity", "infosec", "hacking", "kotlin", "golang", "rust", "swift", "java", "python", "javascript", "js", "html", "css", "mobile", "ios", "android", "backend", "frontend", "web", "database", "systems"]

def scrape_podcasts(page, query, category):
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
                description = f"**[{category}]** {description}"
                
                results.append({
                    "title": title,
                    "description": description,
                    "link": link
                })
    except Exception as e:
        print(f"Error scraping {query}: {e}")
    return results

def main():
    search_map = {
        "Software Engineering & Development": ["software engineering", "programming", "coding", "software architecture"],
        "Web Development": ["web development", "frontend", "reactjs", "javascript developer", "html css"],
        "Backend & Systems": ["backend developer", "distributed systems", "microservices"],
        "Programming Languages": ["python programming", "golang", "rust programming", "java developer", "c++ programming"],
        "Mobile Development": ["iOS development", "android development", "swift ui", "kotlin"],
        "DevOps & Infrastructure": ["DevOps", "site reliability", "kubernetes", "docker", "infrastructure as code"],
        "Cloud Computing": ["cloud computing", "AWS developer", "azure developer", "google cloud platform"],
        "Machine Learning & AI": ["machine learning", "artificial intelligence", "data science", "neural networks"],
        "Security & Privacy": ["cybersecurity", "infosec", "ethical hacking"],
        "GTM": ["GTM", "go to market strategy tech"],
        "Developer Marketing": ["developer marketing", "technical content marketing", "devrel", "developer relations"]
    }
    
    all_podcasts = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        for category, queries in search_map.items():
            for q in queries:
                print(f"Fetching podcasts for '{q}'...")
                podcasts = scrape_podcasts(page, q, category)
                all_podcasts.extend(podcasts)
        browser.close()
        
    # Write to podcastindex.json
    import os
    os.makedirs('data', exist_ok=True)
    with open('data/podcastindex.json', "w") as f:
        json.dump(all_podcasts, f, indent=4)
        
    print(f"Saved {len(all_podcasts)} podcasts to podcastindex.json")

if __name__ == "__main__":
    main()