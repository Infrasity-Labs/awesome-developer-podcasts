import json
import re

def extract():
    podcasts = []
    current_category = "Software Engineering & Development"
    
    with open('README.md', 'r', encoding='utf-8') as f:
        for line in f:
            # Check for category heading
            m_cat = re.match(r'^###\s+(.*)', line)
            if m_cat:
                current_category = m_cat.group(1).strip()
                continue
                
            # Check for podcast row
            m_row = re.match(r'^\|\s*\*\*(.*?)\*\*\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|', line)
            if m_row:
                title = m_row.group(1).strip()
                if title == "Podcast Name":
                    continue
                    
                # Clean up <br> tags because update_readme.py will word-wrap again
                desc = m_row.group(2).replace('<br>', ' ').strip()
                
                # Un-escape pipe characters in the title and description if any
                title = title.replace('&#124;', '|')
                desc = desc.replace('&#124;', '|')
                
                # Extract link
                link_col = m_row.group(3)
                link = ""
                m_link = re.search(r'\((.*?)\)', link_col)
                if m_link:
                    link = m_link.group(1)
                    
                # Re-tag the description with the category so update_readme.py knows where to put it
                desc = f"**[{current_category}]** {desc}"
                
                podcasts.append({
                    "title": title,
                    "description": desc,
                    "link": link
                })
                
    with open('data/existing.json', 'w', encoding='utf-8') as f:
        json.dump(podcasts, f, indent=4)
    print(f"Extracted {len(podcasts)} existing podcasts into existing.json")

if __name__ == '__main__':
    extract()
