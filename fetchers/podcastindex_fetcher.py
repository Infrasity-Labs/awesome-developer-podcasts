import json
import os
import podcastindex
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  

try:
    from fetchers.config import DEV_KEYWORDS
except ModuleNotFoundError:
    from config import DEV_KEYWORDS

def scrape_podcasts(index, query, category):
    results = []
    try:
        response = index.search(query)
        if response and str(response.get("status")).lower() == "true":
            feeds = response.get("feeds", [])
            total_feeds = len(feeds)
            filtered_out = 0
            
            for feed in feeds:
                title = feed.get("title") or ""
                description = feed.get("description") or ""
                # Create a link back to podcastindex.org using the feed ID
                feed_id = feed.get("id")
                link = f"https://podcastindex.org/podcast/{feed_id}" if feed_id else feed.get("url", "")
                
                # Filter out completely unrelated podcasts
                title_lower = title.lower()
                desc_lower = description.lower()
                
                matched = False
                # Relax the filter: If the search query itself is in the text, or any of the dev keywords, keep it!
                valid_keywords = DEV_KEYWORDS + [query.lower()]
                for kw in valid_keywords:
                    if kw in title_lower or kw in desc_lower:
                        matched = True
                        break
                        
                if not matched:
                    filtered_out += 1
                    continue
                
                # Prepend category to the description
                description = f"**[{category}]** {description}"
                
                results.append({
                    "title": title,
                    "description": description,
                    "link": link
                })
                
            print(f"[{query}] API returned {total_feeds} feeds. Filtered out {filtered_out}. Kept {len(results)}.")
        else:
            print(f"[{query}] Warning: Unexpected API response or status not 'true': {response}")
            
    except Exception as e:
        print(f"[{query}] Error fetching via API: {e}")
    return results

def main():
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    api_key = os.environ.get("PODCASTINDEX_API_KEY")
    api_secret = os.environ.get("PODCASTINDEX_API_SECRET")
    
    if not api_key or not api_secret:
        print("ERROR: PODCASTINDEX_API_KEY or PODCASTINDEX_API_SECRET environment variables are missing.")
        print("Please sign up at https://api.podcastindex.org/ to get your keys.")
        return
        
    config = {
        "api_key": api_key,
        "api_secret": api_secret
    }
    index = podcastindex.init(config)
    
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
            podcasts = scrape_podcasts(index, q, category)
            print(f"Fetched {len(podcasts)} podcasts for '{q}' via API")
            all_podcasts.extend(podcasts)
            
    # Write to podcastindex.json
    os.makedirs('data', exist_ok=True)
    with open('data/podcastindex.json', "w") as f:
        json.dump(all_podcasts, f, indent=4)
        
    print(f"Saved {len(all_podcasts)} podcasts to podcastindex.json")

if __name__ == "__main__":
    main()