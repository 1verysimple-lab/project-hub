import os
import glob

# The Link
TARGET_URL = "https://1verysimple-lab.github.io/project-hub/"

# The Logo HTML (New "Hub" Button Style)
LOGO_HTML = f"""
<!-- BLUES HUB NAVIGATION -->
<a href="{TARGET_URL}" 
   target="_blank"
   style="position: fixed; top: 20px; left: 20px; z-index: 9999; display: flex; align-items: center; gap: 8px; padding: 8px 12px; background: rgba(15, 23, 42, 0.8); backdrop-filter: blur(8px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; text-decoration: none; color: #e2e8f0; font-family: system-ui, sans-serif; font-size: 13px; font-weight: 500; transition: all 0.2s ease; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);"
   onmouseover="this.style.transform='translateY(-1px)'; this.style.background='rgba(15, 23, 42, 0.95)'"
   onmouseout="this.style.transform='translateY(0)'; this.style.background='rgba(15, 23, 42, 0.8)'">
    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="7" height="7" x="3" y="3" rx="1"/><rect width="7" height="7" x="14" y="3" rx="1"/><rect width="7" height="7" x="14" y="14" rx="1"/><rect width="7" height="7" x="3" y="14" rx="1"/></svg>
    <span>Hub</span>
</a>
<!-- END BLUES HUB NAVIGATION -->
"""

def update_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Pattern used for old logo with comments
    old_start_marker = "<!-- BLUES APP LOGO -->"
    old_end_marker = "<!-- END BLUES APP LOGO -->"
    
    # Pattern for new logo with comments
    new_start_marker = "<!-- BLUES HUB NAVIGATION -->"
    new_end_marker = "<!-- END BLUES HUB NAVIGATION -->"

    # 1. Check for NEW logo
    if new_start_marker in content:
        print(f"[OK] {filepath} already has the new navigation.")
        return

    # 2. Check for OLD logo and Replace
    if old_start_marker in content and old_end_marker in content:
        try:
            start_idx = content.index(old_start_marker)
            end_idx = content.index(old_end_marker) + len(old_end_marker)
            
            new_content = content[:start_idx] + LOGO_HTML.strip() + content[end_idx:]
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"[UPDATED] {filepath} (Replaced old logo)")
            return
        except ValueError:
            pass
            
    # 3. Inject if missing
    if "</body>" in content:
        new_content = content.replace("</body>", f"{LOGO_HTML}\n</body>")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"[INJECTED] {filepath}")
    else:
        # Fallback for files without body tag
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(f"\n{LOGO_HTML}")
        print(f"[APPENDED] {filepath}")

def main():
    # Get all HTML files except index.html
    files = [f for f in glob.glob("*.html") if "index.html" not in f.lower()]
    
    print(f"Found {len(files)} projects to scan.")
    for file in files:
        update_file(file)

if __name__ == "__main__":
    main()