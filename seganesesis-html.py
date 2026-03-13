#!/usr/bin/env python3
"""
genesis_games_blastem Games Grid Generator
Creates an Xemu-style grid website from your genesis_games_blastem games JSON
Shows title as text overlay when image fails to load
"""

import json
import os
from datetime import datetime

# Configuration
JSON_FILE = "genesis_games_blastem.json"
OUTPUT_HTML = "genesis_games_blastem.html"
PLACEHOLDER_IMAGE = "https://raw.githubusercontent.com/igiteam/segagenesis-covers/refs/heads/master/gamecube-cover-default.png"
RAW_BASE_URL = "https://raw.githubusercontent.com/igiteam/segagenesis-covers/tree/master/Named_Boxarts"

def load_games_data():
    """Load games from JSON file and remove duplicates by TITLE"""
    if not os.path.exists(JSON_FILE):
        print(f"❌ Error: {JSON_FILE} not found!")
        print("Please run the cover downloader first to generate the JSON file.")
        return None
    
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        games = json.load(f)
    
    # Remove duplicates by TITLE (keep first occurrence)
    seen_titles = set()
    unique_games = []
    for game in games:
        title = game['title'].lower().strip()
        if title not in seen_titles:
            seen_titles.add(title)
            unique_games.append(game)
    
    if len(unique_games) < len(games):
        print(f"✅ Removed {len(games) - len(unique_games)} duplicates by title")
    
    print(f"✅ Loaded {len(unique_games)} unique games from {JSON_FILE}")
    return unique_games

