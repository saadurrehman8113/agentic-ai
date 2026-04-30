#The reader takes all the sources and extracts the key points from each one. It doesn't summarise everything — it pulls out what's actually useful for a report.
import anthropic

client = anthropic.Anthropic()

def extract_key_points(source: dict) -> dict:
    """
    Extract 3-5 key points from a single source snippet.
    Returns structured data ready for the writer.
    """
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        system="""You are a research analyst. Extract 3-5 key facts or insights
from the provided source. Be specific and factual.
Return ONLY a JSON object like:
{
  "key_points": ["point 1", "point 2", "point 3"],
  "relevance": "high" | "medium" | "low"
}
No markdown, no explanation.""",
        messages=[{
            "role": "user",
            "content": f"""Source title: {source['title']}
Source snippet: {source['snippet']}
Topic being researched: {source.get('query', '')}"""
        }]
    )

    try:
        import json
        data = json.loads(response.content[0].text.strip())
        return {
            "title":      source["title"],
            "link":       source["link"],
            "key_points": data.get("key_points", []),
            "relevance":  data.get("relevance", "medium")
        }
    except Exception:
        return {
            "title":      source["title"],
            "link":       source["link"],
            "key_points": [source["snippet"]],
            "relevance":  "medium"
        }

def read_sources(search_result: dict) -> dict:
    """
    Process all sources from the searcher.
    Filters to high/medium relevance only.
    """
    topic   = search_result["topic"]
    sources = search_result["sources"]

    print(f"\n[Reader] Extracting key points from {len(sources)} sources...")

    processed = []
    for i, source in enumerate(sources, 1):
        print(f"  [{i}/{len(sources)}] {source['title'][:55]}...")
        result = extract_key_points(source)

        # Only keep relevant sources
        if result["relevance"] in ("high", "medium"):
            processed.append(result)

    # Sort: high relevance first
    processed.sort(key=lambda x: 0 if x["relevance"] == "high" else 1)

    print(f"[Reader] Kept {len(processed)} relevant sources.")
    return {
        "topic":   topic,
        "sources": processed
    }