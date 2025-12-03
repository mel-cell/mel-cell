import os
import datetime
import json
import urllib.request
import math
from string import Template

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

def get_github_stats(username):
    # Mock data - in a real implementation, fetch from GitHub API
    return {
        "total_stars": 120,
        "total_commits": 2138,
        "total_prs": 51,
        "total_issues": 12,
        "total_repos": 35,
        "contributed_to": 15,
        "longest_streak": 24,
        "current_streak": 5
    }

def get_language_stats(username):
    # Mock data - represents percentage or raw bytes
    return [
        {"name": "Python", "percent": 40, "color": "#3572A5"},
        {"name": "JavaScript", "percent": 30, "color": "#f1e05a"},
        {"name": "Go", "percent": 15, "color": "#00ADD8"},
        {"name": "HTML/CSS", "percent": 10, "color": "#e34c26"},
        {"name": "Other", "percent": 5, "color": "#ccc"}
    ]

def create_svg(stats, languages):
    width = 800
    height = 450 # Slightly taller for better spacing
    
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

    # Card 1: Profile Identity (Top Left) - 250x140
    svg += f'''
    <g transform="translate(20, 20)">
        <rect width="250" height="140" class="card"/>
        <text x="20" y="40" class="text" font-size="22" font-weight="bold">{GITHUB_USERNAME}</text>
        <text x="20" y="65" class="text-dim" font-size="14">Full Stack Developer</text>
        
        <line x1="20" y1="85" x2="230" y2="85" stroke="{THEME['border']}" stroke-width="1"/>
        
        <text x="20" y="115" class="text-dim" font-size="12">Repositories</text>
        <text x="230" y="115" class="text" font-size="16" font-weight="bold" text-anchor="end">{stats['total_repos']}</text>
    </g>
    '''

    # Card 2: Key Metrics (Top Right) - 510x140
    # Grid of 4 big stats
    svg += f'''
    <g transform="translate(290, 20)">
        <rect width="490" height="140" class="card"/>
        
        <!-- Stat 1: Commits -->
        <g transform="translate(30, 35)">
            <text x="0" y="0" class="text-dim" font-size="12">Total Commits</text>
            <text x="0" y="25" class="text" font-size="28" font-weight="bold">{stats['total_commits']}</text>
        </g>
        
        <!-- Stat 2: Stars -->
        <g transform="translate(150, 35)">
            <text x="0" y="0" class="text-dim" font-size="12">Stars Earned</text>
            <text x="0" y="25" class="text" font-size="28" font-weight="bold">{stats['total_stars']}</text>
        </g>
        
        <!-- Stat 3: PRs -->
        <g transform="translate(270, 35)">
            <text x="0" y="0" class="text-dim" font-size="12">Pull Requests</text>
            <text x="0" y="25" class="text" font-size="28" font-weight="bold">{stats['total_prs']}</text>
        </g>
        
        <!-- Stat 4: Issues -->
        <g transform="translate(390, 35)">
            <text x="0" y="0" class="text-dim" font-size="12">Issues Solved</text>
            <text x="0" y="25" class="text" font-size="28" font-weight="bold">{stats['total_issues']}</text>
        </g>
        
        <!-- Divider -->
        <line x1="30" y1="80" x2="460" y2="80" stroke="{THEME['border']}" stroke-width="1"/>
        
        <!-- Bottom Row of Stats (Smaller) -->
        <g transform="translate(30, 110)">
             <text x="0" y="0" class="text-dim" font-size="12">Contributed to <tspan fill="{THEME['text_main']}" font-weight="bold">{stats['contributed_to']} Repos</tspan></text>
             <text x="240" y="0" class="text-dim" font-size="12">Current Streak <tspan fill="{THEME['text_main']}" font-weight="bold">{stats['current_streak']} Days</tspan></text>
        </g>
    </g>
    '''

    # --- ROW 2 ---

    # Card 3: Top Languages (Bottom Left) - 360x250
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

    # Card 4: Contribution Reach / Activity (Bottom Right) - 400x250
    # Visualizing activity as a "Heatmap" style grid (Mocked)
    svg += f'''
    <g transform="translate(400, 180)">
        <rect width="380" height="250" class="card"/>
        <text x="20" y="40" class="text" font-size="18" font-weight="bold">Contribution Activity</text>
        <text x="20" y="60" class="text-dim" font-size="12">Last 3 Months</text>
        
        <!-- Mock Heatmap Grid -->
        <g transform="translate(20, 80)">
    '''
    
    # Generate a 14x7 grid of squares
    for col in range(14):
        for row in range(7):
            # Random opacity for effect
            opacity = 0.2
            if (col + row) % 3 == 0: opacity = 0.6
            if (col * row) % 5 == 0: opacity = 0.9
            if (col + row) % 7 == 0: opacity = 0.1
            
            color = THEME['accent']
            svg += f'<rect x="{col * 24}" y="{row * 24}" width="18" height="18" fill="{color}" opacity="{opacity}" rx="2"/>'

    svg += '''
        </g>
    </g>
    '''

    svg += "</svg>"
    return svg

def main():
    stats = get_github_stats(GITHUB_USERNAME)
    languages = get_language_stats(GITHUB_USERNAME)
    svg_content = create_svg(stats, languages)
    
    with open(OUTPUT_FILE, "w") as f:
        f.write(svg_content)
    print(f"Generated {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
