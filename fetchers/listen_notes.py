import json
import os
import requests
import time
import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Listen Notes FREE plan allows 300 requests/month.
# Thus, we run 10/day to keep us within budget, given we make run the script once a day/
MAX_REQUESTS_PER_DAY = 10

DEV_KEYWORDS = ["developer", "software", "programming", "engineer", "code", "tech", "dev", "devrel", "saas", "developer marketing", "b2b", "gtm", "technical content marketing", "ops", "devops", "sre", "kubernetes", "docker", "infrastructure", "cloud", "aws", "azure", "gcp", "ai", "machine learning", "artificial intelligence", "data science", "neural", "security", "cybersecurity", "infosec", "hacking", "kotlin", "golang", "rust", "swift", "java", "python", "javascript", "js", "html", "css", "mobile", "ios", "android", "backend", "frontend", "web", "database", "systems"]

def scrape_listennotes_podcasts(api_key, query, category):
    results = []
    search_url = "https://listen-api.listennotes.com/api/v2/search"

    params = {
        "q": query,
        "type": "podcast",
        "page_size": 10
    }
    headers = {"X-ListenAPI-Key": api_key}

    try:
        response = requests.get(search_url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            shows = response.json().get("results", [])
            filtered_out = 0
            valid_keywords = DEV_KEYWORDS + [query.lower()]

            for show in shows:
                title = show.get("title_original") or ""
                description = show.get("description_original") or ""
                link = show.get("listennotes_url") or ""

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

                results.append({
                    "title": title,
                    "description": f"**[{category}]** {description}",
                    "link": link
                })

            print(f"[{query}] API returned {len(shows)} shows. Filtered out {filtered_out}. Kept {len(results)}.")
        else:
            print(f"[{query}] Error from API: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"[{query}] Error fetching via API: {e}")

    return results

def main():
    api_key = os.environ.get("LISTENNOTES_API_KEY")
    if not api_key:
        print("ERROR: LISTENNOTES_API_KEY environment variable is missing.")
        print("Please sign up at https://www.listennotes.com/api/ to get your key.")
        return

    # Load existing podcasts to aggregate over time.
    filepath = 'data/listennotes.json'
    podcast_map = {}
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for p in json.load(f):
                    title = p.get("title")
                    if title:
                        podcast_map[title] = p
        except Exception as e:
            print(f"Warning: Could not load existing podcasts: {e}")

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

    # rotate which slice we search each day so the whole map gets covered over several days while never firing
    # more than MAX_REQUESTS_PER_DAY requests in a single run. The slice wraps around.
    all_queries = [(q, category) for category, queries in search_map.items() for q in queries]
    day_of_year = datetime.date.today().timetuple().tm_yday
    start = (day_of_year * MAX_REQUESTS_PER_DAY) % len(all_queries)
    rotated = all_queries[start:] + all_queries[:start]
    todays_queries = rotated[:MAX_REQUESTS_PER_DAY]
    print(f"Day {day_of_year}: querying {[q for q, _cat in todays_queries]}")

    for query, category in todays_queries:
        podcasts = scrape_listennotes_podcasts(api_key, query, category)
        print(f"Fetched {len(podcasts)} podcasts for '{query}' via Listen Notes API")
        for p in podcasts:
            title = p.get("title")
            if title:
                podcast_map[title] = p
        time.sleep(2)

    os.makedirs('data', exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(list(podcast_map.values()), f, indent=4)

    print(f"Saved {len(podcast_map)} podcasts to listennotes.json")

if __name__ == "__main__":
    main()
