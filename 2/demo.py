import asyncio
import sys

import main


async def entrypoint():
    scrapper = main.GithubReposScraper(sys.argv[1])
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
        print(f"MAX COMMITS IN {max_repo.owner}/{max_repo.name} ({max_commits_n}\n\n{max_repo})")
    finally:
        await scrapper.close()


if __name__ == "__main__":
    asyncio.run(entrypoint())
