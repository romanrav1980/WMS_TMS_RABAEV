"""Authenticated scoped CASE metadata; native current scope remains authoritative."""
from typing import Any
from fastapi import APIRouter,Depends,HTTPException,Query
from fastapi.responses import JSONResponse
from ...platform.public import AdminUser,get_current_user
from ..contracts_case_resource import CaseResourceCommand,CaseResourceError,CaseResourcePort,case_resource_service
router=APIRouter(prefix="/api/case-pick",tags=["case-resource-commands"])


def failure(error:CaseResourceError)->HTTPException:
    return HTTPException(error.status,dict(code=error.code,operation_id=error.operation_id,outcome_confirmed=False,read_before_retry=True))


@router.get("/tasks/{task_id}/transfer-receipt")
def transfer_receipt(task_id:int,offline_event_id:str=Query(min_length=1,max_length=100),
                     user:AdminUser=Depends(get_current_user),
                     service:CaseResourcePort=Depends(case_resource_service))->dict[str,Any]:
    try:return service.transfer_receipt(task_id,offline_event_id,user.username)
    except CaseResourceError as error:raise failure(error)from error


@router.get("/tasks/{task_id}/resource-context")
def context(task_id:int,user:AdminUser=Depends(get_current_user),service:CaseResourcePort=Depends(case_resource_service))->dict[str,Any]:
    try:return service.context(task_id,user.username)
    except CaseResourceError as error:raise failure(error)from error


@router.post("/tasks/{task_id}/resource-commands",response_model=None)
def command(task_id:int,body:CaseResourceCommand,user:AdminUser=Depends(get_current_user),service:CaseResourcePort=Depends(case_resource_service))->Any:
    try:result=service.command(task_id,body,user.username)
    except CaseResourceError as error:raise failure(error)from error
    return JSONResponse(status_code=409,content=result)if result["outcome"]=="REJECTED"else result


@router.get("/tasks/{task_id}/resource-sessions")
def sessions(task_id:int,user:AdminUser=Depends(get_current_user),service:CaseResourcePort=Depends(case_resource_service))->dict[str,Any]:
    try:return service.sessions(task_id,user.username)
    except CaseResourceError as error:raise failure(error)from error


@router.get("/resource-commands/{operation_id}")
def receipt(operation_id:str,user:AdminUser=Depends(get_current_user),service:CaseResourcePort=Depends(case_resource_service))->dict[str,Any]:
    try:return service.receipt(operation_id,user.username)
    except CaseResourceError as error:raise failure(error)from error
