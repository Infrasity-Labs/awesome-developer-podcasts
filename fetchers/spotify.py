import json
import os
import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Keywords to ensure the podcasts are actually developer or tech-related
DEV_KEYWORDS = ["developer", "software", "programming", "engineer", "code", "tech", "dev", "devrel", "saas", "developer marketing", "b2b", "gtm", "technical content marketing", "ops", "devops", "sre", "kubernetes", "docker", "infrastructure", "cloud", "aws", "azure", "gcp", "ai", "machine learning", "artificial intelligence", "data science", "neural", "security", "cybersecurity", "infosec", "hacking", "kotlin", "golang", "rust", "swift", "java", "python", "javascript", "js", "html", "css", "mobile", "ios", "android", "backend", "frontend", "web", "database", "systems"]

def get_spotify_token(client_id, client_secret):
    auth_url = "https://accounts.spotify.com/api/token"
    response = requests.post(auth_url, data={
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }, timeout=10)
    
    if response.status_code != 200:
        print(f"Error fetching Spotify token: {response.status_code} - {response.text}")
        return None
        
    return response.json().get("access_token")

def scrape_spotify_podcasts(token, query, category):
    results = []
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    search_url = "https://api.spotify.com/v1/search"
    all_shows = []
    
    # Spotify limit max is now 10, so fetch in loop to get more results
    for offset in range(0, 50, 10):
        params = {
            "q": query,
            "type": "show",
            "market": "US",
            "limit": 10,
            "offset": offset
        }
        
        try:
            response = requests.get(search_url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                shows = data.get("shows", {}).get("items", [])
                if not shows:
                    break
                all_shows.extend(shows)
            else:
                print(f"[{query}] Error from API: {response.status_code} - {response.text}")
                break
        except Exception as e:
            print(f"[{query}] Error fetching via API: {e}")
            break
            
    filtered_out = 0
    valid_keywords = DEV_KEYWORDS + [query.lower()]
    for show in all_shows:
        if not show:
            continue
            
        title = show.get("name") or ""
        description = show.get("description") or ""
        link = show.get("external_urls", {}).get("spotify", "")
        
        # Filter out completely unrelated podcasts
        title_lower = title.lower()
        desc_lower = description.lower()
        
        matched = False
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
        
    print(f"[{query}] API returned {len(all_shows)} shows. Filtered out {filtered_out}. Kept {len(results)}.")
    return results

def main():
    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("ERROR: SPOTIFY_CLIENT_ID or SPOTIFY_CLIENT_SECRET environment variables are missing.")
        print("Please provide them in the .env file or as environment variables.")
        return
        
    token = get_spotify_token(client_id, client_secret)
    if not token:
        return
        
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
            podcasts = scrape_spotify_podcasts(token, q, category)
            print(f"Fetched {len(podcasts)} podcasts for '{q}' via Spotify API")
            all_podcasts.extend(podcasts)
            
    # Write to spotify.json
    os.makedirs('data', exist_ok=True)
    with open('data/spotify.json', "w", encoding="utf-8") as f:
        json.dump(all_podcasts, f, indent=4)
        
    print(f"Saved {len(all_podcasts)} podcasts to spotify.json")

if __name__ == "__main__":
    main()
