import anthropic
import subprocess
import json
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

client = anthropic.Anthropic()


async def get_mcp_tools(session: ClientSession) -> list[dict]:
    """Ask the MCP server what tools it has. Convert to Anthropic format."""
    tools_result = await session.list_tools()
    tools = []
    for tool in tools_result.tools:
        tools.append({
            "name":        tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        })
    return tools


async def run_agent_with_mcp(user_message: str):
    """Run an agent that uses tools from our MCP server."""

    # Start the MCP server as a subprocess
    server_params = StdioServerParameters(
        command="python",
        args=["concept3_mcp_server.py"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            # Initialize the MCP connection
            await session.initialize()

            # Discover tools from the server
            tools = await get_mcp_tools(session)
            print(f"[MCP] Connected -- {len(tools)} tools available:")
            for t in tools:
                print(f"  - {t['name']}: {t['description'][:50]}...")

            print(f"\nUser: {user_message}\n")

            messages = [{"role": "user", "content": user_message}]

            while True:
                response = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=1024,
                    system=(
                        "You are a helpful personal assistant with access to "
                        "note-taking, task management, and calculation tools via MCP. "
                        "Use the tools proactively to help the user."
                    ),
                    tools=tools,      # tools discovered from MCP server
                    messages=messages
                )

                if response.stop_reason == "end_turn":
                    answer = next(
                        (b.text for b in response.content if hasattr(b, "text")),
                        ""
                    )
                    print(f"Agent: {answer}")
                    return answer

                if response.stop_reason == "tool_use":
                    messages.append({
                        "role": "assistant",
                        "content": response.content
                    })

                    tool_results = []
                    for block in response.content:
                        if block.type != "tool_use":
                            continue

                        print(f"[MCP tool call] {block.name}({block.input})")

                        # Call the tool on the MCP server
                        result = await session.call_tool(
                            block.name,
                            arguments=block.input
                        )

                        result_text = result.content[0].text
                        print(f"[MCP result] {result_text[:80]}...")

                        tool_results.append({
                            "type":        "tool_result",
                            "tool_use_id": block.id,
                            "content":     result_text
                        })

                    messages.append({
                        "role":    "user",
                        "content": tool_results
                    })


async def main():
    print("=" * 55)
    print("MCP Agent Demo")
    print("=" * 55)

    # Task 1 -- save notes and tasks
    await run_agent_with_mcp(
        "Save a note titled 'MCP Learning' with content: "
        "MCP is a protocol that standardises how agents connect to tools. "
        "Also add two tasks: 'Build a custom MCP server' (high priority) "
        "and 'Read MCP documentation' (medium priority)."
    )

    print("\n" + "-"*55)

    # Task 2 -- retrieve and calculate
    await run_agent_with_mcp(
        "Show me all my notes and tasks. "
        "Also calculate: if I study 2.5 hours per day for 30 days, "
        "how many total hours is that?"
    )


if __name__ == "__main__":
    asyncio.run(main())