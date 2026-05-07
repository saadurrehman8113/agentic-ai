import anthropic
import json
from tools import web_search, run_python

client = anthropic.Anthropic()


# ==================================================
# SPECIALIST AGENTS
# ==================================================

class ResearchAgent:
    """Specialist: finds and summarises information from the web."""

    NAME        = "research_agent"
    DESCRIPTION = (
        "A specialist research agent that searches the web "
        "and returns well-sourced, factual summaries. Use this when the task "
        "requires current information, facts, news, or any external knowledge. "
        "Pass it a clear research question."
    )

    TOOLS = [{
        "name": "web_search",
        "description": "Search the web for current information.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Focused search query"
                }
            },
            "required": ["query"]
        }
    }]

    def run(self, question: str) -> str:
        print(f"    [ResearchAgent] Question: {question[:60]}...")
        messages = [{"role": "user", "content": question}]

        while True:
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=800,
                system=(
                    "You are a specialist research agent. "
                    "Your only job is to find accurate, current information. "
                    "Always use web_search to find facts before answering. "
                    "Return a concise, well-structured summary with key findings. "
                    "Never guess -- only report what you find."
                ),
                tools=self.TOOLS,
                messages=messages
            )

            if response.stop_reason == "end_turn":
                return next(
                    (b.text for b in response.content if hasattr(b, "text")),
                    "No result."
                )

            if response.stop_reason == "tool_use":
                messages.append({
                    "role": "assistant",
                    "content": response.content
                })
                tool_results = []
                for block in response.content:
                    if block.type != "tool_use":
                        continue
                    result = web_search(**block.input)
                    tool_results.append({
                        "type":        "tool_result",
                        "tool_use_id": block.id,
                        "content":     json.dumps(result)
                    })
                messages.append({
                    "role":    "user",
                    "content": tool_results
                })


class CoderAgent:
    """Specialist: writes and executes Python code."""

    NAME        = "coder_agent"
    DESCRIPTION = (
        "A specialist coding agent that writes and runs Python code. "
        "Use this for calculations, data processing, generating tables, "
        "or any task that requires computation. Pass it a clear description of "
        "what you need computed or built."
    )

    TOOLS = [{
        "name": "run_python",
        "description": "Execute Python code and return the output. Always use print().",
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python code to execute. Must use print()."
                }
            },
            "required": ["code"]
        }
    }]

    def run(self, task: str) -> str:
        print(f"    [CoderAgent] Task: {task[:60]}...")
        messages = [{"role": "user", "content": task}]
        attempts = 0

        while attempts < 3:
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=800,
                system=(
                    "You are a specialist Python coding agent. "
                    "Write clean, correct Python code to complete tasks. "
                    "Always use print() to output results. "
                    "IMPORTANT: Only use basic ASCII characters in all strings and output. "
                    "Do not use unicode symbols like arrows, stars, or special characters. "
                    "Use plain text alternatives: -> instead of arrows, * instead of bullets. "
                    "If your code has an error, read the error and fix it. "
                    "Return the final output clearly labelled."
                ),
                tools=self.TOOLS,
                messages=messages
            )

            if response.stop_reason == "end_turn":
                return next(
                    (b.text for b in response.content if hasattr(b, "text")),
                    "No output."
                )

            if response.stop_reason == "tool_use":
                messages.append({
                    "role": "assistant",
                    "content": response.content
                })
                tool_results = []
                for block in response.content:
                    if block.type != "tool_use":
                        continue
                    result = run_python(**block.input)
                    status = "OK" if result["success"] else "FAIL -- retrying"
                    print(f"    [CoderAgent] {status}")
                    tool_results.append({
                        "type":        "tool_result",
                        "tool_use_id": block.id,
                        "content":     json.dumps(result)
                    })
                messages.append({
                    "role":    "user",
                    "content": tool_results
                })
                attempts += 1

        return "Code execution failed after 3 attempts. Could not complete this step."


class WriterAgent:
    """Specialist: writes polished content. No external tools."""

    NAME        = "writer_agent"
    DESCRIPTION = (
        "A specialist writing agent that produces polished, "
        "well-structured content. Use this LAST, after all research and analysis "
        "is complete. Pass it all gathered information and clear writing instructions. "
        "It returns publication-ready markdown."
    )

    def run(self, instructions: str) -> str:
        print(f"    [WriterAgent] Writing: {instructions[:60]}...")
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1200,
            system=(
                "You are a specialist writing agent. "
                "You produce clear, professional, well-structured markdown content. "
                "Use the provided information accurately -- do not invent facts. "
                "Structure output with headers, bullet points, and sections as appropriate."
            ),
            messages=[{"role": "user", "content": instructions}]
        )
        return response.content[0].text


