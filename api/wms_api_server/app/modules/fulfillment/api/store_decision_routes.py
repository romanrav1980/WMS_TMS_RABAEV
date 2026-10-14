"""Bounded normalized ERP decision input; authenticated actor comes from server."""
import xml.etree.ElementTree as ET
from typing import Protocol
from fastapi import APIRouter, Depends, HTTPException, Request
from starlette.concurrency import run_in_threadpool
from ...platform.public import AdminUser, require_permission
from ..application.ports import StoreOrderConflict

router = APIRouter(prefix="/api/integrations/sap/store-decisions", tags=["sap-store-decisions"])


class StoreAdmissionPort(Protocol):
    def receive(self, raw: bytes, actor: str) -> dict: ...


def store_admission_service() -> StoreAdmissionPort:
    raise RuntimeError("Store admission not wired")


@router.post("", status_code=202)
async def receive_decision(request: Request,
                           user: AdminUser = Depends(require_permission("sap_store_decision_import")),
                           service: StoreAdmissionPort = Depends(store_admission_service)) -> dict:
    raw = bytearray()
    async for block in request.stream():
        if len(raw) + len(block) > 4 * 1024 * 1024:
            raise HTTPException(413, "Decision XML exceeds 4 MiB")
        raw.extend(block)
    try:
        return await run_in_threadpool(service.receive, bytes(raw), user.username)
    except PermissionError as exc:
        raise HTTPException(403, str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc
    except StoreOrderConflict as exc:
        raise HTTPException(409, str(exc)) from exc
    except (ValueError, ET.ParseError, UnicodeDecodeError) as exc:
        raise HTTPException(422, str(exc)) from exc
