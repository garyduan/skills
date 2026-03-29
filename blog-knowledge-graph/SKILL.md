---
name: wordpress-travel-knowledge-graph
description: "Build an interactive knowledge graph from a WordPress travel blog. Use when the user wants to visualize connections between travel articles, places, activities, wildlife, and food across a blog. Handles multilingual blogs (e.g. WPGlobus EN/ZH), scrapes article content, extracts named entities, and produces a standalone interactive D3.js HTML graph with language switching. Trigger on: 'build a knowledge graph from my blog', 'visualize my travel posts', 'map connections between articles', or any request combining WordPress + knowledge graph."
---

# WordPress Travel Blog — Knowledge Graph

## Overview

Builds a standalone interactive D3.js force-directed knowledge graph from a WordPress travel blog. Scrapes article content, extracts entities (places, activities, wildlife, food), and renders two fully independent graphs for multilingual blogs (EN + ZH), switchable via a toggle.

## Quick Reference

| Task | Approach |
|------|----------|
| Discover posts | Fetch `/category/travelog/` (or relevant category), paginate through listing pages |
| Fetch article content | `web_fetch` each article URL, extract body text |
| Find ZH category | Fetch `/zh/category/travelog/` — same pagination structure |
| Detect real ZH translation | Compare body text fingerprint of `/slug` vs `/zh/slug` (NOT title, NOT just URL existence) |
| Render graph | D3.js v7 force simulation, standalone HTML artifact |

---

## Hard Rules — Data Integrity

These rules are absolute and must never be violated:

1. **Every node must come from a crawled post.** A node may only be added to the graph after fetching that post's own URL and reading its body content. No exceptions.

2. **Never use the nav menu as a data source.** WordPress listing pages return full HTML including a header nav with links like `/places/africa/travel-uganda/`. These are WordPress **pages** (static content), not **posts**. Ignore the entire nav, sidebar, and footer — they must never produce nodes, titles, countries, places, or any other graph data.

3. **Never infer or fabricate.** Do not guess entity names, article titles, or relationships from: nav menus, sidebar widgets, session summaries, prior conversation context, or any source other than the crawled post body.

4. **All posts in the category must be crawled.** The graph is only complete when every post in the target category (`/category/travelog/`) has been individually fetched and its content extracted. Partial crawls produce incomplete graphs — clearly mark which posts have and have not been crawled.

---
## Functions

- Type filter toggles (country / place / article / wildlife / food / activity)
- Text search (EN + ZH)
- Highlight-on-click (show neighborhood)
- Language toggle (EN / 中文)
- Zoom + pan + drag
- Tooltip on hover
- Cross-destination edges as dashed red lines
- Single click the article nodes, highlight-neighborhood nodes; Double click on an article node, opens the blog post in a new tab.

---

## Step 1 — Crawl All Posts via Listing Pages

WordPress category listing pages render full post content inline — each page contains ~8 complete articles. This means the listing pages themselves are the content source. There is no need for a separate URL collection phase.

Fetch each listing page without a token limit and extract entities directly from all posts on that page:

```
GET https://{domain}/category/travelog/           (no token limit)
GET https://{domain}/category/travelog/page/2/    (no token limit)
... paginate until no "next page" link
```

From each listing page, for each post in the main content area extract:
- Post title and URL
- All complete content of posts.

**Ignore everything outside the main content area** — nav, sidebar, footer, recent posts widget.

For the ZH graph, repeat the same pagination:
```
GET https://{domain}/zh/category/travelog/        (no token limit)
GET https://{domain}/zh/category/travelog/page/2/ (no token limit)
```

### Rate limiting

- **No token limit** on listing pages — full content is needed for entity extraction
- **Batch across turns**: fetch 3–4 listing pages per turn to stay under the 100 requests/hour limit
- If a fetch fails, retry in the next turn rather than immediately
- Build the graph once after all listing pages have been crawled — do not rebuild incrementally
- The purpose is not to build the graph fast, you can spread the fetch into hours, the key is to build the graph completely and correctly.
---

## Step 2 — Detect Real ZH Translations (WPGlobus)

