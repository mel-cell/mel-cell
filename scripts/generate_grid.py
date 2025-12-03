import os
import datetime
import json
import urllib.request
import math
import random
import base64
from collections import Counter

# Configuration
GITHUB_USERNAME = "mel-cell"
OUTPUT_FILE = "assets/grid.svg"

# Monochrome Ultra Premium Theme
THEME = {
    "bg": "#050505",          # Almost Black
    "card_bg": "#111111",     # Very Dark Gray
    "text_main": "#ffffff",
    "text_dim": "#888888",
    "border": "#222222",
    # Monochrome Palette for Chart
    "palette": ["#ffffff", "#dddddd", "#bbbbbb", "#999999", "#777777", "#555555", "#333333"]
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

def get_local_image_base64(path):
    try:
        if os.path.exists(path):
            with open(path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode()
    except Exception as e:
        print(f"Error reading image {path}: {e}")
    return None

def get_real_stats(username):
    user_url = f"https://api.github.com/users/{username}"
    repos_url = f"https://api.github.com/users/{username}/repos?per_page=100&type=owner"
    
    user_data = fetch_json(user_url)
    repos_data = fetch_json(repos_url)
    
    if not user_data or not repos_data:
        return {
            "stats": {"total_stars": 0, "total_forks": 0, "followers": 0, "total_repos": 0, "avatar": ""},
            "languages": []
        }

    total_stars = sum(repo['stargazers_count'] for repo in repos_data)
    total_forks = sum(repo['forks_count'] for repo in repos_data)
    
    # Fetch Local Image
    avatar_b64 = get_local_image_base64("assets/image.png")
    
    # Get ALL languages
    langs = []
    for repo in repos_data:
        if repo['language']:
            langs.append(repo['language'])
            
    lang_counts = Counter(langs)
    total_langs = sum(lang_counts.values())
    
    top_languages = []
    # Take top 6, group rest as "Others"
    sorted_langs = lang_counts.most_common()
    
    current_sum = 0
    for i, (lang, count) in enumerate(sorted_langs[:6]):
        percent = (count / total_langs) * 100
        top_languages.append({
            "name": lang,
            "percent": percent,
            "color": THEME['palette'][i]
        })
        current_sum += percent
        
    if len(sorted_langs) > 6:
        top_languages.append({
            "name": "Others",
            "percent": 100 - current_sum,
            "color": THEME['palette'][-1]
        })

    return {
        "stats": {
            "total_stars": total_stars,
            "total_forks": total_forks,
            "followers": user_data['followers'],
            "total_repos": user_data['public_repos'],
            "bio": user_data.get('bio', 'Full Stack Developer'),
            "name": user_data.get('name', username),
            "avatar": avatar_b64
        },
        "languages": top_languages
    }

def polar_to_cartesian(cx, cy, radius, angle_in_degrees):
    angle_in_radians = (angle_in_degrees - 90) * math.pi / 180.0
    return {
        "x": cx + (radius * math.cos(angle_in_radians)),
        "y": cy + (radius * math.sin(angle_in_radians))
    }

def describe_arc(x, y, radius, start_angle, end_angle):
    start = polar_to_cartesian(x, y, radius, end_angle)
    end = polar_to_cartesian(x, y, radius, start_angle)
    large_arc_flag = "0" if end_angle - start_angle <= 180 else "1"
    return f"M {x} {y} L {start['x']} {start['y']} A {radius} {radius} 0 {large_arc_flag} 0 {end['x']} {end['y']} Z"

def make_donut_chart(languages, cx, cy, radius):
    svg_paths = ""
    start_angle = 0
    
    # Sort by percent desc to make it look neat
    languages.sort(key=lambda x: x['percent'], reverse=True)
    
    for lang in languages:
        degrees = (lang['percent'] / 100) * 360
        end_angle = start_angle + degrees
        
        # Don't draw tiny slices
        if degrees > 1:
            path_d = describe_arc(cx, cy, radius, start_angle, end_angle)
            svg_paths += f'<path d="{path_d}" fill="{lang["color"]}" stroke="{THEME["card_bg"]}" stroke-width="2" />'
        
        start_angle = end_angle
        
    # Inner circle to make it a donut
    svg_paths += f'<circle cx="{cx}" cy="{cy}" r="{radius * 0.6}" fill="{THEME["card_bg"]}" />'
    
    # Center Text
    svg_paths += f'''
    <text x="{cx}" y="{cy-5}" text-anchor="middle" fill="{THEME['text_main']}" font-size="24" font-weight="bold">{len(languages)}</text>
    <text x="{cx}" y="{cy+15}" text-anchor="middle" fill="{THEME['text_dim']}" font-size="10">LANGS</text>
    '''
    
    return svg_paths

def make_dense_sparkline(width, height):
    points = []
    steps = 40 # Increased density
    step_w = width / (steps - 1)
    
    prev_y = height / 2
    path_d = f"M 0 {height}" 
    
    line_points = []
    for i in range(steps):
        x = i * step_w
        # More chaotic movement
        change = random.randint(-20, 20)
        y = prev_y + change
        # Clamp
        y = max(10, min(height - 10, y))
        
        prev_y = y
        line_points.append(f"{x},{y}")
    
    path_d += " L " + " L ".join(line_points) + f" L {width} {height} Z"
    stroke_d = "M " + " L ".join(line_points)
    
    return f'''
    <defs>
        <linearGradient id="grad1" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:{THEME['text_main']};stop-opacity:0.2" />
            <stop offset="100%" style="stop-color:{THEME['text_main']};stop-opacity:0" />
        </linearGradient>
    </defs>
    <path d="{path_d}" fill="url(#grad1)" />
    <path d="{stroke_d}" fill="none" stroke="{THEME['text_main']}" stroke-width="1.5" />
    '''

def create_svg(data):
    stats = data['stats']
    languages = data['languages']
    
    # Bento Grid Layout Config
    # Canvas: 1000 x 600
    width = 1000
    height = 600
    gap = 20
    
    svg = f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
    <style>
        .text {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; fill: {THEME['text_main']}; }}
        .text-dim {{ fill: {THEME['text_dim']}; }}
        .card {{ fill: {THEME['card_bg']}; }}
        .label {{ font-size: 12px; fill: {THEME['text_dim']}; }}
        .value {{ font-size: 32px; font-weight: bold; fill: {THEME['text_main']}; }}
    </style>
    <rect width="{width}" height="{height}" fill="{THEME['bg']}" rx="0"/>
    '''

    # --- GRID DEFINITIONS ---
    # Col 1: x=0, w=320
    # Col 2: x=340, w=320 (Split into two 150s or one 320)
    # Col 3: x=680, w=320
    
    # Row 1 Height: 320
    # Row 2 Height: 260
    # Y2 Start: 340

    # 1. IMAGE CARD (Top Left) - Full Cover
    # x=0, y=0, w=320, h=320
    img_b64 = stats.get('avatar', '')
    img_content = f'<image x="0" y="0" width="320" height="320" preserveAspectRatio="xMidYMid slice" xlink:href="data:image/png;base64,{img_b64}" clip-path="url(#clip1)" />' if img_b64 else ''
    
    svg += f'''
    <defs><clipPath id="clip1"><rect width="320" height="320" rx="24"/></clipPath></defs>
    <g transform="translate(0, 0)">
        <rect width="320" height="320" class="card" rx="24"/>
        {img_content}
        <!-- Overlay Gradient -->
        <rect width="320" height="320" rx="24" fill="url(#imgOverlay)" style="mix-blend-mode: multiply;"/>
        <defs>
            <linearGradient id="imgOverlay" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="black" stop-opacity="0"/>
                <stop offset="100%" stop-color="black" stop-opacity="0.6"/>
            </linearGradient>
        </defs>
    </g>
    '''

    # 2. STATS 1 (Top Middle Left) - Stars
    # x=340, y=0, w=150, h=150
    svg += f'''
    <g transform="translate(340, 0)">
        <rect width="150" height="150" class="card" rx="24"/>
        <text x="20" y="35" class="label">Total Stars</text>
        <text x="20" y="80" class="value">{stats['total_stars']}</text>
        <text x="20" y="130" font-size="10" fill="{THEME['text_dim']}">All Repos</text>
    </g>
    '''

    # 3. STATS 2 (Top Middle Right) - Forks
    # x=510, y=0, w=150, h=150
    svg += f'''
    <g transform="translate(510, 0)">
        <rect width="150" height="150" class="card" rx="24"/>
        <text x="20" y="35" class="label">Total Forks</text>
        <text x="20" y="80" class="value">{stats['total_forks']}</text>
        <text x="130" y="35" text-anchor="end" font-size="16">⑂</text>
    </g>
    '''

    # 4. ACTIVITY (Middle Center) - Wide
    # x=340, y=170, w=320, h=150
    svg += f'''
    <g transform="translate(340, 170)">
        <rect width="320" height="150" class="card" rx="24"/>
        <text x="20" y="30" class="label">Contribution Activity</text>
        <g transform="translate(0, 40)">
            {make_dense_sparkline(320, 110)}
        </g>
    </g>
    '''

    # 5. MARKET SHARE / LANGUAGES (Top Right) - Large
    # x=680, y=0, w=320, h=320
    svg += f'''
    <g transform="translate(680, 0)">
        <rect width="320" height="320" class="card" rx="24"/>
        <text x="25" y="35" class="label">Language Share</text>
        
        <!-- Donut Chart -->
        <g transform="translate(160, 160)">
            {make_donut_chart(languages, 0, 0, 100)}
        </g>
        
        <!-- Legend (Bottom) -->
        <g transform="translate(25, 280)">
    '''
    
    # Simple Legend for top 3
    for i, lang in enumerate(languages[:3]):
        svg += f'''
        <circle cx="{i*90}" cy="0" r="4" fill="{lang['color']}"/>
        <text x="{i*90 + 10}" y="4" font-size="10" fill="{THEME['text_dim']}">{lang['name']}</text>
        '''
        
    svg += '''
        </g>
    </g>
    '''

    # --- ROW 2 ---
    
    # 6. PROFILE INFO (Bottom Left) - Wide
    # x=0, y=340, w=490, h=260
    svg += f'''
    <g transform="translate(0, 340)">
        <rect width="490" height="260" class="card" rx="24"/>
        <text x="30" y="50" class="text" font-size="32" font-weight="bold">{stats['name']}</text>
        <text x="30" y="80" class="text-dim" font-size="18">@{GITHUB_USERNAME}</text>
        
        <text x="30" y="140" class="text" font-size="16" width="400">{stats['bio']}</text>
        
        <rect x="30" y="200" width="120" height="30" rx="15" fill="#ffffff" fill-opacity="0.1"/>
        <text x="90" y="220" text-anchor="middle" font-size="12" fill="white">Available</text>
    </g>
    '''

    # 7. VERTICAL STAT (Bottom Middle) - Followers
    # x=510, y=340, w=150, h=260
    svg += f'''
    <g transform="translate(510, 340)">
        <rect width="150" height="260" class="card" rx="24"/>
        <text x="75" y="40" text-anchor="middle" class="label">Followers</text>
        <text x="75" y="130" text-anchor="middle" font-size="48" font-weight="bold" fill="{THEME['text_main']}">{stats['followers']}</text>
        
        <!-- Decorative Circle -->
        <circle cx="75" cy="200" r="20" stroke="{THEME['text_dim']}" stroke-width="1" fill="none"/>
        <circle cx="75" cy="200" r="10" fill="{THEME['text_main']}"/>
    </g>
    '''

    # 8. SYSTEM / DATE (Bottom Right)
    # x=680, y=340, w=320, h=260
    now = datetime.datetime.now()
    time_str = now.strftime("%H:%M")
    date_str = now.strftime("%A")
    date_num = now.strftime("%d %b")
    
    svg += f'''
    <g transform="translate(680, 340)">
        <rect width="320" height="260" class="card" rx="24"/>
        
        <text x="30" y="100" font-size="80" font-weight="bold" fill="{THEME['text_main']}" letter-spacing="-4">{time_str}</text>
        <text x="35" y="140" font-size="24" fill="{THEME['text_dim']}">{date_str}, {date_num}</text>
        
        <rect x="260" y="30" width="30" height="30" rx="8" fill="#222"/>
        <path d="M 275 38 L 275 52 M 268 45 L 282 45" stroke="white" stroke-width="2"/>
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
