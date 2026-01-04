import os
import glob

# The Link
TARGET_URL = "https://blueshub.netlify.app/"

# The Logo HTML with inline styles for maximum compatibility
LOGO_HTML = f"""
<!-- BLUES APP LOGO -->
<div style="position: fixed; top: 1rem; right: 1rem; z-index: 9999; font-family: sans-serif;">
    <a href="{TARGET_URL}" style="display: block; width: 200px; opacity: 0.8; transition: opacity 0.2s; background-color: rgba(15, 23, 42, 0.9); backdrop-filter: blur(4px); border-radius: 0.5rem; border: 1px solid #334155; padding: 0.5rem; text-decoration: none; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
        <div style="font-size: 0.75rem; text-align: center; color: #94a3b8; margin-bottom: 0.25rem;">Back to Hub</div>
        <img src="logoani.svg" alt="App by Blues" style="width: 100%; height: auto; display: block;">
    </a>
</div>
<!-- END BLUES APP LOGO -->
"""

def update_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Check if logo is already present (simple check)
    if "logoani.svg" in content and "position: fixed" in content:
        # It might be there, let's try to update the link if it's an old version
        # This is a bit risky with regex, so we'll just report it for now or replace the whole block if we can identify it.
        # simpler approach: if it has the comment <!-- BLUES APP LOGO -->, replace the block.
        if "<!-- BLUES APP LOGO -->" in content:
            start_marker = "<!-- BLUES APP LOGO -->"
            end_marker = "<!-- END BLUES APP LOGO -->"
            try:
                start_idx = content.index(start_marker)
                end_idx = content.index(end_marker) + len(end_marker)
                
                new_content = content[:start_idx] + LOGO_HTML.strip() + content[end_idx:]
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"[UPDATED] {filepath}")
                return
            except ValueError:
                pass
        
        # If it's the React one we just made, it has specific classes
        if "class=\"fixed top-4 right-4 z-50\"" in content:
             print(f"[SKIPPING] {filepath} (Custom React Implementation detected - please update manually if needed)")
             return

        print(f"[EXISTS] {filepath} already has a logo.")
        return

    # If no logo, append before </body>
    if "</body>" in content:
        new_content = content.replace("</body>", f"{LOGO_HTML}\n</body>")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"[INJECTED] {filepath}")
    else:
        # Fallback for files without body tag (rare but possible in partials)
        print(f"[WARNING] {filepath} has no </body> tag. Appending to end.")
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(f"\n{LOGO_HTML}")

def main():
    # Get all HTML files except index.html
    files = [f for f in glob.glob("*.html") if "index.html" not in f.lower()]
    
    print(f"Found {len(files)} projects to process.")
    for file in files:
        update_file(file)

if __name__ == "__main__":
    main()
