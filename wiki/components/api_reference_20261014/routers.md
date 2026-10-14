# Методы: routers

### login

[Исходник: api/wms_api_server/app/routers/admin_auth.py:9](../../../api/wms_api_server/app/routers/admin_auth.py#L9)

```python
login(user: AdminUser=Depends(require_permission(ADMIN_LOGIN_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `require_permission`, `router.get`, `serialize_admin_user`

### me

[Исходник: api/wms_api_server/app/routers/admin_auth.py:14](../../../api/wms_api_server/app/routers/admin_auth.py#L14)

```python
me(user: AdminUser=Depends(require_permission(ADMIN_LOGIN_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `require_permission`, `router.get`, `serialize_admin_user`

### list_users

[Исходник: api/wms_api_server/app/routers/admin_rights.py:16](../../../api/wms_api_server/app/routers/admin_rights.py#L16)

```python
list_users(query: str | None=None, group_id: str | None=None, include_deleted: int=0, limit: int=200, _user: AdminUser=Depends(require_permission(RIGHTS_ADMIN_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `Depends`, `OracleGateway`, `OracleGateway().fetch_all`, `max`, `min`, `require_permission`, `router.get`, `where.append`

### list_groups

[Исходник: api/wms_api_server/app/routers/admin_rights.py:48](../../../api/wms_api_server/app/routers/admin_rights.py#L48)

```python
list_groups(_user: AdminUser=Depends(require_permission(RIGHTS_ADMIN_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `OracleGateway`, `OracleGateway().fetch_all`, `require_permission`, `router.get`

### upsert_group

[Исходник: api/wms_api_server/app/routers/admin_rights.py:75](../../../api/wms_api_server/app/routers/admin_rights.py#L75)

```python
upsert_group(request: RightsGroupRequest, _user: AdminUser=Depends(require_permission(RIGHTS_ADMIN_EDIT_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `OracleGateway`, `OracleGateway().execute`, `normalize_group_id`, `request.name.strip`, `require_permission`, `router.post`

### list_group_rights

[Исходник: api/wms_api_server/app/routers/admin_rights.py:95](../../../api/wms_api_server/app/routers/admin_rights.py#L95)

```python
list_group_rights(group_id: str, _user: AdminUser=Depends(require_permission(RIGHTS_ADMIN_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `OracleGateway`, `OracleGateway().fetch_all`, `require_permission`, `router.get`

### grant_group_right

[Исходник: api/wms_api_server/app/routers/admin_rights.py:111](../../../api/wms_api_server/app/routers/admin_rights.py#L111)

```python
grant_group_right(group_id: str, request: RightsGrantRequest, _user: AdminUser=Depends(require_permission(RIGHTS_ADMIN_EDIT_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `OracleGateway`, `OracleGateway().execute`, `OracleGateway().fetch_all`, `normalize_right_name`, `require_permission`, `router.post`

### revoke_group_right

[Исходник: api/wms_api_server/app/routers/admin_rights.py:154](../../../api/wms_api_server/app/routers/admin_rights.py#L154)

```python
revoke_group_right(group_id: str, right_name: str, _user: AdminUser=Depends(require_permission(RIGHTS_ADMIN_EDIT_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `OracleGateway`, `OracleGateway().execute`, `normalize_right_name`, `require_permission`, `router.delete`

### update_user_group

[Исходник: api/wms_api_server/app/routers/admin_rights.py:172](../../../api/wms_api_server/app/routers/admin_rights.py#L172)

```python
update_user_group(user_id: str, request: RightsUserGroupRequest, _user: AdminUser=Depends(require_permission(RIGHTS_ADMIN_EDIT_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `OracleGateway`, `OracleGateway().execute`, `legacy_group_exists`, `normalize_group_id`, `require_permission`, `router.put`

### normalize_group_id

[Исходник: api/wms_api_server/app/routers/admin_rights.py:199](../../../api/wms_api_server/app/routers/admin_rights.py#L199)

```python
normalize_group_id(value: str) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `len`, `value.strip`, `value.strip().upper`

### legacy_group_exists

[Исходник: api/wms_api_server/app/routers/admin_rights.py:208](../../../api/wms_api_server/app/routers/admin_rights.py#L208)

```python
legacy_group_exists(group_id: str) -> bool
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `OracleGateway().fetch_all`, `bool`

### normalize_right_name

[Исходник: api/wms_api_server/app/routers/admin_rights.py:226](../../../api/wms_api_server/app/routers/admin_rights.py#L226)

```python
normalize_right_name(value: str) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `len`, `value.strip`, `value.strip().upper`

### list_api_calls

[Исходник: api/wms_api_server/app/routers/api_audit.py:11](../../../api/wms_api_server/app/routers/api_audit.py#L11)

```python
list_api_calls(from_call_id: int | None=None, to_call_id: int | None=None, from_at: str | None=None, to_at: str | None=None, method: str | None=None, path_like: str | None=None, status: str | None=None, replayable: int | None=None, limit: int=100, offset: int=0, _user: AdminUser=Depends(require_permission(API_AUDIT_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ApiAuditService`, `ApiAuditService().list_calls`, `Depends`, `require_permission`, `router.get`

### get_api_call

[Исходник: api/wms_api_server/app/routers/api_audit.py:39](../../../api/wms_api_server/app/routers/api_audit.py#L39)

```python
get_api_call(api_call_id: int, _user: AdminUser=Depends(require_permission(API_AUDIT_VIEW_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ApiAuditService`, `ApiAuditService().get_call`, `Depends`, `HTTPException`, `require_permission`, `router.get`

### replay_api_calls

[Исходник: api/wms_api_server/app/routers/api_audit.py:50](../../../api/wms_api_server/app/routers/api_audit.py#L50)

```python
replay_api_calls(request: ApiReplayRequest, user: AdminUser=Depends(require_permission(API_AUDIT_VIEW_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ApiAuditService`, `ApiAuditService().replay_calls`, `Depends`, `HTTPException`, `hasattr`, `request.dict`, `request.model_dump`, `require_permission`, `router.post`

### list_boms

[Исходник: api/wms_api_server/app/routers/bom.py:29](../../../api/wms_api_server/app/routers/bom.py#L29)

```python
list_boms(target_articul: str | None=None, status: str | None=None, is_primary: int | None=None, active_on: date | None=None, limit: int=100, _user: AdminUser=Depends(require_permission(BOM_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `BomService`, `BomService().list_boms`, `Depends`, `require_permission`, `router.get`

### create_bom

[Исходник: api/wms_api_server/app/routers/bom.py:47](../../../api/wms_api_server/app/routers/bom.py#L47)

```python
create_bom(request: BomCreateRequest, _user: AdminUser=Depends(require_permission(BOM_EDIT_PERMISSION))) -> IdResponse
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `BomService`, `BomService().create_bom`, `Depends`, `IdResponse`, `require_permission`, `router.post`

### find_default_bom

[Исходник: api/wms_api_server/app/routers/bom.py:55](../../../api/wms_api_server/app/routers/bom.py#L55)

```python
find_default_bom(target_articul: str, planned_date: date | None=None, target_mod_id: int | None=None, ware_id: int | None=None, production_line: str | None=None, _user: AdminUser=Depends(require_permission(BOM_VIEW_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `BomService`, `BomService().find_primary`, `Depends`, `HTTPException`, `require_permission`, `router.get`

### get_bom

[Исходник: api/wms_api_server/app/routers/bom.py:76](../../../api/wms_api_server/app/routers/bom.py#L76)

```python
get_bom(bom_id: int, _user: AdminUser=Depends(require_permission(BOM_VIEW_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `BomService`, `BomService().get_bom`, `Depends`, `HTTPException`, `require_permission`, `router.get`

### update_bom

[Исходник: api/wms_api_server/app/routers/bom.py:87](../../../api/wms_api_server/app/routers/bom.py#L87)

```python
update_bom(bom_id: int, request: BomUpdateRequest, _user: AdminUser=Depends(require_permission(BOM_EDIT_PERMISSION))) -> dict[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `BomService`, `BomService().update_bom`, `Depends`, `require_permission`, `router.patch`

### add_bom_line

[Исходник: api/wms_api_server/app/routers/bom.py:97](../../../api/wms_api_server/app/routers/bom.py#L97)

```python
add_bom_line(bom_id: int, request: BomLineRequest, _user: AdminUser=Depends(require_permission(BOM_EDIT_PERMISSION))) -> IdResponse
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `BomService`, `BomService().add_line`, `Depends`, `IdResponse`, `require_permission`, `router.post`

### update_bom_line

[Исходник: api/wms_api_server/app/routers/bom.py:106](../../../api/wms_api_server/app/routers/bom.py#L106)

```python
update_bom_line(bom_id: int, line_id: int, request: BomLineRequest, _user: AdminUser=Depends(require_permission(BOM_EDIT_PERMISSION))) -> dict[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `BomService`, `BomService().update_line`, `Depends`, `require_permission`, `router.patch`

### delete_bom_line

[Исходник: api/wms_api_server/app/routers/bom.py:118](../../../api/wms_api_server/app/routers/bom.py#L118)

```python
delete_bom_line(bom_id: int, line_id: int, deleted_by: str | None=None, _user: AdminUser=Depends(require_permission(BOM_EDIT_PERMISSION))) -> dict[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `BomService`, `BomService().delete_line`, `Depends`, `require_permission`, `router.delete`

### approve_bom

[Исходник: api/wms_api_server/app/routers/bom.py:130](../../../api/wms_api_server/app/routers/bom.py#L130)

```python
approve_bom(bom_id: int, request: BomLifecycleRequest, _user: AdminUser=Depends(require_permission(BOM_APPROVE_PERMISSION))) -> dict[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `BomService`, `BomService().approve_bom`, `Depends`, `require_permission`, `router.post`

### block_bom

[Исходник: api/wms_api_server/app/routers/bom.py:140](../../../api/wms_api_server/app/routers/bom.py#L140)

```python
block_bom(bom_id: int, request: BomLifecycleRequest, _user: AdminUser=Depends(require_permission(BOM_BLOCK_PERMISSION))) -> dict[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `BomService`, `BomService().block_bom`, `Depends`, `require_permission`, `router.post`

### archive_bom

[Исходник: api/wms_api_server/app/routers/bom.py:150](../../../api/wms_api_server/app/routers/bom.py#L150)

```python
archive_bom(bom_id: int, request: BomLifecycleRequest, _user: AdminUser=Depends(require_permission(BOM_BLOCK_PERMISSION))) -> dict[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `BomService`, `BomService().archive_bom`, `Depends`, `require_permission`, `router.post`

### make_primary

[Исходник: api/wms_api_server/app/routers/bom.py:160](../../../api/wms_api_server/app/routers/bom.py#L160)

```python
make_primary(bom_id: int, request: BomLifecycleRequest, _user: AdminUser=Depends(require_permission(BOM_MAKE_PRIMARY_PERMISSION))) -> dict[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `BomService`, `BomService().make_primary`, `Depends`, `require_permission`, `router.post`

### clone_bom

[Исходник: api/wms_api_server/app/routers/bom.py:170](../../../api/wms_api_server/app/routers/bom.py#L170)

```python
clone_bom(bom_id: int, request: BomCloneRequest, _user: AdminUser=Depends(require_permission(BOM_EDIT_PERMISSION))) -> IdResponse
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `BomService`, `BomService().clone_bom`, `Depends`, `IdResponse`, `require_permission`, `router.post`

### calculate_bom

[Исходник: api/wms_api_server/app/routers/bom.py:179](../../../api/wms_api_server/app/routers/bom.py#L179)

```python
calculate_bom(bom_id: int, request: BomCalculateRequest, _user: AdminUser=Depends(require_permission(BOM_VIEW_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `BomService`, `BomService().calculate`, `Depends`, `require_permission`, `router.post`

### ensure_wave_case_pick_tasks

[Исходник: api/wms_api_server/app/routers/case_pick.py:27](../../../api/wms_api_server/app/routers/case_pick.py#L27)

```python
ensure_wave_case_pick_tasks(pick_wave_id: int, user: AdminUser=Depends(require_permission(CASE_PICK_MANAGE_PERMISSION))) -> dict[str, int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CasePickService`, `CasePickService().ensure_wave_case_pick_tasks`, `Depends`, `require_permission`, `router.post`

### list_case_pick_tasks

[Исходник: api/wms_api_server/app/routers/case_pick.py:36](../../../api/wms_api_server/app/routers/case_pick.py#L36)

```python
list_case_pick_tasks(resource_id: int | None=None, scope: str='mine', status: str | None=None, limit: int=100, user: AdminUser=Depends(require_permission(CASE_PICK_VIEW_PERMISSION)), service: CaseReadPort=Depends(case_read_service)) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.get`, `service.tasks`, `str`

### get_case_pick_task

[Исходник: api/wms_api_server/app/routers/case_pick.py:48](../../../api/wms_api_server/app/routers/case_pick.py#L48)

```python
get_case_pick_task(case_pick_task_id: int, user: AdminUser=Depends(require_permission(CASE_PICK_VIEW_PERMISSION)), service: CaseReadPort=Depends(case_read_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.get`, `service.task`, `str`

### claim_case_pick_task

[Исходник: api/wms_api_server/app/routers/case_pick.py:60](../../../api/wms_api_server/app/routers/case_pick.py#L60)

```python
claim_case_pick_task(case_pick_task_id: int, request: CasePickTaskActionRequest, user: AdminUser=Depends(require_permission(CASE_PICK_EXECUTE_PERMISSION))) -> dict[str, int | str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CasePickService`, `CasePickService().claim_task`, `Depends`, `require_permission`, `router.post`

### start_case_pick_task

[Исходник: api/wms_api_server/app/routers/case_pick.py:71](../../../api/wms_api_server/app/routers/case_pick.py#L71)

```python
start_case_pick_task(case_pick_task_id: int, request: CasePickTaskActionRequest, user: AdminUser=Depends(require_permission(CASE_PICK_EXECUTE_PERMISSION))) -> dict[str, int | str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CasePickService`, `CasePickService().start_task`, `Depends`, `require_permission`, `router.post`

### transfer_case_pick_task

[Исходник: api/wms_api_server/app/routers/case_pick.py:82](../../../api/wms_api_server/app/routers/case_pick.py#L82)

```python
transfer_case_pick_task(case_pick_task_id: int, request: CasePickTransferRequest, user: AdminUser=Depends(require_permission(CASE_PICK_MANAGE_PERMISSION))) -> dict[str, int | str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CasePickService`, `CasePickService().transfer_task`, `Depends`, `require_permission`, `router.post`

### move_case_carrier

[Исходник: api/wms_api_server/app/routers/case_pick.py:103](../../../api/wms_api_server/app/routers/case_pick.py#L103)

```python
move_case_carrier(case_pick_task_id: int, request: CaseCarrierMoveRequest, user: AdminUser=Depends(require_permission(CASE_PICK_EXECUTE_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `build_case_carrier_move_service`, `build_case_carrier_move_service().execute`, `require_permission`, `router.post`, `str`

### case_line_marking_policy

[Исходник: api/wms_api_server/app/routers/case_pick.py:120](../../../api/wms_api_server/app/routers/case_pick.py#L120)

```python
case_line_marking_policy(case_pick_task_id: int, line_id: int, user: AdminUser=Depends(require_permission(CASE_PICK_EXECUTE_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `build_case_task_services`, `build_case_task_services().marking_policy`, `require_permission`, `router.get`, `str`

### confirm_case_pick_line

[Исходник: api/wms_api_server/app/routers/case_pick.py:134](../../../api/wms_api_server/app/routers/case_pick.py#L134)

```python
confirm_case_pick_line(case_pick_task_id: int, line_id: int, request: CasePickLineConfirmRequest, user: AdminUser=Depends(require_permission(CASE_PICK_EXECUTE_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CasePickService`, `CasePickService().confirm_line`, `Depends`, `require_permission`, `router.post`

### create_case_pick_short

[Исходник: api/wms_api_server/app/routers/case_pick.py:146](../../../api/wms_api_server/app/routers/case_pick.py#L146)

```python
create_case_pick_short(case_pick_task_id: int, line_id: int, request: CasePickLineShortRequest, user: AdminUser=Depends(require_permission(CASE_PICK_EXECUTE_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CasePickService`, `CasePickService().short_line`, `Depends`, `HTTPException`, `detail.get`, `isinstance`, `require_permission`, `router.post`, `str`

### close_case_pick_task

[Исходник: api/wms_api_server/app/routers/case_pick.py:167](../../../api/wms_api_server/app/routers/case_pick.py#L167)

```python
close_case_pick_task(case_pick_task_id: int, request: CaseCarrierCloseRequest, user: AdminUser=Depends(require_permission(CASE_PICK_EXECUTE_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CasePickService`, `CasePickService().close_task`, `Depends`, `HTTPException`, `require_permission`, `router.post`, `str`

### list_case_pick_shorts

[Исходник: api/wms_api_server/app/routers/case_pick.py:181](../../../api/wms_api_server/app/routers/case_pick.py#L181)

```python
list_case_pick_shorts(status: str | None=None, limit: int=200, user: AdminUser=Depends(require_permission(CASE_PICK_VIEW_PERMISSION)), service: CaseReadPort=Depends(case_read_service)) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.get`, `service.shorts`, `str`

### approve_case_pick_short

[Исходник: api/wms_api_server/app/routers/case_pick.py:193](../../../api/wms_api_server/app/routers/case_pick.py#L193)

```python
approve_case_pick_short(short_id: int, request: CasePickShortDecisionRequest, user: AdminUser=Depends(require_permission(CASE_PICK_SHORT_APPROVE_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CasePickService`, `CasePickService().approve_short`, `Depends`, `require_permission`, `router.post`

### reject_case_pick_short

[Исходник: api/wms_api_server/app/routers/case_pick.py:203](../../../api/wms_api_server/app/routers/case_pick.py#L203)

```python
reject_case_pick_short(short_id: int, request: CasePickShortDecisionRequest, user: AdminUser=Depends(require_permission(CASE_PICK_SHORT_APPROVE_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CasePickService`, `CasePickService().reject_short`, `Depends`, `HTTPException`, `require_permission`, `router.post`, `str`

### list_pallet_types

[Исходник: api/wms_api_server/app/routers/case_pick.py:216](../../../api/wms_api_server/app/routers/case_pick.py#L216)

```python
list_pallet_types(active_only: int | None=None, _user: AdminUser=Depends(require_permission(CASE_PICK_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CasePickService`, `CasePickService().list_pallet_types`, `Depends`, `require_permission`, `router.get`

### upsert_pallet_type

[Исходник: api/wms_api_server/app/routers/case_pick.py:224](../../../api/wms_api_server/app/routers/case_pick.py#L224)

```python
upsert_pallet_type(request: PalletTypeUpsertRequest, user: AdminUser=Depends(require_permission(CASE_PICK_MANAGE_PERMISSION))) -> dict[str, int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CasePickService`, `CasePickService().upsert_pallet_type`, `Depends`, `require_permission`, `router.post`

### bind_case_shipment

[Исходник: api/wms_api_server/app/routers/case_pick.py:240](../../../api/wms_api_server/app/routers/case_pick.py#L240)

```python
bind_case_shipment(case_pick_task_id: int, request: CaseShipmentBindRequest, user: AdminUser=Depends(require_permission(CASE_PICK_EXECUTE_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `build_case_task_services`, `build_case_task_services().bind_shipment`, `require_permission`, `router.post`, `str`

### return_case_carrier

[Исходник: api/wms_api_server/app/routers/case_pick.py:255](../../../api/wms_api_server/app/routers/case_pick.py#L255)

```python
return_case_carrier(case_pick_task_id: int, request: CaseCarrierReturnRequest, user: AdminUser=Depends(require_permission(CASE_PICK_MANAGE_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `require_permission`, `return_existing_case_carrier`, `router.post`

### list_customers

[Исходник: api/wms_api_server/app/routers/customer_orders.py:20](../../../api/wms_api_server/app/routers/customer_orders.py#L20)

```python
list_customers(search: str | None=None, limit: int=200, _user: AdminUser=Depends(require_permission(CUSTOMER_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CustomerOrderService`, `CustomerOrderService().list_customers`, `Depends`, `require_permission`, `router.get`

### create_customer

[Исходник: api/wms_api_server/app/routers/customer_orders.py:29](../../../api/wms_api_server/app/routers/customer_orders.py#L29)

```python
create_customer(request: CustomerCreateRequest, user: AdminUser=Depends(require_permission(CUSTOMER_EDIT_PERMISSION))) -> dict[str, int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CustomerOrderService`, `CustomerOrderService().create_customer`, `Depends`, `require_permission`, `router.post`

### get_customer

[Исходник: api/wms_api_server/app/routers/customer_orders.py:39](../../../api/wms_api_server/app/routers/customer_orders.py#L39)

```python
get_customer(customer_id: int, _user: AdminUser=Depends(require_permission(CUSTOMER_VIEW_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CustomerOrderService`, `CustomerOrderService().get_customer`, `Depends`, `HTTPException`, `require_permission`, `router.get`

### update_customer

[Исходник: api/wms_api_server/app/routers/customer_orders.py:50](../../../api/wms_api_server/app/routers/customer_orders.py#L50)

```python
update_customer(customer_id: int, request: CustomerUpdateRequest, user: AdminUser=Depends(require_permission(CUSTOMER_EDIT_PERMISSION))) -> dict[str, int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CustomerOrderService`, `CustomerOrderService().update_customer`, `Depends`, `require_permission`, `router.patch`

### create_customer_address

[Исходник: api/wms_api_server/app/routers/customer_orders.py:61](../../../api/wms_api_server/app/routers/customer_orders.py#L61)

```python
create_customer_address(customer_id: int, request: CustomerAddressCreateRequest, user: AdminUser=Depends(require_permission(CUSTOMER_EDIT_PERMISSION))) -> dict[str, int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CustomerOrderService`, `CustomerOrderService().create_customer_address`, `Depends`, `require_permission`, `router.post`

### list_customer_orders

[Исходник: api/wms_api_server/app/routers/customer_orders.py:72](../../../api/wms_api_server/app/routers/customer_orders.py#L72)

```python
list_customer_orders(status: str | None=None, order_no: str | None=None, legacy_order_id: int | None=None, limit: int=200, before_id: int | None=None, _user: AdminUser=Depends(require_permission(CUSTOMER_ORDER_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `build_customer_order_read_service`, `build_customer_order_read_service().list`, `require_permission`, `router.get`, `str`

### get_customer_order

[Исходник: api/wms_api_server/app/routers/customer_orders.py:92](../../../api/wms_api_server/app/routers/customer_orders.py#L92)

```python
get_customer_order(customer_order_id: int, _user: AdminUser=Depends(require_permission(CUSTOMER_ORDER_VIEW_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `build_customer_order_read_service`, `build_customer_order_read_service().get`, `require_permission`, `router.get`, `str`

### import_legacy_order

[Исходник: api/wms_api_server/app/routers/customer_orders.py:107](../../../api/wms_api_server/app/routers/customer_orders.py#L107)

```python
import_legacy_order(legacy_order_id: int, user: AdminUser=Depends(require_permission(CUSTOMER_ORDER_IMPORT_PERMISSION))) -> dict[str, int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CustomerOrderService`, `CustomerOrderService().import_legacy_order`, `Depends`, `require_permission`, `router.post`

### get_customer_order_fulfillment

[Исходник: api/wms_api_server/app/routers/customer_orders.py:119](../../../api/wms_api_server/app/routers/customer_orders.py#L119)

```python
get_customer_order_fulfillment(customer_order_id: int, _user: AdminUser=Depends(require_permission(CUSTOMER_FULFILLMENT_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CustomerOrderService`, `CustomerOrderService().get_fulfillment`, `Depends`, `HTTPException`, `require_permission`, `router.get`, `str`

### list_product_rules

[Исходник: api/wms_api_server/app/routers/customer_rules.py:24](../../../api/wms_api_server/app/routers/customer_rules.py#L24)

```python
list_product_rules(customer_id: int, _user: AdminUser=Depends(require_permission(CUSTOMER_RULE_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CustomerRuleService`, `CustomerRuleService().list_product_rules`, `Depends`, `require_permission`, `router.get`

### create_product_rule

[Исходник: api/wms_api_server/app/routers/customer_rules.py:32](../../../api/wms_api_server/app/routers/customer_rules.py#L32)

```python
create_product_rule(customer_id: int, request: CustomerProductRuleCreateRequest, user: AdminUser=Depends(require_permission(CUSTOMER_RULE_EDIT_PERMISSION))) -> dict[str, int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CustomerRuleService`, `CustomerRuleService().create_product_rule`, `Depends`, `require_permission`, `router.post`

### list_shelf_life_rules

[Исходник: api/wms_api_server/app/routers/customer_rules.py:43](../../../api/wms_api_server/app/routers/customer_rules.py#L43)

```python
list_shelf_life_rules(customer_id: int, _user: AdminUser=Depends(require_permission(CUSTOMER_RULE_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CustomerRuleService`, `CustomerRuleService().list_shelf_life_rules`, `Depends`, `require_permission`, `router.get`

### create_shelf_life_rule

[Исходник: api/wms_api_server/app/routers/customer_rules.py:51](../../../api/wms_api_server/app/routers/customer_rules.py#L51)

```python
create_shelf_life_rule(customer_id: int, request: CustomerShelfLifeRuleCreateRequest, user: AdminUser=Depends(require_permission(CUSTOMER_RULE_EDIT_PERMISSION))) -> dict[str, int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CustomerRuleService`, `CustomerRuleService().create_shelf_life_rule`, `Depends`, `require_permission`, `router.post`

### list_stack_rules

[Исходник: api/wms_api_server/app/routers/customer_rules.py:62](../../../api/wms_api_server/app/routers/customer_rules.py#L62)

```python
list_stack_rules(customer_id: int, _user: AdminUser=Depends(require_permission(CUSTOMER_RULE_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CustomerRuleService`, `CustomerRuleService().list_stack_rules`, `Depends`, `require_permission`, `router.get`

### create_stack_rule

[Исходник: api/wms_api_server/app/routers/customer_rules.py:70](../../../api/wms_api_server/app/routers/customer_rules.py#L70)

```python
create_stack_rule(customer_id: int, request: CustomerStackRuleCreateRequest, user: AdminUser=Depends(require_permission(CUSTOMER_RULE_EDIT_PERMISSION))) -> dict[str, int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CustomerRuleService`, `CustomerRuleService().create_stack_rule`, `Depends`, `require_permission`, `router.post`

### list_vehicle_rules

[Исходник: api/wms_api_server/app/routers/customer_rules.py:81](../../../api/wms_api_server/app/routers/customer_rules.py#L81)

```python
list_vehicle_rules(customer_id: int, _user: AdminUser=Depends(require_permission(CUSTOMER_RULE_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CustomerRuleService`, `CustomerRuleService().list_vehicle_rules`, `Depends`, `require_permission`, `router.get`

### create_vehicle_rule

[Исходник: api/wms_api_server/app/routers/customer_rules.py:89](../../../api/wms_api_server/app/routers/customer_rules.py#L89)

```python
create_vehicle_rule(customer_id: int, request: CustomerVehicleRuleCreateRequest, user: AdminUser=Depends(require_permission(CUSTOMER_RULE_EDIT_PERMISSION))) -> dict[str, int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CustomerRuleService`, `CustomerRuleService().create_vehicle_rule`, `Depends`, `require_permission`, `router.post`

### list_vehicle_types

[Исходник: api/wms_api_server/app/routers/customer_rules.py:100](../../../api/wms_api_server/app/routers/customer_rules.py#L100)

```python
list_vehicle_types(active_only: int | None=None, _user: AdminUser=Depends(require_permission(VEHICLE_TYPE_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CustomerRuleService`, `CustomerRuleService().list_vehicle_types`, `Depends`, `require_permission`, `router.get`

### create_vehicle_type

[Исходник: api/wms_api_server/app/routers/customer_rules.py:108](../../../api/wms_api_server/app/routers/customer_rules.py#L108)

```python
create_vehicle_type(request: VehicleTypeCreateRequest, user: AdminUser=Depends(require_permission(VEHICLE_TYPE_EDIT_PERMISSION))) -> dict[str, int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CustomerRuleService`, `CustomerRuleService().create_vehicle_type`, `Depends`, `require_permission`, `router.post`

### _gw

[Исходник: api/wms_api_server/app/routers/export_1c.py:19](../../../api/wms_api_server/app/routers/export_1c.py#L19)

```python
_gw() -> OracleGateway
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`

### _build_1c_xml

[Исходник: api/wms_api_server/app/routers/export_1c.py:23](../../../api/wms_api_server/app/routers/export_1c.py#L23)

```python
_build_1c_xml(orders: list[dict]) -> bytes
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ET.Element`, `ET.SubElement`, `ET.tostring`, `date.today`, `o.get`, `str`, `t.get`

### export_order_1c

[Исходник: api/wms_api_server/app/routers/export_1c.py:47](../../../api/wms_api_server/app/routers/export_1c.py#L47)

```python
export_order_1c(order_id: int, _user: AdminUser=Depends(require_permission(BILLING_EDIT_PERMISSION))) -> Response
```

Экспорт счёта в XML формат 1С CommerceML (Sprint 113).

Вызывает: `Depends`, `HTTPException`, `Response`, `_build_1c_xml`, `_gw`, `gw.fetch_all`, `order_rows[0].items`, `require_permission`, `router.get`, `str`, `str(k).lower`, `t.items`

### export_orders_1c

[Исходник: api/wms_api_server/app/routers/export_1c.py:83](../../../api/wms_api_server/app/routers/export_1c.py#L83)

```python
export_orders_1c(date_from: date=Query(...), date_to: date=Query(...), status: str | None=Query(default=None), _user: AdminUser=Depends(require_permission(BILLING_EDIT_PERMISSION))) -> Response
```

Реестр счетов в XML формат 1С (Sprint 113).

Вызывает: `Depends`, `Query`, `Response`, `_build_1c_xml`, `_gw`, `gw.fetch_all`, `r.items`, `require_permission`, `router.get`, `str`, `str(k).lower`

### list_finished_goods_skus

[Исходник: api/wms_api_server/app/routers/finished_goods.py:18](../../../api/wms_api_server/app/routers/finished_goods.py#L18)

```python
list_finished_goods_skus(search: str | None=None, only_active: int | None=1, only_with_stock: int | None=None, limit: int=200, _user: AdminUser=Depends(require_permission(FINISHED_GOODS_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `FinishedGoodsService`, `FinishedGoodsService().list_skus`, `require_permission`, `router.get`

### update_finished_goods_sku

[Исходник: api/wms_api_server/app/routers/finished_goods.py:34](../../../api/wms_api_server/app/routers/finished_goods.py#L34)

```python
update_finished_goods_sku(articul: str, request: FinishedGoodsSkuSettingsUpdateRequest, _user: AdminUser=Depends(require_permission(FINISHED_GOODS_EDIT_PERMISSION))) -> dict[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `FinishedGoodsService`, `FinishedGoodsService().update_sku_settings`, `require_permission`, `router.patch`

### list_finished_goods_warehouses

[Исходник: api/wms_api_server/app/routers/finished_goods.py:44](../../../api/wms_api_server/app/routers/finished_goods.py#L44)

```python
list_finished_goods_warehouses(limit: int=200, _user: AdminUser=Depends(require_permission(FINISHED_GOODS_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `FinishedGoodsService`, `FinishedGoodsService().list_warehouses`, `require_permission`, `router.get`

### list_finished_goods_batches

[Исходник: api/wms_api_server/app/routers/finished_goods.py:52](../../../api/wms_api_server/app/routers/finished_goods.py#L52)

```python
list_finished_goods_batches(prod_batch_id: int | None=None, articul: str | None=None, batch_no: str | None=None, quality_status: str | None=None, limit: int=200, _user: AdminUser=Depends(require_permission(FINISHED_GOODS_BATCH_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `FinishedGoodsService`, `FinishedGoodsService().list_batches`, `require_permission`, `router.get`

### list_finished_goods_remains

[Исходник: api/wms_api_server/app/routers/finished_goods.py:70](../../../api/wms_api_server/app/routers/finished_goods.py#L70)

```python
list_finished_goods_remains(prod_batch_id: int | None=None, articul: str | None=None, ware_id: int | None=None, ware_ids: str | None=None, prod_batch_no: str | None=None, cell: str | None=None, quality_status: str | None=None, only_available: int | None=1, limit: int=500, _user: AdminUser=Depends(require_permission(FINISHED_GOODS_STOCK_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `FinishedGoodsService`, `FinishedGoodsService().list_remains`, `require_permission`, `router.get`

### _gw

[Исходник: api/wms_api_server/app/routers/gps.py:43](../../../api/wms_api_server/app/routers/gps.py#L43)

```python
_gw() -> OracleGateway
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`

### receive_gps_track

[Исходник: api/wms_api_server/app/routers/gps.py:52](../../../api/wms_api_server/app/routers/gps.py#L52)

```python
receive_gps_track(req: GpsTrackRequest) -> dict
```

Принять координату от GPS-трекера (Sprint 110).
Endpoint без admin-авторизации — защищён IP-whitelist через nginx на prod.

Вызывает: `HTTPException`, `_gw`, `check_geofences`, `ingest_gps`, `router.post`, `str`

### list_geofences

[Исходник: api/wms_api_server/app/routers/gps.py:80](../../../api/wms_api_server/app/routers/gps.py#L80)

```python
list_geofences(addr_mask: str | None=Query(default=None), _user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> list[dict]
```

Sprint 118: список геозон адресов (радиус в метрах).

Вызывает: `Depends`, `Query`, `_gw`, `list_address_geofences`, `require_permission`, `router.get`

### update_geofence_radius

[Исходник: api/wms_api_server/app/routers/gps.py:95](../../../api/wms_api_server/app/routers/gps.py#L95)

```python
update_geofence_radius(body: GeofenceRadiusUpdate, addr_id: str=Path(min_length=1, max_length=255), _user: AdminUser=Depends(require_permission('warehouse_settings_edit'))) -> dict
```

Update radius using the actual ADDR key, including embedded slashes.

Вызывает: `Depends`, `HTTPException`, `Path`, `_gw`, `require_permission`, `router.patch`, `update_address_geofence`

### get_vehicle_positions

[Исходник: api/wms_api_server/app/routers/gps.py:109](../../../api/wms_api_server/app/routers/gps.py#L109)

```python
get_vehicle_positions(_user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> list[dict]
```

Текущие позиции всех машин (Sprint 111 — live иконки на карте).

Вызывает: `Depends`, `_gw`, `_gw().fetch_all`, `float`, `int`, `r.get`, `require_permission`, `router.get`, `str`

### get_vehicle_track

[Исходник: api/wms_api_server/app/routers/gps.py:144](../../../api/wms_api_server/app/routers/gps.py#L144)

```python
get_vehicle_track(vehicle_id: int, track_date: date=Query(default=None), _user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> list[dict]
```

Трек машины за день — список координат по времени (Sprint 110).

Вызывает: `Depends`, `Query`, `_date.today`, `_gw`, `_gw().fetch_all`, `float`, `r.get`, `require_permission`, `router.get`, `str`

### validate_timestamp

[Исходник: api/wms_api_server/app/routers/gps.py:32](../../../api/wms_api_server/app/routers/gps.py#L32)

```python
validate_timestamp(cls, value)
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `datetime.strptime`, `field_validator`, `isinstance`, `re.fullmatch`

### health

[Исходник: api/wms_api_server/app/routers/health.py:10](../../../api/wms_api_server/app/routers/health.py#L10)

```python
health() -> dict[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `router.get`

### db_ping

[Исходник: api/wms_api_server/app/routers/health.py:15](../../../api/wms_api_server/app/routers/health.py#L15)

```python
db_ping() -> dict[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `OracleGateway().ping`, `router.get`

### _gw

[Исходник: api/wms_api_server/app/routers/maintenance.py:16](../../../api/wms_api_server/app/routers/maintenance.py#L16)

```python
_gw() -> OracleGateway
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`

### get_table_stats

[Исходник: api/wms_api_server/app/routers/maintenance.py:21](../../../api/wms_api_server/app/routers/maintenance.py#L21)

```python
get_table_stats(_user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> list[dict]
```

Размеры основных таблиц TMS-2 (Sprint 114).

Вызывает: `(cnt[0] if cnt else {}).get`, `Depends`, `_gw`, `gw.fetch_all`, `int`, `require_permission`, `result.append`, `router.get`, `str`

### archive_old_tasks

[Исходник: api/wms_api_server/app/routers/maintenance.py:47](../../../api/wms_api_server/app/routers/maintenance.py#L47)

```python
archive_old_tasks(older_than_months: int=Query(default=24, ge=1, le=120), dry_run: bool=Query(default=True, description='True=только подсчёт, False=реальное архивирование'), _user: AdminUser=Depends(require_permission(RIGHTS_ADMIN_EDIT_PERMISSION))) -> dict
```

Архивировать рейсы старше N месяцев (Sprint 114).

При dry_run=True только показывает количество без изменений.
При dry_run=False копирует в RRL_TRANSPORT_TASK_ARCH и удаляет из основной таблицы.

Вызывает: `(count_rows[0] if count_rows else {}).get`, `Depends`, `Query`, `_gw`, `gw.execute`, `gw.fetch_all`, `int`, `require_permission`, `router.post`

### list_production_orders

[Исходник: api/wms_api_server/app/routers/mes.py:34](../../../api/wms_api_server/app/routers/mes.py#L34)

```python
list_production_orders(status: str | None=None, target_articul: str | None=None, limit: int=100, _user: AdminUser=Depends(require_permission(MES_PRODUCTION_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `MesService`, `MesService().list_orders`, `require_permission`, `router.get`

### create_production_order

[Исходник: api/wms_api_server/app/routers/mes.py:44](../../../api/wms_api_server/app/routers/mes.py#L44)

```python
create_production_order(request: MesProductionOrderCreateRequest, _user: AdminUser=Depends(require_permission(MES_PRODUCTION_EDIT_PERMISSION))) -> IdResponse
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `IdResponse`, `MesService`, `MesService().create_order`, `require_permission`, `router.post`

### get_production_order

[Исходник: api/wms_api_server/app/routers/mes.py:52](../../../api/wms_api_server/app/routers/mes.py#L52)

```python
get_production_order(production_order_id: int, _user: AdminUser=Depends(require_permission(MES_PRODUCTION_VIEW_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `MesService`, `MesService().get_order`, `require_permission`, `router.get`

### issue_raw

[Исходник: api/wms_api_server/app/routers/mes.py:63](../../../api/wms_api_server/app/routers/mes.py#L63)

```python
issue_raw(production_order_id: int, request: MesRawIssueRequest, _user: AdminUser=Depends(require_permission(MES_PRODUCTION_EDIT_PERMISSION))) -> IdResponse
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `IdResponse`, `MesService`, `MesService().issue_raw`, `require_permission`, `router.post`

### complete_order

[Исходник: api/wms_api_server/app/routers/mes.py:72](../../../api/wms_api_server/app/routers/mes.py#L72)

```python
complete_order(production_order_id: int, request: MesCompleteOrderRequest, _user: AdminUser=Depends(require_permission(MES_PRODUCTION_COMPLETE_PERMISSION))) -> IdResponse
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `IdResponse`, `MesService`, `MesService().complete_order`, `require_permission`, `router.post`

### apply_wms

[Исходник: api/wms_api_server/app/routers/mes.py:81](../../../api/wms_api_server/app/routers/mes.py#L81)

```python
apply_wms(production_order_id: int, request: MesApplyWmsRequest, _user: AdminUser=Depends(require_permission(MES_WMS_BRIDGE_APPLY_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `MesService`, `MesService().apply_wms`, `require_permission`, `router.post`

### get_genealogy

[Исходник: api/wms_api_server/app/routers/mes.py:91](../../../api/wms_api_server/app/routers/mes.py#L91)

```python
get_genealogy(production_order_id: int, _user: AdminUser=Depends(require_permission(MES_PRODUCTION_VIEW_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `MesService`, `MesService().get_genealogy`, `require_permission`, `router.get`

### calculate_raw_supply

[Исходник: api/wms_api_server/app/routers/mes.py:99](../../../api/wms_api_server/app/routers/mes.py#L99)

```python
calculate_raw_supply(production_order_id: int, request: MesRawSupplyCalculateRequest, _user: AdminUser=Depends(require_permission(MES_RAW_SUPPLY_CALCULATE_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `MesService`, `MesService().calculate_raw_supply`, `require_permission`, `router.post`

### get_raw_supply

[Исходник: api/wms_api_server/app/routers/mes.py:109](../../../api/wms_api_server/app/routers/mes.py#L109)

```python
get_raw_supply(production_order_id: int, _user: AdminUser=Depends(require_permission(MES_RAW_SUPPLY_VIEW_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `MesService`, `MesService().get_raw_supply`, `require_permission`, `router.get`

### release_to_production

[Исходник: api/wms_api_server/app/routers/mes.py:117](../../../api/wms_api_server/app/routers/mes.py#L117)

```python
release_to_production(production_order_id: int, request: MesReleaseToProductionRequest, _user: AdminUser=Depends(require_permission(MES_RAW_TRANSFER_CREATE_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `MesService`, `MesService().release_to_production`, `require_permission`, `router.post`

### list_raw_transfer_tasks

[Исходник: api/wms_api_server/app/routers/mes.py:127](../../../api/wms_api_server/app/routers/mes.py#L127)

```python
list_raw_transfer_tasks(production_order_id: int | None=None, status: str | None=None, limit: int=100, _user: AdminUser=Depends(require_permission(MES_RAW_SUPPLY_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `MesService`, `MesService().list_raw_transfer_tasks`, `require_permission`, `router.get`

### get_raw_transfer_task

[Исходник: api/wms_api_server/app/routers/mes.py:141](../../../api/wms_api_server/app/routers/mes.py#L141)

```python
get_raw_transfer_task(task_id: int, _user: AdminUser=Depends(require_permission(MES_RAW_SUPPLY_VIEW_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `MesService`, `MesService().get_raw_transfer_task_or_404`, `require_permission`, `router.get`

### list_raw_shortages

[Исходник: api/wms_api_server/app/routers/mes.py:149](../../../api/wms_api_server/app/routers/mes.py#L149)

```python
list_raw_shortages(production_order_id: int | None=None, status: str | None=None, raw_articul: str | None=None, limit: int=100, _user: AdminUser=Depends(require_permission(MES_RAW_SUPPLY_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `MesService`, `MesService().list_raw_shortages`, `require_permission`, `router.get`

### confirm_raw_transfer_task

[Исходник: api/wms_api_server/app/routers/mes.py:165](../../../api/wms_api_server/app/routers/mes.py#L165)

```python
confirm_raw_transfer_task(task_id: int, request: MesRawTransferTaskConfirmRequest, _user: AdminUser=Depends(require_permission(MES_RAW_TRANSFER_CONFIRM_PERMISSION))) -> IdResponse
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `IdResponse`, `MesService`, `MesService().confirm_raw_transfer_task`, `require_permission`, `router.post`

### cancel_raw_transfer_task

[Исходник: api/wms_api_server/app/routers/mes.py:175](../../../api/wms_api_server/app/routers/mes.py#L175)

```python
cancel_raw_transfer_task(task_id: int, request: MesRawTransferTaskCancelRequest, _user: AdminUser=Depends(require_permission(MES_RAW_TRANSFER_CANCEL_PERMISSION))) -> dict[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `MesService`, `MesService().cancel_raw_transfer_task`, `require_permission`, `router.post`

### list_movements

[Исходник: api/wms_api_server/app/routers/mes.py:186](../../../api/wms_api_server/app/routers/mes.py#L186)

```python
list_movements(production_order_id: int | None=None, status: str | None=None, movement_type: str | None=None, limit: int=100, _user: AdminUser=Depends(require_permission(MES_PRODUCTION_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `MesService`, `MesService().list_movements`, `require_permission`, `router.get`

### retry_movement

[Исходник: api/wms_api_server/app/routers/mes.py:202](../../../api/wms_api_server/app/routers/mes.py#L202)

```python
retry_movement(movement_id: int, request: MesRetryMovementRequest, _user: AdminUser=Depends(require_permission(MES_WMS_BRIDGE_APPLY_PERMISSION))) -> dict[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `MesService`, `MesService().retry_movement`, `require_permission`, `router.post`

### _gw

[Исходник: api/wms_api_server/app/routers/notifications.py:43](../../../api/wms_api_server/app/routers/notifications.py#L43)

```python
_gw() -> OracleGateway
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`

### _send_push

[Исходник: api/wms_api_server/app/routers/notifications.py:47](../../../api/wms_api_server/app/routers/notifications.py#L47)

```python
_send_push(subscription: dict[str, Any], title: str, body: str) -> bool
```

Отправить push через pywebpush или логировать если не установлен.

Вызывает: `get_settings`, `getattr`, `json.dumps`, `log.debug`, `log.warning`, `subscription.get`, `webpush`

### _send_email

[Исходник: api/wms_api_server/app/routers/notifications.py:75](../../../api/wms_api_server/app/routers/notifications.py#L75)

```python
_send_email(to: str, subject: str, body: str) -> bool
```

Отправить email через SMTP.

Вызывает: `MIMEText`, `get_settings`, `getattr`, `int`, `log.debug`, `log.warning`, `s.login`, `s.send_message`, `smtplib.SMTP`

### subscribe_push

[Исходник: api/wms_api_server/app/routers/notifications.py:106](../../../api/wms_api_server/app/routers/notifications.py#L106)

```python
subscribe_push(req: PushSubscriptionRequest, user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> dict
```

Сохранить push-подписку (Sprint 106).

Вызывает: `Depends`, `_gw`, `gw.execute`, `gw.fetch_all`, `require_permission`, `router.post`

### unsubscribe_push

[Исходник: api/wms_api_server/app/routers/notifications.py:138](../../../api/wms_api_server/app/routers/notifications.py#L138)

```python
unsubscribe_push(req: PushSubscriptionRequest, user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> None
```

Удалить push-подписку (Sprint 106).

Вызывает: `Depends`, `_gw`, `_gw().execute`, `require_permission`, `router.delete`

### broadcast_push

[Исходник: api/wms_api_server/app/routers/notifications.py:150](../../../api/wms_api_server/app/routers/notifications.py#L150)

```python
broadcast_push(body: dict, user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> dict
```

Отправить push всем активным подписчикам (Sprint 106). Internal use.

Вызывает: `Depends`, `_gw`, `_send_push`, `body.get`, `gw.fetch_all`, `len`, `require_permission`, `router.post`, `str`

### get_notification_settings

[Исходник: api/wms_api_server/app/routers/notifications.py:173](../../../api/wms_api_server/app/routers/notifications.py#L173)

```python
get_notification_settings(user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> dict
```

Настройки уведомлений пользователя (Sprint 107).

Вызывает: `Depends`, `_gw`, `_gw().fetch_all`, `bool`, `json.loads`, `r.get`, `require_permission`, `router.get`

### save_notification_settings

[Исходник: api/wms_api_server/app/routers/notifications.py:197](../../../api/wms_api_server/app/routers/notifications.py#L197)

```python
save_notification_settings(req: NotificationSettingsRequest, user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> dict
```

Сохранить настройки уведомлений (Sprint 107).

Вызывает: `Depends`, `_gw`, `gw.execute`, `gw.fetch_all`, `json.dumps`, `require_permission`, `router.post`

### send_test_email

[Исходник: api/wms_api_server/app/routers/notifications.py:229](../../../api/wms_api_server/app/routers/notifications.py#L229)

```python
send_test_email(user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> dict
```

Отправить тестовое письмо (Sprint 107).

Вызывает: `Depends`, `HTTPException`, `_gw`, `_gw().fetch_all`, `_send_email`, `require_permission`, `router.post`, `rows[0].get`

### create_picking_plan

[Исходник: api/wms_api_server/app/routers/picking.py:42](../../../api/wms_api_server/app/routers/picking.py#L42)

```python
create_picking_plan(request: PickingPlanCreateRequest, user: AdminUser=Depends(require_permission(PICK_PLAN_CREATE_PERMISSION))) -> dict[str, int | str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `PickingService`, `PickingService().create_plan`, `require_permission`, `router.post`

### list_picking_plans

[Исходник: api/wms_api_server/app/routers/picking.py:52](../../../api/wms_api_server/app/routers/picking.py#L52)

```python
list_picking_plans(status: str | None=None, customer_order_id: int | None=None, customer_id: int | None=None, limit: int=100, _user: AdminUser=Depends(require_permission(PICK_PLAN_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `PickingService`, `PickingService().list_plans`, `require_permission`, `router.get`

### get_picking_plan

[Исходник: api/wms_api_server/app/routers/picking.py:68](../../../api/wms_api_server/app/routers/picking.py#L68)

```python
get_picking_plan(pick_plan_id: int, _user: AdminUser=Depends(require_permission(PICK_PLAN_VIEW_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `PickingService`, `PickingService().get_plan`, `require_permission`, `router.get`

### cancel_picking_plan

[Исходник: api/wms_api_server/app/routers/picking.py:79](../../../api/wms_api_server/app/routers/picking.py#L79)

```python
cancel_picking_plan(pick_plan_id: int, request: PickingPlanCancelRequest, user: AdminUser=Depends(require_permission(PICK_PLAN_CANCEL_PERMISSION))) -> dict[str, str | int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `PickingService`, `PickingService().cancel_plan`, `require_permission`, `router.post`

### list_picking_reservations

[Исходник: api/wms_api_server/app/routers/picking.py:89](../../../api/wms_api_server/app/routers/picking.py#L89)

```python
list_picking_reservations(pick_plan_id: int | None=None, status: str | None=None, customer_order_id: int | None=None, pallet_uid: str | None=None, articul: str | None=None, limit: int=200, _user: AdminUser=Depends(require_permission(PICK_RESERVATION_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `PickingService`, `PickingService().list_reservations`, `require_permission`, `router.get`

### list_picking_shortages

[Исходник: api/wms_api_server/app/routers/picking.py:109](../../../api/wms_api_server/app/routers/picking.py#L109)

```python
list_picking_shortages(pick_plan_id: int | None=None, limit: int=200, _user: AdminUser=Depends(require_permission(PICK_SHORTAGE_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `PickingService`, `PickingService().list_shortages`, `require_permission`, `router.get`

### list_picking_plan_shortages

[Исходник: api/wms_api_server/app/routers/picking.py:118](../../../api/wms_api_server/app/routers/picking.py#L118)

```python
list_picking_plan_shortages(pick_plan_id: int, limit: int=200, _user: AdminUser=Depends(require_permission(PICK_SHORTAGE_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `PickingService`, `PickingService().list_shortages`, `require_permission`, `router.get`

### list_pick_waves

[Исходник: api/wms_api_server/app/routers/picking.py:127](../../../api/wms_api_server/app/routers/picking.py#L127)

```python
list_pick_waves(status: str | None=None, ware_id: int | None=None, customer_id: int | None=None, limit: int=100, user: AdminUser=Depends(require_permission(PICK_WAVE_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `PickingService`, `PickingService(gateway).list_waves`, `build_wave_queue_reads`, `build_wave_queue_reads().waves`, `require_permission`, `router.get`

### create_pick_wave

[Исходник: api/wms_api_server/app/routers/picking.py:143](../../../api/wms_api_server/app/routers/picking.py#L143)

```python
create_pick_wave(request: PickWaveCreateRequest, user: AdminUser=Depends(require_permission(PICK_WAVE_CREATE_PERMISSION))) -> dict[str, int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `PickingService`, `PickingService().create_wave`, `require_permission`, `router.post`

### list_pick_wave_candidates

[Исходник: api/wms_api_server/app/routers/picking.py:156](../../../api/wms_api_server/app/routers/picking.py#L156)

```python
list_pick_wave_candidates(ware_id: int | None=None, route_id: int | None=None, dock_id: int | None=None, shipment_from: str | None=None, shipment_to: str | None=None, limit: int=100, _user: AdminUser=Depends(require_permission(PICK_WAVE_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `PickingService`, `PickingService().list_wave_candidates`, `require_permission`, `router.get`

### get_pick_wave_header

[Исходник: api/wms_api_server/app/routers/picking.py:176](../../../api/wms_api_server/app/routers/picking.py#L176)

```python
get_pick_wave_header(pick_wave_id: int, user: AdminUser=Depends(require_permission(PICK_WAVE_VIEW_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `PickingService`, `PickingService(gateway).get_wave_header`, `build_wave_queue_reads`, `build_wave_queue_reads().wave`, `require_permission`, `router.get`

### get_pick_wave

[Исходник: api/wms_api_server/app/routers/picking.py:185](../../../api/wms_api_server/app/routers/picking.py#L185)

```python
get_pick_wave(pick_wave_id: int, user: AdminUser=Depends(require_permission(PICK_WAVE_VIEW_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `PickingService`, `PickingService(gateway).get_wave`, `build_wave_queue_reads`, `build_wave_queue_reads().wave`, `require_permission`, `router.get`

### get_pick_wave_readiness

[Исходник: api/wms_api_server/app/routers/picking.py:195](../../../api/wms_api_server/app/routers/picking.py#L195)

```python
get_pick_wave_readiness(pick_wave_id: int, user: AdminUser=Depends(require_permission(PICK_WAVE_VIEW_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `PickingService`, `PickingService(gateway).get_wave_readiness`, `build_wave_queue_reads`, `build_wave_queue_reads().wave`, `require_permission`, `router.get`

### add_pick_wave_plan

[Исходник: api/wms_api_server/app/routers/picking.py:205](../../../api/wms_api_server/app/routers/picking.py#L205)

```python
add_pick_wave_plan(pick_wave_id: int, request: PickWaveAddPlanRequest, user: AdminUser=Depends(require_permission(PICK_WAVE_CREATE_PERMISSION))) -> dict[str, str | int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `PickingService`, `PickingService().add_wave_plan`, `require_permission`, `router.post`

### calculate_pick_wave

[Исходник: api/wms_api_server/app/routers/picking.py:219](../../../api/wms_api_server/app/routers/picking.py#L219)

```python
calculate_pick_wave(pick_wave_id: int, request: PickWaveActionRequest, user: AdminUser=Depends(require_permission(PICK_WAVE_CALCULATE_PERMISSION))) -> dict[str, str | int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `PickingService`, `PickingService().preview_wave`, `require_permission`, `router.post`

### launch_pick_wave

[Исходник: api/wms_api_server/app/routers/picking.py:230](../../../api/wms_api_server/app/routers/picking.py#L230)

```python
launch_pick_wave(pick_wave_id: int, request: PickWaveActionRequest, user: AdminUser=Depends(require_permission(PICK_WAVE_LAUNCH_PERMISSION))) -> dict[str, str | int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `PickingService`, `PickingService().launch_wave`, `require_permission`, `router.post`

### cancel_pick_wave

[Исходник: api/wms_api_server/app/routers/picking.py:241](../../../api/wms_api_server/app/routers/picking.py#L241)

```python
cancel_pick_wave(pick_wave_id: int, request: PickWaveActionRequest, user: AdminUser=Depends(require_permission(PICK_WAVE_CANCEL_PERMISSION))) -> dict[str, str | int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `PickingService`, `PickingService().cancel_wave`, `require_permission`, `router.post`

### release_pick_wave_reservations

[Исходник: api/wms_api_server/app/routers/picking.py:252](../../../api/wms_api_server/app/routers/picking.py#L252)

```python
release_pick_wave_reservations(pick_wave_id: int, request: PickWaveActionRequest, user: AdminUser=Depends(require_permission(PICK_WAVE_RELEASE_RESERVES_PERMISSION))) -> dict[str, str | int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `PickingService`, `PickingService().release_wave_reservations`, `require_permission`, `router.post`

### release_pick_wave_minimax_replenishment

[Исходник: api/wms_api_server/app/routers/picking.py:263](../../../api/wms_api_server/app/routers/picking.py#L263)

```python
release_pick_wave_minimax_replenishment(pick_wave_id: int, request: PickWaveActionRequest, user: AdminUser=Depends(require_permission(PICK_WAVE_LAUNCH_PERMISSION))) -> dict[str, str | int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `PickingService`, `PickingService().release_minimax_replenishment`, `require_permission`, `router.post`

### release_pick_wave_staging

[Исходник: api/wms_api_server/app/routers/picking.py:274](../../../api/wms_api_server/app/routers/picking.py#L274)

```python
release_pick_wave_staging(pick_wave_id: int, request: PickWaveStagingReleaseRequest, user: AdminUser=Depends(require_permission(PICK_WAVE_LAUNCH_PERMISSION))) -> dict[str, str | int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `PickingService`, `PickingService().release_wave_staging`, `require_permission`, `router.post`

### list_pick_wave_reservations

[Исходник: api/wms_api_server/app/routers/picking.py:288](../../../api/wms_api_server/app/routers/picking.py#L288)

```python
list_pick_wave_reservations(pick_wave_id: int, limit: int=200, user: AdminUser=Depends(require_permission(PICK_WAVE_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `PickingService`, `PickingService(gateway).list_wave_reservations`, `build_wave_queue_reads`, `build_wave_queue_reads().wave`, `require_permission`, `router.get`

### list_pick_wave_replenishment_tasks

[Исходник: api/wms_api_server/app/routers/picking.py:296](../../../api/wms_api_server/app/routers/picking.py#L296)

```python
list_pick_wave_replenishment_tasks(pick_wave_id: int, limit: int=200, user: AdminUser=Depends(require_permission(PICK_WAVE_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `PickingService`, `PickingService(gateway).list_wave_replenishment_tasks`, `build_wave_queue_reads`, `build_wave_queue_reads().wave`, `require_permission`, `router.get`

### list_pick_wave_tasks

[Исходник: api/wms_api_server/app/routers/picking.py:304](../../../api/wms_api_server/app/routers/picking.py#L304)

```python
list_pick_wave_tasks(pick_wave_id: int, limit: int=200, user: AdminUser=Depends(require_permission(PICK_WAVE_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `PickingService`, `PickingService(gateway).list_wave_tasks`, `build_wave_queue_reads`, `build_wave_queue_reads().wave`, `require_permission`, `router.get`

### complete_pick_wave_task

[Исходник: api/wms_api_server/app/routers/picking.py:312](../../../api/wms_api_server/app/routers/picking.py#L312)

```python
complete_pick_wave_task(pick_wave_id: int, pick_task_id: int, request: PickTaskCompleteRequest, user: AdminUser=Depends(require_permission(PICK_WAVE_LAUNCH_PERMISSION))) -> dict[str, str | int | float]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `PickingService`, `PickingService().complete_wave_pick_task`, `require_permission`, `router.post`

### list_pick_wave_audit

[Исходник: api/wms_api_server/app/routers/picking.py:323](../../../api/wms_api_server/app/routers/picking.py#L323)

```python
list_pick_wave_audit(pick_wave_id: int, limit: int=200, _user: AdminUser=Depends(require_permission(PICK_WAVE_AUDIT_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `PickingService`, `PickingService().list_wave_audit`, `require_permission`, `router.get`

### list_pick_routes

[Исходник: api/wms_api_server/app/routers/picking.py:332](../../../api/wms_api_server/app/routers/picking.py#L332)

```python
list_pick_routes(ware_id: int | None=None, active_only: int | None=None, _user: AdminUser=Depends(require_permission(PICK_TOPOLOGY_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `PickingService`, `PickingService().list_routes`, `require_permission`, `router.get`

### upsert_pick_route

[Исходник: api/wms_api_server/app/routers/picking.py:341](../../../api/wms_api_server/app/routers/picking.py#L341)

```python
upsert_pick_route(request: PickRouteUpsertRequest, user: AdminUser=Depends(require_permission(PICK_TOPOLOGY_EDIT_PERMISSION))) -> dict[str, int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `PickingService`, `PickingService().upsert_route`, `require_permission`, `router.post`

### list_pick_route_cells

[Исходник: api/wms_api_server/app/routers/picking.py:351](../../../api/wms_api_server/app/routers/picking.py#L351)

```python
list_pick_route_cells(pick_route_id: int | None=None, ware_id: int | None=None, active_only: int | None=None, _user: AdminUser=Depends(require_permission(PICK_TOPOLOGY_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `PickingService`, `PickingService().list_route_cells`, `require_permission`, `router.get`

### upsert_pick_route_cell

[Исходник: api/wms_api_server/app/routers/picking.py:365](../../../api/wms_api_server/app/routers/picking.py#L365)

```python
upsert_pick_route_cell(request: PickRouteCellUpsertRequest, user: AdminUser=Depends(require_permission(PICK_TOPOLOGY_EDIT_PERMISSION))) -> dict[str, int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `PickingService`, `PickingService().upsert_route_cell`, `require_permission`, `router.post`

### list_pick_faces

[Исходник: api/wms_api_server/app/routers/picking.py:375](../../../api/wms_api_server/app/routers/picking.py#L375)

```python
list_pick_faces(ware_id: int | None=None, articul: str | None=None, active_only: int | None=None, _user: AdminUser=Depends(require_permission(PICK_TOPOLOGY_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `PickingService`, `PickingService().list_pick_faces`, `require_permission`, `router.get`

### upsert_pick_face

[Исходник: api/wms_api_server/app/routers/picking.py:389](../../../api/wms_api_server/app/routers/picking.py#L389)

```python
upsert_pick_face(request: PickFaceUpsertRequest, user: AdminUser=Depends(require_permission(PICK_TOPOLOGY_EDIT_PERMISSION))) -> dict[str, int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `PickingService`, `PickingService().upsert_pick_face`, `require_permission`, `router.post`

### list_pick_face_articuls

[Исходник: api/wms_api_server/app/routers/picking.py:399](../../../api/wms_api_server/app/routers/picking.py#L399)

```python
list_pick_face_articuls(pick_face_id: int, _user: AdminUser=Depends(require_permission(PICK_TOPOLOGY_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `PickingService`, `PickingService().list_pick_face_articuls`, `require_permission`, `router.get`

### assign_pick_face_articul

[Исходник: api/wms_api_server/app/routers/picking.py:407](../../../api/wms_api_server/app/routers/picking.py#L407)

```python
assign_pick_face_articul(pick_face_id: int, request: PickFaceArticulUpsertRequest, user: AdminUser=Depends(require_permission(PICK_TOPOLOGY_EDIT_PERMISSION))) -> dict[str, int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `PickingService`, `PickingService().assign_pick_face_articul`, `require_permission`, `router.post`

### list_articul_replenishment_rules

[Исходник: api/wms_api_server/app/routers/picking.py:419](../../../api/wms_api_server/app/routers/picking.py#L419)

```python
list_articul_replenishment_rules(articul: str | None=None, active_only: int | None=None, _user: AdminUser=Depends(require_permission(PICK_TOPOLOGY_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `PickingService`, `PickingService().list_articul_replenishment_rules`, `require_permission`, `router.get`

### upsert_articul_replenishment_rule

[Исходник: api/wms_api_server/app/routers/picking.py:431](../../../api/wms_api_server/app/routers/picking.py#L431)

```python
upsert_articul_replenishment_rule(request: ArticulReplenishmentRuleUpsertRequest, user: AdminUser=Depends(require_permission(PICK_TOPOLOGY_EDIT_PERMISSION))) -> dict[str, int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `PickingService`, `PickingService().upsert_articul_replenishment_rule`, `require_permission`, `router.post`

### create_production_batch

[Исходник: api/wms_api_server/app/routers/production.py:24](../../../api/wms_api_server/app/routers/production.py#L24)

```python
create_production_batch(request: ProductionBatchCreate) -> IdResponse
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `IdResponse`, `ProductionService`, `ProductionService().create_batch`, `router.post`

### get_production_batch_status

[Исходник: api/wms_api_server/app/routers/production.py:30](../../../api/wms_api_server/app/routers/production.py#L30)

```python
get_production_batch_status(prod_batch_id: int) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `ProductionService`, `ProductionService().get_batch_status`, `router.get`

### attach_pallet

[Исходник: api/wms_api_server/app/routers/production.py:38](../../../api/wms_api_server/app/routers/production.py#L38)

```python
attach_pallet(prod_batch_id: int, request: PalletAttachRequest) -> dict[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ProductionService`, `ProductionService().attach_pallet`, `router.post`

### create_raw_batch

[Исходник: api/wms_api_server/app/routers/production.py:44](../../../api/wms_api_server/app/routers/production.py#L44)

```python
create_raw_batch(request: RawBatchCreate) -> IdResponse
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `IdResponse`, `ProductionService`, `ProductionService().create_raw_batch`, `router.post`

### get_raw_batch

[Исходник: api/wms_api_server/app/routers/production.py:50](../../../api/wms_api_server/app/routers/production.py#L50)

```python
get_raw_batch(raw_batch_id: int) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `ProductionService`, `ProductionService().get_raw_batch`, `router.get`

### add_raw_usage

[Исходник: api/wms_api_server/app/routers/production.py:58](../../../api/wms_api_server/app/routers/production.py#L58)

```python
add_raw_usage(prod_batch_id: int, request: RawUsageRequest) -> IdResponse
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `IdResponse`, `ProductionService`, `ProductionService().add_raw_usage`, `router.post`

### add_crpt_code

[Исходник: api/wms_api_server/app/routers/production.py:64](../../../api/wms_api_server/app/routers/production.py#L64)

```python
add_crpt_code(prod_batch_id: int, request: CrptCodeRequest) -> IdResponse
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `IdResponse`, `ProductionService`, `ProductionService().add_crpt_code`, `router.post`

### create_aggregation

[Исходник: api/wms_api_server/app/routers/production.py:70](../../../api/wms_api_server/app/routers/production.py#L70)

```python
create_aggregation(prod_batch_id: int, request: AggregationCreateRequest) -> IdResponse
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `IdResponse`, `ProductionService`, `ProductionService().create_aggregation`, `router.post`

### add_aggregation_item

[Исходник: api/wms_api_server/app/routers/production.py:76](../../../api/wms_api_server/app/routers/production.py#L76)

```python
add_aggregation_item(aggregation_id: int, request: AggregationItemRequest) -> dict[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ProductionService`, `ProductionService().add_aggregation_item`, `router.post`

### set_mercury_batch

[Исходник: api/wms_api_server/app/routers/production.py:82](../../../api/wms_api_server/app/routers/production.py#L82)

```python
set_mercury_batch(prod_batch_id: int, request: MercuryBatchRequest) -> dict[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ProductionService`, `ProductionService().set_mercury_batch`, `router.post`

### get_regulatory_status

[Исходник: api/wms_api_server/app/routers/production.py:88](../../../api/wms_api_server/app/routers/production.py#L88)

```python
get_regulatory_status(prod_batch_id: int) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `ProductionService`, `ProductionService().get_regulatory_status`, `router.get`

### upsert_mercury_site

[Исходник: api/wms_api_server/app/routers/production.py:96](../../../api/wms_api_server/app/routers/production.py#L96)

```python
upsert_mercury_site(request: MercurySiteRequest) -> IdResponse
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `IdResponse`, `ProductionService`, `ProductionService().upsert_mercury_site`, `router.post`

### list_mercury_sites

[Исходник: api/wms_api_server/app/routers/production.py:102](../../../api/wms_api_server/app/routers/production.py#L102)

```python
list_mercury_sites(active: int | None=None) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ProductionService`, `ProductionService().list_mercury_sites`, `router.get`

### create_batch_mercury_operation

[Исходник: api/wms_api_server/app/routers/production.py:107](../../../api/wms_api_server/app/routers/production.py#L107)

```python
create_batch_mercury_operation(prod_batch_id: int, request: MercuryOperationCreateRequest) -> IdResponse
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `IdResponse`, `ProductionService`, `ProductionService().create_mercury_operation`, `router.post`

### create_mercury_operation

[Исходник: api/wms_api_server/app/routers/production.py:115](../../../api/wms_api_server/app/routers/production.py#L115)

```python
create_mercury_operation(request: MercuryOperationCreateRequest) -> IdResponse
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `IdResponse`, `ProductionService`, `ProductionService().create_mercury_operation`, `router.post`

### update_mercury_operation

[Исходник: api/wms_api_server/app/routers/production.py:121](../../../api/wms_api_server/app/routers/production.py#L121)

```python
update_mercury_operation(operation_row_id: int, request: MercuryOperationUpdateRequest) -> dict[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ProductionService`, `ProductionService().update_mercury_operation`, `router.patch`

### set_crpt_code_status

[Исходник: api/wms_api_server/app/routers/production.py:129](../../../api/wms_api_server/app/routers/production.py#L129)

```python
set_crpt_code_status(request: CrptCodeStatusRequest) -> IdResponse
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `IdResponse`, `ProductionService`, `ProductionService().set_crpt_code_status`, `router.post`

### list_regulatory_journal

[Исходник: api/wms_api_server/app/routers/production.py:135](../../../api/wms_api_server/app/routers/production.py#L135)

```python
list_regulatory_journal(prod_batch_id: int | None=None, system_code: str | None=None, limit: int=100) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ProductionService`, `ProductionService().list_journal`, `router.get`

### list_regulatory_outbox

[Исходник: api/wms_api_server/app/routers/production.py:148](../../../api/wms_api_server/app/routers/production.py#L148)

```python
list_regulatory_outbox(status: str | None=None, system_code: str | None=None, limit: int=100) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ProductionService`, `ProductionService().list_outbox`, `router.get`

### list_product_shipment_settings

[Исходник: api/wms_api_server/app/routers/products.py:16](../../../api/wms_api_server/app/routers/products.py#L16)

```python
list_product_shipment_settings(articul_like: str | None=None, only_with_aging: int | None=None, limit: int=200, _user: AdminUser=Depends(require_permission(QUALITY_BATCH_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `ProductService`, `ProductService().list_shipment_settings`, `require_permission`, `router.get`

### update_product_shipment_settings

[Исходник: api/wms_api_server/app/routers/products.py:30](../../../api/wms_api_server/app/routers/products.py#L30)

```python
update_product_shipment_settings(articul: str, request: ProductShipmentSettingsUpdateRequest, _user: AdminUser=Depends(require_permission(QUALITY_BATCH_EDIT_PERMISSION))) -> dict[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `ProductService`, `ProductService().update_shipment_settings`, `require_permission`, `router.patch`

### list_raw_material_skus

[Исходник: api/wms_api_server/app/routers/raw_material.py:17](../../../api/wms_api_server/app/routers/raw_material.py#L17)

```python
list_raw_material_skus(search: str | None=None, only_active: int | None=1, only_with_stock: int | None=None, limit: int=200, _user: AdminUser=Depends(require_permission(RAW_MATERIAL_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `RawMaterialService`, `RawMaterialService().list_skus`, `require_permission`, `router.get`

### update_raw_material_sku

[Исходник: api/wms_api_server/app/routers/raw_material.py:33](../../../api/wms_api_server/app/routers/raw_material.py#L33)

```python
update_raw_material_sku(articul: str, request: RawMaterialSkuSettingsUpdateRequest, _user: AdminUser=Depends(require_permission(RAW_MATERIAL_EDIT_PERMISSION))) -> dict[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `RawMaterialService`, `RawMaterialService().update_sku_settings`, `require_permission`, `router.patch`

### list_raw_material_warehouses

[Исходник: api/wms_api_server/app/routers/raw_material.py:43](../../../api/wms_api_server/app/routers/raw_material.py#L43)

```python
list_raw_material_warehouses(limit: int=200, _user: AdminUser=Depends(require_permission(RAW_MATERIAL_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `RawMaterialService`, `RawMaterialService().list_warehouses`, `require_permission`, `router.get`

### list_raw_material_remains

[Исходник: api/wms_api_server/app/routers/raw_material.py:51](../../../api/wms_api_server/app/routers/raw_material.py#L51)

```python
list_raw_material_remains(articul: str | None=None, ware_id: int | None=None, ware_ids: str | None=None, cell: str | None=None, batch_no: str | None=None, quality_status: str | None=None, only_available: int | None=1, limit: int=500, _user: AdminUser=Depends(require_permission(RAW_MATERIAL_STOCK_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `RawMaterialService`, `RawMaterialService().list_remains`, `require_permission`, `router.get`

### list_resource_types

[Исходник: api/wms_api_server/app/routers/resource_management.py:28](../../../api/wms_api_server/app/routers/resource_management.py#L28)

```python
list_resource_types(active: int | None=1, _user: AdminUser=Depends(require_permission(RESOURCE_MANAGEMENT_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `ResourceManagementService`, `ResourceManagementService().list_resource_types`, `require_permission`, `router.get`

### list_equipment

[Исходник: api/wms_api_server/app/routers/resource_management.py:36](../../../api/wms_api_server/app/routers/resource_management.py#L36)

```python
list_equipment(equipment_type: str | None=None, service_status: str | None=None, active: int | None=1, limit: int=200, _user: AdminUser=Depends(require_permission(RESOURCE_MANAGEMENT_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `ResourceManagementService`, `ResourceManagementService().list_equipment`, `require_permission`, `router.get`

### create_equipment

[Исходник: api/wms_api_server/app/routers/resource_management.py:52](../../../api/wms_api_server/app/routers/resource_management.py#L52)

```python
create_equipment(request: ResourceEquipmentCreateRequest, _user: AdminUser=Depends(require_permission(RESOURCE_MANAGEMENT_EDIT_PERMISSION))) -> IdResponse
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `IdResponse`, `ResourceManagementService`, `ResourceManagementService().create_equipment`, `require_permission`, `router.post`

### list_resources

[Исходник: api/wms_api_server/app/routers/resource_management.py:60](../../../api/wms_api_server/app/routers/resource_management.py#L60)

```python
list_resources(resource_type: str | None=None, resource_class: str | None=None, status: str | None=None, ware_id: int | None=None, zone_code: str | None=None, active: int | None=1, limit: int=200, _user: AdminUser=Depends(require_permission(RESOURCE_MANAGEMENT_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `ResourceManagementService`, `ResourceManagementService().list_resources`, `require_permission`, `router.get`

### create_resource

[Исходник: api/wms_api_server/app/routers/resource_management.py:82](../../../api/wms_api_server/app/routers/resource_management.py#L82)

```python
create_resource(request: ResourceCreateRequest, _user: AdminUser=Depends(require_permission(RESOURCE_MANAGEMENT_EDIT_PERMISSION))) -> IdResponse
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `IdResponse`, `ResourceManagementService`, `ResourceManagementService().create_resource`, `require_permission`, `router.post`

### list_shifts

[Исходник: api/wms_api_server/app/routers/resource_management.py:90](../../../api/wms_api_server/app/routers/resource_management.py#L90)

```python
list_shifts(shift_date: str | None=None, ware_id: int | None=None, status: str | None=None, limit: int=100, _user: AdminUser=Depends(require_permission(RESOURCE_SHIFT_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `ResourceManagementService`, `ResourceManagementService().list_shifts`, `require_permission`, `router.get`

### create_shift

[Исходник: api/wms_api_server/app/routers/resource_management.py:106](../../../api/wms_api_server/app/routers/resource_management.py#L106)

```python
create_shift(request: ResourceShiftCreateRequest, _user: AdminUser=Depends(require_permission(RESOURCE_SHIFT_EDIT_PERMISSION))) -> IdResponse
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `IdResponse`, `ResourceManagementService`, `ResourceManagementService().create_shift`, `require_permission`, `router.post`

### list_sessions

[Исходник: api/wms_api_server/app/routers/resource_management.py:114](../../../api/wms_api_server/app/routers/resource_management.py#L114)

```python
list_sessions(session_id: int | None=None, shift_id: int | None=None, resource_id: int | None=None, status: str | None=None, limit: int=100, _user: AdminUser=Depends(require_permission(RESOURCE_SESSION_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `ResourceManagementService`, `ResourceManagementService().list_sessions`, `require_permission`, `router.get`

### login_session

[Исходник: api/wms_api_server/app/routers/resource_management.py:132](../../../api/wms_api_server/app/routers/resource_management.py#L132)

```python
login_session(request: ResourceSessionLoginRequest, _user: AdminUser=Depends(require_permission(RESOURCE_SESSION_MANAGE_PERMISSION))) -> IdResponse
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `IdResponse`, `ResourceManagementService`, `ResourceManagementService().login_session`, `require_permission`, `router.post`

### login_tsd_session

[Исходник: api/wms_api_server/app/routers/resource_management.py:141](../../../api/wms_api_server/app/routers/resource_management.py#L141)

```python
login_tsd_session(request: ResourceTsdLoginRequest, _user: AdminUser=Depends(require_permission(RESOURCE_SESSION_MANAGE_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `ResourceManagementService`, `ResourceManagementService().login_tsd`, `require_permission`, `router.post`

### heartbeat_session

[Исходник: api/wms_api_server/app/routers/resource_management.py:149](../../../api/wms_api_server/app/routers/resource_management.py#L149)

```python
heartbeat_session(session_id: int, _user: AdminUser=Depends(require_permission(RESOURCE_SESSION_MANAGE_PERMISSION))) -> dict[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `ResourceManagementService`, `ResourceManagementService().heartbeat`, `require_permission`, `router.post`

### pause_session

[Исходник: api/wms_api_server/app/routers/resource_management.py:158](../../../api/wms_api_server/app/routers/resource_management.py#L158)

```python
pause_session(session_id: int, request: ResourceSessionStatusRequest, _user: AdminUser=Depends(require_permission(RESOURCE_SESSION_MANAGE_PERMISSION))) -> dict[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `ResourceManagementService`, `ResourceManagementService().pause_session`, `require_permission`, `router.post`

### resume_session

[Исходник: api/wms_api_server/app/routers/resource_management.py:168](../../../api/wms_api_server/app/routers/resource_management.py#L168)

```python
resume_session(session_id: int, request: ResourceSessionStatusRequest, _user: AdminUser=Depends(require_permission(RESOURCE_SESSION_MANAGE_PERMISSION))) -> dict[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `ResourceManagementService`, `ResourceManagementService().resume_session`, `require_permission`, `router.post`

### logout_session

[Исходник: api/wms_api_server/app/routers/resource_management.py:178](../../../api/wms_api_server/app/routers/resource_management.py#L178)

```python
logout_session(session_id: int, request: ResourceSessionStatusRequest, _user: AdminUser=Depends(require_permission(RESOURCE_SESSION_MANAGE_PERMISSION))) -> dict[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `ResourceManagementService`, `ResourceManagementService().logout_session`, `require_permission`, `router.post`

### list_slow_sql

[Исходник: api/wms_api_server/app/routers/slow_sql.py:10](../../../api/wms_api_server/app/routers/slow_sql.py#L10)

```python
list_slow_sql(from_log_id: int | None=None, to_log_id: int | None=None, api_call_id: int | None=None, path_like: str | None=None, sql_hash: str | None=None, min_elapsed_ms: int | None=None, error_only: int | None=None, limit: int=100, offset: int=0, _user: AdminUser=Depends(require_permission(SLOW_SQL_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `SlowSqlService`, `SlowSqlService().list_entries`, `require_permission`, `router.get`

### top_slow_sql

[Исходник: api/wms_api_server/app/routers/slow_sql.py:36](../../../api/wms_api_server/app/routers/slow_sql.py#L36)

```python
top_slow_sql(limit: int=50, _user: AdminUser=Depends(require_permission(SLOW_SQL_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `SlowSqlService`, `SlowSqlService().top_entries`, `require_permission`, `router.get`

### oracle_top_sql

[Исходник: api/wms_api_server/app/routers/slow_sql.py:44](../../../api/wms_api_server/app/routers/slow_sql.py#L44)

```python
oracle_top_sql(limit: int=50, _user: AdminUser=Depends(require_permission(SLOW_SQL_VIEW_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `SlowSqlService`, `SlowSqlService().oracle_top_sql`, `require_permission`, `router.get`

### get_slow_sql

[Исходник: api/wms_api_server/app/routers/slow_sql.py:52](../../../api/wms_api_server/app/routers/slow_sql.py#L52)

```python
get_slow_sql(log_id: int, _user: AdminUser=Depends(require_permission(SLOW_SQL_VIEW_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `SlowSqlService`, `SlowSqlService().get_entry`, `require_permission`, `router.get`

### list_stock_reservations

[Исходник: api/wms_api_server/app/routers/stock_reservations.py:21](../../../api/wms_api_server/app/routers/stock_reservations.py#L21)

```python
list_stock_reservations(reservation_kind: str | None=None, reservation_domain: str | None=None, status: str | None=None, source_doc_type: str | None=None, source_doc_id: int | None=None, articul: str | None=None, ware_id: int | None=None, cell: str | None=None, uid_pallet: str | None=None, batch_id: str | None=None, production_order_id: int | None=None, pick_plan_id: int | None=None, pick_wave_id: int | None=None, only_active: int | None=None, limit: int=200, _user: AdminUser=Depends(require_permission(STOCK_RESERVATION_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `StockReservationService`, `StockReservationService().list_reservations`, `require_permission`, `router.get`

### get_stock_reservation

[Исходник: api/wms_api_server/app/routers/stock_reservations.py:59](../../../api/wms_api_server/app/routers/stock_reservations.py#L59)

```python
get_stock_reservation(reservation_id: int, _user: AdminUser=Depends(require_permission(STOCK_RESERVATION_VIEW_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `StockReservationService`, `StockReservationService().get_reservation`, `require_permission`, `router.get`

### create_stock_reservation

[Исходник: api/wms_api_server/app/routers/stock_reservations.py:70](../../../api/wms_api_server/app/routers/stock_reservations.py#L70)

```python
create_stock_reservation(request: StockReservationCreateRequest, _user: AdminUser=Depends(require_permission(STOCK_RESERVATION_EDIT_PERMISSION))) -> IdResponse
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `IdResponse`, `StockReservationService`, `StockReservationService().create_reservation`, `require_permission`, `router.post`, `str`

### promote_stock_reservation_to_hard

[Исходник: api/wms_api_server/app/routers/stock_reservations.py:82](../../../api/wms_api_server/app/routers/stock_reservations.py#L82)

```python
promote_stock_reservation_to_hard(reservation_id: int, request: StockReservationPromoteRequest, _user: AdminUser=Depends(require_permission(STOCK_RESERVATION_EDIT_PERMISSION))) -> dict[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `StockReservationService`, `require_permission`, `router.post`, `service.promote_to_hard`, `str`

### release_stock_reservation

[Исходник: api/wms_api_server/app/routers/stock_reservations.py:98](../../../api/wms_api_server/app/routers/stock_reservations.py#L98)

```python
release_stock_reservation(reservation_id: int, request: StockReservationStatusRequest, _user: AdminUser=Depends(require_permission(STOCK_RESERVATION_EDIT_PERMISSION))) -> dict[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `StockReservationService`, `StockReservationService().release_reservation`, `require_permission`, `router.post`, `str`

### consume_stock_reservation

[Исходник: api/wms_api_server/app/routers/stock_reservations.py:111](../../../api/wms_api_server/app/routers/stock_reservations.py#L111)

```python
consume_stock_reservation(reservation_id: int, request: StockReservationStatusRequest, _user: AdminUser=Depends(require_permission(STOCK_RESERVATION_EDIT_PERMISSION))) -> dict[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `StockReservationService`, `StockReservationService().consume_reservation`, `require_permission`, `router.post`, `str`

### cancel_stock_reservation

[Исходник: api/wms_api_server/app/routers/stock_reservations.py:124](../../../api/wms_api_server/app/routers/stock_reservations.py#L124)

```python
cancel_stock_reservation(reservation_id: int, request: StockReservationStatusRequest, _user: AdminUser=Depends(require_permission(STOCK_RESERVATION_EDIT_PERMISSION))) -> dict[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `StockReservationService`, `StockReservationService().cancel_reservation`, `require_permission`, `router.post`, `str`

### trace_forward

[Исходник: api/wms_api_server/app/routers/traceability.py:17](../../../api/wms_api_server/app/routers/traceability.py#L17)

```python
trace_forward(entity_type: str, entity_id: str, limit: int=100, _user: AdminUser=Depends(require_permission(TRACEABILITY_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `TraceabilityService`, `TraceabilityService().list_edges`, `require_permission`, `router.get`

### trace_backward

[Исходник: api/wms_api_server/app/routers/traceability.py:32](../../../api/wms_api_server/app/routers/traceability.py#L32)

```python
trace_backward(entity_type: str, entity_id: str, limit: int=100, _user: AdminUser=Depends(require_permission(TRACEABILITY_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `TraceabilityService`, `TraceabilityService().list_edges`, `require_permission`, `router.get`

### list_event_outbox

[Исходник: api/wms_api_server/app/routers/traceability.py:47](../../../api/wms_api_server/app/routers/traceability.py#L47)

```python
list_event_outbox(status: str | None=None, target_system: str | None=None, event_type: str | None=None, aggregate_type: str | None=None, aggregate_id: str | None=None, limit: int=100, _user: AdminUser=Depends(require_permission(EXTERNAL_OUTBOX_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `TraceabilityService`, `TraceabilityService().list_outbox`, `require_permission`, `router.get`

### get_event_outbox

[Исходник: api/wms_api_server/app/routers/traceability.py:67](../../../api/wms_api_server/app/routers/traceability.py#L67)

```python
get_event_outbox(event_outbox_id: int, _user: AdminUser=Depends(require_permission(EXTERNAL_OUTBOX_VIEW_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `TraceabilityService`, `TraceabilityService().get_outbox_event`, `require_permission`, `router.get`

### retry_event_outbox

[Исходник: api/wms_api_server/app/routers/traceability.py:78](../../../api/wms_api_server/app/routers/traceability.py#L78)

```python
retry_event_outbox(event_outbox_id: int, request: ExternalOutboxRetryRequest, user: AdminUser=Depends(require_permission(EXTERNAL_OUTBOX_VIEW_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `TraceabilityService`, `TraceabilityService().retry_outbox_event`, `require_permission`, `router.post`

### list_adapter_requests

[Исходник: api/wms_api_server/app/routers/traceability.py:101](../../../api/wms_api_server/app/routers/traceability.py#L101)

```python
list_adapter_requests(event_outbox_id: int | None=None, system_code: str | None=None, status: str | None=None, business_key: str | None=None, limit: int=100, _user: AdminUser=Depends(require_permission(EXTERNAL_OUTBOX_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `TraceabilityService`, `TraceabilityService().list_adapter_requests`, `require_permission`, `router.get`

### get_adapter_request

[Исходник: api/wms_api_server/app/routers/traceability.py:119](../../../api/wms_api_server/app/routers/traceability.py#L119)

```python
get_adapter_request(adapter_request_id: int, _user: AdminUser=Depends(require_permission(EXTERNAL_OUTBOX_VIEW_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `TraceabilityService`, `TraceabilityService().get_adapter_request`, `require_permission`, `router.get`

### list_vehicles

[Исходник: api/wms_api_server/app/routers/transport.py:109](../../../api/wms_api_server/app/routers/transport.py#L109)

```python
list_vehicles(_user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `TransportService`, `TransportService().list_vehicles`, `require_permission`, `router.get`

### list_vehicles_full

[Исходник: api/wms_api_server/app/routers/transport.py:117](../../../api/wms_api_server/app/routers/transport.py#L117)

```python
list_vehicles_full(_user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> list[dict]
```

Полный список ТС с деталями для страницы управления флотом (Sprint 97).

Вызывает: `Depends`, `TransportService`, `TransportService().list_vehicles_full`, `require_permission`, `router.get`

### create_vehicle

[Исходник: api/wms_api_server/app/routers/transport.py:125](../../../api/wms_api_server/app/routers/transport.py#L125)

```python
create_vehicle(req: VehicleCreateRequest, _user: AdminUser=Depends(require_permission(TRANSPORT_FLEET_EDIT_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `TransportService`, `TransportService().create_vehicle`, `require_permission`, `router.post`

### update_vehicle

[Исходник: api/wms_api_server/app/routers/transport.py:141](../../../api/wms_api_server/app/routers/transport.py#L141)

```python
update_vehicle(vehicle_id: int, req: VehicleUpdateRequest, _user: AdminUser=Depends(require_permission(TRANSPORT_FLEET_EDIT_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `TransportService`, `TransportService().update_vehicle`, `require_permission`, `router.patch`

### delete_vehicle

[Исходник: api/wms_api_server/app/routers/transport.py:159](../../../api/wms_api_server/app/routers/transport.py#L159)

```python
delete_vehicle(vehicle_id: int, _user: AdminUser=Depends(require_permission(TRANSPORT_FLEET_EDIT_PERMISSION))) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `TransportService`, `TransportService().delete_vehicle`, `require_permission`, `router.delete`

### list_drivers

[Исходник: api/wms_api_server/app/routers/transport.py:167](../../../api/wms_api_server/app/routers/transport.py#L167)

```python
list_drivers(_user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `TransportService`, `TransportService().list_drivers`, `require_permission`, `router.get`

### list_drivers_full

[Исходник: api/wms_api_server/app/routers/transport.py:175](../../../api/wms_api_server/app/routers/transport.py#L175)

```python
list_drivers_full(_user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> list[dict]
```

Полный список водителей для страницы управления флотом (Sprint 98).

Вызывает: `Depends`, `TransportService`, `TransportService().list_drivers_full`, `require_permission`, `router.get`

### create_driver

[Исходник: api/wms_api_server/app/routers/transport.py:183](../../../api/wms_api_server/app/routers/transport.py#L183)

```python
create_driver(req: DriverCreateRequest, _user: AdminUser=Depends(require_permission(TRANSPORT_FLEET_EDIT_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `TransportService`, `TransportService().create_driver`, `require_permission`, `router.post`

### update_driver

[Исходник: api/wms_api_server/app/routers/transport.py:197](../../../api/wms_api_server/app/routers/transport.py#L197)

```python
update_driver(driver_id: int, req: DriverUpdateRequest, _user: AdminUser=Depends(require_permission(TRANSPORT_FLEET_EDIT_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `TransportService`, `TransportService().update_driver`, `require_permission`, `router.patch`

### delete_driver

[Исходник: api/wms_api_server/app/routers/transport.py:213](../../../api/wms_api_server/app/routers/transport.py#L213)

```python
delete_driver(driver_id: int, _user: AdminUser=Depends(require_permission(TRANSPORT_FLEET_EDIT_PERMISSION))) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `TransportService`, `TransportService().delete_driver`, `require_permission`, `router.delete`

### list_transport_types

[Исходник: api/wms_api_server/app/routers/transport.py:221](../../../api/wms_api_server/app/routers/transport.py#L221)

```python
list_transport_types(_user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `TransportService`, `TransportService().list_transport_types`, `require_permission`, `router.get`

### list_available_sts

[Исходник: api/wms_api_server/app/routers/transport.py:232](../../../api/wms_api_server/app/routers/transport.py#L232)

```python
list_available_sts(stdate: date | None=None, date_to: date | None=None, unassigned_only: bool=True, ware_id: int | None=None, ware_ids: Annotated[list[int] | None, Query()]=None, page: int | None=Query(default=None, ge=1), page_size: int | None=Query(default=None, ge=1, le=500), addr_mask: str | None=None, st_mask: str | None=None, st_mask_exclude: bool=False, transport_type: str | None=None, assembled_only: bool=False, not_assembled_only: bool=False, max_weight_kg: float | None=None, max_volume_m3: float | None=None, articul: str | None=None, raion: str | None=None, _user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Query`, `TransportService`, `TransportService().list_available_sts`, `require_permission`, `router.get`

### list_clusters

[Исходник: api/wms_api_server/app/routers/transport.py:279](../../../api/wms_api_server/app/routers/transport.py#L279)

```python
list_clusters(stdate: date | None=None, ware_ids: Annotated[list[int] | None, Query()]=None, _user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Query`, `TransportService`, `TransportService().list_clusters`, `require_permission`, `router.get`

### create_task_from_cluster

[Исходник: api/wms_api_server/app/routers/transport.py:288](../../../api/wms_api_server/app/routers/transport.py#L288)

```python
create_task_from_cluster(raion: str, req: ClusterCreateTaskRequest, _user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_EDIT_PERMISSION))) -> dict
```

Создать рейс из всех свободных СТ района одним запросом — Sprint 29, Phase 2 полуавто.

Вызывает: `Depends`, `TransportService`, `TransportService().create_task_from_cluster`, `require_permission`, `router.post`

### export_tasks_xlsx

[Исходник: api/wms_api_server/app/routers/transport.py:302](../../../api/wms_api_server/app/routers/transport.py#L302)

```python
export_tasks_xlsx(shipment_date: date | None=None, condition: str | None=Query(default=None), task_id: int | None=Query(default=None), transport_mask: str | None=Query(default=None), company_mask: str | None=Query(default=None), date_from: date | None=Query(default=None), date_to: date | None=Query(default=None), no_payments_only: bool=False, _user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)))
```

Экспорт списка рейсов в Excel — Sprint 28, ТЗ §3 «В Excel».

Вызывает: `Depends`, `Query`, `StreamingResponse`, `TransportService`, `TransportService().export_tasks_xlsx`, `io.BytesIO`, `require_permission`, `router.get`

### list_tasks

[Исходник: api/wms_api_server/app/routers/transport.py:334](../../../api/wms_api_server/app/routers/transport.py#L334)

```python
list_tasks(shipment_date: date | None=None, stdate: date | None=Query(default=None, description='Legacy alias for shipment_date'), condition: str | None=None, include_readiness: bool=False, task_id: int | None=None, transport_mask: str | None=None, company_mask: str | None=None, date_from: date | None=None, date_to: date | None=None, no_payments_only: bool=False, _user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Query`, `TransportService`, `TransportService().list_tasks`, `require_permission`, `router.get`

### create_task

[Исходник: api/wms_api_server/app/routers/transport.py:361](../../../api/wms_api_server/app/routers/transport.py#L361)

```python
create_task(req: TransportTaskCreateRequest, user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_EDIT_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `TransportService`, `require_permission`, `router.post`, `str`, `svc.create_task`, `ws_manager.broadcast_sync`

### get_task

[Исходник: api/wms_api_server/app/routers/transport.py:375](../../../api/wms_api_server/app/routers/transport.py#L375)

```python
get_task(task_id: int, _user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `TransportService`, `TransportService().get_task`, `require_permission`, `router.get`

### update_task

[Исходник: api/wms_api_server/app/routers/transport.py:383](../../../api/wms_api_server/app/routers/transport.py#L383)

```python
update_task(task_id: int, req: TransportTaskUpdateRequest, user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_EDIT_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `TransportService`, `TransportService().update_task`, `require_permission`, `router.patch`, `ws_manager.broadcast_sync`

### close_task

[Исходник: api/wms_api_server/app/routers/transport.py:394](../../../api/wms_api_server/app/routers/transport.py#L394)

```python
close_task(task_id: int, user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_CLOSE_PERMISSION)), loading: TransportLoadingPort=Depends(transport_loading_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `TransportService`, `TransportService(departure=lambda trip, actor: loading.depart('TRIP.DEPART:' + str(trip), trip, actor)).close_task`, `loading.depart`, `require_permission`, `router.post`, `str`, `ws_manager.broadcast_sync`

### cancel_task

[Исходник: api/wms_api_server/app/routers/transport.py:405](../../../api/wms_api_server/app/routers/transport.py#L405)

```python
cancel_task(task_id: int, user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_EDIT_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `TransportService`, `TransportService().cancel_task`, `require_permission`, `router.post`, `ws_manager.broadcast_sync`

### get_task_sts

[Исходник: api/wms_api_server/app/routers/transport.py:419](../../../api/wms_api_server/app/routers/transport.py#L419)

```python
get_task_sts(task_id: int, _user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `TransportService`, `TransportService().get_task_sts`, `require_permission`, `router.get`

### assign_sts

[Исходник: api/wms_api_server/app/routers/transport.py:427](../../../api/wms_api_server/app/routers/transport.py#L427)

```python
assign_sts(task_id: int, req: TransportStAssignRequest, user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_EDIT_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `TransportService`, `TransportService().assign_sts`, `require_permission`, `router.post`, `ws_manager.broadcast_sync`

### unassign_st

[Исходник: api/wms_api_server/app/routers/transport.py:441](../../../api/wms_api_server/app/routers/transport.py#L441)

```python
unassign_st(task_id: int, st_number: str, user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_EDIT_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `TransportService`, `TransportService().unassign_st`, `require_permission`, `router.delete`, `ws_manager.broadcast_sync`

### set_st_load_type

[Исходник: api/wms_api_server/app/routers/transport.py:455](../../../api/wms_api_server/app/routers/transport.py#L455)

```python
set_st_load_type(task_id: int, st_number: str, req: TransportStLoadTypeRequest, user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_EDIT_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `TransportService`, `TransportService().set_st_load_type`, `require_permission`, `router.patch`

### set_st_order

[Исходник: api/wms_api_server/app/routers/transport.py:466](../../../api/wms_api_server/app/routers/transport.py#L466)

```python
set_st_order(task_id: int, st_number: str, req: TransportStOrderRequest, user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_EDIT_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `TransportService`, `TransportService().set_st_order`, `require_permission`, `router.patch`

### list_st_pallets

[Исходник: api/wms_api_server/app/routers/transport.py:481](../../../api/wms_api_server/app/routers/transport.py#L481)

```python
list_st_pallets(st_number: str, _user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `TransportService`, `TransportService().list_st_pallets`, `require_permission`, `router.get`

### get_planner_orders

[Исходник: api/wms_api_server/app/routers/transport.py:493](../../../api/wms_api_server/app/routers/transport.py#L493)

```python
get_planner_orders(date: date | None=None, plan_date: date | None=Query(default=None, description='Legacy alias for date'), ware_ids: Annotated[list[int] | None, Query()]=None, transport_type: str | None=None, _user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Query`, `TransportService`, `TransportService().get_planner_orders`, `require_permission`, `router.get`

### get_routing_status

[Исходник: api/wms_api_server/app/routers/transport.py:508](../../../api/wms_api_server/app/routers/transport.py#L508)

```python
get_routing_status(_user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `TransportService`, `TransportService().get_routing_status`, `require_permission`, `router.get`

### rebuild_distance_matrix

[Исходник: api/wms_api_server/app/routers/transport.py:519](../../../api/wms_api_server/app/routers/transport.py#L519)

```python
rebuild_distance_matrix(source: str=Query(default='auto', description='auto|haversine|osrm|valhalla'), force: bool=Query(default=False, description='Force full rewrite instead of incremental refresh'), max_age_hours: int=Query(default=24 * 30, ge=1, le=24 * 365), _user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_EDIT_PERMISSION))) -> dict
```

Пересчитывает матрицу расстояний RRL_ADDR_DISTANCE_MATRIX.

Вызывает: `Depends`, `DistanceMatrixService`, `DistanceMatrixService().rebuild`, `Query`, `require_permission`, `router.post`

### solve_vrp

[Исходник: api/wms_api_server/app/routers/transport.py:534](../../../api/wms_api_server/app/routers/transport.py#L534)

```python
solve_vrp(body: VrpSolveRequest, async_response: bool=Query(default=False, description='Return Sprint 101 job_id/SSE shape instead of direct VrpPlan'), _user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_EDIT_PERMISSION))) -> dict
```

Sprint 8 compatibility: by default returns a direct VrpPlan.
Sprint 101 async mode is explicit via ?async_response=true:
returns job_id, progress via GET /planner/solve/{job_id}/stream (SSE),
cancellation via DELETE /planner/solve/{job_id}.

Вызывает: `Depends`, `Query`, `TransportService`, `_time.sleep`, `dict`, `hasattr`, `int`, `job.cancel_event.is_set`, `job.cancel_event.set`, `job.put_event`, `job.result.get`, `len`, `min`, `require_permission`, `result.model_dump`, `router.post`, `str`, `svc.solve_vrp`, `t.start`, `threading.Thread`, `threading.Thread(target=_timeout, daemon=True).start`, `vrp_job_store.create`

### stream_vrp_job

[Исходник: api/wms_api_server/app/routers/transport.py:603](../../../api/wms_api_server/app/routers/transport.py#L603)

```python
stream_vrp_job(job_id: str, _user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_EDIT_PERMISSION)))
```

Sprint 101: SSE-стрим прогресса VRP-задачи.

Вызывает: `Depends`, `StreamingResponse`, `_HTTPException`, `job.stream`, `require_permission`, `router.get`, `vrp_job_store.get`

### cancel_vrp_job

[Исходник: api/wms_api_server/app/routers/transport.py:620](../../../api/wms_api_server/app/routers/transport.py#L620)

```python
cancel_vrp_job(job_id: str, _user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_EDIT_PERMISSION))) -> None
```

Sprint 101: отменить запущенный VRP-оптимизатор.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.delete`, `vrp_job_store.cancel`

### apply_vrp_plan

[Исходник: api/wms_api_server/app/routers/transport.py:630](../../../api/wms_api_server/app/routers/transport.py#L630)

```python
apply_vrp_plan(body: VrpApplyRequest, _user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_EDIT_PERMISSION))) -> dict
```

Создаёт рейсы (TRANSPORT_TASK) по сохранённому плану через Oracle-пакеты.
Возвращает {"tasks_created": int, "plan_id": int}.

Вызывает: `Depends`, `TransportService`, `require_permission`, `router.post`, `svc.apply_vrp_plan`

### get_planner_metrics

[Исходник: api/wms_api_server/app/routers/transport.py:648](../../../api/wms_api_server/app/routers/transport.py#L648)

```python
get_planner_metrics(plan_id: int | None=Query(default=None, description='ID плана; null = последний'), _user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> dict
```

Возвращает агрегированные метрики плана.

Вызывает: `Depends`, `Query`, `TransportService`, `TransportService().get_plan_metrics`, `require_permission`, `router.get`

### get_planner_templates

[Исходник: api/wms_api_server/app/routers/transport.py:657](../../../api/wms_api_server/app/routers/transport.py#L657)

```python
get_planner_templates(plan_date: date=Query(default=..., description='Дата СТ для поиска похожих планов'), lookback_days: int=Query(default=90, ge=7, le=365), min_jaccard: float=Query(default=0.7, ge=0.1, le=1.0), _user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> list[dict]
```

Возвращает исторические планы с Jaccard ≥ min_jaccard за последние lookback_days дней.

Вызывает: `Depends`, `Query`, `TransportService`, `TransportService().get_plan_templates`, `require_permission`, `router.get`

### get_planner_history

[Исходник: api/wms_api_server/app/routers/transport.py:672](../../../api/wms_api_server/app/routers/transport.py#L672)

```python
get_planner_history(date_from: date=Query(default=..., description='Начало периода'), date_to: date=Query(default=..., description='Конец периода'), limit: int=Query(default=25, ge=1, le=500, description='Максимум строк истории'), _user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> list[dict]
```

История применённых планов с метриками (Score, утилизация, пробег).

Вызывает: `Depends`, `Query`, `TransportService`, `TransportService().get_plan_history`, `require_permission`, `router.get`

### get_demand_forecast

[Исходник: api/wms_api_server/app/routers/transport.py:683](../../../api/wms_api_server/app/routers/transport.py#L683)

```python
get_demand_forecast(target_date: date=Query(default=..., description='Дата для прогноза'), lookback_weeks: int=Query(default=8, ge=2, le=52), _user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> dict
```

Прогноз числа СТ на целевую дату на основе истории аналогичных дней недели.

Вызывает: `Depends`, `Query`, `TransportService`, `TransportService().get_demand_forecast`, `require_permission`, `router.get`

### plan_operations

[Исходник: api/wms_api_server/app/routers/transport.py:699](../../../api/wms_api_server/app/routers/transport.py#L699)

```python
plan_operations(task_id: int, _user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_EDIT_PERMISSION))) -> list[dict]
```

Рассчитывает и сохраняет цепочку плановых операций рейса по нормативам.

Вызывает: `Depends`, `TransportService`, `TransportService().plan_operations`, `require_permission`, `router.post`

### get_operations

[Исходник: api/wms_api_server/app/routers/transport.py:708](../../../api/wms_api_server/app/routers/transport.py#L708)

```python
get_operations(task_id: int, _user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> list[dict]
```

Список операций рейса с плановыми и фактическими временами.

Вызывает: `Depends`, `TransportService`, `TransportService().get_operations`, `require_permission`, `router.get`

### get_vehicles_gantt

[Исходник: api/wms_api_server/app/routers/transport.py:719](../../../api/wms_api_server/app/routers/transport.py#L719)

```python
get_vehicles_gantt(gantt_date: date | None=Query(default=None, description='Дата для Ганта'), plan_date: date | None=Query(default=None, description='Legacy alias for gantt_date'), _user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> list[dict]
```

Данные диаграммы Ганта для всех машин на день.

Вызывает: `Depends`, `HTTPException`, `Query`, `TransportService`, `TransportService().get_vehicles_gantt`, `require_permission`, `router.get`

### get_vehicles_available

[Исходник: api/wms_api_server/app/routers/transport.py:736](../../../api/wms_api_server/app/routers/transport.py#L736)

```python
get_vehicles_available(shipment_time: str=Query(default=..., description='Плановое время отгрузки YYYY-MM-DD HH:MM'), pallets: int=Query(default=0, ge=0, description='Требуемое число паллет'), _user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> list[dict]
```

Список машин с индикатором доступности (green/yellow/red) к времени отгрузки.

Вызывает: `Depends`, `Query`, `TransportService`, `TransportService().get_vehicles_available`, `require_permission`, `router.get`

### get_plan_fact

[Исходник: api/wms_api_server/app/routers/transport.py:746](../../../api/wms_api_server/app/routers/transport.py#L746)

```python
get_plan_fact(date_from: date=Query(default=..., description='Начало периода'), date_to: date=Query(default=..., description='Конец периода'), vehicle: str | None=Query(default=None, description='Фильтр по гос. номеру'), _user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> list[dict]
```

Сводный план-фактный отчёт по всем рейсам периода.

Вызывает: `Depends`, `Query`, `TransportService`, `TransportService().get_plan_fact`, `require_permission`, `router.get`

### list_billing_orders

[Исходник: api/wms_api_server/app/routers/transport.py:761](../../../api/wms_api_server/app/routers/transport.py#L761)

```python
list_billing_orders(company: str | None=Query(default=None, description='Фильтр по компании'), date_from: date | None=Query(default=None, description='Начало периода'), date_to: date | None=Query(default=None, description='Конец периода'), closed: int | None=Query(default=None, description='0=открыт, 1=закрыт'), payed: int | None=Query(default=None, description='0=не оплачен, 1=оплачен'), _user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> list[dict]
```

Список биллинг-заказов с суммой и числом рейсов.

Вызывает: `Depends`, `Query`, `TransportService`, `TransportService().list_billing_orders`, `require_permission`, `router.get`

### export_billing_registry_xlsx

[Исходник: api/wms_api_server/app/routers/transport.py:774](../../../api/wms_api_server/app/routers/transport.py#L774)

```python
export_billing_registry_xlsx(company: str | None=Query(default=None), date_from: date | None=Query(default=None), date_to: date | None=Query(default=None), closed: int | None=Query(default=None), payed: int | None=Query(default=None), _user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)))
```

Экспорт реестра биллинг-заказов в Excel — Sprint 27.

Вызывает: `Depends`, `Query`, `StreamingResponse`, `TransportService`, `TransportService().export_billing_registry_xlsx`, `io.BytesIO`, `require_permission`, `router.get`

### create_billing_order

[Исходник: api/wms_api_server/app/routers/transport.py:793](../../../api/wms_api_server/app/routers/transport.py#L793)

```python
create_billing_order(req: BillingOrderCreate, _user: AdminUser=Depends(require_permission(BILLING_EDIT_PERMISSION))) -> dict
```

Создать новый биллинг-заказ.

Вызывает: `Depends`, `TransportService`, `next`, `require_permission`, `router.post`, `svc.create_billing_order`, `svc.list_billing_orders`

### get_billing_order

[Исходник: api/wms_api_server/app/routers/transport.py:806](../../../api/wms_api_server/app/routers/transport.py#L806)

```python
get_billing_order(order_id: int, _user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> dict
```

Один биллинг-заказ по ID.

Вызывает: `Depends`, `HTTPException`, `TransportService`, `TransportService().get_billing_order`, `require_permission`, `router.get`

### close_billing_order

[Исходник: api/wms_api_server/app/routers/transport.py:819](../../../api/wms_api_server/app/routers/transport.py#L819)

```python
close_billing_order(order_id: int, _user: AdminUser=Depends(require_permission(BILLING_EDIT_PERMISSION))) -> dict
```

Закрыть биллинг-заказ (вызывает RRL_CLOSE_BILLINGORDER).

Вызывает: `Depends`, `TransportService`, `TransportService().close_billing_order`, `require_permission`, `router.patch`

### pay_billing_order

[Исходник: api/wms_api_server/app/routers/transport.py:828](../../../api/wms_api_server/app/routers/transport.py#L828)

```python
pay_billing_order(order_id: int, _user: AdminUser=Depends(require_permission(BILLING_EDIT_PERMISSION))) -> dict
```

Отметить биллинг-заказ как оплаченный (вызывает RRL_PAY_BILLINGORDER).

Вызывает: `Depends`, `TransportService`, `TransportService().pay_billing_order`, `require_permission`, `router.patch`

### get_billing_order_tasks

[Исходник: api/wms_api_server/app/routers/transport.py:837](../../../api/wms_api_server/app/routers/transport.py#L837)

```python
get_billing_order_tasks(order_id: int, _user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> list[dict]
```

Рейсы, привязанные к биллинг-заказу.

Вызывает: `Depends`, `TransportService`, `TransportService().get_billing_order_tasks`, `require_permission`, `router.get`

### export_billing_order_xlsx

[Исходник: api/wms_api_server/app/routers/transport.py:846](../../../api/wms_api_server/app/routers/transport.py#L846)

```python
export_billing_order_xlsx(order_id: int, _user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)))
```

Экспорт счёта в Excel (.xlsx) — Sprint 26, DoD §12 #7.

Вызывает: `Depends`, `StreamingResponse`, `TransportService`, `TransportService().export_billing_order_xlsx`, `io.BytesIO`, `require_permission`, `router.get`

### add_tasks_to_billing_order

[Исходник: api/wms_api_server/app/routers/transport.py:862](../../../api/wms_api_server/app/routers/transport.py#L862)

```python
add_tasks_to_billing_order(order_id: int, req: BillingAddTasksRequest, _user: AdminUser=Depends(require_permission(BILLING_EDIT_PERMISSION))) -> dict
```

Привязать рейсы к биллинг-заказу.

Вызывает: `Depends`, `TransportService`, `TransportService().add_tasks_to_order`, `len`, `require_permission`, `router.post`

### get_task_billing

[Исходник: api/wms_api_server/app/routers/transport.py:873](../../../api/wms_api_server/app/routers/transport.py#L873)

```python
get_task_billing(task_id: int, _user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> dict
```

Биллинг-данные рейса (заказ, к которому привязан).

Вызывает: `Depends`, `HTTPException`, `TransportService`, `TransportService().get_task_billing`, `require_permission`, `router.get`

### open_billing_for_task

[Исходник: api/wms_api_server/app/routers/transport.py:886](../../../api/wms_api_server/app/routers/transport.py#L886)

```python
open_billing_for_task(task_id: int, _user: AdminUser=Depends(require_permission(BILLING_EDIT_PERMISSION))) -> dict
```

Создать биллинг-заказ для рейса и привязать к нему.

Вызывает: `Depends`, `TransportService`, `TransportService().open_billing_for_task`, `require_permission`, `router.post`

### remove_task_from_billing_order

[Исходник: api/wms_api_server/app/routers/transport.py:895](../../../api/wms_api_server/app/routers/transport.py#L895)

```python
remove_task_from_billing_order(order_id: int, tt_id: int, _user: AdminUser=Depends(require_permission(BILLING_EDIT_PERMISSION))) -> dict
```

Отвязать рейс от биллинг-заказа (обнулить PAY_ORDER_ID).

Вызывает: `Depends`, `TransportService`, `TransportService().remove_task_from_billing_order`, `require_permission`, `router.delete`

### recalculate_task_price

[Исходник: api/wms_api_server/app/routers/transport.py:905](../../../api/wms_api_server/app/routers/transport.py#L905)

```python
recalculate_task_price(task_id: int, _user: AdminUser=Depends(require_permission(BILLING_CALC_PRICE_PERMISSION))) -> dict
```

Пересчитать стоимость рейса через Oracle-функцию TRANSPORT_TASK.stoim_tt.

Вызывает: `Depends`, `TransportService`, `TransportService().recalculate_price`, `require_permission`, `router.post`

### set_task_price

[Исходник: api/wms_api_server/app/routers/transport.py:914](../../../api/wms_api_server/app/routers/transport.py#L914)

```python
set_task_price(task_id: int, req: PriceUpdateRequest, _user: AdminUser=Depends(require_permission(BILLING_CREATE_PRICE_PERMISSION))) -> dict
```

Ручная установка стоимости рейса (право CREATE_TT_PRICE).

Вызывает: `Depends`, `TransportService`, `TransportService().set_task_price`, `require_permission`, `router.patch`

### list_billing_companies

[Исходник: api/wms_api_server/app/routers/transport.py:924](../../../api/wms_api_server/app/routers/transport.py#L924)

```python
list_billing_companies(_user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> list[str]
```

Справочник транспортных компаний из RRL_BILL_COMPANY (Sprint 22).

Вызывает: `Depends`, `TransportService`, `TransportService().list_billing_companies`, `require_permission`, `router.get`

### ws_dispatch

[Исходник: api/wms_api_server/app/routers/transport.py:936](../../../api/wms_api_server/app/routers/transport.py#L936)

```python
ws_dispatch(websocket: WebSocket, u: str='', p: str='')
```

WebSocket-канал событий диспетчера.

Sprint 96: broadcast task_created/updated/closed/cancelled, sts_assigned/unassigned.
Аутентификация: query-параметры ?u=login&p=password.
При admin_auth_enabled=False принимает все соединения.

Вызывает: `get_settings`, `load_admin_user`, `router.websocket`, `websocket.close`, `websocket.receive_text`, `ws_manager.connect`, `ws_manager.disconnect`

### ws_status

[Исходник: api/wms_api_server/app/routers/transport.py:962](../../../api/wms_api_server/app/routers/transport.py#L962)

```python
ws_status(_user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> dict
```

Количество активных WebSocket-соединений (Sprint 96).

Вызывает: `Depends`, `require_permission`, `router.get`

### _run

[Исходник: api/wms_api_server/app/routers/transport.py:559](../../../api/wms_api_server/app/routers/transport.py#L559)

```python
_run() -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `dict`, `hasattr`, `job.cancel_event.is_set`, `job.put_event`, `job.result.get`, `len`, `result.model_dump`, `str`, `svc.solve_vrp`

### _timeout

[Исходник: api/wms_api_server/app/routers/transport.py:589](../../../api/wms_api_server/app/routers/transport.py#L589)

```python
_timeout() -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_time.sleep`, `job.cancel_event.set`, `job.put_event`

### _gw

[Исходник: api/wms_api_server/app/routers/transport_kpi.py:22](../../../api/wms_api_server/app/routers/transport_kpi.py#L22)

```python
_gw() -> OracleGateway
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`

### get_fleet_kpi

[Исходник: api/wms_api_server/app/routers/transport_kpi.py:31](../../../api/wms_api_server/app/routers/transport_kpi.py#L31)

```python
get_fleet_kpi(date_from: date=Query(...), date_to: date=Query(...), _user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> list[dict]
```

Утилизация парка по дням (Sprint 108). Вес из TEMP_WEIGHT, паллеты из COUNT(PALLET_UID).

Вызывает: `Depends`, `Query`, `_gw`, `_gw().fetch_all`, `float`, `int`, `r.get`, `require_permission`, `router.get`, `str`

### get_summary_kpi

[Исходник: api/wms_api_server/app/routers/transport_kpi.py:70](../../../api/wms_api_server/app/routers/transport_kpi.py#L70)

```python
get_summary_kpi(date_from: date=Query(...), date_to: date=Query(...), _user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> dict
```

Сводные KPI за период (Sprint 108).

Вызывает: `Depends`, `Query`, `_gw`, `_gw().fetch_all`, `float`, `int`, `r.get`, `require_permission`, `round`, `router.get`, `str`

### get_regions_kpi

[Исходник: api/wms_api_server/app/routers/transport_kpi.py:109](../../../api/wms_api_server/app/routers/transport_kpi.py#L109)

```python
get_regions_kpi(trip_date: date=Query(default=None), date_from: date=Query(default=None), date_to: date=Query(default=None), _user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> list[dict]
```

Топ регионов по паллетам (Sprint 108).

Вызывает: `Depends`, `Query`, `_date.today`, `_date.today().replace`, `_gw`, `_gw().fetch_all`, `float`, `int`, `r.get`, `require_permission`, `router.get`, `str`

### get_billing_kpi

[Исходник: api/wms_api_server/app/routers/transport_kpi.py:160](../../../api/wms_api_server/app/routers/transport_kpi.py#L160)

```python
get_billing_kpi(date_from: date=Query(...), date_to: date=Query(...), _user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> dict
```

Сводка биллинга за период (Sprint 109).

Вызывает: `Depends`, `Query`, `_gw`, `_gw().fetch_all`, `float`, `int`, `r.get`, `require_permission`, `round`, `router.get`, `str`

### get_billing_by_company

[Исходник: api/wms_api_server/app/routers/transport_kpi.py:200](../../../api/wms_api_server/app/routers/transport_kpi.py#L200)

```python
get_billing_by_company(date_from: date=Query(...), date_to: date=Query(...), _user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> list[dict]
```

Расходы на ТК по счетам за период (Sprint 109).

Вызывает: `Depends`, `Query`, `_gw`, `_gw().fetch_all`, `float`, `int`, `r.get`, `require_permission`, `router.get`, `str`

### list_tariffs

[Исходник: api/wms_api_server/app/routers/transport_tariffs.py:11](../../../api/wms_api_server/app/routers/transport_tariffs.py#L11)

```python
list_tariffs(region: str | None=Query(default=None, min_length=1, max_length=255), transport_type: str | None=Query(default=None, min_length=1, max_length=40), _user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> list[dict]
```

Region is the original PRICE_NAME key; rates are exact decimal strings.

Вызывает: `Depends`, `OracleGateway`, `OracleGateway().fetch_all`, `Query`, `require_permission`, `router.get`, `row.items`, `str`, `str(k).upper`

### get_tariff_table_info

[Исходник: api/wms_api_server/app/routers/transport_tariffs.py:34](../../../api/wms_api_server/app/routers/transport_tariffs.py#L34)

```python
get_tariff_table_info(_user: AdminUser=Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `OracleGateway`, `c.get`, `gw.fetch_all`, `int`, `require_permission`, `router.get`, `str`

### _to_models

[Исходник: api/wms_api_server/app/routers/tserver.py:19](../../../api/wms_api_server/app/routers/tserver.py#L19)

```python
_to_models(blocks) -> list[LegacyBlockModel]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LegacyBlockModel`

### _fault_response

[Исходник: api/wms_api_server/app/routers/tserver.py:23](../../../api/wms_api_server/app/routers/tserver.py#L23)

```python
_fault_response(exc: Exception) -> LegacyExecuteResponse
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LegacyExecuteResponse`, `_to_models`, `encode_legacy_blocks`, `fault`, `str`

### execute_legacy_tserver

[Исходник: api/wms_api_server/app/routers/tserver.py:29](../../../api/wms_api_server/app/routers/tserver.py#L29)

```python
execute_legacy_tserver(request: LegacyExecuteRequest, user: AdminUser=Depends(get_current_admin)) -> LegacyExecuteResponse
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `LegacyExecuteResponse`, `TserverService`, `TserverService().execute_legacy_payload`, `_to_models`, `router.post`

### get_terminal_user

[Исходник: api/wms_api_server/app/routers/tserver.py:35](../../../api/wms_api_server/app/routers/tserver.py#L35)

```python
get_terminal_user(user_id: str) -> list[LegacyBlockModel]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TserverService`, `TserverService().get_ruser`, `_to_models`, `fault`, `router.get`, `str`

### get_product_by_barcode

[Исходник: api/wms_api_server/app/routers/tserver.py:43](../../../api/wms_api_server/app/routers/tserver.py#L43)

```python
get_product_by_barcode(barcode: str) -> list[LegacyBlockModel]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TserverService`, `TserverService().get_product_info`, `_to_models`, `fault`, `router.get`, `str`

### get_lot_items

[Исходник: api/wms_api_server/app/routers/tserver.py:51](../../../api/wms_api_server/app/routers/tserver.py#L51)

```python
get_lot_items(usscc: str) -> LegacyExecuteResponse
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LegacyExecuteResponse`, `TserverService`, `TserverService().get_lot_items`, `_fault_response`, `_to_models`, `encode_legacy_blocks`, `router.get`

### get_place_items

[Исходник: api/wms_api_server/app/routers/tserver.py:60](../../../api/wms_api_server/app/routers/tserver.py#L60)

```python
get_place_items(place_id: str) -> LegacyExecuteResponse
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LegacyExecuteResponse`, `TserverService`, `TserverService().get_place_items`, `_fault_response`, `_to_models`, `encode_legacy_blocks`, `router.get`

### confirm_lot_check

[Исходник: api/wms_api_server/app/routers/tserver.py:69](../../../api/wms_api_server/app/routers/tserver.py#L69)

```python
confirm_lot_check(usscc: str, request: LotCheckRequest, user: AdminUser=Depends(get_current_admin)) -> dict[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `TserverService`, `TserverService().confirm_lot_check`, `router.post`, `str`

### confirm_place_check

[Исходник: api/wms_api_server/app/routers/tserver.py:80](../../../api/wms_api_server/app/routers/tserver.py#L80)

```python
confirm_place_check(request: PlaceCheckRequest) -> dict[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TserverService`, `TserverService().confirm_place_check`, `router.post`

### confirm_order_check

[Исходник: api/wms_api_server/app/routers/tserver.py:86](../../../api/wms_api_server/app/routers/tserver.py#L86)

```python
confirm_order_check(request: OrderCheckRequest) -> dict[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TserverService`, `TserverService().confirm_order_check`, `router.post`

### call_spf

[Исходник: api/wms_api_server/app/routers/tserver.py:92](../../../api/wms_api_server/app/routers/tserver.py#L92)

```python
call_spf(request: CallSpfRequest, user: AdminUser=Depends(get_current_admin)) -> dict[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `TserverService`, `TserverService().call_spf`, `router.post`

### terminal_identity

[Исходник: api/wms_api_server/app/routers/tserver.py:98](../../../api/wms_api_server/app/routers/tserver.py#L98)

```python
terminal_identity(user: AdminUser=Depends(get_current_admin)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `router.get`, `serialize_admin_user`

### _gw

[Исходник: api/wms_api_server/app/routers/users.py:44](../../../api/wms_api_server/app/routers/users.py#L44)

```python
_gw() -> OracleGateway
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`

### list_users

[Исходник: api/wms_api_server/app/routers/users.py:53](../../../api/wms_api_server/app/routers/users.py#L53)

```python
list_users(_user: AdminUser=Depends(require_permission(RIGHTS_ADMIN_VIEW_PERMISSION))) -> list[dict]
```

Список пользователей без паролей (Sprint 99).

Вызывает: `Depends`, `_gw`, `_gw().fetch_all`, `bool`, `r.get`, `require_permission`, `router.get`, `str`

### list_groups

[Исходник: api/wms_api_server/app/routers/users.py:81](../../../api/wms_api_server/app/routers/users.py#L81)

```python
list_groups(_user: AdminUser=Depends(require_permission(RIGHTS_ADMIN_VIEW_PERMISSION))) -> list[dict]
```

Список групп с назначенными правами (Sprint 99).

Вызывает: `Depends`, `_gw`, `_gw().fetch_all`, `groups.items`, `groups.setdefault`, `groups.setdefault(g, []).append`, `r.get`, `require_permission`, `router.get`, `sorted`, `str`

### list_all_rights

[Исходник: api/wms_api_server/app/routers/users.py:102](../../../api/wms_api_server/app/routers/users.py#L102)

```python
list_all_rights(_user: AdminUser=Depends(require_permission(RIGHTS_ADMIN_VIEW_PERMISSION))) -> list[str]
```

Полный справочник кодов прав (Sprint 99).

Вызывает: `Depends`, `require_permission`, `router.get`, `sorted`

### create_user

[Исходник: api/wms_api_server/app/routers/users.py:136](../../../api/wms_api_server/app/routers/users.py#L136)

```python
create_user(req: UserCreateRequest, _user: AdminUser=Depends(require_permission(RIGHTS_ADMIN_EDIT_PERMISSION))) -> dict
```

Создать пользователя (Sprint 100). Oracle stores passwords as plaintext (legacy).

Вызывает: `Depends`, `HTTPException`, `_gw`, `existing[0].get`, `gw.execute`, `gw.fetch_all`, `int`, `require_permission`, `router.post`

### update_user

[Исходник: api/wms_api_server/app/routers/users.py:165](../../../api/wms_api_server/app/routers/users.py#L165)

```python
update_user(login: str, req: UserUpdateRequest, _user: AdminUser=Depends(require_permission(RIGHTS_ADMIN_EDIT_PERMISSION))) -> dict
```

Изменить группу / is_admin / имя пользователя (Sprint 100).

Вызывает: `', '.join`, `Depends`, `_gw`, `gw.execute`, `require_permission`, `router.patch`, `sets.append`

### delete_user

[Исходник: api/wms_api_server/app/routers/users.py:185](../../../api/wms_api_server/app/routers/users.py#L185)

```python
delete_user(login: str, _user: AdminUser=Depends(require_permission(RIGHTS_ADMIN_EDIT_PERMISSION))) -> None
```

Мягкое удаление пользователя (Sprint 100).

Вызывает: `Depends`, `_gw`, `_gw().execute`, `require_permission`, `router.delete`

### set_password

[Исходник: api/wms_api_server/app/routers/users.py:197](../../../api/wms_api_server/app/routers/users.py#L197)

```python
set_password(login: str, req: UserPasswordRequest, _user: AdminUser=Depends(require_permission(RIGHTS_ADMIN_EDIT_PERMISSION))) -> None
```

Сменить пароль пользователя (Sprint 100).

Вызывает: `Depends`, `_gw`, `_gw().execute`, `require_permission`, `router.patch`

### add_group_right

[Исходник: api/wms_api_server/app/routers/users.py:210](../../../api/wms_api_server/app/routers/users.py#L210)

```python
add_group_right(group: str, req: GroupRightRequest, _user: AdminUser=Depends(require_permission(RIGHTS_ADMIN_EDIT_PERMISSION))) -> dict
```

Добавить право группе (Sprint 100). Idempotent.

Вызывает: `Depends`, `_gw`, `existing[0].get`, `gw.execute`, `gw.fetch_all`, `int`, `req.right.lower`, `require_permission`, `router.post`

### remove_group_right

[Исходник: api/wms_api_server/app/routers/users.py:230](../../../api/wms_api_server/app/routers/users.py#L230)

```python
remove_group_right(group: str, right: str, _user: AdminUser=Depends(require_permission(RIGHTS_ADMIN_EDIT_PERMISSION))) -> None
```

Удалить право из группы (Sprint 100).

Вызывает: `Depends`, `_gw`, `_gw().execute`, `require_permission`, `router.delete`

### create_group

[Исходник: api/wms_api_server/app/routers/users.py:243](../../../api/wms_api_server/app/routers/users.py#L243)

```python
create_group(body: dict, _user: AdminUser=Depends(require_permission(RIGHTS_ADMIN_EDIT_PERMISSION))) -> dict
```

Создать пустую группу прав (Sprint 100). Группа материализуется первым правом.

Вызывает: `Depends`, `HTTPException`, `body.get`, `require_permission`, `router.post`, `str`, `str(body.get('group') or '').strip`

### list_warehouse_map_canvases

[Исходник: api/wms_api_server/app/routers/warehouse_map.py:21](../../../api/wms_api_server/app/routers/warehouse_map.py#L21)

```python
list_warehouse_map_canvases(ware_id: Annotated[int, Path(gt=0)], _user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Path`, `WarehouseMapService`, `WarehouseMapService().list_canvases`, `require_permission`, `router.get`

### get_warehouse_map_state

[Исходник: api/wms_api_server/app/routers/warehouse_map.py:29](../../../api/wms_api_server/app/routers/warehouse_map.py#L29)

```python
get_warehouse_map_state(ware_id: Annotated[int, Path(gt=0)], canvas_id: int | None=None, _user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_VIEW_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Path`, `WarehouseMapService`, `WarehouseMapService().get_warehouse_state`, `require_permission`, `router.get`

### get_warehouse_map_canvas_state

[Исходник: api/wms_api_server/app/routers/warehouse_map.py:38](../../../api/wms_api_server/app/routers/warehouse_map.py#L38)

```python
get_warehouse_map_canvas_state(canvas_id: int, _user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_VIEW_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseMapService`, `WarehouseMapService().get_canvas_state`, `require_permission`, `router.get`

### archive_warehouse_map_canvas

[Исходник: api/wms_api_server/app/routers/warehouse_map.py:46](../../../api/wms_api_server/app/routers/warehouse_map.py#L46)

```python
archive_warehouse_map_canvas(canvas_id: int, request: WarehouseMapArchiveRequest, user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseMapService`, `WarehouseMapService().archive_canvas`, `require_permission`, `router.post`

### create_warehouse_map_canvas

[Исходник: api/wms_api_server/app/routers/warehouse_map.py:55](../../../api/wms_api_server/app/routers/warehouse_map.py#L55)

```python
create_warehouse_map_canvas(ware_id: Annotated[int, Path(gt=0)], request: WarehouseMapCanvasCreateRequest, user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Path`, `WarehouseMapService`, `WarehouseMapService().create_canvas`, `require_permission`, `router.post`

### create_warehouse_map_camera

[Исходник: api/wms_api_server/app/routers/warehouse_map.py:64](../../../api/wms_api_server/app/routers/warehouse_map.py#L64)

```python
create_warehouse_map_camera(canvas_id: int, request: WarehouseMapCameraCreateRequest, user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseMapService`, `WarehouseMapService().create_camera`, `require_permission`, `router.post`

### clone_warehouse_map_camera

[Исходник: api/wms_api_server/app/routers/warehouse_map.py:73](../../../api/wms_api_server/app/routers/warehouse_map.py#L73)

```python
clone_warehouse_map_camera(camera_id: int, request: WarehouseMapCameraCloneRequest, user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseMapService`, `WarehouseMapService().clone_camera`, `require_permission`, `router.post`

### archive_warehouse_map_camera

[Исходник: api/wms_api_server/app/routers/warehouse_map.py:82](../../../api/wms_api_server/app/routers/warehouse_map.py#L82)

```python
archive_warehouse_map_camera(camera_id: int, request: WarehouseMapArchiveRequest, user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseMapService`, `WarehouseMapService().archive_camera`, `require_permission`, `router.post`

### patch_warehouse_map_camera_objects

[Исходник: api/wms_api_server/app/routers/warehouse_map.py:91](../../../api/wms_api_server/app/routers/warehouse_map.py#L91)

```python
patch_warehouse_map_camera_objects(camera_id: int, request: WarehouseMapObjectsPatchRequest, user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseMapService`, `WarehouseMapService().replace_camera_objects`, `require_permission`, `router.patch`

### patch_warehouse_map_camera_passages

[Исходник: api/wms_api_server/app/routers/warehouse_map.py:100](../../../api/wms_api_server/app/routers/warehouse_map.py#L100)

```python
patch_warehouse_map_camera_passages(camera_id: int, request: WarehouseMapPassagesPatchRequest, user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseMapService`, `WarehouseMapService().replace_camera_passages`, `require_permission`, `router.patch`

### patch_warehouse_map_camera_links

[Исходник: api/wms_api_server/app/routers/warehouse_map.py:109](../../../api/wms_api_server/app/routers/warehouse_map.py#L109)

```python
patch_warehouse_map_camera_links(canvas_id: int, request: WarehouseMapCameraLinksPatchRequest, user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseMapService`, `WarehouseMapService().replace_camera_links`, `require_permission`, `router.patch`

### list_warehouse_map_drafts

[Исходник: api/wms_api_server/app/routers/warehouse_map_drafts.py:29](../../../api/wms_api_server/app/routers/warehouse_map_drafts.py#L29)

```python
list_warehouse_map_drafts(_user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseMapDraftService`, `WarehouseMapDraftService().list_drafts`, `require_permission`, `router.get`

### create_warehouse_map_draft

[Исходник: api/wms_api_server/app/routers/warehouse_map_drafts.py:36](../../../api/wms_api_server/app/routers/warehouse_map_drafts.py#L36)

```python
create_warehouse_map_draft(request: WarehouseMapDraftCreateRequest, user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseMapDraftService`, `WarehouseMapDraftService().create_draft`, `require_permission`, `router.post`

### load_warehouse_map_draft_from_db

[Исходник: api/wms_api_server/app/routers/warehouse_map_drafts.py:44](../../../api/wms_api_server/app/routers/warehouse_map_drafts.py#L44)

```python
load_warehouse_map_draft_from_db(request: WarehouseMapDraftLoadFromDbRequest, user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseMapDraftService`, `WarehouseMapDraftService().load_from_db`, `require_permission`, `router.post`

### get_warehouse_map_draft

[Исходник: api/wms_api_server/app/routers/warehouse_map_drafts.py:52](../../../api/wms_api_server/app/routers/warehouse_map_drafts.py#L52)

```python
get_warehouse_map_draft(draft_id: str, _user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_VIEW_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseMapDraftService`, `WarehouseMapDraftService().get_draft`, `require_permission`, `router.get`

### patch_warehouse_map_draft_cells

[Исходник: api/wms_api_server/app/routers/warehouse_map_drafts.py:60](../../../api/wms_api_server/app/routers/warehouse_map_drafts.py#L60)

```python
patch_warehouse_map_draft_cells(draft_id: str, request: WarehouseMapDraftCellsPatchRequest, user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseMapDraftService`, `WarehouseMapDraftService().patch_cells`, `require_permission`, `router.patch`

### get_warehouse_map_draft_diff

[Исходник: api/wms_api_server/app/routers/warehouse_map_drafts.py:69](../../../api/wms_api_server/app/routers/warehouse_map_drafts.py#L69)

```python
get_warehouse_map_draft_diff(draft_id: str, _user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_VIEW_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseMapDraftService`, `WarehouseMapDraftService().diff_draft`, `require_permission`, `router.get`

### save_warehouse_map_draft_to_db

[Исходник: api/wms_api_server/app/routers/warehouse_map_drafts.py:77](../../../api/wms_api_server/app/routers/warehouse_map_drafts.py#L77)

```python
save_warehouse_map_draft_to_db(draft_id: str, request: WarehouseMapDraftSaveToDbRequest, user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseMapDraftService`, `WarehouseMapDraftService().save_to_db`, `require_permission`, `router.post`

### patch_warehouse_map_draft_metadata

[Исходник: api/wms_api_server/app/routers/warehouse_map_drafts.py:86](../../../api/wms_api_server/app/routers/warehouse_map_drafts.py#L86)

```python
patch_warehouse_map_draft_metadata(draft_id: str, request: WarehouseMapDraftMetadataPatchRequest, user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseMapDraftService`, `WarehouseMapDraftService().patch_metadata`, `require_permission`, `router.patch`

### build_warehouse_map_draft_route

[Исходник: api/wms_api_server/app/routers/warehouse_map_drafts.py:95](../../../api/wms_api_server/app/routers/warehouse_map_drafts.py#L95)

```python
build_warehouse_map_draft_route(draft_id: str, request: WarehouseMapDraftRouteBuildRequest, user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseMapDraftService`, `WarehouseMapDraftService().build_route`, `require_permission`, `router.post`

### patch_warehouse_map_draft_route

[Исходник: api/wms_api_server/app/routers/warehouse_map_drafts.py:104](../../../api/wms_api_server/app/routers/warehouse_map_drafts.py#L104)

```python
patch_warehouse_map_draft_route(draft_id: str, request: WarehouseMapDraftRoutePatchRequest, user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseMapDraftService`, `WarehouseMapDraftService().patch_route`, `require_permission`, `router.patch`

### save_warehouse_map_draft_route_to_db

[Исходник: api/wms_api_server/app/routers/warehouse_map_drafts.py:113](../../../api/wms_api_server/app/routers/warehouse_map_drafts.py#L113)

```python
save_warehouse_map_draft_route_to_db(draft_id: str, request: WarehouseMapDraftRouteSaveToDbRequest, user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseMapDraftService`, `WarehouseMapDraftService().save_route_to_db`, `require_permission`, `router.post`

### publish_warehouse_map_draft_to_oracle

[Исходник: api/wms_api_server/app/routers/warehouse_map_drafts.py:122](../../../api/wms_api_server/app/routers/warehouse_map_drafts.py#L122)

```python
publish_warehouse_map_draft_to_oracle(draft_id: str, request: WarehouseMapDraftOraclePublishRequest, user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseMapDraftService`, `WarehouseMapDraftService().publish_oracle`, `require_permission`, `router.post`

### apply_warehouse_map_bulk_role

[Исходник: api/wms_api_server/app/routers/warehouse_map_drafts.py:131](../../../api/wms_api_server/app/routers/warehouse_map_drafts.py#L131)

```python
apply_warehouse_map_bulk_role(draft_id: str, request: WarehouseMapBulkRoleRequest, user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseMapDraftService`, `WarehouseMapDraftService().bulk_role`, `require_permission`, `router.post`

### generate_warehouse_map_pick_face_addresses

[Исходник: api/wms_api_server/app/routers/warehouse_map_drafts.py:140](../../../api/wms_api_server/app/routers/warehouse_map_drafts.py#L140)

```python
generate_warehouse_map_pick_face_addresses(draft_id: str, request: WarehouseMapPickFaceAddressRequest, user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseMapDraftService`, `WarehouseMapDraftService().generate_pick_face_addresses`, `require_permission`, `router.post`

### generate_warehouse_map_small_pick_faces

[Исходник: api/wms_api_server/app/routers/warehouse_map_drafts.py:149](../../../api/wms_api_server/app/routers/warehouse_map_drafts.py#L149)

```python
generate_warehouse_map_small_pick_faces(draft_id: str, request: WarehouseMapSmallPickFaceGenerateRequest, user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseMapDraftService`, `WarehouseMapDraftService().generate_small_pick_faces`, `require_permission`, `router.post`

### patch_warehouse_map_small_pick_face

[Исходник: api/wms_api_server/app/routers/warehouse_map_drafts.py:158](../../../api/wms_api_server/app/routers/warehouse_map_drafts.py#L158)

```python
patch_warehouse_map_small_pick_face(draft_id: str, small_pick_face_id: str, request: WarehouseMapSmallPickFacePatchRequest, user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseMapDraftService`, `WarehouseMapDraftService().patch_small_pick_face`, `require_permission`, `router.patch`

### renumber_warehouse_map_small_pick_faces

[Исходник: api/wms_api_server/app/routers/warehouse_map_drafts.py:168](../../../api/wms_api_server/app/routers/warehouse_map_drafts.py#L168)

```python
renumber_warehouse_map_small_pick_faces(draft_id: str, request: WarehouseMapSmallPickFaceRenumberRequest, user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseMapDraftService`, `WarehouseMapDraftService().renumber_small_pick_faces`, `require_permission`, `router.post`

### generate_warehouse_map_storage_slots

[Исходник: api/wms_api_server/app/routers/warehouse_map_drafts.py:177](../../../api/wms_api_server/app/routers/warehouse_map_drafts.py#L177)

```python
generate_warehouse_map_storage_slots(draft_id: str, request: WarehouseMapStorageSlotGenerateRequest, user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseMapDraftService`, `WarehouseMapDraftService().generate_storage_slots`, `require_permission`, `router.post`

### patch_warehouse_map_storage_slot

[Исходник: api/wms_api_server/app/routers/warehouse_map_drafts.py:186](../../../api/wms_api_server/app/routers/warehouse_map_drafts.py#L186)

```python
patch_warehouse_map_storage_slot(draft_id: str, storage_slot_id: str, request: WarehouseMapStorageSlotPatchRequest, user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseMapDraftService`, `WarehouseMapDraftService().patch_storage_slot`, `require_permission`, `router.patch`

### validate_warehouse_map_draft

[Исходник: api/wms_api_server/app/routers/warehouse_map_drafts.py:196](../../../api/wms_api_server/app/routers/warehouse_map_drafts.py#L196)

```python
validate_warehouse_map_draft(draft_id: str, _user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_VIEW_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseMapDraftService`, `WarehouseMapDraftService().validate_draft`, `require_permission`, `router.post`

### preview_warehouse_map_draft_projection

[Исходник: api/wms_api_server/app/routers/warehouse_map_drafts.py:204](../../../api/wms_api_server/app/routers/warehouse_map_drafts.py#L204)

```python
preview_warehouse_map_draft_projection(draft_id: str, _user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_VIEW_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseMapDraftService`, `WarehouseMapDraftService().preview_projection`, `require_permission`, `router.post`

### save_warehouse_map_draft_projection_to_topology

[Исходник: api/wms_api_server/app/routers/warehouse_map_drafts.py:212](../../../api/wms_api_server/app/routers/warehouse_map_drafts.py#L212)

```python
save_warehouse_map_draft_projection_to_topology(draft_id: str, request: WarehouseMapDraftProjectionSaveRequest, user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseMapDraftService`, `WarehouseMapDraftService().save_projection_to_topology`, `require_permission`, `router.post`

### publish_warehouse_map_draft

[Исходник: api/wms_api_server/app/routers/warehouse_map_drafts.py:221](../../../api/wms_api_server/app/routers/warehouse_map_drafts.py#L221)

```python
publish_warehouse_map_draft(draft_id: str, user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseMapDraftService`, `WarehouseMapDraftService().publish_draft`, `require_permission`, `router.post`

### _read

[Исходник: api/wms_api_server/app/routers/warehouse_tasks.py:21](../../../api/wms_api_server/app/routers/warehouse_tasks.py#L21)

```python
_read(user: AdminUser, loader: Callable[[TransactionGateway, TaskViewScope], ReadResult], task_id: int | None=None) -> ReadResult
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `WarehouseTaskService`, `read_task_snapshot`

### list_warehouse_tasks

[Исходник: api/wms_api_server/app/routers/warehouse_tasks.py:30](../../../api/wms_api_server/app/routers/warehouse_tasks.py#L30)

```python
list_warehouse_tasks(status: str | None=None, task_type: str | None=None, task_source: str | None=None, assigned_to: str | None=None, production_order_id: int | None=None, source_doc_type: str | None=None, source_doc_id: int | None=None, limit: int=Query(default=100, ge=1, le=500), queue_group: Literal['SHIPPING', 'DEFER_WAITING'] | None=None, _user: AdminUser=Depends(require_permission(WAREHOUSE_TASK_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Query`, `WarehouseTaskService`, `WarehouseTaskService(gateway).list_tasks`, `_read`, `require_permission`, `router.get`

### list_warehouse_task_sync

[Исходник: api/wms_api_server/app/routers/warehouse_tasks.py:55](../../../api/wms_api_server/app/routers/warehouse_tasks.py#L55)

```python
list_warehouse_task_sync(status: str | None=None, task_source: str | None=None, source_doc_type: str | None=None, source_doc_id: int | None=None, limit: int=100, _user: AdminUser=Depends(require_permission(WAREHOUSE_TASK_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseTaskDomainSyncService`, `WarehouseTaskDomainSyncService(gateway).list_sync`, `_read`, `require_permission`, `router.get`

### get_warehouse_task

[Исходник: api/wms_api_server/app/routers/warehouse_tasks.py:73](../../../api/wms_api_server/app/routers/warehouse_tasks.py#L73)

```python
get_warehouse_task(task_id: int, _user: AdminUser=Depends(require_permission(WAREHOUSE_TASK_VIEW_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseTaskService`, `WarehouseTaskService(gateway).get_task_or_404`, `_read`, `require_permission`, `router.get`

### get_warehouse_task_progress

[Исходник: api/wms_api_server/app/routers/warehouse_tasks.py:81](../../../api/wms_api_server/app/routers/warehouse_tasks.py#L81)

```python
get_warehouse_task_progress(task_id: int, _user: AdminUser=Depends(require_permission(WAREHOUSE_TASK_VIEW_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `WarehouseTaskService`, `read_task_progress_snapshot`, `require_permission`, `router.get`

### get_warehouse_task_sync

[Исходник: api/wms_api_server/app/routers/warehouse_tasks.py:92](../../../api/wms_api_server/app/routers/warehouse_tasks.py#L92)

```python
get_warehouse_task_sync(task_id: int, _user: AdminUser=Depends(require_permission(WAREHOUSE_TASK_VIEW_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseTaskDomainSyncService`, `WarehouseTaskDomainSyncService(gateway).get_task_sync`, `_read`, `require_permission`, `router.get`

### assign_warehouse_task

[Исходник: api/wms_api_server/app/routers/warehouse_tasks.py:101](../../../api/wms_api_server/app/routers/warehouse_tasks.py#L101)

```python
assign_warehouse_task(task_id: int, request: WarehouseTaskStatusRequest, _user: AdminUser=Depends(require_permission(WAREHOUSE_TASK_EXECUTE_PERMISSION))) -> dict[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseTaskService`, `WarehouseTaskService().assign_task`, `require_permission`, `router.post`

### start_warehouse_task

[Исходник: api/wms_api_server/app/routers/warehouse_tasks.py:112](../../../api/wms_api_server/app/routers/warehouse_tasks.py#L112)

```python
start_warehouse_task(task_id: int, request: WarehouseTaskStatusRequest, _user: AdminUser=Depends(require_permission(WAREHOUSE_TASK_EXECUTE_PERMISSION))) -> dict[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseTaskService`, `WarehouseTaskService().start_task`, `require_permission`, `router.post`

### complete_warehouse_task

[Исходник: api/wms_api_server/app/routers/warehouse_tasks.py:123](../../../api/wms_api_server/app/routers/warehouse_tasks.py#L123)

```python
complete_warehouse_task(task_id: int, request: WarehouseTaskStatusRequest, _user: AdminUser=Depends(require_permission(WAREHOUSE_TASK_EXECUTE_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseTaskService`, `WarehouseTaskService().complete_task`, `require_permission`, `router.post`

### retry_warehouse_task_sync

[Исходник: api/wms_api_server/app/routers/warehouse_tasks.py:134](../../../api/wms_api_server/app/routers/warehouse_tasks.py#L134)

```python
retry_warehouse_task_sync(task_id: int, request: WarehouseTaskStatusRequest, _user: AdminUser=Depends(require_permission(WAREHOUSE_TASK_EXECUTE_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseTaskDomainSyncService`, `WarehouseTaskDomainSyncService().retry_task_sync`, `require_permission`, `router.post`

### cancel_warehouse_task

[Исходник: api/wms_api_server/app/routers/warehouse_tasks.py:144](../../../api/wms_api_server/app/routers/warehouse_tasks.py#L144)

```python
cancel_warehouse_task(task_id: int, request: WarehouseTaskStatusRequest, _user: AdminUser=Depends(require_permission('warehouse_task_edit'))) -> dict[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseTaskService`, `WarehouseTaskService().cancel_task`, `require_permission`, `router.post`

### list_topologies

[Исходник: api/wms_api_server/app/routers/warehouse_topology.py:27](../../../api/wms_api_server/app/routers/warehouse_topology.py#L27)

```python
list_topologies(ware_id: int | None=None, status: str | None=None, _user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseTopologyService`, `WarehouseTopologyService().list_topologies`, `require_permission`, `router.get`

### create_topology

[Исходник: api/wms_api_server/app/routers/warehouse_topology.py:36](../../../api/wms_api_server/app/routers/warehouse_topology.py#L36)

```python
create_topology(request: WarehouseTopologyCreateRequest, user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION))) -> dict[str, int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseTopologyService`, `WarehouseTopologyService().create_topology`, `require_permission`, `router.post`

### get_topology_map

[Исходник: api/wms_api_server/app/routers/warehouse_topology.py:46](../../../api/wms_api_server/app/routers/warehouse_topology.py#L46)

```python
get_topology_map(topology_id: int, _user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_VIEW_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `WarehouseTopologyService`, `WarehouseTopologyService().get_topology_map`, `require_permission`, `router.get`

### generate_cells

[Исходник: api/wms_api_server/app/routers/warehouse_topology.py:57](../../../api/wms_api_server/app/routers/warehouse_topology.py#L57)

```python
generate_cells(topology_id: int, request: WarehouseTopologyGenerateRequest, user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION))) -> dict[str, int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseTopologyService`, `WarehouseTopologyService().generate_cells`, `require_permission`, `router.post`

### generate_gates

[Исходник: api/wms_api_server/app/routers/warehouse_topology.py:67](../../../api/wms_api_server/app/routers/warehouse_topology.py#L67)

```python
generate_gates(topology_id: int, request: TopologyGateGenerateRequest, user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION))) -> dict[str, int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseTopologyService`, `WarehouseTopologyService().generate_gates`, `require_permission`, `router.post`

### recalculate_gate_distances

[Исходник: api/wms_api_server/app/routers/warehouse_topology.py:77](../../../api/wms_api_server/app/routers/warehouse_topology.py#L77)

```python
recalculate_gate_distances(topology_id: int, request: TopologyDistanceRecalculateRequest, user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION))) -> dict[str, int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseTopologyService`, `WarehouseTopologyService().recalculate_gate_distances`, `require_permission`, `router.post`

### validate_topology

[Исходник: api/wms_api_server/app/routers/warehouse_topology.py:87](../../../api/wms_api_server/app/routers/warehouse_topology.py#L87)

```python
validate_topology(topology_id: int, _user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_VIEW_PERMISSION))) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseTopologyService`, `WarehouseTopologyService().validate_topology`, `require_permission`, `router.post`

### normalize_topology_cell_codes

[Исходник: api/wms_api_server/app/routers/warehouse_topology.py:95](../../../api/wms_api_server/app/routers/warehouse_topology.py#L95)

```python
normalize_topology_cell_codes(topology_id: int, user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION))) -> dict[str, int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseTopologyService`, `WarehouseTopologyService().normalize_pick_face_cell_codes`, `require_permission`, `router.post`

### publish_topology

[Исходник: api/wms_api_server/app/routers/warehouse_topology.py:103](../../../api/wms_api_server/app/routers/warehouse_topology.py#L103)

```python
publish_topology(topology_id: int, user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_PUBLISH_PERMISSION))) -> dict[str, int | str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseTopologyService`, `WarehouseTopologyService().publish_topology`, `require_permission`, `router.post`

### patch_topology_cell

[Исходник: api/wms_api_server/app/routers/warehouse_topology.py:112](../../../api/wms_api_server/app/routers/warehouse_topology.py#L112)

```python
patch_topology_cell(topology_cell_id: int, request: TopologyCellPatchRequest, user: AdminUser=Depends(require_permission(WAREHOUSE_TOPOLOGY_EDIT_PERMISSION))) -> dict[str, int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseTopologyService`, `WarehouseTopologyService().patch_cell`, `require_permission`, `router.patch`

### list_admin_pick_routes

[Исходник: api/wms_api_server/app/routers/warehouse_topology.py:123](../../../api/wms_api_server/app/routers/warehouse_topology.py#L123)

```python
list_admin_pick_routes(topology_id: int | None=None, ware_id: int | None=None, status: str | None=None, _user: AdminUser=Depends(require_permission(PICK_ROUTE_ADMIN_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseTopologyService`, `WarehouseTopologyService().list_pick_routes`, `require_permission`, `router.get`

### build_pick_route

[Исходник: api/wms_api_server/app/routers/warehouse_topology.py:133](../../../api/wms_api_server/app/routers/warehouse_topology.py#L133)

```python
build_pick_route(request: PickRouteBuildRequest, user: AdminUser=Depends(require_permission(PICK_ROUTE_ADMIN_EDIT_PERMISSION))) -> dict[str, int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseTopologyService`, `WarehouseTopologyService().build_pick_route`, `require_permission`, `router.post`

### publish_pick_route

[Исходник: api/wms_api_server/app/routers/warehouse_topology.py:142](../../../api/wms_api_server/app/routers/warehouse_topology.py#L142)

```python
publish_pick_route(pick_route_id: int, user: AdminUser=Depends(require_permission(PICK_ROUTE_ADMIN_PUBLISH_PERMISSION))) -> dict[str, int | str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseTopologyService`, `WarehouseTopologyService().publish_pick_route`, `require_permission`, `router.post`

### list_warehouses

[Исходник: api/wms_api_server/app/routers/warehouses.py:16](../../../api/wms_api_server/app/routers/warehouses.py#L16)

```python
list_warehouses(role: str | None=None, mes_enabled: int | None=None, limit: int=200, _user: AdminUser=Depends(require_permission(WAREHOUSE_SETTINGS_VIEW_PERMISSION))) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `WarehouseService`, `WarehouseService().list_warehouses`, `require_permission`, `router.get`

### update_warehouse

[Исходник: api/wms_api_server/app/routers/warehouses.py:30](../../../api/wms_api_server/app/routers/warehouses.py#L30)

```python
update_warehouse(ware_id: int, request: WarehouseSettingsUpdateRequest, _user: AdminUser=Depends(require_permission(WAREHOUSE_SETTINGS_EDIT_PERMISSION))) -> dict[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `WarehouseService`, `WarehouseService().update_warehouse`, `require_permission`, `router.patch`
