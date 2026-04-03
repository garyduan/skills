#!/usr/bin/env python3
"""Parse WordPress WXR export, split WPGlobus multilingual content."""

import xml.etree.ElementTree as ET
import re, json, html

NS = {
    'content': 'http://purl.org/rss/1.0/modules/content/',
    'wp': 'http://wordpress.org/export/1.2/',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'excerpt': 'http://wordpress.org/export/1.2/excerpt/',
}

def split_wpglobus(text):
    """Split {:en}...{:}{:zh}...{:} into (en, zh) tuple."""
    if not text:
        return ('', '')
    en = ''
    zh = ''
    # Find {:en}...{:} and {:zh}...{:}
    en_match = re.search(r'\{:en\}(.*?)(?:\{:\}|\{:zh\})', text, re.DOTALL)
    zh_match = re.search(r'\{:zh\}(.*?)(?:\{:\}|\{:en\}|$)', text, re.DOTALL)
    if en_match:
        en = en_match.group(1).strip()
    if zh_match:
        zh = zh_match.group(1).strip()
    # If no WPGlobus markers, detect language by character ratio
    if not en and not zh and '{:' not in text:
        cleaned = text.strip()
        if cleaned:
            zh_chars = len(re.findall(r'[\u4e00-\u9fff]', cleaned))
            total_alpha = len(re.findall(r'[a-zA-Z]', cleaned))
            # If more than 20% of text chars are Chinese, treat as ZH
            if zh_chars > 0 and (total_alpha == 0 or zh_chars / (zh_chars + total_alpha) > 0.2):
                zh = cleaned
            else:
                en = cleaned
    return (en, zh)

def strip_html(text):
    """Remove HTML tags and shortcodes, decode entities."""
    if not text:
        return ''
    # Remove WordPress shortcodes like [singlepic ...] [gallery ...]
    text = re.sub(r'\[/?[a-zA-Z_]+[^\]]*\]', '', text)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Decode HTML entities
    text = html.unescape(text)
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

tree = ET.parse('/mnt/user-data/uploads/wavelet.xml')
root = tree.getroot()
channel = root.find('channel')

posts = []
for item in channel.findall('item'):
    post_type = item.find('wp:post_type', NS)
    status = item.find('wp:status', NS)
    if post_type is None or post_type.text != 'post':
        continue
    if status is None or status.text != 'publish':
        continue

    title_raw = item.find('title').text or ''
    link = item.find('link').text or ''
    content_el = item.find('content:encoded', NS)
    content_raw = content_el.text if content_el is not None else ''

    en_title, zh_title = split_wpglobus(title_raw)
    en_content_html, zh_content_html = split_wpglobus(content_raw)
    en_content = strip_html(en_content_html)
    zh_content = strip_html(zh_content_html)

    # Get tags
    tags = []
    cats = []
    for cat in item.findall('category'):
        domain = cat.get('domain', '')
        name = cat.text or ''
        if domain == 'post_tag':
            tags.append(name)
        elif domain == 'category':
            cats.append(name)

    posts.append({
        'url': link,
        'en_title': en_title,
        'zh_title': zh_title,
        'en_content': en_content,
        'zh_content': zh_content,
        'tags': tags,
        'categories': cats,
    })

# Save
with open('/home/claude/posts.json', 'w', encoding='utf-8') as f:
    json.dump(posts, f, ensure_ascii=False, indent=2)

print(f"Extracted {len(posts)} posts")
print(f"Posts with EN content: {sum(1 for p in posts if p['en_content'])}")
print(f"Posts with ZH content: {sum(1 for p in posts if p['zh_content'])}")
print(f"Posts with both: {sum(1 for p in posts if p['en_content'] and p['zh_content'])}")
print()

# Show first 5 posts summary
for i, p in enumerate(posts[:5]):
    print(f"--- Post {i+1} ---")
    print(f"  EN title: {p['en_title'][:80]}")
    print(f"  ZH title: {p['zh_title'][:80]}")
    print(f"  URL: {p['url']}")
    print(f"  EN content length: {len(p['en_content'])}")
    print(f"  ZH content length: {len(p['zh_content'])}")
    print(f"  Tags: {p['tags']}")
    print()

# Show all unique tags
all_tags = set()
for p in posts:
    all_tags.update(p['tags'])
print(f"All tags ({len(all_tags)}): {sorted(all_tags)}")
