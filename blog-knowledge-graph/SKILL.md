The XML exported using wordpress export function is provided. Use this to create the knowledge graph, with the following rules

1. Only extract the title, URL and content of the post
2. The website use multi-lingual plugin WPGlobal. Each post can have English and Chinese version, you should separate them.
3. Build independent English and Chinese graph
4. The knowledge graph should only be based on content of the graph, not title or URL
5. The post URL is used to create 'article' node

knowledge graph function

- Type filter toggles (country / place / article / wildlife / food / activity)
- Text search (EN + ZH)
- Highlight-on-click (show neighborhoods and links to neighbors)
- Language toggle (EN / 中文)
- Zoom + pan + drag
- Tooltip on hover
- Cross-destination edges as dashed red lines
- Single click the article nodes, highlight-neighborhood nodes; Double click on an article node, opens the blog post in a new tab.

---

## Step 0 — Parse WordPress XML Export

Use Python `xml.etree.ElementTree` to parse the WXR (WordPress eXtended RSS) export file.

### Key namespaces
```python
NS = {
    'content': 'http://purl.org/rss/1.0/modules/content/',
    'wp': 'http://wordpress.org/export/1.2/',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'excerpt': 'http://wordpress.org/export/1.2/excerpt/',
}
```

### Extraction rules
- Filter items by `<wp:post_type>post</wp:post_type>` AND `<wp:status>publish</wp:status>`
- Title is in `<title>` element
- Content is in `<content:encoded>` element
- URL is in `<link>` element
- Tags and categories are in `<category domain="post_tag">` and `<category domain="category">`

### WPGlobus splitting
Content and titles use the pattern `{:en}...{:}{:zh}...{:}`. Use regex to split:
```python
import re
def split_wpglobus(text):
    en_match = re.search(r'\{:en\}(.*?)(?:\{:\}|\{:zh\})', text, re.DOTALL)
    zh_match = re.search(r'\{:zh\}(.*?)(?:\{:\}|\{:en\}|$)', text, re.DOTALL)
    en = en_match.group(1).strip() if en_match else ''
    zh = zh_match.group(1).strip() if zh_match else ''
    # If no WPGlobus markers, detect language by character ratio
    if not en and not zh and '{:' not in text:
        cleaned = text.strip()
        if cleaned:
            zh_chars = len(re.findall(r'[\u4e00-\u9fff]', cleaned))
            total_alpha = len(re.findall(r'[a-zA-Z]', cleaned))
            if zh_chars > 0 and (total_alpha == 0 or zh_chars / (zh_chars + total_alpha) > 0.2):
                zh = cleaned
            else:
                en = cleaned
    return (en, zh)
```

**Important**: Not all posts use WPGlobus markers. Some posts (especially older ones or single-language posts) store Chinese content directly without `{:en}...{:}{:zh}...{:}` wrapping. Without language detection, these posts are misclassified as English. The 20% CJK character threshold reliably separates Chinese-dominant content from English content that may contain occasional CJK characters (e.g., transliterations).

### Node merge for spelling variants
The same entity may be spelled differently across posts (e.g., `卢卡索` and `卢克索` both mean Luxor in Chinese). Add all known variants as keys mapping to the same canonical name in the place dictionary:
```python
'卢卡索': '卢卡索', '卢克索': '卢卡索',  # both spellings → same node
```

### HTML/shortcode cleanup
Strip WordPress shortcodes (`[singlepic ...]`, `[gallery ...]`, etc.) and HTML tags before entity extraction:
```python
import html
def strip_html(text):
    text = re.sub(r'\[/?[a-zA-Z_]+[^\]]*\]', '', text)  # shortcodes
    text = re.sub(r'<[^>]+>', ' ', text)                   # HTML tags
    text = html.unescape(text)                              # entities
    text = re.sub(r'\s+', ' ', text).strip()                # whitespace
    return text
```

---

## Step 1 — Extract Entities

For each article, extract named entities from the body text:

