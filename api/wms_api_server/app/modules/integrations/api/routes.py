import xml.etree.ElementTree as ET

from fastapi import APIRouter, Depends, HTTPException, Request
from starlette.concurrency import run_in_threadpool

from ....auth import AdminUser, require_permission
from ..application.ingestion import ArtmasIngestion, IdocConflict
from ..domain.artmas import MAX_IDOC_BYTES

router = APIRouter(prefix="/api/integrations/sap/artmas", tags=["sap-retail"])


def artmas_service() -> ArtmasIngestion:
    raise RuntimeError("ARTMAS inbox is not wired by composition root.")


@router.post("", status_code=202)
async def receive_artmas(request: Request, user: AdminUser = Depends(require_permission("sap_article_import")),
                         service: ArtmasIngestion = Depends(artmas_service)) -> dict:
    raw = bytearray()
    async for chunk in request.stream():
        if len(raw) + len(chunk) > MAX_IDOC_BYTES:
            raise HTTPException(413, "ARTMAS payload exceeds 4 MiB.")
        raw.extend(chunk)
    try:
        return await run_in_threadpool(service.receive, bytes(raw), user.username)
    except IdocConflict as exc:
        raise HTTPException(409, str(exc)) from exc
    except (ValueError, ET.ParseError, UnicodeDecodeError) as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/{inbox_id}")
def get_artmas(inbox_id: str, user: AdminUser = Depends(require_permission("sap_article_import")),
               service: ArtmasIngestion = Depends(artmas_service)) -> dict:
    try:
        return service.get(inbox_id)
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc
