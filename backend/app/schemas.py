from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.models import HttpMethod, MonitorStatus


class MonitorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    url: HttpUrl
    method: HttpMethod = HttpMethod.GET
    expected_status: int = Field(default=200, ge=100, le=599)
    interval_seconds: int = Field(default=60, ge=5, le=86400)
    timeout_seconds: int = Field(default=5, ge=1, le=60)
    is_active: bool = True


class MonitorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    url: HttpUrl | None = None
    method: HttpMethod | None = None
    expected_status: int | None = Field(default=None, ge=100, le=599)
    interval_seconds: int | None = Field(default=None, ge=5, le=86400)
    timeout_seconds: int | None = Field(default=None, ge=1, le=60)
    is_active: bool | None = None


class MonitorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    url: str
    method: HttpMethod
    expected_status: int
    interval_seconds: int
    timeout_seconds: int
    is_active: bool
    status: MonitorStatus
    last_checked_at: datetime | None
    created_at: datetime
    updated_at: datetime


class CheckRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    monitor_id: int
    success: bool
    status_code: int | None
    response_time_ms: float | None
    error_message: str | None
    checked_at: datetime


class IncidentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    monitor_id: int
    cause: str
    started_at: datetime
    resolved_at: datetime | None
    is_active: bool


class MonitorStats(BaseModel):
    monitor_id: int
    window_hours: int
    total_checks: int
    successful_checks: int
    uptime_percentage: float
    average_response_time_ms: float | None


class CheckEvent(BaseModel):
    monitor_id: int
    monitor_name: str
    status: MonitorStatus
    check: CheckRead
