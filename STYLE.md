# Blues' Lab Design System

This guide defines the visual style and technical constraints for pages within the **Apps by Blues** ecosystem. Follow these guidelines to ensure consistency across all projects.

## 1. Core Technologies
All pages should utilize the following CDN-based stack for consistency and ease of deployment:

*   **Tailwind CSS:** `<script src="https://cdn.tailwindcss.com"></script>`
*   **Lucide Icons:** `<script src="https://unpkg.com/lucide@latest"></script>`
*   **Fonts:** Google Fonts (Inter & JetBrains Mono)

### Standard `<head>` Setup
Copy this block to ensure fonts, animations, and Tailwind config are identical.

```html
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    
    <!-- Scripts -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    
    <!-- Config -->
    <script>
        tailwind.config = {
            darkMode: 'class', // allows manual toggle if needed
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['Inter', 'sans-serif'],
                        mono: ['JetBrains Mono', 'monospace'],
                    },
                    animation: {
                        'float': 'float 6s ease-in-out infinite',
                        'fade-in': 'fadeIn 0.5s ease-out forwards',
                    },
                    keyframes: {
                        float: {
                            '0%, 100%': { transform: 'translateY(0)' },
                            '50%': { transform: 'translateY(-10px)' },
                        },
                        fadeIn: {
                            '0%': { opacity: '0', transform: 'translateY(10px)' },
                            '100%': { opacity: '1', transform: 'translateY(0)' },
                        }
                    }
                }
            }
        }
    </script>
    
    <!-- Base Styles -->
    <style>
        body { font-family: 'Inter', sans-serif; }
        .glass {
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        .dark .glass {
            background: rgba(30, 41, 59, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
    </style>
</head>
```

## 2. Color Palette & Theme

*   **Backgrounds:** 
    *   Light: `bg-slate-50`
    *   Dark: `bg-[#0f1117]` (Very dark slate)
*   **Text:**
    *   Primary: `text-slate-900` (Dark) / `text-slate-100` (Light)
    *   Secondary: `text-slate-500` / `text-slate-400`
*   **Accents:**
    *   Primary Brand: `indigo-500` / `indigo-600`
    *   Tools: `blue-500`
    *   Guides: `cyan-500`

## 3. UI Components

### The "Hub" Navigation Widget
For pages that are not the index, include this fixed navigation button to allow users to return to the main list. This matches the style injected by `inject_logo.py`.

**Placement:** Directly inside `<body>`, preferably at the top or bottom.

```html
<!-- BLUES HUB NAVIGATION -->
<a href="https://1verysimple-lab.github.io/project-hub/" 
   target="_blank"
   style="position: fixed; top: 20px; left: 20px; z-index: 9999; display: flex; align-items: center; gap: 8px; padding: 8px 12px; background: rgba(15, 23, 42, 0.8); backdrop-filter: blur(8px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; text-decoration: none; color: #e2e8f0; font-family: system-ui, sans-serif; font-size: 13px; font-weight: 500; transition: all 0.2s ease; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);"
   onmouseover="this.style.transform='translateY(-1px)'; this.style.background='rgba(15, 23, 42, 0.95)'"
   onmouseout="this.style.transform='translateY(0)'; this.style.background='rgba(15, 23, 42, 0.8)'">
    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect width="7" height="7" x="3" y="3" rx="1"/>
        <rect width="7" height="7" x="14" y="3" rx="1"/>
        <rect width="7" height="7" x="14" y="14" rx="1"/>
        <rect width="7" height="7" x="3" y="14" rx="1"/>
    </svg>
    <span>Hub</span>
</a>
<!-- END BLUES HUB NAVIGATION -->
```

### Glass Card (Container)
Use this structure for main content areas to match the "Apps" grid.

```html
<div class="glass rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-lg">
    <h2 class="text-xl font-bold text-slate-900 dark:text-white mb-4">Title</h2>
    <p class="text-slate-600 dark:text-slate-300">Content goes here...</p>
</div>
```

### Floating Background Blobs
To replicate the "Atmosphere" of the main page, place this immediately inside `<body>`.

```html
<div class="fixed inset-0 overflow-hidden pointer-events-none -z-10">
    <div class="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-indigo-500/10 rounded-full blur-[100px] animate-float"></div>
    <div class="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-500/10 rounded-full blur-[100px] animate-float" style="animation-delay: -3s;"></div>
</div>
```

## 4. Typography Rules
*   **Headings:** Use `font-bold` or `font-extrabold`. Tighter tracking (`tracking-tight`) often looks better on large headings.
*   **Body:** `text-slate-600` (Light mode) or `text-slate-400` (Dark mode) for readability.
*   **Code:** Use `font-mono` (JetBrains Mono) with a slightly smaller text size (`text-sm` or `text-xs`) and a dark background.

## 5. Deployment
*   Ensure `inject_logo.py` is run before deployment to automatically add the Hub Navigation to all HTML files.
*   Ensure `projects.json` is updated if the new page is a standalone app that should appear on the index.
