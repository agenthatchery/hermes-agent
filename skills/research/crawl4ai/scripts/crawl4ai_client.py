import argparse
import requests
import json
import sys

# Default Crawl4AI Server on tower.local
API_URL = "http://10.42.82.6:11235/crawl"

def crawl_url(url: str, max_chars: int):
    """Hits the local Crawl4AI docker service to extract clean markdown."""
    payload = {
        "urls": [url],
        "priority": 10,  # Ensure it is prioritized
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer "  # Empty token if auth isn't strict
    }
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Assuming the API returns a list of result objects
        results = data.get("results", [])
        if not results:
            print(f"Error: No results returned for {url}. Raw response: {data}")
            sys.exit(1)
            
        markdown_content = results[0].get("markdown", "")
        if not markdown_content:
            markdown_content = results[0].get("content", "No markdown or content extracted.")
            
        # Truncate if requested
        if max_chars > 0 and len(markdown_content) > max_chars:
            markdown_content = markdown_content[:max_chars] + "... [TRUNCATED]"
            
        print(f"--- Extraction for {url} ---\n{markdown_content}")
        
    except requests.exceptions.RequestException as e:
        print(f"Failed to connect or fetch from Crawl4AI at {API_URL}: {e}")
        if e.response is not None:
            print(f"Response snippet: {e.response.text[:200]}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Deep research extractor using local Crawl4AI API.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    crawl_parser = subparsers.add_parser("crawl", help="Extract markdown from a URL.")
    crawl_parser.add_argument("url", help="Target URL to extract.")
    crawl_parser.add_argument("--max-chars", type=int, default=15000, help="Max length of output text.")
    
    args = parser.parse_args()
    
    if args.command == "crawl":
        crawl_url(args.url, args.max_chars)
        
if __name__ == "__main__":
    main()
