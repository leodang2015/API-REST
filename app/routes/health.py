from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.dependencies import SessionDep

router = APIRouter(tags=["salud"])


@router.get("/health")
def health(db: SessionDep) -> dict[str, str]:
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Base de datos no disponible",
        ) from exc
    return {"status": "ok", "database": "ok"}