# ==================================================
# ORCHESTRATOR
# ==================================================

research_agent = ResearchAgent()
coder_agent    = CoderAgent()
writer_agent   = WriterAgent()

AGENT_TOOLS = [
    {
        "name":        ResearchAgent.NAME,
        "description": ResearchAgent.DESCRIPTION,
        "input_schema": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The research question to investigate"
                }
            },
            "required": ["question"]
        }
    },
    {
        "name":        CoderAgent.NAME,
        "description": CoderAgent.DESCRIPTION,
        "input_schema": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "The computation or coding task to perform"
                }
            },
            "required": ["task"]
        }
    },
    {
        "name":        WriterAgent.NAME,
        "description": WriterAgent.DESCRIPTION,
        "input_schema": {
            "type": "object",
            "properties": {
                "instructions": {
                    "type": "string",
                    "description": "Full writing instructions including all content to incorporate"
                }
            },
            "required": ["instructions"]
        }
    }
]

AGENT_MAP = {
    ResearchAgent.NAME: research_agent.run,
    CoderAgent.NAME:    coder_agent.run,
    WriterAgent.NAME:   writer_agent.run,
}


def orchestrate(task: str) -> str:
    print(f"\n{'='*55}")
    print(f"Task: {task}")
    print(f"{'='*55}")

    messages     = [{"role": "user", "content": task}]
    step         = 0
    writer_result = None

    while True:
        step += 1
        print(f"\n[Orchestrator -- Step {step}]")

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=(
                "You are an orchestrator agent. You plan and delegate.\n"
                "You have access to three specialist agents as tools:\n"
                "- research_agent: for finding current facts and information\n"
                "- coder_agent: for calculations, data processing, code execution\n"
                "- writer_agent: for producing polished written output\n\n"
                "Your job:\n"
                "1. Break the task into logical steps\n"
                "2. Call the right specialist for each step\n"
                "3. Pass ALL gathered information to writer_agent last\n"
                "4. After writer_agent returns, stop immediately. No more tools.\n\n"
                "Never do the specialists work yourself. Always delegate."
            ),
            tools=AGENT_TOOLS,
            messages=messages
        )

        # Orchestrator produced a text response -- done
        if response.stop_reason == "end_turn":
            if writer_result is not None:
                print(f"\n{'='*55}")
                print(f"[Done in {step} steps]")
                print(f"{'='*55}")
                return writer_result

            result = next(
                (b.text for b in response.content if hasattr(b, "text")),
                ""
            )
            print(f"\n{'='*55}")
            print(f"[Done in {step} steps]")
            print(f"{'='*55}")
            return result

        if response.stop_reason == "tool_use":
            messages.append({
                "role": "assistant",
                "content": response.content
            })

            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue

                agent_name = block.name
                agent_args = block.input
                print(f"  -> Delegating to {agent_name}")

                fn     = AGENT_MAP[agent_name]
                result = fn(**agent_args)

                if result is None:
                    result = "Agent returned no output."

                print(f"  OK {agent_name} returned {len(result)} chars")

                if agent_name == WriterAgent.NAME:
                    writer_result = result

                tool_results.append({
                    "type":        "tool_result",
                    "tool_use_id": block.id,
                    "content":     result
                })

            messages.append({
                "role":    "user",
                "content": tool_results
            })

            # Exit immediately after writer runs
            if writer_result is not None:
                print(f"\n{'='*55}")
                print(f"[Done in {step} steps -- writer finished]")
                print(f"{'='*55}")
                return writer_result

        if step > 10:
            break

    return "Could not complete within step limit."


# ==================================================
# RUN TASKS
# ==================================================

print("\n" + "#"*55)
print("TASK 1 -- Writing only")
print("#"*55)
result = orchestrate("Write a 3-bullet summary of what makes Python great for beginners.")
print(f"\nFinal output:\n{result}")

print("\n" + "#"*55)
print("TASK 2 -- Research + Write")
print("#"*55)
result = orchestrate(
    "Research the current state of AI agents in 2025, "
    "then write a short professional summary I can share with my team."
)
print(f"\nFinal output:\n{result}")

print("\n" + "#"*55)
print("TASK 3 -- Research + Code + Write")
print("#"*55)
result = orchestrate(
    "Research the top 3 Python web frameworks in 2025. "
    "Then write code to create a comparison table showing their "
    "GitHub stars (use realistic estimates). "
    "Finally write a recommendation report based on both."
)
print(f"\nFinal output:\n{result}")