import anthropic
from knowledge_base import search

client = anthropic.Anthropic()

def rag_agent(user_question: str) -> str:
    """
    Answer a question using the knowledge base.
    1. Search for relevant chunks
    2. Inject them into the prompt
    3. LLM answers from real context — not from memory
    """
    print(f"\n{'='*55}")
    print(f"Question: {user_question}")

    # ── Step 1: Retrieve relevant chunks ──
    hits = search(user_question, top_k=3)

    if not hits:
        return "I could not find relevant information in the knowledge base."

    print(f"Retrieved {len(hits)} chunks:")
    for h in hits:
        print(f"  [{h['relevance']:.2f}] {h['text'][:60]}...")

    # ── Step 2: Build context from retrieved chunks ──
    context_blocks = []
    for i, hit in enumerate(hits, 1):
        context_blocks.append(
            f"[Source {i} — {hit['source']}]\n{hit['text']}"
        )
    context = "\n\n".join(context_blocks)

    # ── Step 3: Call LLM with context injected ──
    system = """You are a helpful customer support assistant.
Answer the user's question using ONLY the context provided below.
If the answer is not in the context, say "I don't have that information."
Always be concise and cite which source your answer comes from."""

    prompt = f"""Context from knowledge base:
{context}

User question: {user_question}"""

    response = client.messages.create(
        model      = "claude-haiku-4-5-20251001",
        max_tokens = 512,
        system     = system,
        messages   = [{"role": "user", "content": prompt}]
    )

    answer = response.content[0].text
    print(f"\nAnswer: {answer}")
    return answer


# ── Test it ──
rag_agent("How do I reset my password?")
rag_agent("What payment methods do you accept?")
rag_agent("Can I get a refund on my monthly plan?")
rag_agent("What is included in the Pro plan?")
rag_agent("How do I authenticate API requests?")

# This one has no answer in the knowledge base — watch what happens
rag_agent("Do you support dark mode?")