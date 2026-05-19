from fastapi import APIRouter, Depends

from ..auth import (
    AdminUser,
    RESOURCE_MANAGEMENT_EDIT_PERMISSION,
    RESOURCE_MANAGEMENT_VIEW_PERMISSION,
    RESOURCE_SESSION_MANAGE_PERMISSION,
    RESOURCE_SESSION_VIEW_PERMISSION,
    RESOURCE_SHIFT_EDIT_PERMISSION,
    RESOURCE_SHIFT_VIEW_PERMISSION,
    require_permission,
)
from ..schemas import (
    IdResponse,
    ResourceCreateRequest,
    ResourceEquipmentCreateRequest,
    ResourceSessionLoginRequest,
    ResourceSessionStatusRequest,
    ResourceShiftCreateRequest,
    ResourceTsdLoginRequest,
)
from ..services.resource_management_service import ResourceManagementService

router = APIRouter(prefix="/api/resources", tags=["resources"])


@router.get("/types")
def list_resource_types(
    active: int | None = 1,
    _user: AdminUser = Depends(require_permission(RESOURCE_MANAGEMENT_VIEW_PERMISSION)),
) -> list[dict]:
    return ResourceManagementService().list_resource_types(active=active)


@router.get("/equipment")
def list_equipment(
    equipment_type: str | None = None,
    service_status: str | None = None,
    active: int | None = 1,
    limit: int = 200,
    _user: AdminUser = Depends(require_permission(RESOURCE_MANAGEMENT_VIEW_PERMISSION)),
) -> list[dict]:
    return ResourceManagementService().list_equipment(
        equipment_type=equipment_type,
        service_status=service_status,
        active=active,
        limit=limit,
    )


@router.post("/equipment")
def create_equipment(
    request: ResourceEquipmentCreateRequest,
    _user: AdminUser = Depends(require_permission(RESOURCE_MANAGEMENT_EDIT_PERMISSION)),
) -> IdResponse:
    return IdResponse(id=ResourceManagementService().create_equipment(request))


@router.get("")
def list_resources(
    resource_type: str | None = None,
    resource_class: str | None = None,
    status: str | None = None,
    ware_id: int | None = None,
    zone_code: str | None = None,
    active: int | None = 1,
    limit: int = 200,
    _user: AdminUser = Depends(require_permission(RESOURCE_MANAGEMENT_VIEW_PERMISSION)),
) -> list[dict]:
    return ResourceManagementService().list_resources(
        resource_type=resource_type,
        resource_class=resource_class,
        status=status,
        ware_id=ware_id,
        zone_code=zone_code,
        active=active,
        limit=limit,
    )


@router.post("")
def create_resource(
    request: ResourceCreateRequest,
    _user: AdminUser = Depends(require_permission(RESOURCE_MANAGEMENT_EDIT_PERMISSION)),
) -> IdResponse:
    return IdResponse(id=ResourceManagementService().create_resource(request))


@router.get("/shifts")
def list_shifts(
    shift_date: str | None = None,
    ware_id: int | None = None,
    status: str | None = None,
    limit: int = 100,
    _user: AdminUser = Depends(require_permission(RESOURCE_SHIFT_VIEW_PERMISSION)),
) -> list[dict]:
    return ResourceManagementService().list_shifts(
        shift_date=shift_date,
        ware_id=ware_id,
        status=status,
        limit=limit,
    )


@router.post("/shifts")
def create_shift(
    request: ResourceShiftCreateRequest,
    _user: AdminUser = Depends(require_permission(RESOURCE_SHIFT_EDIT_PERMISSION)),
) -> IdResponse:
    return IdResponse(id=ResourceManagementService().create_shift(request))


@router.get("/sessions")
def list_sessions(
    session_id: int | None = None,
    shift_id: int | None = None,
    resource_id: int | None = None,
    status: str | None = None,
    limit: int = 100,
    _user: AdminUser = Depends(require_permission(RESOURCE_SESSION_VIEW_PERMISSION)),
) -> list[dict]:
    return ResourceManagementService().list_sessions(
        session_id=session_id,
        shift_id=shift_id,
        resource_id=resource_id,
        status=status,
        limit=limit,
    )


@router.post("/sessions/login")
def login_session(
    request: ResourceSessionLoginRequest,
    _user: AdminUser = Depends(require_permission(RESOURCE_SESSION_MANAGE_PERMISSION)),
) -> IdResponse:
    return IdResponse(id=ResourceManagementService().login_session(request))


@router.post("/sessions/tsd-login")
def login_tsd_session(
    request: ResourceTsdLoginRequest,
    _user: AdminUser = Depends(require_permission(RESOURCE_SESSION_MANAGE_PERMISSION)),
) -> dict:
    return ResourceManagementService().login_tsd(request)


@router.post("/sessions/{session_id}/heartbeat")
def heartbeat_session(
    session_id: int,
    _user: AdminUser = Depends(require_permission(RESOURCE_SESSION_MANAGE_PERMISSION)),
) -> dict[str, str]:
    ResourceManagementService().heartbeat(session_id)
    return {"status": "ok"}


@router.post("/sessions/{session_id}/pause")
def pause_session(
    session_id: int,
    request: ResourceSessionStatusRequest,
    _user: AdminUser = Depends(require_permission(RESOURCE_SESSION_MANAGE_PERMISSION)),
) -> dict[str, str]:
    ResourceManagementService().pause_session(session_id, request)
    return {"status": "ok"}


@router.post("/sessions/{session_id}/resume")
def resume_session(
    session_id: int,
    request: ResourceSessionStatusRequest,
    _user: AdminUser = Depends(require_permission(RESOURCE_SESSION_MANAGE_PERMISSION)),
) -> dict[str, str]:
    ResourceManagementService().resume_session(session_id, request)
    return {"status": "ok"}


@router.post("/sessions/{session_id}/logout")
def logout_session(
    session_id: int,
    request: ResourceSessionStatusRequest,
    _user: AdminUser = Depends(require_permission(RESOURCE_SESSION_MANAGE_PERMISSION)),
) -> dict[str, str]:
    ResourceManagementService().logout_session(session_id, request)
    return {"status": "ok"}
