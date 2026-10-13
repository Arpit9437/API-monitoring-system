from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import MonitorCreate, MonitorRead, MonitorStats, MonitorUpdate
from app.services import monitor_service, stats_service

router = APIRouter(prefix="/api/monitors", tags=["monitors"])


@router.get("", response_model=list[MonitorRead])
def list_monitors(db: Session = Depends(get_db)) -> list[MonitorRead]:
    return monitor_service.list_monitors(db)


@router.post("", response_model=MonitorRead, status_code=status.HTTP_201_CREATED)
def create_monitor(data: MonitorCreate, db: Session = Depends(get_db)) -> MonitorRead:
    return monitor_service.create_monitor(db, data)


@router.get("/{monitor_id}", response_model=MonitorRead)
def get_monitor(monitor_id: int, db: Session = Depends(get_db)) -> MonitorRead:
    return monitor_service.get_monitor_or_404(db, monitor_id)


@router.patch("/{monitor_id}", response_model=MonitorRead)
def update_monitor(monitor_id: int, data: MonitorUpdate, db: Session = Depends(get_db)) -> MonitorRead:
    monitor = monitor_service.get_monitor_or_404(db, monitor_id)
    return monitor_service.update_monitor(db, monitor, data)


@router.delete("/{monitor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_monitor(monitor_id: int, db: Session = Depends(get_db)) -> None:
    monitor = monitor_service.get_monitor_or_404(db, monitor_id)
    monitor_service.delete_monitor(db, monitor)


@router.get("/{monitor_id}/stats", response_model=MonitorStats)
def get_monitor_stats(
    monitor_id: int,
    window_hours: int = Query(default=24, ge=1, le=8760),
    db: Session = Depends(get_db),
) -> MonitorStats:
    monitor_service.get_monitor_or_404(db, monitor_id)
    return stats_service.compute_monitor_stats(db, monitor_id, window_hours)
