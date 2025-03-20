import asyncio
import sys

from aiohttp import ClientResponseError

import main


async def entrypoint():
    if len(sys.argv) != 2:
        print(f"FORMAT: {sys.argv[0]} <GITHUB_TOKEN>")
        sys.exit(1)

    scrapper = main.GithubReposScraper(sys.argv[1], 10, 10)
    try:
        repos = await scrapper.get_repositories()

        max_commits_n = 0
        max_commits_index = -1
        for i, repo in enumerate(repos):
            commits_n = sum(e.commits_num for e in repo.authors_commits_num_today)
            if commits_n > max_commits_n:
                max_commits_n = commits_n
                max_commits_index = i

        max_repo = repos[max_commits_index]
        print(f"MAX COMMITS IN {max_repo.owner}/{max_repo.name} ({max_commits_n})\n\n{max_repo}")
    except ClientResponseError as ex:
        print(f"Error scraping GitHub: {ex.status} {ex.message}")
        sys.exit(1)
    finally:
        await scrapper.close()


if __name__ == "__main__":
    asyncio.run(entrypoint())
