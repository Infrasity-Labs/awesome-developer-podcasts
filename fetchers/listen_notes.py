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

# Developer/tech keywords mapped to their respective categories (one request per keyword).
DEV_KEYWORDS = [
    ("developer", "Software Engineering & Development"),
    ("software", "Software Engineering & Development"),
    ("programming", "Software Engineering & Development"),
    ("engineer", "Software Engineering & Development"),
    ("code", "Software Engineering & Development"),
    ("tech", "Software Engineering & Development"),
    ("dev", "Software Engineering & Development"),
    ("devrel", "Developer Marketing"),
    ("saas", "Software Engineering & Development"),
    ("developer marketing", "Developer Marketing"),
    ("b2b", "GTM"),
    ("gtm", "GTM"),
    ("technical content marketing", "Developer Marketing"),
    ("ops", "DevOps & Infrastructure"),
    ("devops", "DevOps & Infrastructure"),
    ("sre", "DevOps & Infrastructure"),
    ("kubernetes", "DevOps & Infrastructure"),
    ("docker", "DevOps & Infrastructure"),
    ("infrastructure", "DevOps & Infrastructure"),
    ("cloud", "Cloud Computing"),
    ("aws", "Cloud Computing"),
    ("azure", "Cloud Computing"),
    ("gcp", "Cloud Computing"),
    ("ai", "Machine Learning & AI"),
    ("machine learning", "Machine Learning & AI"),
    ("artificial intelligence", "Machine Learning & AI"),
    ("data science", "Machine Learning & AI"),
    ("neural", "Machine Learning & AI"),
    ("security", "Security & Privacy"),
    ("cybersecurity", "Security & Privacy"),
    ("infosec", "Security & Privacy"),
    ("hacking", "Security & Privacy"),
    ("kotlin", "Mobile Development"),
    ("golang", "Programming Languages"),
    ("rust", "Programming Languages"),
    ("swift", "Mobile Development"),
    ("java", "Programming Languages"),
    ("python", "Programming Languages"),
    ("javascript", "Programming Languages"),
    ("js", "Programming Languages"),
    ("html", "Web Development"),
    ("css", "Web Development"),
    ("mobile", "Mobile Development"),
    ("ios", "Mobile Development"),
    ("android", "Mobile Development"),
    ("backend", "Backend & Systems"),
    ("frontend", "Web Development"),
    ("web", "Web Development"),
    ("database", "Backend & Systems"),
    ("systems", "Backend & Systems")
]

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
            for show in shows:
                description = show.get("description_original") or ""
                results.append({
                    "title": show.get("title_original") or "",
                    "description": f"**[{category}]** {description}",
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

    # Load existing podcasts to aggregate over time. Note: in CI this file is
    # not persisted between runs (data/ is gitignored, artifacts expire), so this
    # merge only accumulates across repeated local runs.
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

    # Rotate which keywords we search each day so that, over several days, the
    # whole list gets covered while never firing more than MAX_REQUESTS_PER_DAY
    # requests in a single run. The slice wraps around the end of the list.
    day_of_year = datetime.date.today().timetuple().tm_yday
    start = (day_of_year * MAX_REQUESTS_PER_DAY) % len(DEV_KEYWORDS)
    rotated = DEV_KEYWORDS[start:] + DEV_KEYWORDS[:start]
    todays_keywords = rotated[:MAX_REQUESTS_PER_DAY]
    print(f"Day {day_of_year}: querying {[k[0] for k in todays_keywords]}")

    for query, category in todays_keywords:
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
