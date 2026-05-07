import anthropic
import json
from tools import web_search, run_python

client = anthropic.Anthropic()

# ── Specialist functions (simple wrappers for now) ──

def researcher_agent(question: str) -> str:
    """Search the web and return a summary."""
    results = web_search(question, max_results=3)
    snippets = "\n".join(
        f"- {r['title']}: {r['snippet']}"
        for r in results.get("results", [])
    )
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        system="Summarise these search results concisely in 3-4 sentences.",
        messages=[{"role": "user", "content": f"Question: {question}\n\nResults:\n{snippets}"}]
    )
    return response.content[0].text

def coder_agent(task: str) -> str:
    """Write and run Python code for a task."""
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=400,
        system="""Write Python code to complete the task.
Return ONLY the code, no explanation, no markdown fences.""",
        messages=[{"role": "user", "content": task}]
    )
    code = response.content[0].text.strip()
    result = run_python(code)
    if result["success"]:
        return f"Code output:\n{result['output']}"
    return f"Code error: {result['error']}"

def writer_agent(instructions: str) -> str:
    """Write content based on instructions."""
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=600,
        system="You are a professional writer. Write clear, concise content.",
        messages=[{"role": "user", "content": instructions}]
    )
    return response.content[0].text


# ════════════════════════════════════════
# PATTERN A — Fixed pipeline
# ════════════════════════════════════════

def fixed_pipeline(topic: str) -> str:
    """
    Always runs: research → analyse → write.
    Simple but inflexible.
    """
    print("\n── Fixed Pipeline ──")

    print("[1/3] Researching...")
    research = researcher_agent(f"Latest trends in {topic}")

    print("[2/3] Analysing with code...")
    analysis = coder_agent(
        f"Print 5 key statistics or numbers related to: {topic}. "
        f"Use realistic estimated values and label each clearly."
    )

    print("[3/3] Writing report...")
    report = writer_agent(
        f"Write a short report on {topic}.\n\n"
        f"Research findings:\n{research}\n\n"
        f"Analysis:\n{analysis}"
    )
    return report


# ════════════════════════════════════════
# PATTERN B — Dynamic orchestration
# ════════════════════════════════════════

# Describe our agents as tools the planner can call
AGENT_TOOLS = [
    {
        "name": "researcher_agent",
        "description": """Search the web to find current facts, news, and information.
Use this when the task requires up-to-date or factual information.""",
        "input_schema": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The research question to search for"
                }
            },
            "required": ["question"]
        }
    },
    {
        "name": "coder_agent",
        "description": """Write and execute Python code to perform calculations,
data processing, or generate structured data.
Use this for any task that requires computation or logic.""",
        "input_schema": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "Clear description of what the code should do"
                }
            },
            "required": ["task"]
        }
    },
    {
        "name": "writer_agent",
        "description": """Write polished content — reports, summaries, emails,
explanations. Use this when the task requires well-written output.
Always call this LAST after gathering all needed information.""",
        "input_schema": {
            "type": "object",
            "properties": {
                "instructions": {
                    "type": "string",
                    "description": "Detailed writing instructions including all content to incorporate"
                }
            },
            "required": ["instructions"]
        }
    }
]

AGENT_MAP = {
    "researcher_agent": researcher_agent,
    "coder_agent":      coder_agent,
    "writer_agent":     writer_agent,
}

def dynamic_orchestrator(task: str) -> str:
    """
    Planner dynamically decides which agents to call,
    in what order, based on the task and results so far.
    """
    print("\n── Dynamic Orchestrator ──")
    print(f"Task: {task}\n")

    messages = [{"role": "user", "content": task}]
    step = 0
    results_so_far = []

    while True:
        step += 1
        print(f"[Step {step}] Planner thinking...")

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system="""You are a planning agent that breaks complex tasks into steps.
You have access to specialist agents as tools.
Call agents one at a time in a logical order.
When you have everything needed to give a complete answer, stop calling tools
and write your final response directly.""",
            tools=AGENT_TOOLS,
            messages=messages
        )

        # Planner is done — return final answer
        if response.stop_reason == "end_turn":
            final = next(
                (b.text for b in response.content if hasattr(b, "text")), ""
            )
            print(f"\n[Done in {step} steps]")
            return final

        # Planner called an agent
        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue

                agent_name = block.name
                agent_args = block.input
                print(f"  → Calling {agent_name}({list(agent_args.keys())})")

                fn     = AGENT_MAP[agent_name]
                result = fn(**agent_args)
                results_so_far.append(f"{agent_name}: {result[:100]}...")

                print(f"  ✓ Got result ({len(result)} chars)")

                tool_results.append({
                    "type":        "tool_result",
                    "tool_use_id": block.id,
                    "content":     result
                })

            messages.append({"role": "user", "content": tool_results})

        if step > 10:   # safety limit
            break

    return "Task could not be completed within step limit."


# ── Run both patterns on the same task ──

topic = "Python programming language growth in 2025"

print("=" * 55)
print("PATTERN A — Fixed Pipeline")
print("=" * 55)
result_a = fixed_pipeline(topic)
print(f"\nOutput:\n{result_a[:400]}...")

print("\n" + "=" * 55)
print("PATTERN B — Dynamic Orchestrator")
print("=" * 55)
result_b = dynamic_orchestrator(
    f"I need a brief report on: {topic}. "
    f"Research it, calculate some key numbers, then write a summary."
)
print(f"\nOutput:\n{result_b[:400]}...")