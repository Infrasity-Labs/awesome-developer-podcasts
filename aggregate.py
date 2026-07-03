import json
import glob
import textwrap
import re
from collections import defaultdict

def update_readme():
    podcasts = {}
    
    # Read all JSON files produced by fetchers
    for filepath in glob.glob("data/*.json"):
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
        
    # Preserve existing header and footer
    header = ""
    footer = ""
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            table_start_idx = len(lines)
            footer_start_idx = len(lines)
            for i, line in enumerate(lines):
                # Stop header at the first category heading, table, or TOC
                if line.strip().startswith("### ") or line.strip().startswith("## Table of Contents") or line.strip().startswith("| Podcast Name"):
                    if table_start_idx == len(lines):
                        table_start_idx = i
                # Start footer at the FOOTER comment or About heading
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
        
    # Group podcasts into verticals dynamically
    verticals = defaultdict(list)
    
    for title in sorted(podcasts.keys()):
        p = podcasts[title]
        raw_desc = (p.get('description') or '').replace('\n', ' ').replace('\r', ' ').replace('|', '&#124;').strip()
        # Remove raw URLs, domain names, and leftover link fragments from description 
        # to prevent ugly formatting and broken links in the table
        raw_desc = re.sub(r'https?://[^\s<>"]+|www\.[^\s<>"]+|\b\w+\.(?:com|io|org|net|co|se|fm)\b/?\S*|https\.\.\.', '', raw_desc, flags=re.IGNORECASE).strip()
        # Clean up any leftover double spaces caused by the regex
        raw_desc = re.sub(r'\s{2,}', ' ', raw_desc)
        safe_title = title.replace('|', '&#124;')
        link = (p.get('link') or '').strip()
        
        # Determine vertical dynamically
        match = re.match(r'^\*\*\[(.*?)\]\*\*\s*(.*)', raw_desc, flags=re.IGNORECASE)
        if match:
            tag = match.group(1).strip()
            if tag.upper() == "GTM":
                vertical = "GTM"
            elif tag.lower() in ("software engineering & general tech", "software engineering and general tech"):
                vertical = "Software Engineering & Development"
            else:
                vertical = tag.title()
            desc = match.group(2).strip()
        else:
            vertical = "Software Engineering & Development"
            desc = raw_desc
            
        # Word wrap the description to prevent horizontal scrolling
        desc = '<br>'.join(textwrap.wrap(desc, width=80, break_long_words=False, break_on_hyphens=False))
            
        link_md = f"[↗]({link})" if link else ""
        verticals[vertical].append(f"| **{safe_title}** | {desc} | {link_md} |\n")
        
    # Generate the new README content
    content = header.rstrip() + '\n\n'
        
    # Generate tables for each vertical
    sorted_verticals = sorted(verticals.keys())
    # Ensure Software Engineering is always first
    if "Software Engineering & Development" in sorted_verticals:
        sorted_verticals.remove("Software Engineering & Development")
        sorted_verticals.insert(0, "Software Engineering & Development")

        
    # Generate Table of Contents
    content += "## Table of Contents\n"
    for vertical_name in sorted_verticals:
        if verticals[vertical_name]:
            # Create GitHub-compatible anchor link
            anchor = re.sub(r'[^\w\- ]', '', vertical_name.lower()).replace(' ', '-')
            content += f"- [{vertical_name}](#{anchor})\n"
    content += "\n"
        
    for vertical_name in sorted_verticals:
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
        
    print(f"README.md successfully updated with {len(podcasts)} total podcasts across {len(verticals)} verticals!")

if __name__ == "__main__":
    update_readme()
