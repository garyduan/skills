# Nabu Notes — Post Writing Skill

## Overview
This skill is used to compose blog posts for nabunotes.github.io based on a conversation.
Posts are published to Jekyll Chirpy theme.

## Tone
- Semi-formal: not colloquial, not academic
- Clear and direct
- First person is acceptable but not required

## Length
- Short and concise
- Avoid padding or repetition
- Every sentence should add value

## Structure
- Use bullet points as the primary structure
- For bullets that need elaboration, add 1-2 supporting sentences beneath them
- Use headers (##) to separate major sections if the topic warrants it
- Use **bold** for key terms, important concepts, or names being introduced
- Use *italic* for emphasis, foreign words, or titles of works
- End with a ## 参考 or ## References section if sources are cited

## Language
- If the conversation is in English, write the post in English
- If the conversation is in Chinese, write the post in Chinese
- Keep technical terms, proper nouns, and names in their original language where translation would be awkward
  (e.g. "Baroque风格", "DNA双螺旋结构")
- If a translation exists and is commonly used, prefer the conversation's language

## Citations
- Cite major sources at the end under ## 参考 (Chinese) or ## References (English)
- Format: `- [Title](URL)`
- Only cite significant sources, not every lookup

## Front Matter Template
```yaml
---
layout: post
title: ""
date: YYYY-MM-DD HH:MM:SS -0800
categories: [分类]
tags: []
image:
  path: /assets/img/posts/YYYY-MM-DD-slug/cover.jpg
  alt: ""
---
```

## Categories (in Chinese)
Use one or more from this list:
- 历史
- 音乐
- 自然
- 健身
- 美食
- 建筑
- 艺术
- 摄影
- 科技

New categories can be added as needed.

## Tags — Knowledge Map Guidelines
- If the conversation is in English, tags are in English, lowercase, hyphen-separated
- If the conversation is in Chinese, tags are in Chinese
- Suggested by Claude based on the conversation content
- Typically 3-6 tags per post
- Should reflect specific topics, people, places, periods, or concepts discussed
- Prefer reusing existing tags over inventing new ones — consistency builds the knowledge map
- Before suggesting tags, Claude should check existing tags on the site and reuse where appropriate
- User reviews and approves tags before post is pushed

## Related Notes
- At the end of each post, add a ## 相关笔记 (Chinese) or ## Related Notes (English) section
- List links to existing posts that share tags or topics with the current post
- Format: `- [Post Title]({% post_url YYYY-MM-DD-slug %})`
- If no related posts exist yet, omit the section

## Images
- Every post must have at least one image
- Search for suitable public domain images during the conversation and show them to the user
- If no suitable public domain images are found, or if the user does not like the suggested images,
  the user will provide their own images
- The first/only image is the preview/featured image, set in front matter under `image.path`
- Additional images go at the end of the post, after the main content and before ## 参考 / ## References
- Images are stored in `/assets/img/posts/YYYY-MM-DD-slug/`
- Use descriptive alt text in the post's language

## File Naming
- Post files: `_posts/YYYY-MM-DD-slug.md`
- Slug should be short, lowercase English, hyphen-separated
- Image folder matches the post slug: `assets/img/posts/YYYY-MM-DD-slug/`

## Workflow
1. Read the conversation and determine the language (English or Chinese)
2. Search for suitable public domain images and show them to the user during the conversation
3. If no suitable images found or user dislikes them, ask the user to provide their own images
4. Suggest tags based on the conversation content, preferring existing tags where possible
5. Ask the user for: structure preference, category, tag approval
6. Compose the post following the rules above
7. Show the user a full preview of the post before pushing
8. Wait for explicit user permission before pushing anything to the repo
9. Only after permission is given: push the markdown file and images to the repo via Cowork

## Permissions
- NEVER push to the repo without explicit user approval
- Always show a full preview first
- User must say something like "go ahead", "push it", or "approved" before any push