| Entity Type | Examples | Node Color |
|-------------|----------|------------|
| `article` | Post titles | `#a78bfa` purple |
| `country` | Iceland, Faroe Islands, Greenland | `#3b82f6` blue |
| `place` | Kallur Lighthouse, Icefjord, Tórshavn | `#22c55e` green |
| `arts` | The Louvre, Musée d'Orsay, Sydney Opera House, Harpa Concert Hall | `#e879f9` magenta |
| `monument` | Pyramids of Giza, Acropolis, Machu Picchu, Notre-Dame, Chichén Itzá | `#fb5050` red |
| `activity` | Hiking, Photography, Ferry Travel | `#fb923c` orange |
| `wildlife` | Atlantic Puffins, Humpback Whales, Icebergs | `#2dd4bf` teal |
| `food` | Seafood Cuisine, Barbara Restaurant | `#facc15` yellow |

Node size encodes importance (connection count or explicit prominence). Articles default to `size: 14`, high-frequency entities scaled up.

### Entity type definitions
- **arts**: Museums, art galleries, theatres, opera houses, concert halls, and cultural performance venues. Named institutions you visit for art or performance.
- **monument**: Major historical monuments, ruins (古迹), temples, fortresses, castles, cathedrals, and ancient structures. Named historical sites of architectural or archaeological significance.
- **place**: Geographic locations — cities, neighborhoods, islands, lakes, trails, national parks. If it's primarily a geographic destination rather than a specific building/ruin, it's a place.

### Entity extraction approach
Use keyword-matching dictionaries for each entity type. For each post:
1. **Countries**: Match from post tags (lowercase) AND content keywords
2. **Places**: Match from content using keyword → canonical name mapping
3. **Arts, Monuments**: Match from content keywords, link to country via dedicated country mappings
4. **Activities, Wildlife, Food**: Match from content keywords

### Word-boundary matching for ambiguous keywords
Some short English keywords are substrings of common words (e.g., "lion" appears in "million", "pavilion", "medallion"; "sea lion" contains "lion"). Use word-boundary regex (`\b`) for these ambiguous keywords instead of simple substring `in` matching.

```python
import re

# Keywords that need word-boundary matching
_WORD_BOUNDARY_KW = {
    'lion':  re.compile(r'\blion\b', re.IGNORECASE),
    'lions': re.compile(r'\blions\b', re.IGNORECASE),
    'seal':  re.compile(r'\bseal\b', re.IGNORECASE),
    'bear':  re.compile(r'\bbear\b', re.IGNORECASE),
    'bears': re.compile(r'\bbears\b', re.IGNORECASE),
    'elk':   re.compile(r'\belk\b', re.IGNORECASE),
}

# Compound phrases that should suppress the shorter keyword
# e.g. "sea lion" should NOT also trigger "lion"
WILDLIFE_COMPOUND_EXCLUDES = {
    'lion':  re.compile(r'\bsea\s+lions?\b', re.IGNORECASE),
    'lions': re.compile(r'\bsea\s+lions?\b', re.IGNORECASE),
}

def match_wildlife(keyword, search_lower):
    if keyword in _WORD_BOUNDARY_KW:
        if not _WORD_BOUNDARY_KW[keyword].search(search_lower):
            return False
        if keyword in WILDLIFE_COMPOUND_EXCLUDES:
            all_matches = list(_WORD_BOUNDARY_KW[keyword].finditer(search_lower))
            compound_matches = list(WILDLIFE_COMPOUND_EXCLUDES[keyword].finditer(search_lower))
            compound_positions = set()
            for m in compound_matches:
                for i in range(m.start(), m.end()):
                    compound_positions.add(i)
            # Only match if at least one occurrence is standalone (outside compounds)
            return any(m.start() not in compound_positions for m in all_matches)
        return True
    # CJK and non-ambiguous keywords use simple substring match
    return keyword in search_lower
```

**Important**: Do NOT add a fallback `or (kw in search_text)` after `match_wildlife()` — this bypasses the word-boundary logic and reintroduces false positives.

### Word-boundary matching for place keywords
The same substring collision problem affects place names. For example, "quito" matches inside "mosquitoes" and "Iquitos", "lima" inside "climbing"/"kilimanjaro", "pisa" inside "Pisano"/"Pisac", "lucca" inside "felucca". Use word-boundary regex for these ambiguous place keywords:

