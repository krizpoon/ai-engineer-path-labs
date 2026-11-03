# Generated from src/content/chapters (chapter 8) by `npm run labs`. Edit the chapter, not this file.
import asyncio
from anthropic import AsyncAnthropic
from llm_utils import check_stop, response_text
from anthropic.lib.tools.mcp import async_mcp_tool
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

async def main():
    client = AsyncAnthropic()
    server = StdioServerParameters(command="python", args=["docs_server.py"])

    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            listed = await session.list_tools()

            runner = client.beta.messages.tool_runner(
                model="claude-opus-5-5",
                max_tokens=16000,
                max_iterations=10,
                tools=[async_mcp_tool(t, session) for t in listed.tools],
                messages=[{"role": "user", "content": "How do I deploy to staging?"}],
            )
            async for message in runner:
                if message.stop_reason == "tool_use":
                    continue  # the runner calls the MCP tools
                check_stop(message)
                print(response_text(message))
                break
            else:
                raise RuntimeError("No answer within 10 replies")

asyncio.run(main())
