import json
import glob
import re
import sys
from langdetect import detect, LangDetectException
from spellchecker import SpellChecker

def is_acronym_or_tech(word):
    # Ignore uppercase acronyms (e.g. AWS, CROs)
    if word.isupper() or (word.endswith('s') and word[:-1].isupper()):
        return True
    # Ignore camelCase or PascalCase (e.g. YouTube)
    if re.search(r'[a-z][A-Z]', word):
        return True
    # Ignore words with numbers
    if any(char.isdigit() for char in word):
        return True
    # Ignore small fragments that are often false positives
    if len(word) <= 2:
        return True
    return False

def fix_text(text, spell):
    try:
        # If the text is not English, skip spell checking completely!
        if not text or detect(text) != 'en':
            return text
    except LangDetectException:
        return text

    # Find all alphabetical words
    words = re.findall(r'\b[a-zA-Z]+\b', text)
    misspelled = spell.unknown(words)
    
    for word in misspelled:
        if is_acronym_or_tech(word):
            continue
            
        correction = spell.correction(word)
        if correction and correction != word:
            # Safely replace exact word match, preserving capitalization
            pattern = r'\b' + re.escape(word) + r'\b'
            
            if word.istitle():
                correction = correction.capitalize()
            elif word.isupper():
                correction = correction.upper()
                
            text = re.sub(pattern, correction, text)
            print(f"Fixed Typo: {word} -> {correction}")
            
    return text

def run_spell_check():
    spell = SpellChecker()
    # Add common developer terms so they aren't marked as typos
    tech_words = [
        'kubernetes', 'devops', 'api', 'frontend', 'backend', 'js', 'react', 'vue', 
        'npm', 'linux', 'mac', 'windows', 'ios', 'android', 'github', 'repo', 'ui', 
        'ux', 'ai', 'ml', 'sql', 'nosql', 'aws', 'gcp', 'azure', 'podcast', 'podcasts', 
        'coder', 'coders', 'docker', 'golang', 'rust', 'typescript', 'javascript',
        'python', 'java', 'ruby', 'php', 'html', 'css', 'git', 'sass', 'less', 'json'
    ]
    spell.word_frequency.load_words(tech_words)

    total_fixed = 0
    # Loop over all scraped JSON data
    for filepath in glob.glob("data/*.json"):
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        changed = False
        for item in data:
            orig_desc = item.get('description', '')
            new_desc = fix_text(orig_desc, spell)
            if orig_desc != new_desc:
                item['description'] = new_desc
                changed = True
                total_fixed += 1
                
        # Save fixes back to the JSON file
        if changed:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)
                
    print(f"Spell check complete! Fixed {total_fixed} descriptions.")

if __name__ == "__main__":
    run_spell_check()
