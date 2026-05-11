import anthropic
import json
from workflow.specialists import (
    market_researcher,
    data_analyst,
    strategist,
    report_writer
)

client = anthropic.Anthropic()

# Describe specialists as tools for the coordinator
SPECIALIST_TOOLS = [
    {
        "name": "market_researcher",
        "description": (
            "Search the web and compile market intelligence on a topic. "
            "Returns market size, key players, and recent trends. "
            "Always call this FIRST."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "The business topic to research"
                }
            },
            "required": ["topic"]
        }
    },
    {
        "name": "data_analyst",
        "description": (
            "Perform quantitative analysis on research findings. "
            "Generates projections, metrics, and scoring tables. "
            "Call this AFTER market_researcher."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "The business topic"
                },
                "research_findings": {
                    "type": "string",
                    "description": "The full output from market_researcher"
                }
            },
            "required": ["topic", "research_findings"]
        }
    },
    {
        "name": "strategist",
        "description": (
            "Generate strategic recommendations and risk assessment. "
            "Call this AFTER data_analyst, passing both research and analysis."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "The business topic"
                },
                "research": {
                    "type": "string",
                    "description": "Output from market_researcher"
                },
                "analysis": {
                    "type": "string",
                    "description": "Output from data_analyst"
                }
            },
            "required": ["topic", "research", "analysis"]
        }
    },
    {
        "name": "report_writer",
        "description": (
            "Write the final polished business intelligence report. "
            "Call this LAST, passing all previous outputs."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "The business topic"
                },
                "research": {
                    "type": "string",
                    "description": "Output from market_researcher"
                },
                "analysis": {
                    "type": "string",
                    "description": "Output from data_analyst"
                },
                "strategy": {
                    "type": "string",
                    "description": "Output from strategist"
                }
            },
            "required": ["topic", "research", "analysis", "strategy"]
        }
    }
]

SPECIALIST_MAP = {
    "market_researcher": market_researcher,
    "data_analyst":      data_analyst,
    "strategist":        strategist,
    "report_writer":     report_writer,
}


def run_workflow(topic: str) -> str:
    """
    Coordinator dynamically plans and drives the workflow.
    It decides which specialists to call and in what order
    based on the topic -- no hardcoded sequence.
    """
    print(f"\n[Coordinator] Starting dynamic workflow for: {topic}")

    # Give the coordinator the topic and full autonomy --
    # no sequence instructions. It decides the plan itself.
    messages = [{"role": "user", "content": (
        f"Produce a complete business intelligence report on this topic:\n\n"
        f"{topic}\n\n"
        f"You have four specialist agents available as tools. "
        f"Decide which ones to call, in what order, and what to pass each one. "
        f"Use your judgment -- not every topic needs every specialist. "
        f"Your only requirement: the final output must be a polished report."
    )}]

    step         = 0
    final_report = None
    agents_called = []      # track what the coordinator decides to call

    while True:
        step += 1
        print(f"\n[Coordinator -- Step {step}]")

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2048,
            system=(
                "You are an autonomous workflow coordinator. "
                "You have four specialist agents available as tools.\n\n"
                "Your job:\n"
                "- Analyse the topic and decide which specialists are needed\n"
                "- Choose the most logical order to call them\n"
                "- Pass complete outputs between agents -- never truncate\n"
                "- Call report_writer last to produce the final deliverable\n"
                "- Adapt if a specialist returns weak results -- "
                "you can call researcher twice with different angles if needed\n\n"
                "You are fully autonomous. Plan the best workflow for the topic."
            ),
            tools=SPECIALIST_TOOLS,
            messages=messages
        )

        if response.stop_reason == "end_turn":
            if final_report is not None:
                print(f"\n[Coordinator] Workflow complete in {step} steps.")
                print(f"[Coordinator] Agents called: {' -> '.join(agents_called)}")
                return final_report
            return next(
                (b.text for b in response.content if hasattr(b, "text")),
                "Workflow did not produce a report."
            )

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue

                name = block.name
                args = block.input
                agents_called.append(name)
                print(f"  -> Calling {name}")

                fn     = SPECIALIST_MAP[name]
                result = fn(**args)

                if result is None:
                    result = f"{name} returned no output."

                print(f"  OK {name} -- {len(result)} chars")

                if name == "report_writer":
                    final_report = result

                tool_results.append({
                    "type":        "tool_result",
                    "tool_use_id": block.id,
                    "content":     result
                })

            messages.append({"role": "user", "content": tool_results})

            if final_report is not None:
                print(f"\n[Coordinator] Workflow complete in {step} steps.")
                print(f"[Coordinator] Agents called: {' -> '.join(agents_called)}")
                return final_report

        if step > 15:
            break

    return final_report or "Workflow could not complete within step limit."