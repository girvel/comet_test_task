import asyncio
import os
from datetime import datetime

from aiohttp import ClientSession
from aiochclient import ChClient

from scraper import GithubReposScraper

USER = os.getenv("CLICKHOUSE_USER")
PASSWORD = os.getenv("CLICKHOUSE_PASSWORD")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

assert len(USER) > 0 and len(PASSWORD) > 0 and len(GITHUB_TOKEN) > 0


async def main():
    async with (
        ClientSession() as session,
        ChClient(session, "http://db:8123", user=USER, password=PASSWORD) as client
    ):
        assert await client.is_alive()
        print(f"Version is {await client.fetchval('SELECT version()')}")

        scraper = GithubReposScraper(GITHUB_TOKEN, mcr=10, rps=10)
        try:
            repos = await scraper.get_repositories()
        finally:
            await scraper.close()

        print("Scraped repositories")

        updated_time = datetime.now().replace(microsecond=0)

        await client.execute(
            "INSERT INTO test.repositories SETTINGS async_insert=1, wait_for_async_insert=1 VALUES",
            *(
                (repo.name, repo.owner, repo.stars, repo.watchers, repo.forks, repo.language, updated_time)
                for repo in repos
            )
        )

        await client.execute(
            """
                INSERT INTO test.repositories_authors_commits
                SETTINGS async_insert=1, wait_for_async_insert=1
                VALUES
            """,
            *(
                (updated_time.date(), f"{repo.owner}/{repo.name}", entry.author, entry.commits_num)
                for repo in repos
                for entry in repo.authors_commits_num_today
            )
        )

        await client.execute(
            """
                INSERT INTO test.repositories_positions
                SETTINGS async_insert=1, wait_for_async_insert=1
                VALUES
            """,
            *(
                (updated_time.date(), f"{repo.owner}/{repo.name}", repo.position)
                for repo in repos
            )
        )

        print(f"Pushed results ({len(repos)}) to the DB")


if __name__ == "__main__":
    asyncio.run(main())
