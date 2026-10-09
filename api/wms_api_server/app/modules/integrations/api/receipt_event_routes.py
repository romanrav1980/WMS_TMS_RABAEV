import xml.etree.ElementTree as ET
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from starlette.concurrency import run_in_threadpool
from ....auth import AdminUser, require_permission
from ..application.ingestion import IdocConflict
from ..domain.artmas import MAX_IDOC_BYTES
from ..application.receipt_ports import AcknowledgementPort as ReceiptAcknowledgements

router = APIRouter(prefix="/api/integrations/sap/receipt-events", tags=["sap-receipt-events"])


def acknowledgement_service() -> ReceiptAcknowledgements:
    raise RuntimeError("SAP acknowledgement service not wired")


@router.get("")
def list_receipt_events(limit: int = Query(100, ge=1, le=200), user: AdminUser = Depends(require_permission("sap_supply_view")),
                        service: ReceiptAcknowledgements = Depends(acknowledgement_service)) -> list[dict]:
    return service.list_events(limit)


@router.post("/acknowledgements")
async def receive_ack(request: Request, user: AdminUser = Depends(require_permission("sap_supply_import")),
                       service: ReceiptAcknowledgements = Depends(acknowledgement_service)) -> dict:
    raw = bytearray()
    async for chunk in request.stream():
        if len(raw)+len(chunk)>MAX_IDOC_BYTES:
            raise HTTPException(413, "XML exceeds 4 MiB")
        raw.extend(chunk)
    try:
        return await run_in_threadpool(service.receive, bytes(raw), user.username)
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc
    except IdocConflict as exc:
        raise HTTPException(409, str(exc)) from exc
    except (ValueError, ET.ParseError, UnicodeDecodeError) as exc:
        raise HTTPException(422, str(exc)) from exc


@router.post("/{event_id}/retry")
def retry_receipt_event(event_id: str, user: AdminUser = Depends(require_permission("sap_supply_import")),
                        service: ReceiptAcknowledgements = Depends(acknowledgement_service)) -> dict:
    try:
        return service.retry(event_id)
    except IdocConflict as exc:
        raise HTTPException(409, str(exc)) from exc
