import os
import datetime
import json
import urllib.request
import math
import random
from collections import Counter

# Configuration
GITHUB_USERNAME = "mel-cell"
OUTPUT_FILE = "assets/grid.svg"

# Monochrome Premium Theme
THEME = {
    "bg": "#0d1117",          # Dark background
    "card_bg": "#161b22",     # Slightly lighter card
    "text_main": "#ffffff",
    "text_dim": "#8b949e",
    "border": "#30363d",
    "accent_1": "#ffffff",    # Brightest
    "accent_2": "#9ca3af",    # Mid gray
    "accent_3": "#4b5563",    # Dark gray
    "graph_fill": "rgba(255, 255, 255, 0.1)" # Glassy fill
}

def fetch_json(url):
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Python-Script')
        token = os.environ.get('GITHUB_TOKEN')
        if token:
            req.add_header('Authorization', f'token {token}')
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def get_real_stats(username):
    user_url = f"https://api.github.com/users/{username}"
    repos_url = f"https://api.github.com/users/{username}/repos?per_page=100&type=owner"
    
    user_data = fetch_json(user_url)
    repos_data = fetch_json(repos_url)
    
    if not user_data or not repos_data:
        return {
            "stats": {"total_stars": 0, "total_forks": 0, "followers": 0, "total_repos": 0},
            "languages": []
        }

    total_stars = sum(repo['stargazers_count'] for repo in repos_data)
    total_forks = sum(repo['forks_count'] for repo in repos_data)
    
    langs = [repo['language'] for repo in repos_data if repo['language']]
    lang_counts = Counter(langs)
    total_langs = sum(lang_counts.values())
    
    top_languages = []
    # Monochrome palette mapping based on rank
    mono_palette = [THEME['accent_1'], THEME['accent_2'], THEME['accent_3'], "#333333", "#222222"]
    
    for i, (lang, count) in enumerate(lang_counts.most_common(4)):
        percent = math.floor((count / total_langs) * 100)
        top_languages.append({
            "name": lang,
            "percent": percent,
            "color": mono_palette[i] if i < len(mono_palette) else "#222222"
        })

    return {
        "stats": {
            "total_stars": total_stars,
            "total_forks": total_forks,
            "followers": user_data['followers'],
            "total_repos": user_data['public_repos']
        },
        "languages": top_languages
    }

def make_circle_chart(percent, radius, stroke, color, cx, cy):
    circumference = 2 * math.pi * radius
    offset = circumference - (percent / 100) * circumference
    return f'''
    <circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" stroke="{THEME['border']}" stroke-width="{stroke}" />
    <circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" stroke="{color}" stroke-width="{stroke}" 
            stroke-dasharray="{circumference}" stroke-dashoffset="{offset}" stroke-linecap="round" transform="rotate(-90 {cx} {cy})" />
    <text x="{cx}" y="{cy+5}" text-anchor="middle" font-family="sans-serif" font-weight="bold" font-size="14" fill="{THEME['text_main']}">{percent}%</text>
    '''

def make_sparkline(width, height):
    # Generate a smooth-ish random curve
    points = []
    steps = 10
    step_w = width / (steps - 1)
    
    prev_y = height / 2
    path_d = f"M 0 {height}" # Start bottom left
    
    line_points = []
    for i in range(steps):
        x = i * step_w
        # Randomize y but keep it somewhat centered
        y = random.randint(10, height - 10)
        # Smoothing (simple average)
        y = (y + prev_y) / 2
        prev_y = y
        line_points.append(f"{x},{y}")
    
    # Create the area path
    path_d += " L " + " L ".join(line_points) + f" L {width} {height} Z"
    
    # Create the stroke path
    stroke_d = "M " + " L ".join(line_points)
    
    return f'''
    <path d="{path_d}" fill="{THEME['graph_fill']}" />
    <path d="{stroke_d}" fill="none" stroke="{THEME['accent_1']}" stroke-width="2" />
    '''

