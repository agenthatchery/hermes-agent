#!/usr/bin/env python3
"""Deep research helper with search + markdown extraction fallbacks.

Usage:
    python3 scripts/deep_research.py search "query" [--provider auto] [--max 8]
    python3 scripts/deep_research.py fetch "https://example.com" [url ...]
    python3 scripts/deep_research.py research "query" [--search-results 8] [--fetch-count 3]
"""

import argparse
import json
import re
import sys
from html import unescape
from typing import Dict, List, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def _log(message: str) -> None:
    """Write structured debug messages to stderr."""
    print(f"[deep-research] {message}", file=sys.stderr)


def _normalize_text(text: str) -> str:
    """Normalize whitespace for stable output in logs and markdown bodies."""
    text = unescape(text)
    text = re.sub(r"\xa0", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _strip_html(html: str) -> str:
    """Best-effort HTML to text conversion using stdlib only."""
    html = re.sub(r"(?is)<(script|style|noscript)\b[^>]*>.*?</\1>", " ", html)
    html = re.sub(r"(?is)<[^>]+>", " ", html)
    return _normalize_text(re.sub(r"\s+", " ", html))


def _extract_with_trafilatura(html: str) -> str:
    """Use Trafilatura when installed, else return empty string."""
    try:
        from trafilatura import extract

        return _normalize_text(extract(html, include_comments=False, output_format="markdown") or "")
    except Exception as exc:
        _log(f"trafilatura unavailable or failed: {exc}")
        return ""


def _to_markdown(html: str) -> Tuple[str, str]:
    """Convert HTML to markdown-like text with a hard fallback."""
    text = _extract_with_trafilatura(html)
    if text:
        return text, "trafilatura"

    return _strip_html(html), "stdlib"


def _fetch_url(url: str, timeout: int = 20) -> Tuple[str, str]:
    """Fetch page text. Returns (html, final_url)."""
    request = Request(
        url,
        headers={
            "User-Agent": "hermes-agent-deep-research/1.0",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        final_url = response.geturl()
        charset = getattr(response.headers, "get_content_charset", lambda: None)() or "utf-8"
        return response.read().decode(charset, errors="replace"), final_url


def _make_result_entry(url: str, title: str = "", snippet: str = "") -> Dict[str, str]:
    return {
        "title": title or url,
        "url": url,
        "snippet": snippet.strip(),
    }


def search_with_ddgs(query: str, max_results: int) -> List[Dict[str, str]]:
    """Run DDGS text search when package is installed."""
    try:
        from ddgs import DDGS
    except Exception as exc:
        _log(f"DDGS not available for search: {exc}")
        return []

    rows: List[Dict[str, str]] = []
    try:
        with DDGS() as ddgs:
            for row in ddgs.text(query, max_results=max_results):
                if not isinstance(row, dict):
                    continue
                url = row.get("href") or row.get("url")
                if not url:
                    continue
                rows.append(
                    _make_result_entry(
                        url=url,
                        title=row.get("title", ""),
                        snippet=row.get("body", row.get("snippet", "")) or "",
                    )
                )
    except Exception as exc:
        _log(f"DDGS search failed: {exc}")
    return rows


def search_with_search_engines(query: str, max_results: int) -> List[Dict[str, str]]:
    """Search fallback using Search-Engines-Scraper when available."""
    try:
        from search_engines import Google
    except Exception as exc:
        _log(f"Search-Engines-Scraper unavailable: {exc}")
        return []

    rows: List[Dict[str, str]] = []
    try:
        engine = Google()
        raw = engine.search(query)
        if hasattr(raw, "links"):
            raw = raw.links()

        if isinstance(raw, dict):
            candidates = raw.get("results", []) or raw.get("links", []) or []
        else:
            candidates = raw

        for idx, item in enumerate(candidates or []):
            if idx >= max_results:
                break

            if isinstance(item, str):
                rows.append(_make_result_entry(url=item, title="", snippet=""))
                continue
            if not isinstance(item, dict):
                continue

            url = item.get("url") or item.get("href") or item.get("link")
            if not url:
                continue
            rows.append(
                _make_result_entry(
                    url=url,
                    title=item.get("title", ""),
                    snippet=item.get("text", item.get("snippet", "")) or "",
                )
            )
    except Exception as exc:
        _log(f"search-engines-scraper search failed: {exc}")

    return rows


def run_search(query: str, max_results: int, provider: str) -> Dict[str, object]:
    """Search with configured provider preference and return standard payload."""
    provider = provider.lower()
    rows: List[Dict[str, str]] = []
    used_provider = "none"
    error = None

    if provider in {"auto", "ddgs"}:
        rows = search_with_ddgs(query, max_results)
        if rows:
            used_provider = "ddgs"

    if not rows and provider in {"auto", "search-engines", "search_engines", "search-engines-scraper"}:
        rows = search_with_search_engines(query, max_results)
        if rows:
            used_provider = "search-engines-scraper"

    if not rows and provider != "auto":
        error = f"No usable search provider installed for '{provider}'."
    elif not rows:
        error = "No search provider installed or all providers returned empty results."

    deduped = []
    seen = set()
    for r in rows:
        if r["url"] in seen:
            continue
        seen.add(r["url"])
        deduped.append(r)

    return {
        "query": query,
        "provider": used_provider,
        "count": len(deduped),
        "results": deduped[:max_results],
        "error": error,
    }


def run_fetch(urls: List[str], max_chars: int) -> Dict[str, object]:
    """Fetch URLs and return markdown-friendly content."""
    outputs: List[Dict[str, object]] = []
    for url in urls:
        result = {
            "input_url": url,
            "final_url": "",
            "markdown": "",
            "error": None,
            "chars": 0,
            "provider": "std-html",
        }
        try:
            html, final_url = _fetch_url(url)
            result["final_url"] = final_url
            markdown, provider = _to_markdown(html)
            result["provider"] = provider
            markdown = markdown[:max_chars]
            result["markdown"] = markdown
            result["chars"] = len(markdown)
        except HTTPError as exc:
            result["error"] = f"HTTP {exc.code}: {exc.reason}"
        except URLError as exc:
            result["error"] = f"URL error: {exc.reason}"
        except Exception as exc:
            result["error"] = f"Unexpected fetch error: {exc}"
        outputs.append(result)

    return {"count": len(outputs), "results": outputs}


def cmd_search(args: argparse.Namespace) -> int:
    payload = run_search(args.query, args.max, args.provider)
    if payload["error"] and not payload["results"]:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 1
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def cmd_fetch(args: argparse.Namespace) -> int:
    payload = run_fetch(args.urls, args.max_chars)
    if not payload["results"]:
        print(json.dumps({"error": "No URLs provided."}, indent=2))
        return 1
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def cmd_research(args: argparse.Namespace) -> int:
    search_payload = run_search(args.query, args.search_results, args.provider)
    if search_payload["error"] and not search_payload["results"]:
        print(json.dumps(search_payload, indent=2, ensure_ascii=False))
        return 1

    selected_urls = [r["url"] for r in search_payload["results"][: args.fetch_count]]
    fetch_payload = run_fetch(selected_urls, args.max_chars)

    payload = {
        "query": args.query,
        "provider": search_payload["provider"],
        "search": search_payload,
        "fetch": fetch_payload,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Hermes deep research helper")
    sub = parser.add_subparsers(dest="command", required=True)

    search = sub.add_parser("search", help="Search query and return candidate URLs")
    search.add_argument("query", help="What to search for")
    search.add_argument("--provider", default="auto", choices=[
        "auto",
        "ddgs",
        "search-engines",
        "search_engines",
        "search-engines-scraper",
    ], help="Search backend preference")
    search.add_argument("--max", type=int, default=8, help="Maximum results")
    search.set_defaults(func=cmd_search)

    fetch = sub.add_parser("fetch", help="Fetch URLs and convert to markdown-like text")
    fetch.add_argument("urls", nargs="+", help="One or more URLs to fetch")
    fetch.add_argument("--max-chars", type=int, default=12000, help="Max chars per URL")
    fetch.set_defaults(func=cmd_fetch)

    research = sub.add_parser(
        "research",
        help="Search then fetch top URLs automatically in one pass",
    )
    research.add_argument("query", help="Research question/topic")
    research.add_argument("--provider", default="auto", choices=[
        "auto",
        "ddgs",
        "search-engines",
        "search_engines",
        "search-engines-scraper",
    ], help="Search backend preference")
    research.add_argument("--search-results", type=int, default=8, help="How many search results to keep")
    research.add_argument("--fetch-count", type=int, default=3, help="Top results to fetch")
    research.add_argument("--max-chars", type=int, default=12000, help="Max chars per fetched URL")
    research.set_defaults(func=cmd_research)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
