from fastapi import APIRouter, Depends, HTTPException

from ..auth import AdminUser, get_current_admin, serialize_admin_user
from ..modules.platform.public import authorize_admin_shell, MetadataError

router = APIRouter(prefix="/api/admin/auth", tags=["admin-auth"])


def shell_user(user: AdminUser = Depends(get_current_admin)) -> AdminUser:
    try:
        return authorize_admin_shell(user)
    except MetadataError as error:
        raise HTTPException(error.status, detail={"code": error.code}) from error


@router.get("/login")
def login(user: AdminUser = Depends(shell_user)) -> dict:
    return serialize_admin_user(user)


@router.get("/me")
def me(user: AdminUser = Depends(shell_user)) -> dict:
    return serialize_admin_user(user)
