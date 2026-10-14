"""Authenticated existing driver URLs; identity is not inferred from a numeric ID."""
from datetime import date
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query
from ...platform.public import AdminUser, get_current_user
from ..contracts_driver_workspace import DriverWorkspacePort, driver_workspace_service
from ..contracts_plan import TransportPlanError

router=APIRouter(prefix="/api/driver",tags=["driver-mobile"])

def failure(exc: TransportPlanError) -> HTTPException:
    return HTTPException(exc.status,detail={"code":exc.code,"message":str(exc)})

@router.get("/trips")
def trips(driver_id: int=Query(...,gt=0),trip_date: date|None=None,
          user: AdminUser=Depends(get_current_user),
          service: DriverWorkspacePort=Depends(driver_workspace_service)) -> list[dict[str,Any]]:
    try:
        return service.trips(driver_id,trip_date or date.today(),user.username)
    except TransportPlanError as exc:
        raise failure(exc) from exc

@router.get("/trips/{task_id}/sts")
def stops(task_id: int,driver_id: int=Query(...,gt=0),user: AdminUser=Depends(get_current_user),
          service: DriverWorkspacePort=Depends(driver_workspace_service)) -> list[dict[str,Any]]:
    try:
        return service.details(driver_id,task_id,"sts",user.username)
    except TransportPlanError as exc:
        raise failure(exc) from exc

@router.get("/trips/{task_id}/ops")
def operations(task_id: int,driver_id: int=Query(...,gt=0),user: AdminUser=Depends(get_current_user),
               service: DriverWorkspacePort=Depends(driver_workspace_service)) -> list[dict[str,Any]]:
    try:
        return service.details(driver_id,task_id,"ops",user.username)
    except TransportPlanError as exc:
        raise failure(exc) from exc

@router.post("/ops/{op_id}/start")
def start(op_id: int,driver_id: int=Query(...,gt=0),user: AdminUser=Depends(get_current_user),
          service: DriverWorkspacePort=Depends(driver_workspace_service)) -> dict[str,Any]:
    try:
        return service.mark(driver_id,op_id,"START",user.username)
    except TransportPlanError as exc:
        raise failure(exc) from exc

@router.post("/ops/{op_id}/done")
def done(op_id: int,driver_id: int=Query(...,gt=0),user: AdminUser=Depends(get_current_user),
         service: DriverWorkspacePort=Depends(driver_workspace_service)) -> dict[str,Any]:
    try:
        return service.mark(driver_id,op_id,"DONE",user.username)
    except TransportPlanError as exc:
        raise failure(exc) from exc
