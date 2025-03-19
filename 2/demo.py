import asyncio
import sys

import main


async def entrypoint():
    scrapper = main.GithubReposScraper(sys.argv[1])
    try:
        repos = await scrapper.get_repositories()
        print(len(repos))
        print(repos[10].authors_commits_num_today)
    finally:
        await scrapper.close()


if __name__ == "__main__":
    asyncio.run(entrypoint())
