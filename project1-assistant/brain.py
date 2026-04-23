import anthropic
import json
from memory import format_facts

client = anthropic.Anthropic()

SYSTEM_TEMPLATE = """You are a sharp, helpful personal assistant with persistent memory.

What you know about this user:
{facts}

Your behaviour rules:
1. Be concise and direct — you know this user, no need for formalities.
2. When the user tells you something personal (name, job, skills, goals, preferences),
   extract it and return it in a special JSON block at the END of your reply:
   <remember>{{"key": "value"}}</remember>
3. Use what you know. If you know their name, use it. If you know their stack, reference it.
4. Never mention that you have a memory system. Just act like you naturally remember.
"""

def think(user_message: str, history: list, facts: dict) -> tuple[str, dict]:
    """
    Call the LLM with full context.
    Returns: (reply_text, new_facts_to_save)
    """
    system = SYSTEM_TEMPLATE.format(facts=format_facts({"facts": facts}))

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        temperature=0.3,      # low temp = focused, reliable agent
        system=system,
        messages=history + [{"role": "user", "content": user_message}]
    )

    full_reply = response.content[0].text
    new_facts = {}

    # Extract any facts the agent wants to remember
    if "<remember>" in full_reply and "</remember>" in full_reply:
        try:
            start = full_reply.index("<remember>") + len("<remember>")
            end = full_reply.index("</remember>")
            raw = full_reply[start:end].strip()
            new_facts = json.loads(raw)
            # Clean the <remember> block from the displayed reply
            full_reply = (full_reply[:full_reply.index("<remember>")] +
                          full_reply[full_reply.index("</remember>") + len("</remember>"):])
            full_reply = full_reply.strip()
        except Exception:
            pass  # if parsing fails, just show the reply as-is

    return full_reply, new_facts