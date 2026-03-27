import os
import json
import shutil
import subprocess
import threading
import glob
import hashlib
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

# --- CONFIGURATION ---
SOURCE_DIR = "."
DEST_DIR = "github_pages"
PROJECTS_JSON = os.path.join(DEST_DIR, "projects.json")
MUSIC_SOURCE_DIR = "bgmus"
MUSIC_DEST_DIR = os.path.join(DEST_DIR, "bgmus")
MUSIC_JSON = os.path.join(DEST_DIR, "music.json")

# The Logo HTML (Hub Link)
TARGET_URL = "https://1verysimple-lab.github.io/project-hub/"
LOGO_HTML = f"""
<!-- BLUES HUB NAVIGATION -->
<a href="{TARGET_URL}" 
   target="_blank"
   style="position: fixed; top: 20px; left: 20px; z-index: 9999; display: flex; align-items: center; gap: 8px; padding: 8px 12px; background: rgba(15, 23, 42, 0.8); backdrop-filter: blur(8px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; text-decoration: none; color: #e2e8f0; font-family: system-ui, sans-serif; font-size: 13px; font-weight: 500; transition: all 0.2s ease; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);"
   onmouseover="this.style.transform='translateY(-1px)'; this.style.background='rgba(15, 23, 42, 0.95)'"
   onmouseout="this.style.transform='translateY(0)'; this.style.background='rgba(15, 23, 42, 0.8)'">
    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="7" height="7" x="3" y="3" rx="1"></rect><rect width="7" height="7" x="14" y="3" rx="1"></rect><rect width="7" height="7" x="14" y="14" rx="1"></rect><rect width="7" height="7" x="3" y="14" rx="1"></rect></svg>
    <span>Hub</span>
</a>
<!-- END BLUES HUB NAVIGATION -->
"""

# --- BACKEND LOGIC ---