```python
import re

_PLACE_WORD_BOUNDARY = {}
for kw in ['quito', 'oia', 'lima', 'aspen', 'pisa', 'lucca']:
    _PLACE_WORD_BOUNDARY[kw] = re.compile(r'\b' + re.escape(kw) + r'\b', re.IGNORECASE)

def match_place(keyword, search_text, search_lower):
    kw_lower = keyword.lower()
    if kw_lower in _PLACE_WORD_BOUNDARY:
        return bool(_PLACE_WORD_BOUNDARY[kw_lower].search(search_lower))
    return keyword in search_text or kw_lower in search_lower
```

**Tip**: When adding new place keywords, always check if the keyword is a substring of common English words. If so, add it to the word-boundary list.

### Homograph keywords (same spelling, different meaning)
Some keywords match as both a noun (animal/place) and a common English word. For example, "bear" is both an animal and a verb ("to bear the risk", "colossi bear the crown"), and appears in place names ("Bear Creek", "Bear Lake"). For these, add compound-exclusion patterns that cover verb phrases and place-name compounds:

```python
WILDLIFE_COMPOUND_EXCLUDES = {
    'bear': re.compile(
        r'\b(?:to\s+bear|bear\s+the|bears?\s+some|bears?\s+(?:no|any|little)'
        r'|colossi\s+bear'
        r'|bear\s+(?:creek|lake|rd|road|mountain|island|canyon|river|peak|point|gulch))\b',
        re.IGNORECASE
    ),
}
```

The exclusion logic checks whether ALL occurrences of "bear" in the text are covered by these verb/place-name patterns. If at least one standalone animal usage exists, the match succeeds.

### Critical: ZH entity extraction must search both ZH and EN text
Proper nouns often stay in English within Chinese article text (e.g., "Múlafossur瀑布", "Ilulissat冰川峡湾"). Always search the combined ZH + EN content for pattern matching:
```python
search_text = zh_content + ' ' + zh_title + ' ' + en_content + ' ' + en_title
```

### Country detection from tags
Tags provide the most reliable country signal. Map tag names (lowercased) to country labels:
```python
for tag in post['tags']:
    tl = tag.lower()
    if tl in COUNTRY_TAG_MAP:
        countries.add(COUNTRY_TAG_MAP[tl])
```

### Place → Country linking
Maintain a `PLACE_COUNTRY` mapping so that place nodes are linked to their country node. Only add the link if the country node already exists in the graph.

---

## Step 2 — Naming Convention for ZH Graph

The ZH graph uses entity names **as they appear in the Chinese article text**, not invented translations. Follow these rules:

### Translate (common words)
- Generic nouns: 灯塔, 瀑布, 岛, 湾, 峡湾, 冰川, 餐厅, 徒步, 摄影
- Well-known place names with standard Chinese equivalents: 冰岛, 格陵兰岛, 法罗群岛, 科罗拉多州, 雷克雅未克, 北极圈

### Keep in original language (proper nouns without standard ZH names)
- Specific place names: Ilulissat, Tórshavn, Qeqertarsuaq, Gásadalur, Trælanípa, Grand Junction, Monument Canyon
- Restaurant names: Barbara, Fiskastykkið, Ræst

### Hybrid (keep proper noun, translate generic suffix)
- Kallur灯塔, Múlafossur瀑布, Sørvágsvatn湖, Mykines岛, Vágar岛, Kalsoy岛, Disko岛, Sermeq Kujalleq冰川

### Source of truth
Always defer to how the website's own Chinese articles refer to the place. Scrape the ZH article body and use whatever name appears there — don't invent translations.

### Node Merge
Nodes that refer to the same entity under different names (e.g. "Tórshavn" and "Thor's Harbor" → same place) should be merged.

---

## Step 3 — Graph Architecture

### Two independent graphs (EN and ZH)

```javascript
const GRAPHS = {
  en: { nodes: [...], links: [...] },
  zh: { nodes: [...], links: [...] }
};
```

