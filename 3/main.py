import asyncio
import os

from aiohttp import ClientSession
from aiochclient import ChClient

from scraper import GithubReposScraper

USER = os.getenv("CLICKHOUSE_USER")
PASSWORD = os.getenv("CLICKHOUSE_PASSWORD")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

assert len(USER) > 0 and len(PASSWORD) > 0 and len(GITHUB_TOKEN) > 0
print(GITHUB_TOKEN)


async def main():
    async with ClientSession() as session:
        client = ChClient(session, "http://db:8123", user=USER, password=PASSWORD)
        assert await client.is_alive()
        print(f"version is {await client.fetchval('SELECT version()')}")

        repos = await GithubReposScraper(GITHUB_TOKEN, mcr=10, rps=10).get_repositories()
        print(repos)
        print(await client.fetch('SELECT * FROM test.repositories'))


if __name__ == "__main__":
    asyncio.run(main())