class HubBackend:
    def __init__(self):
        self.ensure_dirs()

    def ensure_dirs(self):
        if not os.path.exists(DEST_DIR):
            os.makedirs(DEST_DIR)
        if not os.path.exists(MUSIC_DEST_DIR):
            os.makedirs(MUSIC_DEST_DIR)

    def load_projects(self):
        if not os.path.exists(PROJECTS_JSON):
            return []
        try:
            with open(PROJECTS_JSON, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []

    def save_projects(self, data):
        with open(PROJECTS_JSON, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    def get_file_hash(self, filepath):
        if not os.path.exists(filepath):
            return None
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def scan_orphans(self):
        """Finds HTML files in SOURCE_DIR that are not in projects.json."""
        projects = self.load_projects()
        registered = {p['filename'] for p in projects}
        
        orphans = []
        
        # 1. Scan Root HTMLs
        excludes = {'index.html', 'template.html', '404.html'}
        root_files = [f for f in glob.glob("*.html") if f not in excludes]
        for f in root_files:
            if f not in registered:
                orphans.append(f)
                
        # 2. Scan Folder Projects (naive check: look for folders with index.html or same-name html)
        # For simplicity, let's just look at immediate subdirectories
        ignored_folders = {'.git', 'github_pages', 'bgmus', '.gemini', 'node_modules', '__pycache__'}
        for item in os.listdir(SOURCE_DIR):
            if os.path.isdir(item) and item not in ignored_folders and not item.startswith('.'):
                # Check for item/item.html or item/index.html
                candidate_1 = os.path.join(item, f"{item}.html")
                candidate_2 = os.path.join(item, "index.html")
                found_html = None
                if os.path.exists(candidate_1): found_html = f"{item}/{item}.html"
                elif os.path.exists(candidate_2): found_html = f"{item}/index.html"
                
                if found_html and found_html not in registered:
                    orphans.append(found_html)
                    
        return orphans

    def add_orphan(self, rel_path, title, desc, p_type):
        projects = self.load_projects()
        projects.insert(0, {
            "filename": rel_path,
            "title": title,
            "description": desc,
            "type": p_type,
            "date_added": datetime.now().strftime("%Y-%m-%d")
        })
        self.save_projects(projects)

    def inject_hub_link(self, rel_path):
        """Injects the Hub button into the given file."""
        # Resolve full path
        filepath = os.path.join(SOURCE_DIR, rel_path)
        if not os.path.exists(filepath):
            return "File not found."

        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        if "<!-- BLUES HUB NAVIGATION -->" in content:
            return "Hub Link already exists."

        # Replace old logic or inject new
        updated = False
        if "<!-- BLUES APP LOGO -->" in content:
            # Replace old
            start = content.index("<!-- BLUES APP LOGO -->")
            end_marker = "<!-- END BLUES APP LOGO -->"
            if end_marker in content:
                end = content.index(end_marker) + len(end_marker)
                content = content[:start] + LOGO_HTML.strip() + content[end:]
                updated = True
        
        if not updated:
            if "</body>" in content:
                content = content.replace("</body>", f"{LOGO_HTML}\n</body>")
            else:
                content += f"\n{LOGO_HTML}"

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return "Hub Link injected successfully."

    def create_project(self, title, filename_base, description, p_type, is_folder, html_content):
        # 1. Determine paths
        clean_filename = filename_base.strip().replace(" ", "_")
        if not clean_filename.endswith(".html"):
            clean_filename += ".html"
            
        if is_folder:
            folder_name = os.path.splitext(clean_filename)[0]
            project_dir = os.path.join(SOURCE_DIR, folder_name)
            if not os.path.exists(project_dir):
                os.makedirs(project_dir)
            full_path = os.path.join(project_dir, clean_filename)
            rel_path_for_json = f"{folder_name}/{clean_filename}"
        else:
            full_path = os.path.join(SOURCE_DIR, clean_filename)
            rel_path_for_json = clean_filename

        # 2. Write File
        if not html_content.strip():
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
</head>
<body>
    <h1>{title}</h1>
    <p>{description}</p>
</body>
</html>"""

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        # 3. Update JSON
        projects = self.load_projects()
        exists = False
        for p in projects:
            if p['filename'] == rel_path_for_json:
                exists = True
                p['title'] = title
                p['description'] = description
                p['type'] = p_type
                break
        
        if not exists:
            projects.insert(0, {
                "filename": rel_path_for_json,
                "title": title,
                "description": description,
                "type": p_type,
                "date_added": datetime.now().strftime("%Y-%m-%d")
            })
            
        self.save_projects(projects)
        return f"Project created at {full_path}"

    def delete_project(self, filename):
        projects = self.load_projects()
        projects = [p for p in projects if p['filename'] != filename]
        self.save_projects(projects)
        
        # Also remove from GitHub Pages folder to keep it clean
        dest_path = os.path.join(DEST_DIR, filename)
        if os.path.exists(dest_path):
            try:
                os.remove(dest_path)
            except:
                pass

    def sync_all(self, log_callback):
        log_callback("Starting Full Sync...")
        self._sync_music(log_callback)
        self._sync_assets(log_callback)
        self._sync_projects(log_callback)
        log_callback("Sync Complete.")

    def _sync_music(self, log_callback):
        if not os.path.exists(MUSIC_SOURCE_DIR): return
        src_files = glob.glob(os.path.join(MUSIC_SOURCE_DIR, "*.mp3"))
        src_names = [os.path.basename(f) for f in src_files]
        dest_files = glob.glob(os.path.join(MUSIC_DEST_DIR, "*.mp3"))
        dest_names = [os.path.basename(f) for f in dest_files]
        
        for f in dest_names:
            if f not in src_names:
                os.remove(os.path.join(MUSIC_DEST_DIR, f))
                log_callback(f"[Music] Deleted {f}")
        for f in src_names:
            src = os.path.join(MUSIC_SOURCE_DIR, f)
            dst = os.path.join(MUSIC_DEST_DIR, f)
            if self._needs_update(src, dst):
                shutil.copy2(src, dst)
                log_callback(f"[Music] Synced {f}")
        
        track_list = [f"bgmus/{n}" for n in sorted(src_names)]
        with open(MUSIC_JSON, 'w', encoding='utf-8') as f:
            json.dump(track_list, f, indent=4)

    def _sync_assets(self, log_callback):
        exts = ['*.webp', '*.png', '*.jpg', '*.jpeg', '*.svg', '*.gif', '*.wav']
        for ext in exts:
            for src in glob.glob(ext):
                fname = os.path.basename(src)
                dst = os.path.join(DEST_DIR, fname)
                if self._needs_update(src, dst):
                    shutil.copy2(src, dst)
                    log_callback(f"[Asset] Synced {fname}")

    def _sync_projects(self, log_callback):
        projects = self.load_projects()
        for p in projects:
            rel_path = p['filename']
            if "/" in rel_path or "\\" in rel_path:
                folder_name = os.path.dirname(rel_path)
                src_folder = os.path.join(SOURCE_DIR, folder_name)
                dst_folder = os.path.join(DEST_DIR, folder_name)
                
                if os.path.exists(src_folder):
                    if not os.path.exists(dst_folder): os.makedirs(dst_folder)
                    for root, dirs, files in os.walk(src_folder):
                        rel_root = os.path.relpath(root, src_folder)
                        cur_dst_root = os.path.join(dst_folder, rel_root)
                        if not os.path.exists(cur_dst_root): os.makedirs(cur_dst_root)
                        for file in files:
                            s = os.path.join(root, file)
                            d = os.path.join(cur_dst_root, file)
                            if self._needs_update(s, d):
                                shutil.copy2(s, d)
                                log_callback(f"[Project] Updated file {file} in {folder_name}")
                else:
                    log_callback(f"[Warning] Source folder missing for {rel_path}")
            else:
                src_path = os.path.join(SOURCE_DIR, rel_path)
                dst_path = os.path.join(DEST_DIR, rel_path)
                if os.path.exists(src_path):
                    if self._needs_update(src_path, dst_path):
                        shutil.copy2(src_path, dst_path)
                        log_callback(f"[Project] Synced {rel_path}")
                else:
                    log_callback(f"[Warning] Source file missing: {rel_path}")

    def _needs_update(self, src, dst):
        if not os.path.exists(dst): return True
        return self.get_file_hash(src) != self.get_file_hash(dst)

    def git_status_check(self):
        original_dir = os.getcwd()
        try:
            os.chdir(DEST_DIR)
            res = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
            if res.stdout.strip():
                return "Modified (Needs Deploy)"
            
            # Check if ahead of remote? (Requires fetch, might be slow)
            # Simple check:
            return "Clean (Local)"
        except:
            return "Git Error"
        finally:
            os.chdir(original_dir)

    def git_deploy(self, message, log_callback):
        def run():
            original_dir = os.getcwd()
            try:
                os.chdir(DEST_DIR)
                log_callback("---")
                res = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
                if not res.stdout.strip():
                    log_callback("No changes to push.")
                    return

                log_callback("Staging changes...")
                subprocess.run("git add .", shell=True, check=True)
                log_callback(f"Committing: {message}")
                subprocess.run(f'git commit -m "{message}"', shell=True, check=True)
                log_callback("Pulling (Rebase)...")
                subprocess.run("git pull --rebase", shell=True, check=True)
                log_callback("Pushing to GitHub...")
                subprocess.run("git push", shell=True, check=True)
                log_callback("SUCCESS: Deployed to GitHub Pages.")
            except Exception as e:
                log_callback(f"ERROR: {e}")
            finally:
                os.chdir(original_dir)
        threading.Thread(target=run, daemon=True).start()

# --- GUI ---

class HubGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Blues' Hub Manager v1.1.1")
        self.geometry("950x700")
        self.backend = HubBackend()
        
        self.configure_styles()
        self.create_widgets()
        
    def configure_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", padding=6, font=('Segoe UI', 10))
        style.configure("TLabel", font=('Segoe UI', 10))
        style.configure("Header.TLabel", font=('Segoe UI', 12, 'bold'))
        
    def create_widgets(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.tab_manage = ttk.Frame(notebook)
        self.tab_create = ttk.Frame(notebook)
        self.tab_publish = ttk.Frame(notebook)
        
        notebook.add(self.tab_manage, text="  Manage Projects  ")
        notebook.add(self.tab_create, text="  Create New  ")
        notebook.add(self.tab_publish, text="  Sync & Publish  ")
        
        self.setup_manage_tab()
        self.setup_create_tab()
        self.setup_publish_tab()
        
        self.status_var = tk.StringVar(value="Ready")
        self.git_var = tk.StringVar(value="Git: Unknown")
        
        status_frame = ttk.Frame(self, relief=tk.SUNKEN)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        ttk.Label(status_frame, text="v1.1.1", font=('Segoe UI', 8, 'italic')).pack(side=tk.LEFT, padx=5)
        ttk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT, padx=5)
        ttk.Label(status_frame, textvariable=self.git_var).pack(side=tk.RIGHT, padx=5)
        
        self.refresh_git_status()

    def refresh_git_status(self):
        status = self.backend.git_status_check()
        self.git_var.set(f"Git: {status}")
        self.after(10000, self.refresh_git_status) # Auto-refresh every 10s

    # --- TAB 1: MANAGE ---
    def setup_manage_tab(self):
        frame = ttk.Frame(self.tab_manage)
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Toolbar
        toolbar = ttk.Frame(frame)
        toolbar.pack(fill='x', pady=10)
        
        ttk.Button(toolbar, text="Refresh List", command=self.load_project_list).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Scan for New Files", command=self.scan_orphans).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Delete Selected", command=self.delete_selected).pack(side=tk.RIGHT, padx=2)
        ttk.Button(toolbar, text="Inject Hub Link", command=self.inject_hub_link).pack(side=tk.RIGHT, padx=2)
        
        # Treeview
        columns = ("title", "type", "filename")
        self.tree = ttk.Treeview(frame, columns=columns, show='headings', selectmode='browse')
        self.tree.heading("title", text="Project Title")
        self.tree.heading("type", text="Type")
        self.tree.heading("filename", text="Filename/Path")
        
        self.tree.column("title", width=300)
        self.tree.column("type", width=100)
        self.tree.column("filename", width=300)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.pack(side=tk.RIGHT, fill='y')
        
        self.load_project_list()

    def load_project_list(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        projects = self.backend.load_projects()
        for p in projects:
            self.tree.insert("", "end", values=(p.get('title'), p.get('type'), p.get('filename')))

    def scan_orphans(self):
        orphans = self.backend.scan_orphans()
        if not orphans:
            messagebox.showinfo("Scan", "No unlisted projects found.")
            return
            
        # Dialog to add them
        top = tk.Toplevel(self)
        top.title(f"Found {len(orphans)} Orphans")
        top.geometry("400x300")
        
        lbl = ttk.Label(top, text="Select files to add to index:")
        lbl.pack(pady=5)
        
        lb = tk.Listbox(top, selectmode=tk.MULTIPLE)
        lb.pack(fill='both', expand=True, padx=10, pady=5)
        for f in orphans: lb.insert(tk.END, f)
            
        def add_selected():
            selection = lb.curselection()
            if not selection: return
            for idx in selection:
                fname = lb.get(idx)
                # Defaults
                title = fname.replace(".html", "").split("/")[-1].replace("_", " ").title()
                self.backend.add_orphan(fname, title, "Restored project", "Other")
            self.load_project_list()
            top.destroy()
            
        ttk.Button(top, text="Add Selected", command=add_selected).pack(pady=10)

    def inject_hub_link(self):
        item = self.tree.selection()
        if not item: return
        fname = self.tree.item(item[0], "values")[2]
        
        res = self.backend.inject_hub_link(fname)
        messagebox.showinfo("Inject Result", res)

    def delete_selected(self):
        item = self.tree.selection()
        if not item: return
        fname = self.tree.item(item[0], "values")[2]
        
        if messagebox.askyesno("Delete", f"Remove '{fname}' from index? (File will also be removed from deployment folder)"):
            self.backend.delete_project(fname)
            self.load_project_list()

    # --- TAB 2: CREATE ---
    def setup_create_tab(self):
        frame = ttk.Frame(self.tab_create)
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        grid = ttk.Frame(frame)
        grid.pack(fill='x')
        
        ttk.Label(grid, text="Project Title:").grid(row=0, column=0, sticky='w', pady=5)
        self.entry_title = ttk.Entry(grid, width=40)
        self.entry_title.grid(row=0, column=1, sticky='w', padx=10)
        
        ttk.Label(grid, text="Filename:").grid(row=1, column=0, sticky='w', pady=5)
        self.entry_filename = ttk.Entry(grid, width=40)
        self.entry_filename.grid(row=1, column=1, sticky='w', padx=10)
        
        ttk.Label(grid, text="Type:").grid(row=2, column=0, sticky='w', pady=5)
        self.combo_type = ttk.Combobox(grid, values=["Tool", "Game", "Guide", "Other"], state="readonly")
        self.combo_type.current(3)
        self.combo_type.grid(row=2, column=1, sticky='w', padx=10)
        
        self.var_folder_mode = tk.BooleanVar()
        cb = ttk.Checkbutton(grid, text="Create in own folder?", variable=self.var_folder_mode)
        cb.grid(row=3, column=1, sticky='w', padx=10, pady=5)
        
        ttk.Label(grid, text="Description:").grid(row=4, column=0, sticky='w', pady=5)
        self.entry_desc = ttk.Entry(grid, width=60)
        self.entry_desc.grid(row=4, column=1, sticky='w', padx=10)
        
        ttk.Label(frame, text="Initial HTML Code (Paste here):").pack(anchor='w', pady=(20, 0))
        self.text_code = scrolledtext.ScrolledText(frame, height=15, font=('Consolas', 9))
        self.text_code.pack(fill='both', expand=True, pady=5)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill='x', pady=10)
        
        ttk.Button(btn_frame, text="Create Project", command=self.action_create_project).pack(side=tk.RIGHT)
        ttk.Button(btn_frame, text="Clear Form", command=self.clear_create_form).pack(side=tk.RIGHT, padx=10)

    def action_create_project(self):
        title = self.entry_title.get().strip()
        fname = self.entry_filename.get().strip()
        desc = self.entry_desc.get().strip()
        p_type = self.combo_type.get()
        is_folder = self.var_folder_mode.get()
        code = self.text_code.get("1.0", tk.END)
        
        if not title or not fname:
            messagebox.showerror("Error", "Title and Filename are required.")
            return
            
        try:
            msg = self.backend.create_project(title, fname, desc, p_type, is_folder, code)
            messagebox.showinfo("Success", msg)
            self.status_var.set(f"Created {title}")
            self.load_project_list() 
            self.clear_create_form()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_create_form(self):
        self.entry_title.delete(0, tk.END)
        self.entry_filename.delete(0, tk.END)
        self.entry_desc.delete(0, tk.END)
        self.text_code.delete("1.0", tk.END)

    # --- TAB 3: PUBLISH ---
    def setup_publish_tab(self):
        frame = ttk.Frame(self.tab_publish)
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        actions = ttk.Frame(frame)
        actions.pack(fill='x', pady=10)
        
        ttk.Button(actions, text="1. Sync All Content", command=self.action_sync).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions, text="2. Deploy to GitHub", command=self.action_deploy).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(frame, text="Activity Log:").pack(anchor='w')
        self.log_text = scrolledtext.ScrolledText(frame, height=20, state='disabled', bg='#1e1e1e', fg='#dcdcdc', font=('Consolas', 9))
        self.log_text.pack(fill='both', expand=True)

    def log(self, msg):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"{msg}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        self.update_idletasks()

    def action_sync(self):
        self.log("---" * 10)
        self.backend.sync_all(self.log)
        self.status_var.set("Sync complete.")
        self.refresh_git_status()

    def action_deploy(self):
        if messagebox.askyesno("Confirm Deploy", "Push all changes to GitHub Pages?"):
            self.log("---" * 10)
            self.backend.git_deploy("Update via Hub Manager", self.log)

if __name__ == "__main__":
    app = HubGUI()
    app.mainloop()
