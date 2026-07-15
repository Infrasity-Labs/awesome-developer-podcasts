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

# Developer/tech keywords used as search queries (one request per keyword).
DEV_KEYWORDS = ["developer", "software", "programming", "engineer", "code", "tech", "dev", "devrel", "saas", "developer marketing", "b2b", "gtm", "technical content marketing", "ops", "devops", "sre", "kubernetes", "docker", "infrastructure", "cloud", "aws", "azure", "gcp", "ai", "machine learning", "artificial intelligence", "data science", "neural", "security", "cybersecurity", "infosec", "hacking", "kotlin", "golang", "rust", "swift", "java", "python", "javascript", "js", "html", "css", "mobile", "ios", "android", "backend", "frontend", "web", "database", "systems"]

def scrape_listennotes_podcasts(api_key, query):
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
            for show in shows:
                results.append({
                    "title": show.get("title_original") or "",
                    "description": show.get("description_original") or "",
                    "link": show.get("listennotes_url") or ""
                })
            print(f"[{query}] Kept {len(results)} podcasts.")
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

    all_podcasts = []

    # Rotate which keywords we search each day so that, over several days, the
    # whole list gets covered while never firing more than MAX_REQUESTS_PER_DAY
    # requests in a single run. The slice wraps around the end of the list.
    day_of_year = datetime.date.today().timetuple().tm_yday
    start = (day_of_year * MAX_REQUESTS_PER_DAY) % len(DEV_KEYWORDS)
    rotated = DEV_KEYWORDS[start:] + DEV_KEYWORDS[:start]
    todays_keywords = rotated[:MAX_REQUESTS_PER_DAY]
    print(f"Day {day_of_year}: querying {todays_keywords}")

    for query in todays_keywords:
        podcasts = scrape_listennotes_podcasts(api_key, query)
        print(f"Fetched {len(podcasts)} podcasts for '{query}' via Listen Notes API")
        all_podcasts.extend(podcasts)
        time.sleep(2)

    # Write to listennotes.json
    os.makedirs('data', exist_ok=True)
    with open('data/listennotes.json', "w", encoding="utf-8") as f:
        json.dump(all_podcasts, f, indent=4)

    print(f"Saved {len(all_podcasts)} podcasts to listennotes.json")

if __name__ == "__main__":
    main()