**Critical:** WPGlobus silently falls back to available language when no translation exists. Visiting `/zh/slug` always returns a page — you cannot use URL existence to detect translation.

### Reliable detection method: body text comparison

1. Fetch `/slug` → extract first ~300 chars of article body text
2. Fetch `/zh/slug` → extract first ~300 chars of article body text
3. If body text is **identical** → WPGlobus fallback, no real ZH content
4. If body text **differs** (ZH page has Chinese characters in body) → real ZH translation exists

### Why title comparison is NOT sufficient

- Some posts have the same title in both languages (e.g. proper nouns, place names)
- Author may have entered a ZH title but left ZH body empty — WPGlobus falls back the body silently
- Only body text comparison catches both cases

### Fallback behavior in the graph

- Posts with no real ZH version: article node still appears in ZH graph, using whatever title `/zh/slug` renders (may be EN fallback title)
- Entity nodes for that post: extract from whichever content the Chinese reader actually sees

---

## Step 3 — Extract Entities

For each article, extract named entities from the body text:

| Entity Type | Examples | Node Color |
|-------------|----------|------------|
| `article` | Post titles | `#a78bfa` purple |
| `country` | Iceland, Faroe Islands, Greenland | `#38bdf8` blue |
| `place` | Kallur Lighthouse, Icefjord, Tórshavn | `#34d399` green |
| `activity` | Hiking, Photography, Ferry Travel | `#fb923c` orange |
| `wildlife` | Atlantic Puffins, Humpback Whales, Icebergs | `#f472b6` pink |
| `food` | Seafood Cuisine, Barbara Restaurant | `#facc15` yellow |

Node size encodes importance (connection count or explicit prominence). Articles default to `size: 13`, high-frequency entities up to `size: 26`.

---

## Step 4 — Naming Convention for ZH Graph

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

---

## Step 5 — Graph Architecture

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
{ id: "unique-id", label: "Display name", type: "article|country|place|activity|wildlife|food", size: 13 }
```

Article nodes in ZH use the ZH title the reader actually sees:
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

---

## Step 6 — Node Sizes

Node sizes encode importance. Use these baselines:

| Node Type | Base size | High-frequency hubs |
|-----------|-----------|---------------------|
| Country/Region | 30–56 | Primary hub, trip organizer |
| Wildlife | 11–22 | Thematic clusters |
| Place | 11–20 | Geographic sub-nodes |
| Activity | 12–26 | Only distinctive ones |
| Article | 14 | Leaf nodes |
| Food | 11–16 | Specific restaurants/cuisines |

---

## Step 7 — Typography

```css
/* Node labels */
.node text {
  font-size: 12px;          /* NOT 9–10px — must be legible without zooming */
  font-weight: 500;         /* Medium weight for readability on dark background */
  fill: #c4cdd8;
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
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Noto Sans CJK SC', sans-serif;
```

---

## Step 8 — Force Simulation Parameters

### Tuning guide

| Parameter | Too tight (bad) | Target | Too loose (bad) |
|-----------|----------------|--------|-----------------|
| link strength | > 0.5 — nodes snap back when dragged | 0.2–0.3 | < 0.1 — no clustering |
| charge | < -200 — nodes cluster | -400 to -600 | < -1000 — explodes |
| center strength | > 0.1 — pulls everything to middle | 0.02–0.03 | 0 — drifts off screen |
| collision radius | < size+5 — nodes overlap | size+18 to size+22 | > size+40 — too sparse |

Key insight: low link strength + high charge = nodes spread out naturally and stay where dragged.

---

## Step 9 — Scaling to More Posts

When expanding beyond 20 posts:

- **Node pruning**: consider hiding degree-1 leaf nodes (only 1 connection) — they add visual noise without insight
- **Entity deduplication**: merge nodes that refer to the same entity under different names (e.g. "Tórshavn" and "Thor's Harbor" → same place)


---

## Caveats

- Entity extraction in this skill is done manually from fetched article text. For full automation, use Claude API with a structured extraction prompt per article.
- WPGlobus fallback detection requires fetching each post twice (EN + ZH). Cache results to avoid re-fetching.
- ZH graph entity names should always be verified against actual ZH article text — do not auto-translate proper nouns.
