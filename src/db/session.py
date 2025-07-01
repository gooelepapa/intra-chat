from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# TODO: Need to create another config file for these information
DATABASE_URL = "postgresql+asyncpg://chatuser:chatpass@localhost:5432/intra_chat"

engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_timeout=30,
    echo=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


if __name__ == "__main__":
    import asyncio

    from sqlalchemy import text

    async def test_connection():
        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(text("SELECT 1"))
                print("✅ PostgreSQL Connected:", result.scalar())
        except Exception as e:
            print("❌ Connection failed:", e)

    asyncio.run(test_connection())
