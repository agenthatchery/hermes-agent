---
name: deep-research
description: Multi-step web research loop with Google-style search fallback + markdown conversion for fast reading.
version: 0.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Research, Web Search, Markdown Extraction, Deep Research, Fallback]
    related_skills: [duckduckgo-search, arxiv]
    fallback_for_toolsets: [web]
prerequisites:
  commands: [python]
---

# Deep Research

This is a **practical fallback workflow** when `web` tool dependencies are missing.

Use this to:
- run a deep, iterative research loop,
- keep all results in simple markdown text blocks,
- and continue searching from evidence gathered in previous steps.

The workflow is especially useful if:
- you want no API-key lock-in,
- you want deterministic command-level behavior,
- or you are in a restricted environment where `web_search` is unavailable.

## Setup

Optional packages:

```bash
pip install ddgs
pip install Search-Engines-Scraper
pip install trafilatura
```

`ddgs` is preferred if installed.
`search-engines-scraper` provides a broad set of engines and serves as fallback.
`trafilatura` improves markdown quality when available.

## Why this skill exists

- `web_search`/`web_extract` is the preferred path when `FIRECRAWL_API_KEY` is available.
- This skill gives a portable fallback with search + conversion behavior you can control.
- It is designed for iterative, multi-pass investigation (not one-shot fact lookup).

## Quick Reference

```bash
# Search only, top 8 results
python scripts/deep_research.py search "your query" --max 8

# Fetch markdown for URLs
python scripts/deep_research.py fetch https://example.com/page https://example.org/report

# Full loop: search then fetch top 3 URLs in the same run
python scripts/deep_research.py research "your query" --search-results 12 --fetch-count 3
```

## Step-by-step Research Loop

1. **Discover**
   ```bash
   python scripts/deep_research.py search "query"
   ```

   Keep `provider=auto` unless you specifically need one engine.

2. **Select sources**
   Review titles/snippets and keep 2-6 primary URLs.

3. **Collect content**
   ```bash
   python scripts/deep_research.py fetch URL1 URL2 URL3
   ```

4. **Synthesize**
   For each extracted doc, build bullets with claim + source URL.

5. **Re-search from gaps**
   Re-run `research` with follow-up query and narrow terms:
   ```bash
   python scripts/deep_research.py research "follow-up question"
   ```

## Standard Commands

### `search`

Search and return JSON-ready results with title, URL, snippet, and provider.

```bash
python scripts/deep_research.py search "energy storage breakthroughs 2026" --provider auto --max 10
```

### `fetch`

Fetch raw HTML and return a markdown-friendly extraction for each URL.

```bash
python scripts/deep_research.py fetch "https://example.com" --max-chars 12000
```

### `research`

One-pass deep research:
search then fetch top links automatically.

```bash
python scripts/deep_research.py research "latest open source RL toolchain" --search-results 12 --fetch-count 4 --max-chars 10000
```

Useful defaults:
- `--search-results`: 8
- `--fetch-count`: 3
- `--provider`: `auto`
- `--max-chars`: 10000

## Fallback and reliability behavior

- Search mode tries providers in order:
  1. `ddgs` (if installed),
  2. `search-engines-scraper` (if installed),
  3. graceful error with explicit provider message.
- Markdown extraction tries:
  1. `trafilatura` when installed,
  2. standard stdlib HTML text cleanup fallback.
- If extraction fails for one URL, research continues with remaining URLs and marks the failed one.

## Pitfalls

- `search-engines-scraper` depends on upstream parser behavior and may vary by engine.
- This is a fallback pipeline; `web_extract` plus Firecrawl still gives richer extraction and citations.
- Keep per-step source count moderate (`--fetch-count 2..5`) to avoid noisy outputs.

## Suggested Deep Research loop in conversation

```text
1) python scripts/deep_research.py search "topic and baseline definition"
2) python scripts/deep_research.py research "related subquestion A"
3) python scripts/deep_research.py fetch "url_a" "url_b" "url_c"
4) Write synthesis with citation links.
5) Repeat with narrower follow-up questions until evidence saturation.
```

## Output contract

All outputs are plain JSON with a stable top-level shape and readable source summaries.
Pass the output into a notes file or paste into `MEMORY.md`/`USER.md` if it adds durable value.

## Optional upgrade path

When credentials allow it:
- switch to `web_search`/`web_extract` for stronger structured extraction,
- add the `agent-browser` toolchain for page verification,
- add `hermes-agent` `deep` or `web` environment keys for larger-scale pipelines.