def create_svg(data):
    stats = data['stats']
    languages = data['languages']
    
    # Full Width Config
    width = 840  # Wider
    height = 400
    padding = 0  # No outer padding
    
    svg = f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg">
    <style>
        .text {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; fill: {THEME['text_main']}; }}
        .text-dim {{ fill: {THEME['text_dim']}; }}
        .card {{ fill: {THEME['card_bg']}; stroke: {THEME['border']}; stroke-width: 1; }}
    </style>
    <rect width="{width}" height="{height}" fill="{THEME['bg']}" rx="0"/>
    '''

    # --- LEFT COLUMN: Identity & Stats (40% width) ---
    col1_w = 340
    
    # Card 1: Profile (Top Left)
    svg += f'''
    <g transform="translate(0, 0)">
        <rect width="{col1_w}" height="195" class="card" rx="20"/>
        
        <!-- Avatar / Icon Placeholder -->
        <circle cx="50" cy="50" r="25" fill="{THEME['border']}"/>
        <text x="50" y="58" text-anchor="middle" font-size="20">⚡</text>
        
        <text x="90" y="45" class="text" font-size="24" font-weight="bold">{GITHUB_USERNAME}</text>
        <text x="90" y="70" class="text-dim" font-size="14">Full Stack Developer</text>
        
        <!-- Big Stats Row -->
        <g transform="translate(30, 110)">
            <text x="0" y="0" class="text-dim" font-size="12">Repositories</text>
            <text x="0" y="25" class="text" font-size="24" font-weight="bold">{stats['total_repos']}</text>
            
            <text x="100" y="0" class="text-dim" font-size="12">Followers</text>
            <text x="100" y="25" class="text" font-size="24" font-weight="bold">{stats['followers']}</text>
            
            <text x="200" y="0" class="text-dim" font-size="12">Stars</text>
            <text x="200" y="25" class="text" font-size="24" font-weight="bold">{stats['total_stars']}</text>
        </g>
    </g>
    '''

    # Card 2: Languages (Bottom Left) - Radial Style
    svg += f'''
    <g transform="translate(0, 205)">
        <rect width="{col1_w}" height="195" class="card" rx="20"/>
        <text x="30" y="35" class="text" font-size="16" font-weight="bold">Top Skills</text>
        
        <!-- Radial Charts Container -->
        <g transform="translate(40, 60)">
    '''
    
    # Draw top 3 languages as circles
    for i, lang in enumerate(languages[:3]):
        cx = i * 100 + 35
        cy = 50
        svg += make_circle_chart(lang['percent'], 35, 6, lang['color'], cx, cy)
        svg += f'<text x="{cx}" y="{cy+55}" text-anchor="middle" class="text-dim" font-size="12">{lang["name"]}</text>'

    svg += '''
        </g>
    </g>
    '''

    # --- RIGHT COLUMN: Visuals (60% width) ---
    col2_x = 350
    col2_w = width - col2_x
    
    # Card 3: Activity Graph (Top Right)
    svg += f'''
    <g transform="translate({col2_x}, 0)">
        <rect width="{col2_w}" height="195" class="card" rx="20"/>
        <text x="30" y="35" class="text" font-size="16" font-weight="bold">Contribution Activity</text>
        <text x="200" y="35" class="text-dim" font-size="12" text-anchor="end">Last 30 Days</text>
        
        <!-- Area Graph -->
        <g transform="translate(0, 50)">
            {make_sparkline(col2_w, 145)}
        </g>
    </g>
    '''

    # Card 4: Date & System (Bottom Right)
    now = datetime.datetime.now()
    time_str = now.strftime("%H:%M")
    date_str = now.strftime("%d %B %Y")
    
    svg += f'''
    <g transform="translate({col2_x}, 205)">
        <rect width="{col2_w}" height="195" class="card" rx="20"/>
        
        <!-- Time Display -->
        <text x="30" y="140" class="text" font-size="64" font-weight="bold" letter-spacing="-2">{time_str}</text>
        <text x="35" y="170" class="text-dim" font-size="18">{date_str}</text>
        
        <!-- Decorative "System" Elements -->
        <rect x="{col2_w - 150}" y="30" width="120" height="60" rx="10" fill="{THEME['border']}" opacity="0.3"/>
        <text x="{col2_w - 90}" y="65" text-anchor="middle" class="text" font-size="14">System Online</text>
        <circle cx="{col2_w - 130}" cy="60" r="4" fill="#4ade80"/>
    </g>
    '''

    svg += "</svg>"
    return svg

def main():
    data = get_real_stats(GITHUB_USERNAME)
    svg_content = create_svg(data)
    
    with open(OUTPUT_FILE, "w") as f:
        f.write(svg_content)
    print(f"Generated {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
