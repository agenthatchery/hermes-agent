---
name: crawl4ai
description: Advanced deep web research using the local Crawl4AI API deployment for markdown conversion, dynamic rendering, and JS handling.
version: 0.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Research, Web Search, Markdown Extraction, Deep Research, Crawl4AI]
    related_skills: [deep-research, duckduckgo-search]
prerequisites:
  commands: [python, requests]
---

# Crawl4AI Deep Research

This skill connects to the local Crawl4AI API deployed on `tower.local:11235`. Crawl4AI is optimized for Large Language Models, capable of generating clean Markdown by navigating JavaScript-heavy sites, waiting for selectors, and bypassing bot protections.

## Standard Commands

### `crawl`
Fetch raw HTML and return a markdown-friendly extraction utilizing Crawl4AI.

```bash
python scripts/crawl4ai_client.py crawl "https://example.com/research-paper"
```

## How It Works

1. The script hits the local REST API `http://10.42.82.6:11235/crawl`.
2. It sends the target URL(s) to be processed.
3. It prints the extracted clean markdown to the console.

## Usage in conversation

```text
1) python scripts/crawl4ai_client.py crawl "https://github.com/NousResearch/hermes-agent"
2) Write synthesis based on the extracted markdown.
```
