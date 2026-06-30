import json
import glob

def update_readme():
    podcasts = {}
    
    # Read all JSON files produced by fetchers
    for filepath in glob.glob("*.json"):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                for item in data:
                    title = item.get('title', '').strip()
                    if title and title not in podcasts:
                        podcasts[title] = item
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            
    if not podcasts:
        print("No podcasts found in JSON files.")
        return
        
    # Generate the new README content
    content = "# Awesome Developer Podcasts\n\n"
    content += "A curated directory of the best podcasts for programmers, web developers, and software engineers.\n\n"
    content += "| Podcast Name | Description | Website Link |\n"
    content += "| --- | --- | --- |\n"
    
    # Sort alphabetically by title
    for title in sorted(podcasts.keys()):
        p = podcasts[title]
        # Clean description of any newlines to avoid breaking the markdown table
        desc = p.get('description', '').replace('\n', ' ').strip()
        link = p.get('link', '')
        
        # Only create a link if one exists
        if link:
            link_md = f"[[↗]]({link})"
        else:
            link_md = ""
            
        content += f"| **{title}** | {desc} | {link_md} |\n"
        
    # Write back to README.md
    with open('README.md', 'w') as f:
        f.write(content)
        
    print(f"README.md successfully updated with {len(podcasts)} total podcasts!")

if __name__ == "__main__":
    update_readme()
