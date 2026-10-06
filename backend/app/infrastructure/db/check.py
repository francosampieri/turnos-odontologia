import os

import asyncpg


async def check_database() -> bool:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL no configurada")
    dsn = database_url.replace("postgresql+asyncpg://", "postgresql://", 1)
    conn = await asyncpg.connect(dsn)
    try:
        value = await conn.fetchval("SELECT 1")
    finally:
        await conn.close()
    return value == 1