The language toggle calls `renderGraph(lang)` which:
1. Stops existing D3 simulation
2. Clears SVG
3. Rebuilds force simulation with new dataset

**Do NOT** just relabel nodes on toggle — the two graphs have different node sets, different entity names, different article titles.

### Node structure

```javascript
{ id: "unique-id", label: "Display name", type: "article|country|place|activity|wildlife|food", size: 13, url: "..." }
```

- Use `en_title` for ID generation to keep IDs stable across both graphs
- Article nodes carry a `url` field for double-click navigation
- ZH article nodes use the ZH title the reader actually sees:
  - Real translation: ZH title (e.g. `"山城秋色 – Grand Junction"`)
  - No translation: EN fallback title (e.g. `"Galápagos Islands"`)

### Link structure

```javascript
{ s: "source-node-id", t: "target-node-id" }
```

Relationship types (not labeled on edges, encoded implicitly by node types):
- `article → country` — post is set in this country
- `article → place` — post features this place
- `article → activity` — post involves this activity
- `article → wildlife` — post features this wildlife
- `article → food` — post mentions this food/restaurant
- `place → country` — place is located in country
- `place → place` — place is part of / near another place

### Error checking

- Every node should have at least one link to the Article node. The article node should have at least one link to the Country node.

---

## Step 4 — Node Sizes

Node sizes encode importance. Use these baselines:

| Node Type | Base size | High-frequency hubs |
|-----------|-----------|---------------------|
| Country/Region | 30–56 | Primary hub, trip organizer |
| Monument | 11–22 | Historical/cultural clusters |
| Arts | 11–20 | Cultural venue clusters |
| Wildlife | 11–22 | Thematic clusters |
| Place | 11–20 | Geographic sub-nodes |
| Activity | 12–26 | Only distinctive ones |
| Article | 14 | Leaf nodes |
| Food | 11–16 | Specific restaurants/cuisines |

Size scaling formula (based on connection count `c`):
```python
if type == 'country':    size = min(56, max(30, 30 + c * 2))
elif type == 'place':    size = min(20, max(11, 11 + c))
elif type == 'arts':     size = min(20, max(11, 11 + c))
elif type == 'monument': size = min(22, max(11, 11 + c))
elif type == 'activity': size = min(26, max(12, 12 + c * 2))
elif type == 'wildlife': size = min(22, max(11, 11 + c))
elif type == 'food':     size = min(16, max(11, 11 + c))
elif type == 'article':  size = 14
```

---

## Step 5 — Typography

```css
/* Node labels */
.node text {
  font-size: 11px;          /* legible without zooming */
  font-weight: 500;         /* Medium weight for readability on dark background */
  fill: #8892a4;
  pointer-events: none;
}

/* Label placement — below node circle */
node.append('text')
  .attr('dy', d => d.size + 11)   /* offset below circle increases with node size */
  .attr('text-anchor', 'middle')
  .text(d => d.label.length > 24 ? d.label.slice(0, 22) + '…' : d.label)
```

Font family should include CJK fallbacks for bilingual graphs:
```css
font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Noto Sans CJK SC', sans-serif;
```

---

## Step 6 — Force Simulation Parameters

### Tuned values (tested with ~400 nodes / ~1000 links)

```javascript
simulation = d3.forceSimulation(nodes)
  .force('link', d3.forceLink(links).id(d => d.id).strength(0.08).distance(160))
  .force('charge', d3.forceManyBody().strength(-800))
  .force('center', d3.forceCenter(0, 0).strength(0.015))
  .force('collision', d3.forceCollide().radius(d => d.size + 24))
  .force('x', d3.forceX(0).strength(0.012))
  .force('y', d3.forceY(0).strength(0.012))
  .alphaDecay(0.02)
```

### Tuning guide

