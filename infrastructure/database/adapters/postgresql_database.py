from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from core.ports import DatabaseManager
from infrastructure.database.models import Base


class PostgreSQLDatabase(DatabaseManager):
    def __init__(self, database_path):
        self.database_path = database_path
        self._engine = None
        self._session_factory = None
        self._create_database()

    def _create_database(self):
        self._engine = create_async_engine(url=self.database_path)
        self._session_factory = async_sessionmaker(self._engine, expire_on_commit=False)

    async def get_session(self):
        return self._session_factory()

    async def create_tables(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def close(self):
        await self._engine.dispose()
