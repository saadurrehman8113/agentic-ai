from knowledge_base import search

queries = [
    "I forgot my password",              # → should find auth-001 (reset password)
    "How much does it cost?",            # → should find plan-001 (pricing)
    "I want my money back",              # → should find bill-002 (refunds)
    "Can I use the API?",                # → should find api-001, api-002
    "When can I talk to someone?",       # → should find support-001 (hours)
]

for query in queries:
    print(f"\nQuery: '{query}'")
    results = search(query, top_k=2)
    for r in results:
        print(f"  [{r['relevance']:.2f}] ({r['source']}) {r['text'][:80]}...")