| Parameter | Too tight (bad) | Target | Too loose (bad) |
|-----------|----------------|--------|-----------------|
| link strength | > 0.2 — nodes crowd together | 0.06–0.10 | < 0.03 — no clustering at all |
| link distance | < 80 — overlapping clusters | 140–180 | > 250 — too spread |
| charge | > -400 — nodes cluster | -700 to -900 | < -1200 — explodes |
| center strength | > 0.05 — pulls everything to middle | 0.01–0.02 | 0 — drifts off screen |
| collision radius | < size+10 — nodes overlap | size+20 to size+26 | > size+40 — too sparse |

Key insight: low link strength + high charge + generous distance = nodes spread out naturally, clusters remain visible, and nodes stay where dragged.

---

## Step 7 — Link Styling

Default (no selection):
```javascript
.attr('stroke', '#4f5f7a')    /* visible against #0f1117 dark background */
.attr('stroke-width', 0.9)
.attr('opacity', 0.5)
```

When a node is selected (highlight neighborhood):
- Neighbor links: opacity 0.6, stroke colored by target node type, width 1.5
- Non-neighbor links: opacity 0.02 (nearly hidden)

On reset: restore defaults above.

**Important**: Link color must be bright enough to see against the dark background. `#1e2330` or similar near-black values are invisible — use `#4f5f7a` or brighter at ≥0.5 opacity.

---

## Step 8 — Interaction Behavior

### Click behavior
- **Single click** on a node: highlight neighborhood (connected nodes + their links). Click again or click background to deselect.
- **Double click** on an article node: `window.open(node.url, '_blank')` to open the blog post.
- **Click background**: reset all highlighting.

### Highlight implementation
When a node is selected:
1. Collect all neighbor IDs (nodes directly connected via any link)
2. Set non-neighbor nodes to opacity 0.06
3. Set non-neighbor links to opacity 0.02
4. Color neighbor links by the connected node's type color

### Search
- Filter nodes by label match (case-insensitive)
- Dim non-matching nodes to opacity 0.08
- Dim all links to opacity 0.04

### Tooltip
Show on hover with: type (colored), label (bold), connection count, and "Double-click to open" hint for articles.

---

## Step 9 — Output Format

Build as a single self-contained HTML file with:
- D3.js loaded from CDN: `https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js`
- Graph data inlined as `const GRAPHS = {...};`
- All CSS inline in `<style>`
- All JS inline in `<script>`
- Dark theme background: `#0f1117`

### Initial zoom
Center the graph and scale to ~0.55 to fit the full graph on screen:
```javascript
svg.call(zoom.transform, d3.zoomIdentity.translate(width/2, height/2).scale(0.55));
```

---

## Step 10 — Entity Extraction via Claude API (for new posts)

The keyword dictionaries in `build_graph.py` cover existing posts but won't recognize entities in new posts about new destinations. Instead of manually extending dictionaries, use the Claude API to extract entities from each post automatically.

### Extraction prompt template

For each post, send the content to Claude API with a structured extraction prompt:

```python
import json

def extract_entities_via_api(title, content, lang='en'):
    """Call Claude API to extract entities from a post."""
    prompt = f"""Extract named entities from this travel blog post. Return ONLY a JSON object with these keys:
- "country": list of countries or US states/regions the post is about
- "place": list of geographic places (cities, neighborhoods, islands, lakes, trails, national parks, beaches)
- "arts": list of museums, art galleries, theatres, opera houses, concert halls (named cultural venues)
- "monument": list of historical monuments, ruins, temples, fortresses, castles, cathedrals, ancient structures (named historical sites)
- "activity": list of distinctive activities (hiking, snorkeling, safari, boat tour, etc. — NOT generic ones like photography or sightseeing)
- "wildlife": list of specific wildlife seen (animal species, NOT generic "animals" or "birds")
- "food": list of specific restaurants or distinctive cuisine mentioned

Rules:
- Only extract entities that are specifically named or described in the text
- For {lang.upper()} graph: use names as they appear in the text
- Do NOT invent translations for proper nouns
- Do NOT include generic terms like "temple", "museum", "beach" without a specific name
- Prefer specific names: "Serengeti" not "national park", "Machu Picchu" not "ruins"
- Each list can be empty if no entities of that type are found

Title: {title}
Content: {content[:4000]}

Return ONLY the JSON object, no other text."""

    response = call_claude_api(prompt)  # your API call here
    return json.loads(response)
```

