from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Incident
from app.schemas import IncidentRead

router = APIRouter(prefix="/api/incidents", tags=["incidents"])


@router.get("", response_model=list[IncidentRead])
def list_incidents(
    monitor_id: int | None = None,
    active_only: bool = False,
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[IncidentRead]:
    stmt = select(Incident).order_by(Incident.started_at.desc()).limit(limit)
    if monitor_id is not None:
        stmt = stmt.where(Incident.monitor_id == monitor_id)
    if active_only:
        stmt = stmt.where(Incident.resolved_at.is_(None))

    return list(db.scalars(stmt))
