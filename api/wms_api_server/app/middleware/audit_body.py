"""Binary archive traffic is bounded and logged as hashes, never replayed as text."""
from dataclasses import dataclass
from fastapi import Request,Response
from ..services.api_audit_service import body_digest,decode_limited,json_dumps

PHOTO_LIMIT=4*1024*1024


@dataclass(frozen=True)
class AuditedRequestBody:
    contents: bytes
    log_body: str
    truncated: int
    too_large: bool=False
    size_error: str="Фотография превышает 4 МиБ"


def is_photo_upload(request: Request) -> bool:
    return request.method.upper()=="POST" and request.url.path.rstrip("/")=="/api/delivery/store-photos/upload"


async def capture_request(request: Request,max_chars: int) -> AuditedRequestBody:
    scale_packet=request.method.upper()=="POST" and request.url.path.rstrip("/") in {"/api/delivery/store-scales/captures", "/api/inventory/warehouse-scales/captures", "/api/inventory/warehouse-scales/final-captures"}
    photo=is_photo_upload(request)
    if not photo and not scale_packet:
        contents=await request.body()
        text,truncated=decode_limited(contents,max_chars)
        return AuditedRequestBody(contents,text,truncated)
    limit=PHOTO_LIMIT if photo else 32000
    collected=bytearray();too_large=False
    async for chunk in request.stream():
        if len(collected)+len(chunk)>limit:
            too_large=True
            break
        collected.extend(chunk)
    contents=bytes(collected)
    request._body=contents  # bounded cache for Starlette _CachedRequest body forwarding
    if scale_packet:
        text,truncated=decode_limited(contents,max_chars)
        return AuditedRequestBody(contents,text,int(too_large) or truncated,too_large,"Пакет весов превышает 32000 байт")
    text=json_dumps({"binary":True,"retained_bytes":len(contents),"sha256":body_digest(contents),
                     "sha256_scope":"retained_prefix" if too_large else "complete_body","too_large":too_large})
    return AuditedRequestBody(contents,text,int(too_large),too_large)


async def capture_response(response: Response,max_chars: int,capture: bool) -> tuple[bytes,str,int]:
    collected=bytearray()
    iterator=getattr(response,"body_iterator",None)
    if iterator is not None:
        async for chunk in iterator:
            collected.extend(chunk)
    else:
        collected.extend(response.body)
    contents=bytes(collected)
    if not capture:
        return contents,"",0
    if response.headers.get("content-type","").split(";",1)[0] in {"image/jpeg","image/png"}:
        return contents,json_dumps({"binary":True,"byte_count":len(contents),"sha256":body_digest(contents)}),0
    text,truncated=decode_limited(contents,max_chars)
    return contents,text,truncated
