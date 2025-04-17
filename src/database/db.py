import contextlib
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from src.conf.config import settings


class DatabaseSessionManager:
    """
    A class for managing asynchronous database sessions.

    This class creates an asynchronous engine and session factory for working with the database.

    Attributes:
    - _engine (AsyncEngine): The asynchronous engine to connect to the database.
    - _session_maker (async_sessionmaker): The factory for creating sessions.

    Methods:
    - _session: Context manager for working with a database session.

    Example usage:
    ```
    async with DatabaseSessionManager(settings.DB_URL).session() as session:
        # Використовуйте session для запитів до бази даних
    ```
    """
    def __init__(self, url: str):
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        """
        Context manager for creating and managing a database session.

        Raises:
        - Exception: If the session factory is not initialized.
        - SQLAlchemyError: If errors occur while working with the session.
        """
        if self._session_maker is None:
            raise Exception("Database session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            raise
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(settings.DB_URL)


async def get_db():
    """
    Generator for getting a database session in FastAPI dependencies.

    Example of use:
    ```
    @router.get("/")
    async def example_endpoint(db: AsyncSession = Depends(get_db)):
    ```
    """
    async with sessionmanager.session() as session:
        yield session
