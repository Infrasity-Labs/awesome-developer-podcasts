import json
import os


def save_podcasts(filename, podcasts):
    os.makedirs("data", exist_ok=True)

    path = os.path.join("data", filename)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(podcasts, f, indent=4)

    print(f"Saved {len(podcasts)} podcasts to {filename}")
