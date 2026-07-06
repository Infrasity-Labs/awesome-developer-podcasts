import json
import os
import podcastindex

# Keywords to ensure the podcasts are actually developer or tech-related
DEV_KEYWORDS = ["developer", "software", "programming", "engineer", "code", "tech", "dev", "devrel", "saas", "developer marketing", "b2b", "gtm", "technical content marketing", "ops", "devops", "sre", "kubernetes", "docker", "infrastructure", "cloud", "aws", "azure", "gcp", "ai", "machine learning", "artificial intelligence", "data science", "neural", "security", "cybersecurity", "infosec", "hacking", "kotlin", "golang", "rust", "swift", "java", "python", "javascript", "js", "html", "css", "mobile", "ios", "android", "backend", "frontend", "web", "database", "systems"]

def scrape_podcasts(index, query, category):
    results = []
    try:
        response = index.search(query)
        if response and response.get("status") == "true":
            feeds = response.get("feeds", [])
            for feed in feeds:
                title = feed.get("title", "")
                description = feed.get("description", "")
                # Create a link back to podcastindex.org using the feed ID
                feed_id = feed.get("id")
                link = f"https://podcastindex.org/podcast/{feed_id}" if feed_id else feed.get("url", "")
                
                # Filter out completely unrelated podcasts
                title_lower = title.lower()
                desc_lower = description.lower()
                if not any(kw in title_lower or kw in desc_lower for kw in DEV_KEYWORDS):
                    continue
                
                # Prepend category to the description
                description = f"**[{category}]** {description}"
                
                results.append({
                    "title": title,
                    "description": description,
                    "link": link
                })
    except Exception as e:
        print(f"Error fetching '{query}' via API: {e}")
    return results

def main():
    api_key = os.environ.get("PODCASTINDEX_API_KEY")
    api_secret = os.environ.get("PODCASTINDEX_API_SECRET")
    
    if not api_key or not api_secret:
        print("ERROR: PODCASTINDEX_API_KEY or PODCASTINDEX_API_SECRET environment variables are missing.")
        print("Please sign up at https://api.podcastindex.org/ to get your keys.")
        exit(1)
        
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
            print(f"Fetching podcasts for '{q}' via API...")
            podcasts = scrape_podcasts(index, q, category)
            all_podcasts.extend(podcasts)
            
    # Write to podcastindex.json
    os.makedirs('data', exist_ok=True)
    with open('data/podcastindex.json', "w") as f:
        json.dump(all_podcasts, f, indent=4)
        
    print(f"Saved {len(all_podcasts)} podcasts to podcastindex.json")

if __name__ == "__main__":
    main()