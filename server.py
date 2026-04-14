#!/usr/bin/env python3
"""MEOK AI Labs — mortgage-calculator-ai-mcp MCP Server. Calculate mortgage payments, amortization, and affordability."""

import asyncio
import json
from datetime import datetime
from typing import Any

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent)
import mcp.types as types

# In-memory store (replace with DB in production)
_store = {}

server = Server("mortgage-calculator-ai-mcp")

@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    return []

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    return [
        Tool(name="calculate_mortgage", description="Calculate mortgage payment", inputSchema={"type":"object","properties":{"principal":{"type":"number"},"rate":{"type":"number"},"years":{"type":"number"}},"required":["principal","rate","years"]}),
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Any | None) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    args = arguments or {}
    if name == "calculate_mortgage":
            p = args["principal"]; r = args["rate"] / 1200; n = args["years"] * 12
            payment = p * (r * (1+r)**n) / ((1+r)**n - 1) if r > 0 else p / n
            return [TextContent(type="text", text=json.dumps({"monthly_payment": round(payment, 2), "total_payments": n}, indent=2))]
    return [TextContent(type="text", text=json.dumps({"error": "Unknown tool"}, indent=2))]

async def main():
    async with stdio_server(server._read_stream, server._write_stream) as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mortgage-calculator-ai-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={})))

if __name__ == "__main__":
    asyncio.run(main())
