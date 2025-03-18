from contextlib import asynccontextmanager
from typing import Annotated, TypeAlias

import asyncpg
import uvicorn
from fastapi import APIRouter, FastAPI, Depends, Request


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with asyncpg.create_pool(
        host="db",
        database="testdb",
        user="postgres",
        password="postgres",
    ) as pool:  # TODO! hardcode
        yield {"db_pool": pool}


async def get_pg_connection(request: Request) -> asyncpg.Connection:
    async with request.state.db_pool.acquire() as conn:
        yield conn

PgConnection: TypeAlias = Annotated[asyncpg.Connection, Depends(get_pg_connection)]


async def get_db_version(conn: PgConnection):
    return await conn.fetchval("SELECT version()")


def register_routes(app: FastAPI):
    router = APIRouter(prefix="/api")
    router.add_api_route(path="/db_version", endpoint=get_db_version)
    app.include_router(router)


def create_app() -> FastAPI:
    app = FastAPI(title="e-Comet", lifespan=lifespan)
    register_routes(app)
    return app


if __name__ == "__main__":
    uvicorn.run("main:create_app", factory=True, host="0.0.0.0")  # TODO! 0.0.0.0 is probably not hardcode, right?
