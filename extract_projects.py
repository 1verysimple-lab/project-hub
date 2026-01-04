import re
import json
import os

def extract():
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Regex to find project cards
        # We look for the href, the h2 (title), and the p (description)
        # We use strict matching for the class structure we know exists
        pattern = r'<a href="(.*?)".*?<h2.*?>(.*?)</h2>.*?<p.*?>(.*?)</p>'
        
        matches = re.findall(pattern, content, re.DOTALL)
        
        projects = []
        for m in matches:
            # Clean up whitespace
            filename = m[0]
            title = m[1].strip()
            desc = m[2].strip()
            
            # Simple check to avoid duplicates if any
            if not any(p['filename'] == filename for p in projects):
                projects.append({
                    "filename": filename,
                    "title": title,
                    "description": desc,
                    "type": "External" if "http" in filename else "HTML/JS"
                })
        
        with open('projects.json', 'w', encoding='utf-8') as f:
            json.dump(projects, f, indent=4)
            
        print(f"Successfully extracted {len(projects)} projects to projects.json")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract()
