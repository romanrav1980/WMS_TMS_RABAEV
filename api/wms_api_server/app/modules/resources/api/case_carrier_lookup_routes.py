"""Scan a carrier using the existing current warehouse and whole-CASE owner read scopes."""
from typing import Any
from fastapi import APIRouter,Depends,HTTPException,Query
from ...platform.public import AdminUser,get_current_user
from ..contracts_case_read import CaseReadPort,CaseReadError,case_read_service
router=APIRouter(prefix='/api/case-pick',tags=['case-carrier-lookup'])

@router.get('/resolve-carrier')
def resolve(warehouse_id:int=Query(gt=0),pallet_identifier:str=Query(min_length=1,max_length=150),user:AdminUser=Depends(get_current_user),service:CaseReadPort=Depends(case_read_service))->dict[str,Any]:
    try:return service.carrier(warehouse_id,pallet_identifier,user.username)
    except CaseReadError as exc:raise HTTPException(exc.status,{'code':exc.code})from exc
