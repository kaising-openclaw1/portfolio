#!/usr/bin/env python3
"""
KaiStudio Enterprise MCP Server
================================
企业级 MCP 工具集：数据库查询、HTTP API 调用、数据分析、文件管理、定时任务

Usage:
    python server.py          # stdio mode (for Claude Desktop, Cursor)
    python http_server.py     # HTTP/SSE mode (for remote clients)
"""

from fastmcp import FastMCP
from typing import Optional
import sqlite3
import httpx
import json
import os
from datetime import datetime

mcp = FastMCP(
    name="KaiStudio Enterprise Tools",
    version="1.0.0",
    instructions=(
        "企业级工具集，支持：\n"
        "1. query_database - SQL 查询（只读）\n"
        "2. call_api - HTTP API 调用\n"
        "3. analyze_data - 数据统计分析\n"
        "4. read_file - 文件读取\n"
        "5. schedule_task - 定时任务管理"
    )
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)


@mcp.tool()
async def query_database(
    sql: str,
    db_path: str = ""
) -> str:
    """Execute a SELECT query against a SQLite database and return results as JSON.
    
    Args:
        sql: The SQL query (SELECT only)
        db_path: Path to the SQLite database file
    """
    if not sql.strip().upper().startswith("SELECT"):
        return "❌ 错误：仅支持 SELECT 查询"

    target = db_path if db_path else os.path.join(DATA_DIR, "analytics.db")

    conn = sqlite3.connect(target)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        cursor.execute(sql)
        columns = [desc[0] for desc in cursor.description]
        rows = [dict(row) for row in cursor.fetchall()]
        return json.dumps({
            "columns": columns,
            "count": len(rows),
            "data": rows
        }, ensure_ascii=False, indent=2, default=str)
    except Exception as e:
        return f"❌ 查询错误: {str(e)}"
    finally:
        conn.close()


@mcp.tool()
async def call_api(
    url: str,
    method: str = "GET",
    headers: Optional[str] = None,
    body: Optional[str] = None
) -> str:
    """Call an external HTTP API.
    
    Args:
        url: Target URL
        method: HTTP method (GET/POST/PUT/DELETE)
        headers: JSON string of request headers
        body: JSON string of request body
    """
    headers_dict = json.loads(headers) if headers else {}

    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers_dict,
                content=body
            )
            return json.dumps({
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response.text[:10000]
            }, ensure_ascii=False, indent=2)
    except httpx.TimeoutException:
        return "❌ 请求超时（30s）"
    except Exception as e:
        return f"❌ 请求失败: {str(e)}"


@mcp.tool()
async def analyze_data(
    data_json: str,
    analysis_type: str = "summary"
) -> str:
    """Perform statistical analysis on JSON data array.
    
    Args:
        data_json: JSON array of objects
        analysis_type: Type of analysis (summary/trend/group)
    """
    try:
        data = json.loads(data_json)
    except json.JSONDecodeError as e:
        return f"❌ JSON 解析错误: {str(e)}"

    if not data or not isinstance(data, list):
        return "❌ 数据格式错误：需要 JSON 对象数组"

    if analysis_type == "summary":
        if not isinstance(data[0], dict):
            return "❌ 数据格式错误：需要 JSON 对象数组"

        numeric_fields = [
            k for k, v in data[0].items()
            if isinstance(v, (int, float))
        ]

        result = {"records": len(data), "numeric_fields": numeric_fields}

        for field in numeric_fields:
            values = [row[field] for row in data if field in row and isinstance(row[field], (int, float))]
            if values:
                result[field] = {
                    "sum": round(sum(values), 2),
                    "avg": round(sum(values) / len(values), 2),
                    "min": round(min(values), 2),
                    "max": round(max(values), 2),
                    "median": round(sorted(values)[len(values) // 2], 2)
                }

        return json.dumps(result, ensure_ascii=False, indent=2)

    elif analysis_type == "trend":
        if len(data) < 2:
            return "❌ 趋势分析需要至少 2 条数据"

        numeric_fields = [
            k for k, v in data[0].items()
            if isinstance(v, (int, float))
        ]

        trends = {}
        for field in numeric_fields:
            values = [row.get(field, 0) for row in data]
            changes = []
            for i in range(1, len(values)):
                if values[i - 1] != 0:
                    change = (values[i] - values[i - 1]) / abs(values[i - 1]) * 100
                    changes.append(round(change, 2))
            trends[field] = {
                "values": values,
                "changes": changes,
                "avg_change": round(sum(changes) / len(changes), 2) if changes else 0,
                "direction": "📈 上升" if changes and sum(changes) > 0 else "📉 下降"
            }

        return json.dumps({"trend_analysis": trends}, ensure_ascii=False, indent=2)

    return f"❌ 不支持的分析类型: {analysis_type}（可选: summary, trend）"


@mcp.tool()
async def read_file(path: str, max_lines: int = 200) -> str:
    """Read file contents with safety limits.
    
    Args:
        path: File path (relative or absolute)
        max_lines: Maximum lines to read (default 200)
    """
    max_lines = min(max_lines, 1000)  # Hard cap
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:max_lines]
            content = ''.join(lines)
            if len(lines) >= max_lines:
                content += f"\n\n... (已截断，共 {max_lines} 行)"
            return content
    except UnicodeDecodeError:
        return "❌ 无法读取：文件不是文本格式"
    except Exception as e:
        return f"❌ 读取失败: {str(e)}"


@mcp.tool()
async def schedule_task(
    task_name: str,
    cron_expr: str,
    action: str
) -> str:
    """Create a scheduled task with cron expression.
    
    Args:
        task_name: Task name
        cron_expr: Cron expression (min hour day month weekday)
        action: Description of action to execute
    """
    parts = cron_expr.split()
    if len(parts) != 5:
        return "❌ Cron 表达式需要 5 个字段 (分 时 日 月 周)，例如: 0 9 * * 1-5"

    task = {
        "name": task_name,
        "cron": cron_expr,
        "action": action,
        "created_at": datetime.now().isoformat(),
        "status": "active",
        "id": f"task_{int(datetime.now().timestamp())}"
    }

    task_file = os.path.join(DATA_DIR, "scheduled_tasks.jsonl")
    with open(task_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(task, ensure_ascii=False) + "\n")

    return json.dumps({
        "message": f"✅ 任务 '{task_name}' 已创建",
        "task": task,
        "tip": f"配置调度器后，将按 '{cron_expr}' 自动执行"
    }, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    mcp.run()
