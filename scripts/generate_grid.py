import os
import datetime
import json
import urllib.request
import math
from collections import Counter

# Configuration
GITHUB_USERNAME = "mel-cell"
OUTPUT_FILE = "assets/grid.svg"
THEME = {
    "bg": "#0d1117",
    "card_bg": "#161b22",
    "text_main": "#ffffff",
    "text_dim": "#8b949e",
    "border": "#30363d",
    "accent": "#ffffff",
    "bar_bg": "#21262d"
}

def fetch_json(url):
    try:
        req = urllib.request.Request(url)
        # Add User-Agent to avoid 403 Forbidden
        req.add_header('User-Agent', 'Python-Script')
        
        # Use GITHUB_TOKEN if available (for higher rate limits in Actions)
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
        # Fallback if API fails
        return {
            "stats": {
                "total_stars": 0,
                "total_forks": 0,
                "followers": 0,
                "total_repos": 0,
                "contributed_to": 0,
                "current_streak": 0
            },
            "languages": []
        }

    # Calculate Stats
    total_stars = sum(repo['stargazers_count'] for repo in repos_data)
    total_forks = sum(repo['forks_count'] for repo in repos_data)
    
    # Calculate Languages
    langs = [repo['language'] for repo in repos_data if repo['language']]
    lang_counts = Counter(langs)
    total_langs = sum(lang_counts.values())
    
    top_languages = []
    colors = {
        "Python": "#3572A5", "JavaScript": "#f1e05a", "Go": "#00ADD8", 
        "HTML": "#e34c26", "CSS": "#563d7c", "Java": "#b07219",
        "TypeScript": "#2b7489", "Vue": "#41b883", "Shell": "#89e051",
        "C++": "#f34b7d", "C": "#555555", "PHP": "#4F5D95"
    }
    
    for lang, count in lang_counts.most_common(5):
        percent = math.floor((count / total_langs) * 100)
        top_languages.append({
            "name": lang,
            "percent": percent,
            "color": colors.get(lang, "#ccc")
        })

    return {
        "stats": {
            "total_stars": total_stars,
            "total_forks": total_forks,
            "followers": user_data['followers'],
            "total_repos": user_data['public_repos'],
            "contributed_to": 0, # Hard to get via simple API
            "current_streak": 0  # Hard to get via simple API
        },
        "languages": top_languages
    }

def create_svg(data):
    stats = data['stats']
    languages = data['languages']
    
    width = 800
    height = 450
    
    svg = f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg">
    <style>
        .text {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; fill: {THEME['text_main']}; }}
        .text-dim {{ fill: {THEME['text_dim']}; }}
        .text-accent {{ fill: {THEME['accent']}; }}
        .card {{ fill: {THEME['card_bg']}; stroke: {THEME['border']}; stroke-width: 1; rx: 10; }}
        .bar-bg {{ fill: {THEME['bar_bg']}; rx: 4; }}
    </style>
    <rect width="{width}" height="{height}" fill="{THEME['bg']}" rx="15"/>
    '''

    # --- ROW 1 ---

    # Card 1: Profile Identity
    svg += f'''
    <g transform="translate(20, 20)">
        <rect width="250" height="140" class="card"/>
        <text x="20" y="40" class="text" font-size="22" font-weight="bold">{GITHUB_USERNAME}</text>
        <text x="20" y="65" class="text-dim" font-size="14">Full Stack Developer</text>
        
        <line x1="20" y1="85" x2="230" y2="85" stroke="{THEME['border']}" stroke-width="1"/>
        
        <text x="20" y="115" class="text-dim" font-size="12">Public Repos</text>
        <text x="230" y="115" class="text" font-size="16" font-weight="bold" text-anchor="end">{stats['total_repos']}</text>
    </g>
    '''

    # Card 2: Key Metrics
    svg += f'''
    <g transform="translate(290, 20)">
        <rect width="490" height="140" class="card"/>
        
        <!-- Stat 1: Stars -->
        <g transform="translate(30, 35)">
            <text x="0" y="0" class="text-dim" font-size="12">Total Stars</text>
            <text x="0" y="25" class="text" font-size="28" font-weight="bold">{stats['total_stars']}</text>
        </g>
        
        <!-- Stat 2: Forks -->
        <g transform="translate(150, 35)">
            <text x="0" y="0" class="text-dim" font-size="12">Total Forks</text>
            <text x="0" y="25" class="text" font-size="28" font-weight="bold">{stats['total_forks']}</text>
        </g>
        
        <!-- Stat 3: Followers -->
        <g transform="translate(270, 35)">
            <text x="0" y="0" class="text-dim" font-size="12">Followers</text>
            <text x="0" y="25" class="text" font-size="28" font-weight="bold">{stats['followers']}</text>
        </g>
        
        <!-- Divider -->
        <line x1="30" y1="80" x2="460" y2="80" stroke="{THEME['border']}" stroke-width="1"/>
        
        <g transform="translate(30, 110)">
             <text x="0" y="0" class="text-dim" font-size="12">Data updated automatically via <tspan fill="{THEME['text_main']}" font-weight="bold">GitHub Actions</tspan></text>
        </g>
    </g>
    '''

    # --- ROW 2 ---

    # Card 3: Top Languages
    svg += f'''
    <g transform="translate(20, 180)">
        <rect width="360" height="250" class="card"/>
        <text x="20" y="40" class="text" font-size="18" font-weight="bold">Top Languages</text>
        
        <g transform="translate(20, 70)">
    '''
    
    y_offset = 0
    for lang in languages:
        svg += f'''
            <g transform="translate(0, {y_offset})">
                <text x="0" y="0" class="text" font-size="12">{lang['name']}</text>
                <text x="320" y="0" class="text-dim" font-size="12" text-anchor="end">{lang['percent']}%</text>
                <rect x="0" y="10" width="320" height="8" class="bar-bg"/>
                <rect x="0" y="10" width="{3.2 * lang['percent']}" height="8" fill="{lang['color']}" rx="4"/>
            </g>
        '''
        y_offset += 35

    svg += '''
        </g>
    </g>
    '''

    # Card 4: Contribution Activity (Heatmap Visual)
    svg += f'''
    <g transform="translate(400, 180)">
        <rect width="380" height="250" class="card"/>
        <text x="20" y="40" class="text" font-size="18" font-weight="bold">Activity Visual</text>
        <text x="20" y="60" class="text-dim" font-size="12">Recent Activity Pattern</text>
        
        <g transform="translate(20, 80)">
    '''
    
    # Generate a decorative grid pattern
    import random
    random.seed(datetime.datetime.now().day) # Change pattern daily
    
    for col in range(14):
        for row in range(7):
            opacity = 0.1
            if random.random() > 0.7: opacity = 0.6
            if random.random() > 0.9: opacity = 0.9
            
            color = THEME['accent']
            svg += f'<rect x="{col * 24}" y="{row * 24}" width="18" height="18" fill="{color}" opacity="{opacity}" rx="2"/>'

    svg += '''
        </g>
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
