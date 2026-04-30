import chromadb
from sentence_transformers import SentenceTransformer

# ── Local embedding model — runs on your machine, no API cost ──
embedder = SentenceTransformer("all-MiniLM-L6-v2")  # downloads ~80MB on first run

# ── Local vector DB — creates a folder called chroma_db/ ──
chroma  = chromadb.PersistentClient(path="./chroma_db")

COLLECTION = "company_docs"

def get_collection():
    return chroma.get_or_create_collection(name=COLLECTION)

def load_documents(docs: list[dict]):
    """
    Load documents into the vector DB.
    Each doc must have: id, text, and optionally metadata.

    Example:
        {"id": "doc1", "text": "...", "metadata": {"source": "faq"}}
    """
    collection = get_collection()

    texts     = [d["text"]                      for d in docs]
    ids       = [d["id"]                        for d in docs]
    metadatas = [d.get("metadata", {})          for d in docs]

    # Convert texts to embeddings
    print(f"Embedding {len(texts)} documents...")
    embeddings = embedder.encode(texts).tolist()

    # Store in ChromaDB
    collection.upsert(
        ids        = ids,
        documents  = texts,
        embeddings = embeddings,
        metadatas  = metadatas
    )
    print(f"Stored {len(texts)} documents in vector DB.")

def search(query: str, top_k: int = 3) -> list[dict]:
    """
    Search the knowledge base by meaning.
    Returns the top_k most relevant chunks.
    """
    collection = get_collection()

    # Embed the query using the same model
    query_embedding = embedder.encode([query]).tolist()

    results = collection.query(
        query_embeddings = query_embedding,
        n_results        = top_k,
        include          = ["documents", "metadatas", "distances"]
    )

    # Package results cleanly
    hits = []
    for i in range(len(results["ids"][0])):
        hits.append({
            "text":      results["documents"][0][i],
            "source":    results["metadatas"][0][i].get("source", "unknown"),
            "relevance": round(1 - results["distances"][0][i], 3)
                         # distance → relevance score (1.0 = perfect match)
        })

    return hits

def count():
    return get_collection().count()