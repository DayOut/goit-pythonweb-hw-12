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