import os
import glob
import subprocess
import sys

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def run_command(command):
    try:
        print(f"Running: {command}")
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing {command}: {e}")

def main():
    clear()
    print("========================================")
    print("   PROJECT HUB MANAGER")
    print("========================================")
    
    # 1. Identify new HTML files
    all_html = [f for f in glob.glob("*.html") if "index.html" not in f.lower()]
    
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            index_content = f.read()
    except FileNotFoundError:
        print("Error: index.html not found!")
        return
    
    # Robust check for existing links
    new_files = []
    for f in all_html:
        if f'href="{f}"' not in index_content and f"href='{f}'" not in index_content:
            new_files.append(f)
    
    if new_files:
        print(f"\nFound {len(new_files)} new project(s) to add!")
        
        insert_buffer = ""
        # Template for new cards
        card_template = """
        <!-- PROJECT: {title} -->
        <a href="{filename}" class="card block p-6 bg-zinc-900 border border-zinc-800 rounded-xl hover:border-emerald-500 group">
            <div class="flex items-center justify-between mb-4">
                <div class="p-3 bg-zinc-800 rounded-lg text-emerald-400 group-hover:text-white transition-colors">
                    <i data-lucide="layout-template"></i>
                </div>
                <span class="text-xs font-mono text-zinc-500">HTML/JS</span>
            </div>
            <h2 class="text-xl font-semibold mb-2 group-hover:text-emerald-400 transition-colors">{title}</h2>
            <p class="text-zinc-400 text-sm">
                {desc}
            </p>
        </a>
"""
        
        for file in new_files:
            print(f"\n--- Configure: {file} ---")
            try:
                print("Project Title: ", end='', flush=True)
                title = sys.stdin.readline().strip()
                if not title: title = file
                
                print("Short Description: ", end='', flush=True)
                desc = sys.stdin.readline().strip()
                if not desc: desc = "A cool web project."
                
                insert_buffer += card_template.format(filename=file, title=title, desc=desc)
            except Exception as e:
                title = file
                desc = "New Project"
                insert_buffer += card_template.format(filename=file, title=title, desc=desc)
        
        # Insert before </main>
        if "</main>" in index_content:
            new_content = index_content.replace("</main>", insert_buffer + "\n    </main>")
            with open("index.html", "w", encoding="utf-8") as f:
                f.write(new_content)
            print("\n[SUCCESS] index.html updated!")
        else:
            print("\n[ERROR] Could not find </main> tag in index.html.")
    else:
        print("\nAll projects are already in the index.")

    # 2. Deploy Option
    print("\n----------------------------------------")
    print("Do you want to upload changes to GitHub now? (y/n): ", end='', flush=True)
    choice = sys.stdin.readline().strip().lower()
    
    if choice == 'y':
        print("\nDeploying...")
        
        # Check remote
        try:
            remotes = subprocess.check_output("git remote", shell=True).decode()
            if "origin" not in remotes:
                print("\n[WARNING] No remote 'origin' found. You can't push yet.")
                print("Run: git remote add origin https://github.com/YOUR_USERNAME/project-hub.git")
            else:
                run_command("git add .")
                run_command('git commit -m "Update project showcase"')
                run_command("git push -u origin HEAD")
                print("\n[DONE] Site updated!")
        except:
             # Try anyway if check fails
            run_command("git add .")
            run_command('git commit -m "Update project showcase"')
            run_command("git push -u origin HEAD")

    else:
        print("\nDone. Run this script again when you want to deploy.")

if __name__ == "__main__":
    main()
