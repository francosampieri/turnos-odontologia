from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.infrastructure.db.check import check_database

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> JSONResponse:
    try:
        await check_database()
    except Exception:
        return JSONResponse(
            status_code=503,
            content={"status": "degraded", "database": "error"},
        )
    return JSONResponse(content={"status": "ok", "database": "ok"})