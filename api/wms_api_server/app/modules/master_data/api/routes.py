from fastapi import APIRouter, Depends, HTTPException

from ....auth import AdminUser, require_permission
from ..contracts import ReceiptPolicyUpdate
from ..application.policy import PolicyConflict, ReceiptPolicyService

router = APIRouter(prefix="/api/finished-goods/skus", tags=["sku-receiving-policy"])


def policy_service() -> ReceiptPolicyService:
    raise RuntimeError("SKU policy service is not wired by composition root.")


@router.get("/{articul}/receiving-policy")
def get_receiving_policy(articul: str, user: AdminUser = Depends(require_permission("finished_goods_view")),
                         service: ReceiptPolicyService = Depends(policy_service)) -> dict:
    try:
        return service.get(articul)
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.put("/{articul}/receiving-policy")
def save_receiving_policy(articul: str, request: ReceiptPolicyUpdate,
                          user: AdminUser = Depends(require_permission("finished_goods_edit")),
                          service: ReceiptPolicyService = Depends(policy_service)) -> dict:
    if len(articul) > 40:
        raise HTTPException(422, "Article identifier exceeds existing SKU key length.")
    try:
        return service.replace(articul, request, user.username)
    except PolicyConflict as exc:
        raise HTTPException(409, str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc
