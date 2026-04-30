#The searcher takes a topic and runs three focused searches — broad overview, recent news, and technical depth. Running three queries instead of one gives the writer agent much richer material to work with.
import anthropic
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from tools import web_search

client = anthropic.Anthropic()

SEARCH_TOOL = [
    {
        "name": "web_search",
        "description": """Search the web for current information on a topic.
Use this to find relevant articles, news, and resources.""",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Focused search query"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Number of results. Default 5."
                }
            },
            "required": ["query"]
        }
    }
]

def run_search(query: str) -> list[dict]:
    """Run a single web search and return results."""
    result = web_search(query, max_results=5)
    return result.get("results", [])

def search_topic(topic: str) -> dict:
    """
    Search a topic from three angles:
    - Broad overview
    - Recent developments
    - Practical / technical depth
    Returns all sources collected.
    """
    print(f"\n[Searcher] Researching: '{topic}'")

    # Ask the LLM to generate 3 focused search queries for this topic
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        system="""Generate exactly 3 focused search queries for researching a topic.
Return ONLY a JSON array of 3 strings. No explanation, no markdown.
Example: ["query one", "query two", "query three"]

Make queries cover:
1. Broad overview of the topic
2. Latest news or developments (add current year)
3. Practical applications or technical details""",
        messages=[{
            "role": "user",
            "content": f"Topic: {topic}"
        }]
    )

    # Parse the 3 queries
    try:
        queries = json.loads(response.content[0].text.strip())
    except Exception:
        # Fallback if parsing fails
        queries = [
            topic,
            f"{topic} 2025",
            f"{topic} practical applications"
        ]

    print(f"[Searcher] Running {len(queries)} searches...")

    # Run all 3 searches and collect results
    all_sources = []
    seen_links  = set()

    for i, query in enumerate(queries, 1):
        print(f"  [{i}/3] {query}")
        results = run_search(query)

        for r in results:
            # Deduplicate by URL
            if r["link"] not in seen_links:
                seen_links.add(r["link"])
                all_sources.append({
                    "title":   r["title"],
                    "link":    r["link"],
                    "snippet": r["snippet"],
                    "query":   query
                })

    print(f"[Searcher] Found {len(all_sources)} unique sources.")
    return {
        "topic":   topic,
        "queries": queries,
        "sources": all_sources
    }