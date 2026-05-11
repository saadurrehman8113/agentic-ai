import anthropic
import json
import sys
import os
import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from tools import run_python

client = anthropic.Anthropic()


# ==================================================
# SPECIALIST 1 -- Market Researcher (uses MCP)
# ==================================================

async def _market_researcher_async(topic: str) -> str:
    """Async inner function -- connects to MCP search server."""

    server_params = StdioServerParameters(
        command="python",
        args=[
            os.path.join(
                os.path.dirname(__file__),
                "search_mcp_server.py"
            )
        ]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Discover tools from MCP server
            tools_result = await session.list_tools()
            mcp_tools = []
            for tool in tools_result.tools:
                mcp_tools.append({
                    "name":         tool.name,
                    "description":  tool.description,
                    "input_schema": tool.inputSchema
                })

            print(f"    [MarketResearcher] MCP connected -- "
                  f"{len(mcp_tools)} tools available")

            messages = [{"role": "user", "content": (
                f"Research this business topic thoroughly: {topic}\n\n"
                "Search for:\n"
                "1. Current market size and growth rate\n"
                "2. Key players and competitors\n"
                "3. Recent trends and developments in 2025\n\n"
                "Run all three searches then write a structured summary."
            )}]

            while True:
                response = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=1200,
                    system=(
                        "You are a senior market research analyst. "
                        "Always search before answering. "
                        "Run multiple targeted searches to cover different angles. "
                        "Return findings in clear sections: "
                        "Market Size, Key Players, Recent Trends. "
                        "Be specific -- include numbers and names where found."
                    ),
                    tools=mcp_tools,
                    messages=messages
                )

                if response.stop_reason == "end_turn":
                    return next(
                        (b.text for b in response.content
                         if hasattr(b, "text")),
                        "No research findings."
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

                        print(f"    [MarketResearcher][MCP] "
                              f"Calling {block.name}: "
                              f"{str(block.input)[:50]}...")

                        # Call tool via MCP protocol
                        result = await session.call_tool(
                            block.name,
                            arguments=block.input
                        )
                        result_text = result.content[0].text

                        tool_results.append({
                            "type":        "tool_result",
                            "tool_use_id": block.id,
                            "content":     result_text
                        })

                    messages.append({
                        "role":    "user",
                        "content": tool_results
                    })


def market_researcher(topic: str) -> str:
    """
    Market researcher specialist.
    Uses MCP server for web search -- Concept 3 applied.
    """
    print(f"    [MarketResearcher] Researching via MCP: {topic[:50]}...")
    return asyncio.run(_market_researcher_async(topic))


# ==================================================
# SPECIALIST 2 -- Data Analyst
# ==================================================

def data_analyst(research_findings: str, topic: str) -> str:
    """
    Takes research findings and generates quantitative
    analysis -- projections, comparisons, key metrics.
    """
    print(f"    [DataAnalyst] Analysing data for: {topic[:50]}...")

    tools = [{
        "name": "run_python",
        "description": "Run Python code for calculations and data analysis.",
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python code. Use print(). ASCII only."
                }
            },
            "required": ["code"]
        }
    }]

    messages = [{"role": "user", "content": (
        f"Based on this research about {topic}, perform quantitative analysis.\n\n"
        f"Research findings:\n{research_findings}\n\n"
        "Write and run Python code to:\n"
        "1. Create a simple market size projection table (next 3 years)\n"
        "2. Calculate key growth metrics\n"
        "3. Score the top 3 players on a scale of 1-10\n\n"
        "Use realistic numbers based on the research. ASCII only in output."
    )}]

    attempts = 0
    while attempts < 3:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1000,
            system=(
                "You are a quantitative business analyst. "
                "Write Python code to analyse data and generate insights. "
                "Always use print() to show results. "
                "Use only ASCII characters -- no unicode symbols. "
                "Label all outputs clearly."
            ),
            tools=tools,
            messages=messages
        )

        if response.stop_reason == "end_turn":
            return next(
                (b.text for b in response.content if hasattr(b, "text")),
                "No analysis produced."
            )

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue
                result = run_python(**block.input)
                status = "OK" if result["success"] else "FAIL"
                print(f"    [DataAnalyst] Code run: {status}")
                tool_results.append({
                    "type":        "tool_result",
                    "tool_use_id": block.id,
                    "content":     json.dumps(result)
                })
            messages.append({"role": "user", "content": tool_results})
            attempts += 1

    return "Data analysis could not be completed."


# ==================================================
# SPECIALIST 3 -- Strategist
# ==================================================

def strategist(research: str, analysis: str, topic: str) -> str:
    """
    Takes research and analysis, generates strategic
    recommendations and risk assessment.
    """
    print(f"    [Strategist] Generating strategy for: {topic[:50]}...")

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1000,
        system=(
            "You are a senior business strategist with 20 years experience. "
            "You give direct, actionable recommendations. "
            "You always consider risks alongside opportunities. "
            "Structure your output clearly."
        ),
        messages=[{"role": "user", "content": (
            f"Topic: {topic}\n\n"
            f"Market Research:\n{research}\n\n"
            f"Quantitative Analysis:\n{analysis}\n\n"
            "Provide:\n"
            "1. Top 3 strategic opportunities (specific and actionable)\n"
            "2. Top 3 risks to watch (with mitigation strategies)\n"
            "3. A clear recommendation: should we pursue this? Why?\n"
            "4. Suggested next steps if we move forward"
        )}]
    )
    return response.content[0].text


# ==================================================
# SPECIALIST 4 -- Report Writer
# ==================================================

def report_writer(
    topic: str,
    research: str,
    analysis: str,
    strategy: str
) -> str:
    """
    Synthesises all inputs into a polished
    business intelligence report in markdown.
    """
    print(f"    [ReportWriter] Writing final report...")

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2000,
        system=(
            "You are an expert business report writer. "
            "You produce clear, professional markdown reports. "
            "Every section must add value -- no filler. "
            "Use the provided content accurately -- do not invent facts."
        ),
        messages=[{"role": "user", "content": (
            f"Write a complete business intelligence report on: {topic}\n\n"
            f"Market Research findings:\n{research}\n\n"
            f"Quantitative Analysis:\n{analysis}\n\n"
            f"Strategic Assessment:\n{strategy}\n\n"
            "Structure the report as:\n"
            "# [Topic] -- Business Intelligence Report\n"
            "## Executive Summary (3-4 sentences)\n"
            "## Market Overview\n"
            "## Quantitative Analysis\n"
            "## Strategic Assessment\n"
            "## Risks and Mitigations\n"
            "## Recommendations\n"
            "## Next Steps\n\n"
            "Make it executive-ready. Clear, concise, actionable."
        )}]
    )
    return response.content[0].text