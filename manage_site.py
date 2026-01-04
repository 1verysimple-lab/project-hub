import os
import glob
import subprocess
import sys
import json

PROJECTS_FILE = "projects.json"

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def run_command(command):
    try:
        print(f"Running: {command}")
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing {command}: {e}")

def load_projects():
    if not os.path.exists(PROJECTS_FILE):
        return []
    try:
        with open(PROJECTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error: {PROJECTS_FILE} is corrupted. Starting with empty list.")
        return []

def save_projects(projects):
    with open(PROJECTS_FILE, "w", encoding="utf-8") as f:
        json.dump(projects, f, indent=4)
    print(f"\n[SUCCESS] Saved {len(projects)} projects to {PROJECTS_FILE}")

def main():
    # Ensure we are working in the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    clear()
    print("========================================")
    print("   PROJECT HUB MANAGER (JSON EDITION)")
    print("========================================")
    
    current_projects = load_projects()
    registered_files = {p.get("filename") for p in current_projects}
    
    # 1. Identify new HTML files
    # Exclude index.html and any other system files if needed
    all_html = [f for f in glob.glob("*.html") if "index.html" not in f.lower()]
    
    new_files = [f for f in all_html if f not in registered_files]
    
    if new_files:
        print(f"\nFound {len(new_files)} new project(s) to add!")
        
        for file in new_files:
            print(f"\n--- Configure: {file} ---")
            try:
                print("Project Title (press Enter to use filename): ", end='', flush=True)
                title = sys.stdin.readline().strip()
                if not title: 
                    title = file.replace(".html", "").replace("_", " ").title()
                
                print("Short Description: ", end='', flush=True)
                desc = sys.stdin.readline().strip()
                if not desc: desc = "An interactive web experiment."

                # Determine type (default to HTML/JS)
                # You could add logic here to detect if it's a game, tool, etc.
                p_type = "HTML/JS" 
                
                new_entry = {
                    "filename": file,
                    "title": title,
                    "description": desc,
                    "type": p_type
                }
                current_projects.append(new_entry)
                
            except KeyboardInterrupt:
                print("\nOperation cancelled.")
                return
        
        save_projects(current_projects)
    else:
        print("\nAll local HTML projects are already in projects.json.")

    # 2. Deploy Option
    print("\n----------------------------------------")
    print("Do you want to upload changes to GitHub now? (y/n): ", end='', flush=True)
    choice = sys.stdin.readline().strip().lower()
    
    if choice == 'y':
        print("\nDeploying...")
        run_command("git add .")
        run_command('git commit -m "Update project list and content"')
        run_command("git push")
        print("\n[DONE] Site updated!")
    else:
        print("\nDone. Run this script again when you want to deploy.")

if __name__ == "__main__":
    main()