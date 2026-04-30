import anthropic
import json

client = anthropic.Anthropic()

# ─────────────────────────────────────────────
# PART A: Define your tools
# You describe them — the LLM decides when to use them
# ─────────────────────────────────────────────

tools = [
    {
        "name": "get_weather",
        "description": "Get the current weather for a city. Use this when the user asks about weather.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The name of the city, e.g. Lahore, London, Tokyo"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Temperature unit. Default to celsius."
                }
            },
            "required": ["city"]
        }
    },
    {
        "name": "calculate",
        "description": "Perform a mathematical calculation. Use this for any math the user asks about.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "A valid Python math expression, e.g. '2 + 2' or '150 * 0.17'"
                }
            },
            "required": ["expression"]
        }
    }
]


# ─────────────────────────────────────────────
# PART B: Real tool implementations
# These are YOUR functions — the LLM never touches them directly
# ─────────────────────────────────────────────

def get_weather(city: str, unit: str = "celsius") -> dict:
    """Fake weather API — replace with a real one later."""
    # In Phase 2 Concept 2 we'll call a real weather API
    fake_data = {
        "lahore":  {"temp": 38, "condition": "Sunny", "humidity": "45%"},
        "karachi": {"temp": 34, "condition": "Humid", "humidity": "80%"},
        "london":  {"temp": 15, "condition": "Cloudy", "humidity": "70%"},
        "tokyo":   {"temp": 28, "condition": "Clear",  "humidity": "60%"},
    }
    city_key = city.lower()
    data = fake_data.get(city_key, {"temp": 25, "condition": "Unknown", "humidity": "50%"})
    temp = data["temp"]
    if unit == "fahrenheit":
        temp = round(temp * 9/5 + 32)
    return {
        "city": city,
        "temperature": f"{temp}°{'C' if unit == 'celsius' else 'F'}",
        "condition": data["condition"],
        "humidity": data["humidity"]
    }


def calculate(expression: str) -> dict:
    """Safely evaluate a math expression."""
    try:
        # Only allow safe math operations
        allowed = set("0123456789+-*/()., ")
        if not all(c in allowed for c in expression):
            return {"error": "Invalid characters in expression"}
        result = eval(expression)
        return {"expression": expression, "result": result}
    except Exception as e:
        return {"error": str(e)}


# Map tool names to actual functions — the dispatcher
TOOL_MAP = {
    "get_weather": get_weather,
    "calculate":   calculate,
}


# ─────────────────────────────────────────────
# PART C: The agent loop with tool use
# ─────────────────────────────────────────────

def run_agent(user_message: str) -> str:
    """
    Run one full agent turn with tool use.
    Handles the full cycle: user → LLM → tool → LLM → answer
    """
    print(f"\nUser: {user_message}")
    messages = [{"role": "user", "content": user_message}]

    while True:
        # Call the LLM with tools available
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            tools=tools,
            messages=messages
        )

        print(f"[LLM stop reason: {response.stop_reason}]")

        # ── Case 1: LLM just replied with text — we're done ──
        if response.stop_reason == "end_turn":
            final_text = next(
                block.text for block in response.content
                if hasattr(block, "text")
            )
            print(f"Agent: {final_text}")
            return final_text

        # ── Case 2: LLM wants to use a tool ──
        if response.stop_reason == "tool_use":

            # Add the LLM's response (including tool call) to history
            messages.append({"role": "assistant", "content": response.content})

            # Process every tool call the LLM requested
            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue

                tool_name = block.name
                tool_args = block.input
                print(f"[Tool call: {tool_name}({tool_args})]")

                # Execute the real function
                fn = TOOL_MAP.get(tool_name)
                if fn:
                    result = fn(**tool_args)
                else:
                    result = {"error": f"Unknown tool: {tool_name}"}

                print(f"[Tool result: {result}]")

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,   # must match the tool call id
                    "content": json.dumps(result)
                })

            # Send tool results back to LLM
            messages.append({"role": "user", "content": tool_results})
            # Loop continues — LLM will now generate final answer


# ─────────────────────────────────────────────
# Test it with different scenarios
# ─────────────────────────────────────────────

print("=" * 50)
run_agent("What's the weather like in Lahore right now?")

print("=" * 50)
run_agent("Calculate 15% tip on a bill of PKR 2,450")

print("=" * 50)
run_agent("Compare the weather in London and Tokyo")