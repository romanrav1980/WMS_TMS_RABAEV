"""Independent store application, using the shared RUSERS identity without admin-shell rights."""
from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from ...platform.public import AdminUser, get_current_user
from ..contracts import StoreReceiptError
from ..contracts_store_app import StoreAppPort, store_app_service

router = APIRouter(prefix="/api/store-app", tags=["store-application"])
StoreKey = Annotated[str, Query(pattern=r"^[a-f0-9]{64}$")]


def failure(error: StoreReceiptError) -> HTTPException:
    return HTTPException(error.status, detail={"code":error.code,"message":str(error)})


@router.get("/session")
def session(user: AdminUser=Depends(get_current_user), service: StoreAppPort=Depends(store_app_service)) -> dict[str, Any]:
    try:
        return service.session(user.username)
    except StoreReceiptError as error:
        raise failure(error) from error


@router.get("/deliveries")
def deliveries(store_id: StoreKey, after: str=Query(default="",max_length=100), limit: int=Query(default=50,ge=1,le=200),
               user: AdminUser=Depends(get_current_user), service: StoreAppPort=Depends(store_app_service)) -> dict[str, Any]:
    try:
        return service.deliveries(user.username,store_id,after,limit)
    except StoreReceiptError as error:
        raise failure(error) from error


@router.get("/deliveries/lookup")
def lookup(store_id: StoreKey, code: str=Query(min_length=1,max_length=200),
           user: AdminUser=Depends(get_current_user), service: StoreAppPort=Depends(store_app_service)) -> dict[str, Any]:
    try:
        return service.lookup(user.username,store_id,code)
    except StoreReceiptError as error:
        raise failure(error) from error


@router.get("/deliveries/{load_operation_id}")
def preview(load_operation_id: Annotated[str,Path(min_length=1,max_length=100)], store_id: StoreKey,
            user: AdminUser=Depends(get_current_user), service: StoreAppPort=Depends(store_app_service)) -> dict[str, Any]:
    try:
        return service.preview(user.username,store_id,load_operation_id)
    except StoreReceiptError as error:
        raise failure(error) from error


@router.get("/receipts/{operation_id}")
def receipt(operation_id: Annotated[str,Path(min_length=1,max_length=100)], store_id: StoreKey,
            user: AdminUser=Depends(get_current_user), service: StoreAppPort=Depends(store_app_service)) -> dict[str, Any]:
    try:
        return service.receipt(user.username,store_id,operation_id)
    except StoreReceiptError as error:
        raise failure(error) from error
