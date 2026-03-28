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

## Step 1 — Discover Posts

Fetch the blog's category listing pages **only to collect post URLs and titles**. Do NOT extract article content from listing pages — listing pages render full post bodies inline, making them large and slow. Content extraction happens in Step 2, one post at a time.

```
GET https://{domain}/category/travelog/
GET https://{domain}/category/travelog/page/2/
... paginate until no "next page" link
```

From each listing page, extract only:
- Post URL (slug)
- Post title (EN)
- Post date / year

**Stop there.** Do not read or use article body text from listing pages.

For the ZH graph, also fetch:
```
GET https://{domain}/zh/category/travelog/
```
Extract only ZH post titles and URLs. If a post appears with a Chinese title, it is a candidate for real translation.

### Rate limiting

The site rate-limits aggressive crawling. Follow these rules:

- **Listing pages**: use `text_content_token_limit: 2000` — enough to capture all post titles and URLs on the page without downloading full article bodies.
- **Individual post pages** (Step 2): do NOT set `text_content_token_limit` — full content is needed for entity extraction.
- **Batch fetches across turns** — fetch 3–4 listing pages per conversation turn, not all 21 in one burst. The `web_fetch` tool has a rate limit of 100 non-cached requests per hour per conversation.
- If a fetch fails or returns an error, wait and retry in the next turn rather than immediately retrying in a loop.
- For ZH translation detection (body comparison), fetch EN and ZH versions of the same post in the same turn to keep requests grouped logically.

```
// Good workflow
Turn 1: listing pages 1–4  → collect URLs only (token_limit: 2000)
Turn 2: listing pages 5–8  → collect URLs only
...
Turn N: fetch individual posts → extract entities (no token limit)

// Bad — reading article content from listing pages
fetch(listing/page/1) → read all article bodies  ← WRONG, wasteful
```

### What counts as "post discovery"
Only add a post to the graph after fetching the post's own URL and reading its content. Never infer article titles, places, or entities from:
- Navigation menus
- Sidebar widgets
- Category/tag pages
- The session summary or prior conversation context

If a destination appears in the nav menu but no post has been fetched for it, it does not exist in the graph yet.

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
| `article` | 15 | 15 (all articles equal) |
| `country` | 22–30 | 30 for most-visited (Faroe, Greenland, Tanzania, Antarctica) |
| `place` | 11–20 | Scale by how many articles reference it |
| `activity` | 13–24 | Hiking/Photography are highest (24/22) |
| `wildlife` | 11–22 | Icebergs/Penguins highest (22/20) |
| `food` | 10–18 | Seafood highest (18) |

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

Use loose parameters so nodes can be dragged freely without snapping back:

```javascript
d3.forceSimulation(nodes)
  .force('link', d3.forceLink(links).id(d => d.id)
    .distance(d => {
      if (src.type==='article' && tgt.type==='country') return 190;
      if (src.type==='country' || tgt.type==='country') return 210;
      return 130;
    })
    .strength(0.28))                                    // MEDIUM-LOW — forms clusters but stays draggable
  .force('charge', d3.forceManyBody()
    .strength(d => -500 - d.size * 9))                 // HIGH repulsion — spread out
  .force('center', d3.forceCenter(W/2, H/2)
    .strength(0.025))                                   // WEAK center pull
  .force('collision', d3.forceCollide(d => d.size + 20))
```

### Tuning guide

| Parameter | Too tight (bad) | Target | Too loose (bad) |
|-----------|----------------|--------|-----------------|
| link strength | > 0.5 — nodes snap back when dragged | 0.2–0.3 | < 0.1 — no clustering |
| charge | < -200 — nodes cluster | -400 to -600 | < -1000 — explodes |
| center strength | > 0.1 — pulls everything to middle | 0.02–0.03 | 0 — drifts off screen |
| collision radius | < size+5 — nodes overlap | size+18 to size+22 | > size+40 — too sparse |

Key insight: low link strength + high charge = nodes spread out naturally and stay where dragged.

---

## Step 9 — Interaction

### Hover highlight
On `mouseenter`, highlight the hovered node and its direct neighbors; dim everything else:

```javascript
node.classed('hi',  n => n.id === d.id)
node.classed('dim', n => n.id !== d.id && !neighbors.has(n.id))
link.classed('dim', l => l.source.id !== d.id && l.target.id !== d.id)
```

### Drag
Standard D3 drag — set `fx/fy` on drag, clear on end. Node stays where dropped.

### Zoom/pan
```javascript
svg.call(d3.zoom().scaleExtent([0.15, 5]).on('zoom', e => g.attr('transform', e.transform)))
```

### Tooltip
Show on hover: node type, label, connection count. Position follows mouse.

---

## Step 10 — Scaling to More Posts

When expanding beyond 20 posts:

- **Node pruning**: consider hiding degree-1 leaf nodes (only 1 connection) — they add visual noise without insight
- **Entity deduplication**: merge nodes that refer to the same entity under different names (e.g. "Tórshavn" and "Thor's Harbor" → same place)
- **Edge type differentiation**: with denser graphs, consider encoding relationship type via edge style (solid/dashed) or color
- **Hierarchical grouping**: islands/sub-locations can be collapsed into parent region nodes, expandable on click

---

## Caveats

- Entity extraction in this skill is done manually from fetched article text. For full automation, use Claude API with a structured extraction prompt per article.
- WPGlobus fallback detection requires fetching each post twice (EN + ZH). Cache results to avoid re-fetching.
- ZH graph entity names should always be verified against actual ZH article text — do not auto-translate proper nouns.
