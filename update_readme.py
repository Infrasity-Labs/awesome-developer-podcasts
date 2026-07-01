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
        
    # Preserve existing header
        # Preserve existing header and footer
    header = ""
    footer = ""
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            table_start_idx = len(lines)
            footer_start_idx = len(lines)
            for i, line in enumerate(lines):
                if line.strip().startswith((
                    "| Podcast Name",
                    "## Software Engineering", "### Software Engineering",
                    "## GTM", "### GTM",
                    "## Developer Marketing", "### Developer Marketing",
                    "## Technical Content Marketing", "### Technical Content Marketing"
                )):
                    if table_start_idx == len(lines):
                        table_start_idx = i
                if "<!-- FOOTER -->" in line or line.strip().startswith("## About"):
                    if footer_start_idx == len(lines):
                        footer_start_idx = i
            if table_start_idx == len(lines) and footer_start_idx < len(lines):
                table_start_idx = footer_start_idx
            header = "".join(lines[:table_start_idx])
            if footer_start_idx < len(lines):
                footer = "".join(lines[footer_start_idx:])
    except Exception as e:
        header = "# Awesome Developer Podcasts\n\n"
    
    if not header.strip():
        header = "# Awesome Developer Podcasts\n\n"
        
    # Group podcasts into verticals
    verticals = {
        "GTM": [],
        "Developer Marketing": [],
        "Technical Content Marketing": [],
        "Software Engineering & Development": []
    }
    
    for title in sorted(podcasts.keys()):
        p = podcasts[title]
        desc = (p.get('description') or '').replace('\n', ' ').replace('\r', ' ').replace('|', '&#124;').strip()
        safe_title = title.replace('|', '&#124;')
        link = (p.get('link') or '').strip()
        
        # Determine vertical
        if desc.startswith('**[GTM]**'):
            vertical = "GTM"
            desc = desc[9:].strip()
        elif desc.startswith('**[DEVELOPER MARKETING]**'):
            vertical = "Developer Marketing"
            desc = desc[25:].strip()
        elif desc.startswith('**[TECHNICAL CONTENT MARKETING]**'):
            vertical = "Technical Content Marketing"
            desc = desc[33:].strip()
        else:
            vertical = "Software Engineering & Development"
            
        link_md = f"[↗]({link})" if link else ""
        verticals[vertical].append(f"| **{safe_title}** | {desc} | {link_md} |\n")
        
    # Generate the new README content
    content = header.rstrip() + '\\n\\n'
        
    # Generate tables for each vertical
    for vertical_name in ["Software Engineering & Development", "GTM", "Developer Marketing", "Technical Content Marketing"]:
        if verticals[vertical_name]:
            content += f"### {vertical_name}\n\n"
            content += "| Podcast Name | Description | Website Link |\n"
            content += "| --- | --- | --- |\n"
            for row in verticals[vertical_name]:
                content += row
            content += "\n"
        
    # Write back to README.md
    if footer:
        content += "\n" + footer
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')
        
    print(f"README.md successfully updated with {len(podcasts)} total podcasts across {sum(1 for v in verticals.values() if v)} verticals!")

if __name__ == "__main__":
    update_readme()
