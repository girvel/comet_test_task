import asyncio
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from time import time
from typing import Final, Any

from aiohttp import ClientSession

GITHUB_API_BASE_URL: Final[str] = "https://api.github.com"


@dataclass
class RepositoryAuthorCommitsNum:
    author: str
    commits_num: int


@dataclass(frozen=True)  # frozen to enable hashing to use in asyncio.gather
class Repository:
    name: str
    owner: str
    position: int
    stars: int
    watchers: int
    forks: int
    language: str
    authors_commits_num_today: list[RepositoryAuthorCommitsNum] = field(hash=False)


class GithubReposScraper:
    def __init__(self, access_token: str, mcr: int, rps: float):
        """
        Args:
            access_token: GitHub access token
            mcr: maximal number of concurrent requests
            rps: maximal number of requests per second
        """

        self._session = ClientSession(
            raise_for_status=True,
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"Bearer {access_token}",
            }
        )

        if mcr <= 0:
            raise ValueError("Can't have less than 1 concurrent request")

        if rps <= 0:
            raise ValueError("Can't have 0 or less requests per second")

        self._semaphore = asyncio.Semaphore(mcr)
        self._rps = rps

    async def _make_request(self, endpoint: str, method: str = "GET", params: dict[str, Any] | None = None) -> Any:
        async with self._semaphore:
            t = time()

            async with self._session.request(method, f"{GITHUB_API_BASE_URL}/{endpoint}", params=params) as response:
                result = await response.json()

            t = time() - t
            wait_time = 1 / self._rps - t
            if wait_time > 0:
                await asyncio.sleep(wait_time)

            return result

    async def _get_top_repositories(self, limit: int = 100) -> list[dict[str, Any]]:
        """GitHub REST API: https://docs.github.com/en/rest/search/search?apiVersion=2022-11-28#search-repositories"""
        data = await self._make_request(
            endpoint="search/repositories",
            params={"q": "stars:>1", "sort": "stars", "order": "desc", "per_page": limit},
        )
        return data["items"]

    async def _get_repository_commits(self, owner: str, repo: str) -> list[dict[str, Any]]:
        """GitHub REST API: https://docs.github.com/en/rest/commits/commits?apiVersion=2022-11-28#list-commits"""
        PER_PAGE = 100
        PAGES_N_SANE_MAX = 10

        data = []
        for i in range(PAGES_N_SANE_MAX):
            page = await self._make_request(
                endpoint=f"repos/{owner}/{repo}/commits",
                params={
                    "since": (datetime.now() - timedelta(days=1)).isoformat(timespec="seconds") + "Z",
                    "per_page": PER_PAGE,
                    "page": i + 1,
                },
            )
            data.extend(page)
            if len(page) < PER_PAGE:
                break

        return data

    async def get_repositories(self) -> list[Repository]:
        """Throws aiohttp exceptions"""
        async def f(i: int, repo_raw: dict[str, Any]):
            commits_by_author = defaultdict(lambda: 0)
            for entry in await self._get_repository_commits(repo_raw["owner"]["login"], repo_raw["name"]):
                commits_by_author[entry["commit"]["author"]["email"]] += 1  # because only email is unique

            return Repository(
                name=repo_raw["name"],
                owner=repo_raw["owner"]["login"],
                position=i,
                stars=repo_raw["stargazers_count"],
                watchers=repo_raw["watchers_count"],
                forks=repo_raw["forks"],
                language=repo_raw["language"],
                authors_commits_num_today=[
                    RepositoryAuthorCommitsNum(author=author, commits_num=n)
                    for author, n in commits_by_author.items()
                ],
            )

        return list(await asyncio.gather(*(
            f(i, repo_raw)
            for i, repo_raw in enumerate(await self._get_top_repositories())
        )))

    async def close(self):
        await self._session.close()
