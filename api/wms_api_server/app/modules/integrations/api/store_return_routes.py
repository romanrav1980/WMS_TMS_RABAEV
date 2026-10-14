from typing import Any
import xml.etree.ElementTree as ET
from fastapi import APIRouter,Depends,HTTPException,Request
from starlette.concurrency import run_in_threadpool
from ...platform.public import AdminUser,require_permission
from ...delivery.public import StoreReceiptError
from ..contracts_returns import SapStoreReturnsPort,sap_store_returns_service
from ..domain.store_return import MAX_RETURN_XML_BYTES

router=APIRouter(prefix="/api/integrations/sap/store-returns",tags=["sap-store-returns"])


@router.post("",status_code=202)
async def receive(request: Request,user: AdminUser=Depends(require_permission("sap_return_import")),
                  service: SapStoreReturnsPort=Depends(sap_store_returns_service)) -> dict[str,Any]:
    raw=bytearray()
    async for chunk in request.stream():
        if len(raw)+len(chunk)>MAX_RETURN_XML_BYTES:
            raise HTTPException(413,"Return XML exceeds16KiB")
        raw.extend(chunk)
    try:
        return await run_in_threadpool(service.receive,bytes(raw),user.username)
    except StoreReceiptError as exc:
        raise HTTPException(exc.status,{"code":exc.code,"message":str(exc),"operation_id":exc.operation_id,"outcome_confirmed":exc.status<500}) from exc
    except (ValueError,ET.ParseError,UnicodeDecodeError) as exc:
        raise HTTPException(422,str(exc)) from exc
