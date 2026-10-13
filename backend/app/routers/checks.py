from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Check
from app.schemas import CheckRead
from app.services.monitor_service import get_monitor_or_404

router = APIRouter(prefix="/api/monitors/{monitor_id}/checks", tags=["checks"])


@router.get("", response_model=list[CheckRead])
def list_checks(
    monitor_id: int,
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[CheckRead]:
    get_monitor_or_404(db, monitor_id)

    checks = db.scalars(
        select(Check).where(Check.monitor_id == monitor_id).order_by(Check.checked_at.desc()).limit(limit)
    )
    return list(checks)
