"""Bounded aware window; native service owns object admission."""
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import AwareDatetime
from ...platform.public import AdminUser, get_current_user
from ..contracts_timeline import ResourceTimelinePort, TimelineError, resource_timeline_service

router = APIRouter(prefix="/api/resources", tags=["resource-timeline"])


@router.get("/timeline")
def timeline(warehouse_id: int = Query(gt=0), start_at: Annotated[AwareDatetime, Query()] = ...,
             finish_at: Annotated[AwareDatetime, Query()] = ...,
             user: AdminUser = Depends(get_current_user),
             service: ResourceTimelinePort = Depends(resource_timeline_service)) -> dict[str, Any]:
    if finish_at <= start_at or finish_at - start_at > timedelta(days=7):
        raise HTTPException(422, detail="Positive interval of at most seven days required")
    try:
        return service.read(warehouse_id, start_at.astimezone(timezone.utc), finish_at.astimezone(timezone.utc), user.username)
    except TimelineError as error:
        raise HTTPException(error.status, detail={"code": error.code}) from error
