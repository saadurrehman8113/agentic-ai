# MCP Server -- exposes web_search as a proper MCP tool
import sys
import os
import json
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from tools import web_search as _web_search

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

app = Server("search-server")


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="web_search",
            description=(
                "Search the web for current business information, "
                "market data, news, and research. "
                "Use specific queries for best results."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Focused search query"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Number of results to return. Default 5."
                    }
                },
                "required": ["query"]
            }
        )
    ]


@app.call_tool()
async def call_tool(
    name: str,
    arguments: dict
) -> list[types.TextContent]:
    if name == "web_search":
        result = _web_search(
            query=arguments["query"],
            max_results=arguments.get("max_results", 5)
        )
        return [types.TextContent(
            type="text",
            text=json.dumps(result)
        )]
    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())