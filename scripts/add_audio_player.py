"""
Restructures all .music-track <li> elements in index.html and music.html:
  - Adds data-sc-url attribute to each <li>
  - Wraps existing content in .track-main
  - Removes data-placeholder from buttons
  - Appends .track-scrubber-row with time display and range input
"""

import re, os

SC_URL = "https://soundcloud.com/noahgiesler/brothers-1"
BASE   = os.path.join(os.path.dirname(__file__), '..')

TRACK_RE = re.compile(
    r'( *)<li class="music-track">\n'
    r'\1  <button class="track-play-btn" (aria-label="Play [^"]+") data-placeholder>\n'
    r'\1    <span class="track-play-icon" aria-hidden="true">▶</span>\n'
    r'\1  </button>\n'
    r'\1  <div class="track-info">\n'
    r'\1    (<span class="track-title">[^<]+</span>)\n'
    r'\1    (<span class="track-sub">[^<]+</span>)\n'
    r'\1  </div>\n'
    r'\1  (<span class="track-dur">[^<]+</span>)\n'
    r'\1</li>',
    re.MULTILINE
)

def replacement(m):
    ind    = m.group(1)   # leading whitespace
    alabel = m.group(2)   # aria-label="Play ..."
    title  = m.group(3)
    sub    = m.group(4)
    dur    = m.group(5)
    return (
        f'{ind}<li class="music-track" data-sc-url="{SC_URL}">\n'
        f'{ind}  <div class="track-main">\n'
        f'{ind}    <button class="track-play-btn" {alabel}>\n'
        f'{ind}      <span class="track-play-icon" aria-hidden="true">▶</span>\n'
        f'{ind}    </button>\n'
        f'{ind}    <div class="track-info">\n'
        f'{ind}      {title}\n'
        f'{ind}      {sub}\n'
        f'{ind}    </div>\n'
        f'{ind}    {dur}\n'
        f'{ind}  </div>\n'
        f'{ind}  <div class="track-scrubber-row">\n'
        f'{ind}    <span class="track-time">0:00</span>\n'
        f'{ind}    <input type="range" class="track-scrubber" value="0" min="0" max="1000" step="1" aria-label="Seek">\n'
        f'{ind}  </div>\n'
        f'{ind}</li>'
    )

for fname in ('index.html', 'music.html'):
    path = os.path.join(BASE, fname)
    with open(path, 'r', encoding='utf-8') as f:
        src = f.read()
    updated, n = TRACK_RE.subn(replacement, src)
    if n:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(updated)
        print(f"  {fname}: {n} track(s) updated")
    else:
        print(f"  {fname}: no matches (already updated?)")
