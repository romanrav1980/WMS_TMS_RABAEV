"""Complete bounded binary response; permission dependencies stay on the existing endpoints."""
from typing import Callable
from fastapi import HTTPException, Response
from ..contracts_billing_export import BillingExportError


def billing_export_response(build: Callable[[], bytes], filename: str) -> Response:
    try:
        data = build()
    except BillingExportError as exc:
        raise HTTPException(status_code=exc.status, detail={"code": exc.code, "message": str(exc)}) from exc
    if len(data) > 32 * 1024 * 1024:
        raise HTTPException(status_code=409, detail={"code": "BILLING_EXPORT_BYTE_BOUND_32MB",
            "message": "Выгрузка превышает 32 МБ; уточните фильтры"})
    return Response(content=data, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'})
