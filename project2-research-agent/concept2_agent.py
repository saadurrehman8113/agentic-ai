import anthropic
import json
from tools import web_search, get_weather, run_python

client = anthropic.Anthropic()

# ── Tool definitions for the LLM ──
TOOLS = [
    {
        "name": "web_search",
        "description": """Search the web for current, up-to-date information.
Use this for: recent news, facts you are uncertain about, current prices,
recent events, or anything that requires information from after your training.
Do NOT use for general knowledge you already know confidently.""",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "A focused search query. Be specific. E.g. 'Python 3.13 new features' not 'Python'"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Number of results to return. Default 5."
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_weather",
        "description": """Get current real-time weather for any city.
Use this whenever the user asks about weather, temperature, climate,
or whether to bring an umbrella.""",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City name, e.g. 'Lahore', 'London', 'New York'"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Temperature unit. Use celsius unless user specifies."
                }
            },
            "required": ["city"]
        }
    },
    {
        "name": "run_python",
        "description": """Execute Python code to perform calculations, data processing,
or any logic that requires computation. Use this for: math beyond simple arithmetic,
working with lists/dicts, string formatting, generating structured data.
Always print() the result so it appears in output.""",
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Valid Python code to execute. Must use print() to show results."
                }
            },
            "required": ["code"]
        }
    }
]

# ── Tool dispatcher ──
TOOL_MAP = {
    "web_search": web_search,
    "get_weather": get_weather,
    "run_python":  run_python,
}

def run_agent(user_message: str) -> str:
    """Full agent loop with real tool use."""
    print(f"\n{'='*55}")
    print(f"User: {user_message}")
    print(f"{'='*55}")

    messages = [{"role": "user", "content": user_message}]

    while True:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2048,
            system="""You are a helpful research assistant with access to
real-time web search, live weather data, and a Python code executor.
Always use tools when they would give a better answer than guessing.
Be concise and cite sources when you use web search.""",
            tools=TOOLS,
            messages=messages
        )

        # ── Text reply — done ──
        if response.stop_reason == "end_turn":
            answer = next(
                (b.text for b in response.content if hasattr(b, "text")),
                ""
            )
            print(f"\nAgent: {answer}")
            return answer

        # ── Tool use requested ──
        if response.stop_reason == "tool_use":
            messages.append({
                "role": "assistant",
                "content": response.content
            })

            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue

                print(f"\n  [calling {block.name}]")
                print(f"  [args: {json.dumps(block.input, indent=2)}]")

                fn     = TOOL_MAP[block.name]
                result = fn(**block.input)

                print(f"  [result preview: {str(result)[:120]}...]")

                tool_results.append({
                    "type":        "tool_result",
                    "tool_use_id": block.id,
                    "content":     json.dumps(result)
                })

            messages.append({
                "role":    "user",
                "content": tool_results
            })


# ── Run test queries ──
run_agent("What is the weather in Lahore right now?")

run_agent("Search for the top 3 AI agent frameworks in 2025 and summarise them briefly.")

run_agent("""
I have a list of monthly salaries in PKR:
[85000, 92000, 78000, 105000, 88000, 96000, 72000, 110000]
Calculate the mean, median, and the highest salary.
Show the results clearly.
""")

run_agent(
    "Search for the latest Python version, then write and run code "
    "that shows what Python version I have installed."
)