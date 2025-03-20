import asyncio

from aiohttp import ClientSession
from aiochclient import ChClient



async def main():
    async with ClientSession() as session:
        client = ChClient(session, "http://db:8123", user="clickhouse", password="clickhouse")
        assert await client.is_alive()
        print("yay!")


if __name__ == "__main__":
    asyncio.run(main())
