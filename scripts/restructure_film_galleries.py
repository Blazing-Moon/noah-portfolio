"""
Replaces each film page's horizontal scroll gallery with a two-column layout:
description on the left, vertical stack of up to 3 thumbnails on the right.

Pages with no gallery are left untouched.
"""

import re, os, glob

FILMS_DIR = os.path.join(os.path.dirname(__file__), '..', 'films')

# Match a single <button class="detail-gallery-thumb" ...>...</button> block
THUMB_RE = re.compile(
    r'<button[^>]*class="detail-gallery-thumb"[^>]*>.*?</button>',
    re.DOTALL
)

# Match the whole <div class="detail-gallery">...</div> block
GALLERY_RE = re.compile(
    r'\n?    <div class="detail-gallery">.*?</div>\n?    </div>\n?  </div>',
    re.DOTALL
)

def extract_gallery_block(html):
    """Return (start, end) indices of the detail-gallery div, or None."""
    start = html.find('    <div class="detail-gallery">')
    if start == -1:
        return None
    # Walk forward counting open/close divs to find the matching close
    depth = 0
    i = start
    while i < len(html):
        open_pos = html.find('<div', i)
        close_pos = html.find('</div>', i)
        if open_pos == -1 and close_pos == -1:
            break
        if open_pos != -1 and (close_pos == -1 or open_pos < close_pos):
            depth += 1
            i = open_pos + 4
        else:
            depth -= 1
            i = close_pos + 6
            if depth == 0:
                return (start, i)
    return None

def extract_detail_body(html):
    """Return (start, end) indices of the detail-body div, or None."""
    start = html.find('    <div class="detail-body">')
    if start == -1:
        return None
    depth = 0
    i = start
    while i < len(html):
        open_pos = html.find('<div', i)
        close_pos = html.find('</div>', i)
        if open_pos == -1 and close_pos == -1:
            break
        if open_pos != -1 and (close_pos == -1 or open_pos < close_pos):
            depth += 1
            i = open_pos + 4
        else:
            depth -= 1
            i = close_pos + 6
            if depth == 0:
                return (start, i)
    return None

def clean_thumb(btn_html):
    """Strip scroll-snap-align inline style if present, normalise whitespace."""
    return btn_html.strip()

def transform(html, filename):
    body_span = extract_detail_body(html)
    gallery_span = extract_gallery_block(html)

    if not gallery_span:
        print(f"  skip (no gallery): {filename}")
        return html

    gallery_html = html[gallery_span[0]:gallery_span[1]]
    thumbs = THUMB_RE.findall(gallery_html)[:3]

    if not thumbs:
        # Gallery div present but empty — just remove it
        new_html = html[:gallery_span[0]] + html[gallery_span[1]:]
        print(f"  removed empty gallery: {filename}")
        return new_html

    body_html = html[body_span[0]:body_span[1]]

    side_thumbs = "\n      ".join(clean_thumb(t) for t in thumbs)
    side_gallery = (
        '    <div class="detail-side-gallery">\n'
        f'      {side_thumbs}\n'
        '    </div>'
    )

    columns_block = (
        '    <div class="detail-columns">\n'
        f'    {body_html}\n'
        f'{side_gallery}\n'
        '    </div>'
    )

    # Replace from start of detail-body through end of detail-gallery
    new_html = html[:body_span[0]] + columns_block + html[gallery_span[1]:]
    print(f"  restructured ({len(thumbs)} thumbs): {filename}")
    return new_html

files = sorted(glob.glob(os.path.join(FILMS_DIR, '*.html')))
for path in files:
    fname = os.path.basename(path)
    with open(path, 'r', encoding='utf-8') as f:
        original = f.read()
    updated = transform(original, fname)
    if updated != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(updated)

print("Done.")