def generate_html(games):
    """Generate the grid website HTML"""
    
    games.sort(key=lambda x: x['title'].lower())
    
    total_games = len(games)
    with_2d = sum(1 for g in games if g['cover_url'] != PLACEHOLDER_IMAGE)
    
    html = f"""<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Sega Genesis Games Collection</title>

  <link rel="icon" href="https://cdn.sdappnet.cloud/rtx/images/sega-genesis-icon.png" type="image/png">
  <link rel="apple-touch-icon" href="https://cdn.sdappnet.cloud/rtx/images/sega-genesis-icon.png" sizes="180x180">
  <link rel="icon" type="image/png" href="https://cdn.sdappnet.cloud/rtx/images/sega-genesis-icon.png" sizes="192x192">
  <link rel="icon" type="image/png" href="https://cdn.sdappnet.cloud/rtx/images/sega-genesis-icon.png" sizes="512x512">
  <meta itemprop="name" content="Sega Genesis Games Collection">
  <meta property="og:title" content="Sega Genesis Games Collection">
  <meta property="og:url" content="">
  <meta property="og:type" content="website">
  <meta name="twitter:title" content="Sega Genesis Games Collection">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="apple-touch-icon" href="https://cdn.sdappnet.cloud/rtx/images/sega-genesis-icon.png" sizes="180x180">

  <style>
    body {{
      background-color: #1a1a1a;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
      margin: 4px 20px;
      padding: 0;
    }}

    #results {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: 10px;
      max-width: 1400px;
      margin: 0 auto;
      background-color: #1a1a1a;
      margin-top: 4px;
      z-index: 1000;
    }}

    .title-card {{
      background: #2a2a2a;
      border-radius: 8px;
      overflow: hidden;
      transition: transform 0.2s;
    }}

    .title-card:hover {{
      transform: scale(1.05);
      z-index: 10;
    }}

    .title-card-link {{
      display: block;
      text-decoration: none;
      color: inherit;
    }}

    .title-card-container {{
      width: 100%;
      position: relative;
    }}

    .title-card-image-container {{
      width: 100%;
      aspect-ratio: 3/4;
      overflow: hidden;
      position: relative;
      background-color: #1a1a1a;
    }}

    .title-card-image-container img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: opacity 0.3s;
    }}

    .title-card-image-container .fallback-title {{
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      padding: 10px;
      box-sizing: border-box;
      background: linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 100%);
      color: #888;
      font-size: 14px;
      font-weight: 500;
      word-break: break-word;
      border: 1px solid #333;
    }}

    .fill-color-Playable {{
      background-color: #42991b !important;
      color: white !important;
      font-weight: 700 !important;
    }}

    .card-body {{
      flex: 1 1 auto;
      min-height: 1px;
      padding: 0.5rem 1.25rem !important;
    }}

    .text-center {{
      text-align: center !important;
    }}

    .py-1 {{
      padding-top: 0.25rem !important;
      padding-bottom: 0.25rem !important;
    }}

    .my-0 {{
      margin-top: 0 !important;
      margin-bottom: 0 !important;
    }}

    small {{
      font-size: 80%;
    }}

    /* Search container */
    #saved-search-container {{
      position: sticky;
      z-index: 10000;
      margin-left: auto;
      margin-right: auto;
      margin: 8px 0px;
    }}

    #saved-search-input {{
      padding: 10px;
      width: calc(100% - 20px);
      border: 1px solid #555;
      border-radius: 4px;
      background: #444;
      color: white;
      flex: 1;
    }}

    .search-row {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .icon {{
      width: 34px;
      height: 34px;
      border-radius: 4px;
      object-fit: cover;
    }}

    #saved-search-input::placeholder {{
      color: #aaa;
    }}

    #saved-results-count {{
      color: white;
      font-size: 14px;
      text-align: center;
      margin-top: 5px;
    }}

    /* Hide classes */
    .hidden-game {{
      display: none !important;
    }}

    .title-card.image-failed {{
      display: none !important;
    }}

    .title-card-link.hidden-game {{
      display: none !important;
    }}
  </style>
</head>

<body>
  <div id="saved-search-container">
    <div class="search-row">
      <img src="https://cdn.sdappnet.cloud/rtx/images/sega-genesis-icon.png" class="icon" alt="Sega Genesis logo">
      <input type="text" id="saved-search-input" placeholder="Search games...">
      <a href="https://www.ppsspp.org/" target="_blank">
        <img src="https://cdn.sdappnet.cloud/rtx/images/sega-genesis-controller.png" class="icon" alt="Sega Genesis">
      </a>
      <a href="https://cdn.sdappnet.cloud/rtx/sega-genesis_magazine.html" target="_blank">
        <img src="https://cdn.sdappnet.cloud/rtx/images/sega-genesis_magazine.png" class="icon" alt="Sega Genesis Magazine">
      </a>
    </div>
    <div id="saved-results-count"></div>
  </div>

  <div class="row" id="results">
"""

    for game in games:
        title = game['title'].replace('"', '&quot;')
        
        if game['cover_url'] != PLACEHOLDER_IMAGE:
            cover_url = game['cover_url']
            has_real_cover = True
        else:
            cover_url = PLACEHOLDER_IMAGE
            has_real_cover = False
        
        # If no real cover, show title overlay immediately
        title_display = "flex" if not has_real_cover else "none"
        
        html += f"""
        <div class="col px-1 mb-4 title-card" data-title-name="{title}" data-title-status="Play">
          <a target="_blank" rel="norefferer" href="https://github.com/igiteam/segagenesis-covers">
            <div class="mx-auto title-card-container">
              <div class="title-card-image-container" style="position: relative;">
                <img
                  src="{cover_url}"
                  loading="lazy"
                  title="{title}"
                  onerror="this.closest('.title-card').classList.add('image-failed');">
                <div class="fallback-title" style="display: {title_display};">{title}</div>
              </div>
              <div class="fill-color-Playable card-body text-center py-1 my-0"><small><strong>Play</strong></small></div>
            </div>
          </a>
        </div>"""

    html += f"""
  </div>

  <script>
    // Convert title cards to links for search
    function wrapCardsWithLinks() {{
      document.querySelectorAll('.title-card').forEach(card => {{
        // Skip if image failed
        if (card.classList.contains('image-failed')) return;

        const title = card.getAttribute('data-title-name');
        const status = card.getAttribute('data-title-status');

        // Remove existing inner link
        const existingInnerLink = card.querySelector('a');
        if (existingInnerLink) {{
          while (existingInnerLink.firstChild) {{
            card.insertBefore(existingInnerLink.firstChild, existingInnerLink);
          }}
          existingInnerLink.remove();
        }}

        let url_path = '';
        if (title) {{
          url_path = title
            .toLowerCase()
            .replace(/[^\\w\\s-]/g, '')
            .replace(/\\s+/g, '-')
            .replace(/-+/g, '-')
            .replace(/^-|-$/g, '');
        }}

        if (url_path) {{
          const link = document.createElement('a');
          link.href = 'https://meyt.netlify.app/search/' + url_path + ' sega genesis';
          link.className = 'title-card-link';
          link.rel = 'noopener noreferrer';
          link.target = '_blank';
          
          if (title) link.setAttribute('data-title-name', title);
          if (status) link.setAttribute('data-title-status', status);

          card.parentNode.insertBefore(link, card);
          link.appendChild(card);
        }}
      }});
    }}

    // Run link wrapping after a delay
    setTimeout(wrapCardsWithLinks, 500);

    // Search functionality - target title-card-link elements
    document.getElementById('saved-search-input').addEventListener('input', function (e) {{
      const searchTerm = e.target.value.toLowerCase();
      const links = document.querySelectorAll('.title-card-link');
      let count = 0;

      links.forEach(link => {{
        const title = link.getAttribute('data-title-name') || '';
        
        if (title.toLowerCase().includes(searchTerm) && searchTerm) {{
          link.classList.remove('hidden-game');
          count++;
        }} else if (searchTerm) {{
          link.classList.add('hidden-game');
        }} else {{
          link.classList.remove('hidden-game');
        }}
      }});

      document.getElementById('saved-results-count').textContent =
        searchTerm ? `Found ${{count}} game${{count !== 1 ? 's' : ''}}` : '';
    }});

    // Keyboard shortcut
    document.addEventListener('keydown', function(e) {{
      if (e.key === '/' && !document.getElementById('saved-search-input').matches(':focus')) {{
        e.preventDefault();
        document.getElementById('saved-search-input').focus();
      }}
    }});

    // Initial hide of any images that already failed
    document.querySelectorAll('.title-card img').forEach(img => {{
      if (img.complete && img.naturalHeight === 0) {{
        img.closest('.title-card').classList.add('image-failed');
      }}
    }});
  </script>
</body>

</html>
"""

    return html

def main():
    print("🎮 Sega Genesis Games Grid Generator (Xemu Style)")
    print("=" * 50)
    
    games = load_games_data()
    if not games:
        return
    
    print("🔄 Generating grid website...")
    html_content = generate_html(games)
    
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Website generated: {OUTPUT_HTML}")
    print(f"\n📊 Statistics:")
    print(f"   - Total games: {len(games)}")
    print(f"   - With covers: {sum(1 for g in games if g['cover_url'] != PLACEHOLDER_IMAGE)}")

if __name__ == "__main__":
    main()