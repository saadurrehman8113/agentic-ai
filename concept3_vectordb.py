import anthropic
import chromadb

client = anthropic.Anthropic()

# --- Step 1: Create a local vector database ---
chroma = chromadb.Client()
collection = chroma.create_collection("agent_docs")

# --- Step 2: Store documents (this would be your company docs, emails, notes) ---
documents = [
    "To reset your password, go to Settings > Security > Change Password.",
    "The refund policy allows returns within 30 days of purchase.",
    "Our offices are open Monday to Friday, 9am to 6pm PKT.",
    "To cancel your subscription, visit Account > Billing > Cancel Plan.",
    "Free shipping is available on orders over $50.",
]

# Store each document with an ID
collection.add(
    documents=documents,
    ids=[f"doc_{i}" for i in range(len(documents))]
)

print(f"Stored {len(documents)} documents in vector DB\n")

# --- Step 3: Agent uses vector DB to answer questions ---
def agent_with_rag(user_question: str) -> str:
    # Search by MEANING — not keyword
    results = collection.query(
        query_texts=[user_question],
        n_results=2  # get top 2 most relevant docs
    )

    # Pull out the relevant chunks
    relevant_docs = results["documents"][0]
    context = "\n".join(f"- {doc}" for doc in relevant_docs)

    print(f"[Agent retrieved]: {relevant_docs[0][:60]}...")

    # Give the LLM only the relevant context
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=150,
        system=f"""Answer the user's question using ONLY the context below.
If the answer isn't in the context, say you don't know.

Context:
{context}""",
        messages=[{"role": "user", "content": user_question}]
    )

    return response.content[0].text

# --- Test it ---
questions = [
    "How do I change my password?",      # matches doc 0
    "Can I get my money back?",           # matches doc 1 (different wording!)
    "What are your working hours?",       # matches doc 2
    "Do you offer free delivery?",        # matches doc 4
]

for q in questions:
    print(f"\nQ: {q}")
    print(f"A: {agent_with_rag(q)}")