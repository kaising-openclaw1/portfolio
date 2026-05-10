#!/usr/bin/env python3
"""
HTTP/SSE server wrapper for the MCP Toolkit.
Exposes the MCP server over HTTP for remote clients.
"""

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(
    title="KaiStudio MCP Gateway",
    description="HTTP gateway for MCP tool calls",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "mcp-gateway"}


@app.get("/tools")
async def list_tools():
    """List available MCP tools."""
    from server import mcp
    tools = mcp._tool_manager.list_tools()
    return {
        "tools": [
            {
                "name": t.name,
                "description": t.description,
                "parameters": {
                    k: {"type": v.get("type", "string")}
                    for k, v in (t.parameters or {}).items()
                }
            }
            for t in tools
        ]
    }


@app.post("/tools/{tool_name}/call")
async def call_tool(tool_name: str, request: Request):
    """Call a specific MCP tool."""
    body = await request.json()
    from server import mcp
    result = await mcp._tool_manager.call_tool(tool_name, body.get("arguments", {}))
    return {"result": result}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
