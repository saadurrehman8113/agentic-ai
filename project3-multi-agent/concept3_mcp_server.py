# MCP Server -- exposes tools to any MCP-compatible agent
import json
import sys
from datetime import datetime
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

# In-memory storage (in production this would be a database)
notes = {}
tasks = []

# Create the MCP server
app = Server("my-tools-server")


# ==================================================
# TOOL 1 -- Note taking
# ==================================================

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """Tell the MCP client what tools this server offers."""
    return [
        types.Tool(
            name="save_note",
            description=(
                "Save a note with a title and content. "
                "Use this to store any information for later retrieval."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Short title for the note"
                    },
                    "content": {
                        "type": "string",
                        "description": "The note content to save"
                    }
                },
                "required": ["title", "content"]
            }
        ),
        types.Tool(
            name="get_notes",
            description=(
                "Retrieve all saved notes. "
                "Use this to recall previously stored information."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="add_task",
            description=(
                "Add a task to the task list with a priority level. "
                "Use this to track things that need to be done."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "Description of the task"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                        "description": "Priority level of the task"
                    }
                },
                "required": ["task", "priority"]
            }
        ),
        types.Tool(
            name="get_tasks",
            description="Get all tasks sorted by priority.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="calculate",
            description=(
                "Perform a mathematical calculation. "
                "Pass a valid math expression as a string."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Math expression e.g. '(150 * 0.17) + 200'"
                    }
                },
                "required": ["expression"]
            }
        )
    ]


@app.call_tool()
async def call_tool(
    name: str,
    arguments: dict
) -> list[types.TextContent]:
    """Handle tool calls from the MCP client."""

    if name == "save_note":
        title   = arguments["title"]
        content = arguments["content"]
        notes[title] = {
            "content":    content,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        return [types.TextContent(
            type="text",
            text=f"Note saved: '{title}'"
        )]

    elif name == "get_notes":
        if not notes:
            return [types.TextContent(type="text", text="No notes saved yet.")]
        result = "Saved notes:\n"
        for title, data in notes.items():
            result += f"\n[{data['created_at']}] {title}:\n{data['content']}\n"
        return [types.TextContent(type="text", text=result)]

    elif name == "add_task":
        task_item = {
            "task":       arguments["task"],
            "priority":   arguments["priority"],
            "created_at": datetime.now().strftime("%H:%M"),
            "done":       False
        }
        tasks.append(task_item)
        return [types.TextContent(
            type="text",
            text=f"Task added ({arguments['priority']} priority): {arguments['task']}"
        )]

    elif name == "get_tasks":
        if not tasks:
            return [types.TextContent(type="text", text="No tasks yet.")]
        order  = {"high": 0, "medium": 1, "low": 2}
        sorted_tasks = sorted(tasks, key=lambda t: order[t["priority"]])
        result = "Tasks by priority:\n"
        for t in sorted_tasks:
            status = "DONE" if t["done"] else "TODO"
            result += f"\n[{t['priority'].upper()}] [{status}] {t['task']}"
        return [types.TextContent(type="text", text=result)]

    elif name == "calculate":
        try:
            expression = arguments["expression"]
            allowed    = set("0123456789+-*/()., ")
            if not all(c in allowed for c in expression):
                return [types.TextContent(
                    type="text",
                    text="Error: invalid characters in expression"
                )]
            result = eval(expression)
            return [types.TextContent(
                type="text",
                text=f"{expression} = {result}"
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Calculation error: {str(e)}"
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
    import asyncio
    asyncio.run(main())