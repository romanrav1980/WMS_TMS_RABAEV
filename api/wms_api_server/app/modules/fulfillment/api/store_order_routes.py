import xml.etree.ElementTree as ET
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool
from ....auth import AdminUser, require_permission
from ..application.ports import StoreOrdersPort, StoreOrderConflict, PreparationPort
from decimal import Decimal

router=APIRouter(prefix='/api/integrations/sap/store-orders',tags=['sap-store-orders'])


def store_order_service() -> StoreOrdersPort:
    raise RuntimeError('Store order service not wired')


def preparation_service() -> PreparationPort:
    raise RuntimeError('Legacy preparation service not wired')


class PalletLine(BaseModel):
    articul: str = Field(min_length=1,max_length=40)
    quantity: Decimal = Field(gt=0,max_digits=18,decimal_places=6,allow_inf_nan=False)


class PalletLayout(BaseModel):
    lines: list[PalletLine] = Field(min_length=1,max_length=1000)


class PreparationRequest(BaseModel):
    operation_id: str = Field(min_length=1,max_length=100,pattern=r'^[A-Za-z0-9_.:-]+$')
    pallets: list[PalletLayout] = Field(min_length=1,max_length=100)


@router.post('/{order_id}/prepare-st')
def prepare_st(order_id: int,body: PreparationRequest,user: AdminUser=Depends(require_permission('customer_order_import')),
               service: PreparationPort=Depends(preparation_service)) -> dict:
    if sum(len(p.lines) for p in body.pallets)>10000:
        raise HTTPException(422,'At most 10000 planned rows')
    try:
        return service.prepare(order_id,body.model_dump(mode='json'),user.username)
    except LookupError as exc:
        raise HTTPException(404,str(exc)) from exc
    except StoreOrderConflict as exc:
        raise HTTPException(409,str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(422,str(exc)) from exc


class StoreCalendar(BaseModel):
    utc_offset_minutes: int = Field(ge=-720,le=840)
    delivery_weekdays: list[Annotated[int,Field(ge=1,le=7)]] = Field(min_length=1,max_length=7)
    allow_same_day: bool = False


@router.post('',status_code=202)
async def receive_order(request: Request,user: AdminUser=Depends(require_permission('sap_store_order_import')),
                        service: StoreOrdersPort=Depends(store_order_service)) -> dict:
    raw=bytearray()
    async for chunk in request.stream():
        if len(raw)+len(chunk)>4*1024*1024:
            raise HTTPException(413,'XML exceeds 4 MiB')
        raw.extend(chunk)
    try:
        return await run_in_threadpool(service.receive,bytes(raw),user.username)
    except StoreOrderConflict as exc:
        raise HTTPException(409,str(exc)) from exc
    except (ValueError,ET.ParseError,UnicodeDecodeError) as exc:
        raise HTTPException(422,str(exc)) from exc


@router.get('')
def list_orders(warehouse_id: int | None=None,limit: int=Query(100,ge=1,le=200),
                user: AdminUser=Depends(require_permission('customer_order_view')),
                service: StoreOrdersPort=Depends(store_order_service)) -> list[dict]:
    return service.list(warehouse_id,limit)


@router.put('/warehouses/{warehouse}/stores/{store_code}/calendar')
def configure_calendar(warehouse: int,store_code: str,body: StoreCalendar,
                       user: AdminUser=Depends(require_permission('customer_rule_edit')),
                       service: StoreOrdersPort=Depends(store_order_service)) -> dict:
    try:
        return service.configure(warehouse,store_code,body.model_dump(),user.username)
    except ValueError as exc:
        raise HTTPException(422,str(exc)) from exc


@router.get('/{order_id}')
def get_order(order_id: int,user: AdminUser=Depends(require_permission('customer_order_view')),
              service: StoreOrdersPort=Depends(store_order_service)) -> dict:
    try:
        return service.get(order_id)
    except LookupError as exc:
        raise HTTPException(404,str(exc)) from exc
