import anthropic

client = anthropic.Anthropic()

print("=" * 50)
print("KNOB 1 — System prompt")
print("=" * 50)

response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=150,
    system="You are a terse senior engineer. Answer in max 2 sentences. No pleasantries.",
    messages=[{"role": "user", "content": "What is an API?"}]
)
print(response.content[0].text)

print("\n" + "=" * 50)
print("KNOB 2 — Conversation memory")
print("=" * 50)

history = []

def think(user_msg):
    history.append({"role": "user", "content": user_msg})
    r = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=150,
        system="You are a helpful assistant. Be concise.",
        messages=history
    )
    reply = r.content[0].text
    history.append({"role": "assistant", "content": reply})
    return reply

print(think("My project uses FastAPI."))
print(think("What database pairs well with my stack?"))

print("\n" + "=" * 50)
print("KNOB 3 — Temperature")
print("=" * 50)

for temp in [0.0, 1.0]:
    r = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=40,
        temperature=temp,
        messages=[{"role": "user", "content": "Name an AI startup."}]
    )
    print(f"Temp {temp}: {r.content[0].text.strip()}")

print("\n" + "=" * 50)
print("KNOB 4 — Chain of thought")
print("=" * 50)

r = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=250,
    system="Think step by step before answering.",
    messages=[{"role": "user", "content": "I have 10 minutes to deploy a fix. My pipeline takes 8 min, tests take 4 min. Can I make it?"}]
)
print(r.content[0].text)