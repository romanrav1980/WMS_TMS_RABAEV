"""Bound the raw photo stream before full decoder/Oracle work."""
from typing import Any,Literal
from fastapi import APIRouter,Depends,HTTPException,Request,Response
from fastapi.concurrency import run_in_threadpool
from ...platform.public import AdminUser,require_permission,get_current_user
from ..contracts import StoreReceiptError
from ..contracts_evidence import StoreEvidencePort,store_evidence_service

router=APIRouter(prefix="/api/delivery/store-photos",tags=["store-evidence"])
MAX_UPLOAD=4*1024*1024


def failure(error: StoreReceiptError) -> HTTPException:
    return HTTPException(error.status,detail={"code":error.code,"message":str(error)})


@router.post("/upload")
async def upload(load_operation_id: str,store_address: str,view: Literal["FRONT","LEFT","RIGHT","BACK","TOP"],
                 request: Request,user: AdminUser=Depends(get_current_user),
                 service: StoreEvidencePort=Depends(store_evidence_service)) -> dict[str,Any]:
    if not 1<=len(load_operation_id)<=100 or not 1<=len(store_address)<=255:
        raise HTTPException(422,"Укажите погрузку и адрес магазина")
    mime_type=request.headers.get("content-type","").split(";",1)[0].lower()
    if mime_type not in {"image/jpeg","image/png"}:
        raise HTTPException(415,"Поддерживаются фотографии JPEG и PNG")
    payload=bytearray()
    async for chunk in request.stream():
        if len(payload)+len(chunk)>MAX_UPLOAD:
            raise HTTPException(413,"Фотография превышает 4 МиБ")
        payload.extend(chunk)
    try:
        return await run_in_threadpool(service.upload,load_operation_id,store_address,view,mime_type,bytes(payload),user.username)
    except StoreReceiptError as exc:
        raise failure(exc) from exc


@router.get("/list")
def photos(load_operation_id: str,store_address: str,
           user: AdminUser=Depends(get_current_user),
           service: StoreEvidencePort=Depends(store_evidence_service)) -> list[dict[str,Any]]:
    if not 1<=len(load_operation_id)<=100 or not 1<=len(store_address)<=255:
        raise HTTPException(422,"Укажите погрузку и адрес магазина")
    try:
        return service.photos(load_operation_id,store_address,user.username)
    except StoreReceiptError as exc:
        raise failure(exc) from exc


@router.get("/{photo_id}/content")
def content(photo_id: str,user: AdminUser=Depends(get_current_user),
            service: StoreEvidencePort=Depends(store_evidence_service)) -> Response:
    if len(photo_id)!=64 or any(character not in "ABCDEF0123456789" for character in photo_id):
        raise HTTPException(422,"Некорректный идентификатор фотографии")
    try:
        archived=service.content(photo_id,user.username)
        return Response(archived.contents,media_type=archived.mime_type,
                        headers={"ETag":'"'+archived.sha256+'"',"X-Content-Type-Options":"nosniff","Cache-Control":"private, no-store"})
    except StoreReceiptError as exc:
        raise failure(exc) from exc
