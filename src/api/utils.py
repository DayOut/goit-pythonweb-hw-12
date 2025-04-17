import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.database.db import get_db

router = APIRouter(tags=["utils"])

logger = logging.getLogger(__name__)

SUCCESS_MESSAGE = "Welcome to FastAPI!"
ERROR_DB_SETUP = "Database is not configured correctly"
ERROR_DB_CONNECTION = "Error connecting to the database"


@router.get("/healthchecker", summary="Check database connection")
async def healthchecker(db: AsyncSession = Depends(get_db)) -> dict:
    """
    Check service health and database connection.

    This endpoint performs a simple database query to check if the database is configured correctly,
    and whether the application can successfully connect to it.

    Parameters:
    - db (AsyncSession): The asynchronous database session obtained through the dependency.

    Returns:
    - A dict: A message about the status of the service.

    Error messages:
    - 500 INTERNAL_SERVER_ERROR: If the database is not configured or an error occurs during connection.
    """
    try:
        result = await db.execute(text("SELECT 1"))
        if result.scalar_one_or_none() != 1:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ERROR_DB_SETUP,
            )
        return {"message": SUCCESS_MESSAGE}
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_DB_CONNECTION,
        )