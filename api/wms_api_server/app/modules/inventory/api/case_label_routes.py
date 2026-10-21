from typing import Literal
from fastapi import APIRouter,Depends,Query,HTTPException
from fastapi.responses import Response
from ...platform.public import AdminUser,get_current_user
from ..contracts_case_labels import CaseSsccLabelRequest,CaseSsccConfirmRequest,CaseLabelPort

router=APIRouter(prefix="/api/case-pick",tags=["case-pick-labels"])
def labels()->CaseLabelPort:raise RuntimeError("CASE labels service not wired")

@router.post("/tasks/{task}/sscc-label")
def issue(task:int,body:CaseSsccLabelRequest,user:AdminUser=Depends(get_current_user),service:CaseLabelPort=Depends(labels))->dict:
    return service.issue(task,body,user.username)

@router.get("/tasks/{task}/sscc-label")
def current(task:int,user:AdminUser=Depends(get_current_user),service:CaseLabelPort=Depends(labels))->dict:
    return service.current(task,user.username)

@router.post("/tasks/{task}/sscc-label/confirm")
def confirm(task:int,body:CaseSsccConfirmRequest,user:AdminUser=Depends(get_current_user),service:CaseLabelPort=Depends(labels))->dict:
    return service.confirm(task,body.scan,user.username)

@router.get("/tasks/{task}/sscc-label/document")
def document(task:int,format:Literal["html","zpl"]="html",dpi:int=Query(203,ge=203,le=600),user:AdminUser=Depends(get_current_user),service:CaseLabelPort=Depends(labels))->Response:
    if dpi not in (203,300,600):raise HTTPException(422,"Supported label printer DPI: 203, 300, 600")
    return Response(service.document(task,user.username,format,dpi),media_type="text/html; charset=utf-8"if format=="html"else "text/plain; charset=utf-8")
