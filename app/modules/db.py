from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row



class Database:
    def __init__(self, dsn: str, min_size: int = 1, max_size: int = 10):
        self._dsn = dsn
        self._pool: AsyncConnectionPool | None = None
        self._min_size = min_size
        self._max_size = max_size

    async def connect(self):
        if self._pool is None:
            self._pool = AsyncConnectionPool(
                conninfo=self._dsn,
                min_size=self._min_size,
                max_size=self._max_size,
                open=False,
            )
            await self._pool.open()

    async def disconnect(self):
        if self._pool is not None:
            await self._pool.close()
            self._pool = None

    async def execute(self, query: str, *args, **kwargs):
        async with self._pool.connection() as conn:
            async with conn.cursor() as cur:
                if kwargs:
                    await cur.execute(query, kwargs)
                else:
                    await cur.execute(query, args)
                return cur.rowcount

    async def fetch(self, query: str, *args, **kwargs):
        async with self._pool.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cur:
                if kwargs:
                    await cur.execute(query, kwargs)
                else:
                    await cur.execute(query, args)
                return await cur.fetchall()

    async def fetchone(self, query: str, *args, **kwargs):
        async with self._pool.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cur:
                if kwargs:
                    await cur.execute(query, kwargs)
                else:
                    await cur.execute(query, args)
                return await cur.fetchone()