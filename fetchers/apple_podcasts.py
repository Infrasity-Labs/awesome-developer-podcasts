import json
import os
import requests
import time

try:
    from fetchers.config import DEV_KEYWORDS
except ModuleNotFoundError:
    from config import DEV_KEYWORDS

def scrape_apple_podcasts(query, category):
    results = []
    search_url = "https://itunes.apple.com/search"
    
    # We can fetch up to 200 items per request in iTunes Search API
    params = {
        "term": query,
        "entity": "podcast",
        "limit": 50
    }
    
    try:
        response = requests.get(search_url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            shows = data.get("results", [])
            filtered_out = 0
            valid_keywords = DEV_KEYWORDS + [query.lower()]
            
            for show in shows:
                title = show.get("collectionName") or ""
                artist = show.get("artistName") or ""
                link = show.get("collectionViewUrl") or show.get("trackViewUrl") or ""
                
                # iTunes Search API typically doesn't return full podcast descriptions.
                # We'll use artistName and genres as extra context for filtering.
                genres = " ".join(show.get("genres", []))
                
                title_lower = title.lower()
                extra_lower = (artist + " " + genres).lower()
                
                matched = False
                for kw in valid_keywords:
                    if kw in title_lower or kw in extra_lower:
                        matched = True
                        break
                        
                if not matched:
                    filtered_out += 1
                    continue
                
                # Create a pseudo-description since iTunes search doesn't provide it directly
                description = f"**[{category}]** Podcast by {artist}. Genres: {', '.join(show.get('genres', []))}"
                
                results.append({
                    "title": title,
                    "description": description,
                    "link": link
                })
                
            print(f"[{query}] API returned {len(shows)} shows. Filtered out {filtered_out}. Kept {len(results)}.")
        else:
            print(f"[{query}] Error from API: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"[{query}] Error fetching via API: {e}")
        
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
    
    for category, queries in search_map.items():
        for q in queries:
            podcasts = scrape_apple_podcasts(q, category)
            print(f"Fetched {len(podcasts)} podcasts for '{q}' via Apple Podcasts API")
            all_podcasts.extend(podcasts)
            time.sleep(2)
            
    # Write to apple_podcasts.json
    os.makedirs('data', exist_ok=True)
    with open('data/apple_podcasts.json', "w", encoding="utf-8") as f:
        json.dump(all_podcasts, f, indent=4)
        
    print(f"Saved {len(all_podcasts)} podcasts to apple_podcasts.json")

if __name__ == "__main__":
    main()
