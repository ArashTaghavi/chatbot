import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient


async def main():
    client = MultiServerMCPClient({
        "my_server": {
            "transport": "streamable_http",
            "url": "http://127.0.0.1:8000/mcp",
        }
    })

    tools = await client.get_tools()
    print([tool.name for tool in tools])

    hello = next(t for t in tools if t.name == "say_hello")
    result = await hello.ainvoke({"name": "Arash"})

    print(result)


asyncio.run(main())