### Merge strategy

When combining API-extracted entities with existing dictionary-based ones:

1. **Run API extraction** on all posts (or just new ones)
2. **Deduplicate** — merge entities that refer to the same thing (e.g., "Tórshavn" and "Thor's Harbor")
3. **Validate** — spot-check API output for false positives (generic terms, misclassified types)
4. **Merge with existing graph** — add new nodes and links, keeping existing ones intact

### Hybrid approach (recommended)

Use both methods together:
- **Dictionary matching** (`build_graph.py`) for existing posts where keywords are well-tuned
- **Claude API extraction** for new posts not covered by dictionaries
- After API extraction, add confirmed new entities back to the dictionaries for consistency

```python
# Pseudocode for hybrid extraction
for post in posts:
    # First pass: dictionary matching (fast, precise for known entities)
    dict_entities = extract_from_dictionaries(post)
    
    # Second pass: API extraction (catches new entities)
    api_entities = extract_entities_via_api(post['title'], post['content'])
    
    # Merge: union of both, with dictionary results taking priority for naming
    merged = merge_entities(dict_entities, api_entities)
```

---

## Caveats

- Entity extraction uses keyword-matching dictionaries for known posts. For new posts with unknown destinations, use Claude API extraction (see Step 10) to automatically discover entities.
- **Overly generic keywords**: Avoid keywords that are common English words with multiple meanings. For example, `'trail'` was initially used for Hiking but matched temple walkways, star trails, and general paths in 30+ posts — remove it, real hiking posts match via `'hiking'`, `'hike'`, or `'trek'`. `'photography'` was used as an Activity but matched nearly every travel post since most mention taking photos — remove it, it's not a distinctive activity. Similarly, `'pyramid'` is too generic (matches Louvre glass pyramid, Mayan pyramids, etc.) — use specific forms like `'pyramids of giza'`, `'great pyramid'`. Generic CJK keywords like `'歌剧院'`, `'神庙'`, `'城堡'` have the same problem — prefer specific names like `'巴黎歌剧院'`, `'阿布辛拜神庙'`, `'Rosenborg城堡'`.
- **Substring collision pitfall (English)**: Short English keywords like "lion", "seal", "bear", "elk" are substrings of common words ("million", "pavilion", "revealed", "bearded") or compound animal names ("sea lion"). Always use word-boundary regex (`\b`) for these, not simple `in` matching. Additionally, compound phrases like "sea lion" must suppress the shorter keyword "lion" — use positional exclusion logic (see Step 1).
- **Substring collision pitfall (CJK)**: Chinese keywords can be substrings of other keywords too — e.g., `'卢卡'` (Lucca) is a prefix of `'卢卡索'` (Luxor). Since `\b` word boundaries don't work for CJK, use a post-match deduplication step for places: after collecting all matched keywords, for each pair where one keyword is a substring of another mapping to a *different* place, remove all occurrences of the longer keyword from the text and re-check whether the shorter keyword still matches. If it doesn't, it was a false positive. Implementation:
  ```python
  # After initial matching, remove false substring matches
  to_remove = set()
  for short_kw in matched_keywords:
      for long_kw in matched_keywords:
          if short_kw != long_kw and short_kw in long_kw and places[short_kw] != places[long_kw]:
              cleaned = text.replace(long_kw, '').replace(long_kw.lower(), '')
              if short_kw not in cleaned and short_kw.lower() not in cleaned:
                  to_remove.add(places[short_kw])
  found_places -= to_remove
  ```
- WPGlobus splitting uses regex — assumes well-formed `{:en}...{:}{:zh}...{:}` markers.
- ZH graph entity names should always be verified against actual ZH article text — do not auto-translate proper nouns.
- For graphs with 400+ nodes, the inlined JSON data will be ~165KB. This is fine for a self-contained HTML file but too large for a React artifact. Use HTML output.
- When adding new posts, use Claude API extraction (Step 10) rather than manually extending keyword dictionaries. Add confirmed new entities back to dictionaries for future consistency.
