import asyncio
import os
import sys
from datetime import datetime

from aiohttp import ClientSession, ClientResponseError
from aiochclient import ChClient

from scraper import GithubReposScraper


async def main():
    USER = os.getenv("CLICKHOUSE_USER")
    PASSWORD = os.getenv("CLICKHOUSE_PASSWORD")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

    if not (len(USER) > 0 and len(PASSWORD) > 0 and len(GITHUB_TOKEN) > 0):
        print("Error: environment variables CLICKHOUSE_USER, CLICKHOUSE_PASSWORD and GITHUB_TOKEN are required")
        sys.exit(1)

    async with (
        ClientSession() as session,
        ChClient(session, "http://db:8123", user=USER, password=PASSWORD) as client
    ):
        if not await client.is_alive():
            print("Unable to connect to clickhouse")
            sys.exit(1)

        print(f"DB version is {await client.fetchval('SELECT version()')}")

        scraper = GithubReposScraper(GITHUB_TOKEN, mcr=10, rps=10)
        try:
            repos = await scraper.get_repositories()
        except ClientResponseError as ex:
            print(f"Error scraping github: {ex.status}, {ex.message}")
            sys.exit(1)
        finally:
            await scraper.close()

        print("Scraped repositories")

        updated_time = datetime.now().replace(microsecond=0)
        # .replace prevents aiochclient datetime bug

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
        print("Finished.")


if __name__ == "__main__":
    asyncio.run(main())
