import asyncio
import sys

import main


async def entrypoint():
    scrapper = main.GithubReposScraper(sys.argv[1])
    try:
        print(await scrapper.get_repositories())
    finally:
        await scrapper.close()


if __name__ == "__main__":
    asyncio.run(entrypoint())
