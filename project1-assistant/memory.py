import json
import os
from datetime import datetime

MEMORY_FILE = "memory.json"

def load():
    """Load all memory from disk. Returns a dict with facts + history."""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    # First time ever — return a clean slate
    return {
        "facts": {},           # long-term: name, job, preferences
        "history": [],         # short-term: recent messages
        "created_at": datetime.now().isoformat()
    }

def save(memory: dict):
    """Persist memory to disk."""
    memory["last_seen"] = datetime.now().isoformat()
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def add_fact(memory: dict, key: str, value: str):
    """Store a single fact about the user."""
    memory["facts"][key] = value

def add_message(memory: dict, role: str, content: str):
    """Add a message to short-term history. Keep last 20 only."""
    memory["history"].append({"role": role, "content": content})
    if len(memory["history"]) > 20:
        memory["history"] = memory["history"][-20:]  # trim oldest

def format_facts(memory: dict) -> str:
    """Turn facts dict into a readable string for the system prompt."""
    if not memory["facts"]:
        return "No facts known yet about this user."
    lines = [f"- {k}: {v}" for k, v in memory["facts"].items()]
    return "\n".join(lines)


#temp

# if __name__ == "__main__":
#     m = load()
#     add_fact(m, "name", "Ahmed")
#     add_fact(m, "goal", "Learning Agentic AI")
#     add_message(m, "user", "Hello!")
#     add_message(m, "assistant", "Hi Ahmed!")
#     save(m)
#     print("Saved. Facts:", m["facts"])

#     # Reload and verify persistence
#     m2 = load()
#     print("Reloaded facts:", m2["facts"])
#     print("History length:", len(m2["history"]))