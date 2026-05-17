from fastapi import APIRouter, Depends

from ..auth import ADMIN_LOGIN_PERMISSION, AdminUser, require_permission, serialize_admin_user

router = APIRouter(prefix="/api/admin/auth", tags=["admin-auth"])


@router.get("/login")
def login(user: AdminUser = Depends(require_permission(ADMIN_LOGIN_PERMISSION))) -> dict:
    return serialize_admin_user(user)


@router.get("/me")
def me(user: AdminUser = Depends(require_permission(ADMIN_LOGIN_PERMISSION))) -> dict:
    return serialize_admin_user(user)
