# Тестовое задание

[Текст задания](/TASK.md)

TODO!

## Задание #1

how to launch: fill .env + docker compose
why single-file

## Задание #2

If it was real case, I would:
- talk about using BaseModel instead of dataclasses for consistency
- consider using `with` instead of manual `.close()`
- no bounds for scraping were provided => none introduced, assumed non-important, just scraping 100 values for now
- Renamed Scrapper -> Scraper
- Assumed that `position` means "index", would've clarified if it was a real task
- `watchers_count` field in github API search seems to be broken (at least in my tests)
- Uses email, not login/full name as "author", as only email is unique
- There is a `demo.py` for manual testing/demonstration purposes; launch by passing a token through
- Throws aiohttp exceptions, should be handled on user-side as shown in `demo.py`

## Задание #3

## Задание #4
