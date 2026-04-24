from memory import load, save, add_fact, add_message

def run(brain_fn):
    """
    Main conversation loop.
    brain_fn: a function(user_message, history, facts) -> (reply, new_facts)
    """
    memory = load()
    facts = memory["facts"]
    history = memory["history"]

    # Greet returning users differently
    if facts.get("name"):
        print(f"\nAssistant: Welcome back, {facts['name']}! How can I help?")
    else:
        print("\nAssistant: Hello! I'm your personal assistant. I'll remember things about you over time.")

    print("(Type 'quit' to exit, 'memory' to see what I know)\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not user_input:
            continue

        if user_input.lower() == "quit":
            print("Assistant: Goodbye! I'll remember everything for next time.")
            break

        if user_input.lower() == "memory":
            print("\n--- What I know about you ---")
            for k, v in facts.items():
                print(f"  {k}: {v}")
            print(f"  conversation turns: {len(history)}")
            print()
            continue

        # Get reply from the brain
        reply, new_facts = brain_fn(user_input, history, facts)

        # Update memory
        add_message(memory, "user", user_input)
        add_message(memory, "assistant", reply)

        for key, value in new_facts.items():
            add_fact(memory, key, value)
            facts[key] = value

        # Persist to disk every turn
        save(memory)

        print(f"\nAssistant: {reply}\n")