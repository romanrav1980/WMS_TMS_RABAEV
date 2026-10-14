# Методы: inventory

### labels

[Исходник: api/wms_api_server/app/modules/inventory/api/case_label_routes.py:8](../../../api/wms_api_server/app/modules/inventory/api/case_label_routes.py#L8)

```python
labels() -> CaseLabelPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### issue

[Исходник: api/wms_api_server/app/modules/inventory/api/case_label_routes.py:11](../../../api/wms_api_server/app/modules/inventory/api/case_label_routes.py#L11)

```python
issue(task: int, body: CaseSsccLabelRequest, user: AdminUser=Depends(require_permission('case_pick_execute')), service: CaseLabelPort=Depends(labels)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `require_permission`, `router.post`, `service.issue`

### current

[Исходник: api/wms_api_server/app/modules/inventory/api/case_label_routes.py:15](../../../api/wms_api_server/app/modules/inventory/api/case_label_routes.py#L15)

```python
current(task: int, user: AdminUser=Depends(require_permission('case_pick_execute')), service: CaseLabelPort=Depends(labels)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `require_permission`, `router.get`, `service.current`

### confirm

[Исходник: api/wms_api_server/app/modules/inventory/api/case_label_routes.py:19](../../../api/wms_api_server/app/modules/inventory/api/case_label_routes.py#L19)

```python
confirm(task: int, body: CaseSsccConfirmRequest, user: AdminUser=Depends(require_permission('case_pick_execute')), service: CaseLabelPort=Depends(labels)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `require_permission`, `router.post`, `service.confirm`

### document

[Исходник: api/wms_api_server/app/modules/inventory/api/case_label_routes.py:23](../../../api/wms_api_server/app/modules/inventory/api/case_label_routes.py#L23)

```python
document(task: int, format: Literal['html', 'zpl']='html', dpi: int=Query(203, ge=203, le=600), user: AdminUser=Depends(require_permission('case_pick_execute')), service: CaseLabelPort=Depends(labels)) -> Response
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Query`, `Response`, `require_permission`, `router.get`, `service.document`

### failure

[Исходник: api/wms_api_server/app/modules/inventory/api/case_type_routes.py:18](../../../api/wms_api_server/app/modules/inventory/api/case_type_routes.py#L18)

```python
failure(exc: StockPostingError) -> HTTPException
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `str`

### read

[Исходник: api/wms_api_server/app/modules/inventory/api/case_type_routes.py:25](../../../api/wms_api_server/app/modules/inventory/api/case_type_routes.py#L25)

```python
read(task_id: int=Path(ge=1), user: AdminUser=Depends(require_permission('case_pick_view')), service: CaseTypePort=Depends(case_type_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Path`, `failure`, `require_permission`, `router.get`, `service.read`

### change

[Исходник: api/wms_api_server/app/modules/inventory/api/case_type_routes.py:31](../../../api/wms_api_server/app/modules/inventory/api/case_type_routes.py#L31)

```python
change(body: CaseTypeRequest, task_id: int=Path(ge=1), user: AdminUser=Depends(require_permission('case_pick_execute')), service: CaseTypePort=Depends(case_type_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Path`, `body.model_dump`, `failure`, `require_permission`, `router.post`, `service.change`, `str`, `values.items`

### install_stock_error_handlers

[Исходник: api/wms_api_server/app/modules/inventory/api/error_handlers.py:11](../../../api/wms_api_server/app/modules/inventory/api/error_handlers.py#L11)

```python
install_stock_error_handlers(app: FastAPI) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `JSONResponse`, `app.add_exception_handler`

### posting_error

[Исходник: api/wms_api_server/app/modules/inventory/api/error_handlers.py:12](../../../api/wms_api_server/app/modules/inventory/api/error_handlers.py#L12)

```python
posting_error(_request: Request, error: StockPostingError) -> JSONResponse
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `JSONResponse`

### fullpal_shipment_service

[Исходник: api/wms_api_server/app/modules/inventory/api/fullpal_shipment_routes.py:16](../../../api/wms_api_server/app/modules/inventory/api/fullpal_shipment_routes.py#L16)

```python
fullpal_shipment_service() -> FullPalletPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### preview

[Исходник: api/wms_api_server/app/modules/inventory/api/fullpal_shipment_routes.py:28](../../../api/wms_api_server/app/modules/inventory/api/fullpal_shipment_routes.py#L28)

```python
preview(task_id: int, _user: AdminUser=Depends(require_permission('warehouse_task_view')), service: FullPalletPort=Depends(fullpal_shipment_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.get`, `service.preview`, `str`

### bind

[Исходник: api/wms_api_server/app/modules/inventory/api/fullpal_shipment_routes.py:41](../../../api/wms_api_server/app/modules/inventory/api/fullpal_shipment_routes.py#L41)

```python
bind(task_id: int, body: FullPalletBindingRequest, user: AdminUser=Depends(require_permission('warehouse_task_execute')), service: FullPalletPort=Depends(fullpal_shipment_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `body.model_dump`, `require_permission`, `router.post`, `service.bind`

### preview

[Исходник: api/wms_api_server/app/modules/inventory/api/fullpal_shipment_routes.py:9](../../../api/wms_api_server/app/modules/inventory/api/fullpal_shipment_routes.py#L9)

```python
preview(self, task_id: int, actor: str | None=None) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### bind

[Исходник: api/wms_api_server/app/modules/inventory/api/fullpal_shipment_routes.py:10](../../../api/wms_api_server/app/modules/inventory/api/fullpal_shipment_routes.py#L10)

```python
bind(self, task_id: int, body: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### group_source

[Исходник: api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py:15](../../../api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py#L15)

```python
group_source(load_id: str, user: AdminUser=Depends(require_permission('transport_dispatch_edit')), service: InterwarehousePort=Depends(interwarehouse_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.get`, `service.group_source`, `str`

### group_queue

[Исходник: api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py:22](../../../api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py#L22)

```python
group_queue(ware_id: int, limit: int=Query(default=200, ge=1, le=200), after_operation_id: str | None=Query(default=None, min_length=1, max_length=100), user: AdminUser=Depends(require_permission('transport_dispatch_view')), service: InterwarehousePort=Depends(interwarehouse_service)) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Query`, `require_permission`, `router.get`, `service.group_queue`, `str`

### group_detail

[Исходник: api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py:27](../../../api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py#L27)

```python
group_detail(plan_id: str, user: AdminUser=Depends(require_permission('transport_dispatch_view')), service: InterwarehousePort=Depends(interwarehouse_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.get`, `service.group_detail`, `str`

### group_proof

[Исходник: api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py:53](../../../api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py#L53)

```python
group_proof(load_id: str, user: AdminUser=Depends(require_permission('transport_dispatch_edit')), service: InterwarehousePort=Depends(interwarehouse_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.get`, `service.group_source_proof`, `str`

### group_plan

[Исходник: api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py:60](../../../api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py#L60)

```python
group_plan(body: GroupPlan, user: AdminUser=Depends(require_permission('transport_dispatch_edit')), service: InterwarehousePort=Depends(interwarehouse_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `body.model_dump`, `require_permission`, `router.post`, `service.plan_group`, `str`

### plan

[Исходник: api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py:67](../../../api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py#L67)

```python
plan(body: Plan, user: AdminUser=Depends(require_permission('transport_dispatch_edit')), service: InterwarehousePort=Depends(interwarehouse_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.post`, `service.plan`, `str`

### queue

[Исходник: api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py:74](../../../api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py#L74)

```python
queue(ware_id: int, include_completed: bool=Query(default=False), user: AdminUser=Depends(require_permission('transport_dispatch_view')), service: InterwarehousePort=Depends(interwarehouse_service)) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Query`, `require_permission`, `router.get`, `service.queue`, `str`

### physical

[Исходник: api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py:120](../../../api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py#L120)

```python
physical(kind: str, body: PhysicalAction, user: AdminUser, service: InterwarehousePort) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `body.model_dump`, `service.receive_action`, `str`

### unload

[Исходник: api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py:131](../../../api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py#L131)

```python
unload(body: Unload, user: AdminUser=Depends(require_permission('interwarehouse_receive')), service: InterwarehousePort=Depends(interwarehouse_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `physical`, `require_permission`, `router.post`

### receive

[Исходник: api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py:135](../../../api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py#L135)

```python
receive(body: Receive, user: AdminUser=Depends(require_permission('interwarehouse_receive')), service: InterwarehousePort=Depends(interwarehouse_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `physical`, `require_permission`, `router.post`

### group_receive

[Исходник: api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py:159](../../../api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py#L159)

```python
group_receive(body: GroupReceive, user: AdminUser=Depends(require_permission('interwarehouse_receive')), service: InterwarehousePort=Depends(interwarehouse_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `physical`, `require_permission`, `router.post`

### group_placement

[Исходник: api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py:189](../../../api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py#L189)

```python
group_placement(body: GroupPlacement, user: AdminUser=Depends(require_permission('warehouse_task_execute')), service: InterwarehousePort=Depends(interwarehouse_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `body.model_dump`, `require_permission`, `router.post`, `service.plan_group_placement`, `str`

### group_onward

[Исходник: api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py:204](../../../api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py#L204)

```python
group_onward(body: GroupOnward, user: AdminUser=Depends(require_permission('outgoing_pallet_edit')), service: InterwarehousePort=Depends(interwarehouse_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.post`, `service.prepare_group_onward`, `str`

### placement

[Исходник: api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py:219](../../../api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py#L219)

```python
placement(body: PlacementReplan, user: AdminUser=Depends(require_permission('interwarehouse_receive')), service: InterwarehousePort=Depends(interwarehouse_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.post`, `service.plan_placement`, `str`

### release_custody

[Исходник: api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py:228](../../../api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py#L228)

```python
release_custody(body: PlacementPlan, user: AdminUser=Depends(require_permission('interwarehouse_receive')), service: InterwarehousePort=Depends(interwarehouse_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.post`, `service.release_custody`, `str`

### prepare_onward

[Исходник: api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py:242](../../../api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py#L242)

```python
prepare_onward(body: OnwardPlan, user: AdminUser=Depends(require_permission('outgoing_pallet_edit')), service: InterwarehousePort=Depends(interwarehouse_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.post`, `service.prepare_onward`, `str`

### source_units

[Исходник: api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py:249](../../../api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py#L249)

```python
source_units(plan_id: str, user: AdminUser=Depends(require_permission('interwarehouse_receive')), service: InterwarehousePort=Depends(interwarehouse_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.get`, `service.unit_manifest`, `str`

### dispatch_decision

[Исходник: api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py:288](../../../api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py#L288)

```python
dispatch_decision(body: DispatchDecision, user: AdminUser=Depends(require_permission('transport_dispatch_edit')), service: InterwarehousePort=Depends(interwarehouse_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `body.model_dump`, `require_permission`, `router.post`, `service.record_decision`, `str`

### temperature_decision

[Исходник: api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py:316](../../../api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py#L316)

```python
temperature_decision(body: ThermalDecision, user: AdminUser=Depends(require_permission('transport_dispatch_edit')), service: InterwarehousePort=Depends(interwarehouse_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `body.model_dump`, `require_permission`, `router.post`, `service.record_temperature`, `str`

### incoming

[Исходник: api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py:324](../../../api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py#L324)

```python
incoming(trip_id: int, user: AdminUser=Depends(require_permission('transport_dispatch_view')), service: InterwarehousePort=Depends(interwarehouse_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.get`, `service.incoming`, `str`

### decisions

[Исходник: api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py:331](../../../api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py#L331)

```python
decisions(plan_id: str, after_revision: int=Query(default=0, ge=0, le=9999999999), user: AdminUser=Depends(require_permission('transport_dispatch_view')), service: InterwarehousePort=Depends(interwarehouse_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Query`, `require_permission`, `router.get`, `service.decisions`, `str`

### close_incident

[Исходник: api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py:348](../../../api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py#L348)

```python
close_incident(body: IncidentClosure, user: AdminUser=Depends(require_permission('transport_dispatch_edit')), service: InterwarehousePort=Depends(interwarehouse_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `body.model_dump`, `require_permission`, `router.post`, `service.close_incident`, `str`

### shortage

[Исходник: api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py:354](../../../api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py#L354)

```python
shortage(receipt_id: str, selected_request: str | None=Query(default=None, min_length=1, max_length=100), user: AdminUser=Depends(require_permission('transport_dispatch_view')), service: InterwarehousePort=Depends(interwarehouse_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Query`, `len`, `require_permission`, `router.get`, `service.shortage`, `str`

### post_shortage

[Исходник: api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py:373](../../../api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py#L373)

```python
post_shortage(kind: str, body: ShortageEvidence, source_id: str, user: AdminUser, service: InterwarehousePort) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `action`, `body.model_dump`, `kind.startswith`, `str`

### report_shortage

[Исходник: api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py:383](../../../api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py#L383)

```python
report_shortage(body: ShortageReport, user: AdminUser=Depends(require_permission('transport_dispatch_edit')), service: InterwarehousePort=Depends(interwarehouse_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `post_shortage`, `require_permission`, `router.post`

### confirm_shortage

[Исходник: api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py:388](../../../api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py#L388)

```python
confirm_shortage(body: ShortageConfirmation, user: AdminUser=Depends(require_permission('store_return_approve')), service: InterwarehousePort=Depends(interwarehouse_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `post_shortage`, `require_permission`, `router.post`

### report_recovery

[Исходник: api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py:397](../../../api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py#L397)

```python
report_recovery(body: RecoveryReport, user: AdminUser=Depends(require_permission('transport_dispatch_edit')), service: InterwarehousePort=Depends(interwarehouse_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `post_shortage`, `require_permission`, `router.post`

### approve_recovery

[Исходник: api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py:402](../../../api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py#L402)

```python
approve_recovery(body: ShortageConfirmation, user: AdminUser=Depends(require_permission('store_return_approve')), service: InterwarehousePort=Depends(interwarehouse_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `post_shortage`, `require_permission`, `router.post`

### receive_recovery

[Исходник: api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py:425](../../../api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py#L425)

```python
receive_recovery(body: RecoveryReceipt, user: AdminUser=Depends(require_permission('interwarehouse_receive')), service: InterwarehousePort=Depends(interwarehouse_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `body.model_dump`, `require_permission`, `router.post`, `service.receive_recovery`, `str`

### recovery_placement

[Исходник: api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py:440](../../../api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py#L440)

```python
recovery_placement(body: RecoveryPlacement, user: AdminUser=Depends(require_permission('interwarehouse_receive')), service: InterwarehousePort=Depends(interwarehouse_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.post`, `service.plan_recovery_placement`, `str`

### prepare_recovery_onward

[Исходник: api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py:454](../../../api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py#L454)

```python
prepare_recovery_onward(body: RecoveryOnward, user: AdminUser=Depends(require_permission('transport_dispatch_edit')), service: InterwarehousePort=Depends(interwarehouse_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.post`, `service.prepare_recovery_onward`, `str`

### cancel_recovery

[Исходник: api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py:460](../../../api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py#L460)

```python
cancel_recovery(body: ShortageConfirmation, user: AdminUser=Depends(require_permission('store_return_approve')), service: InterwarehousePort=Depends(interwarehouse_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `post_shortage`, `require_permission`, `router.post`

### deadlines

[Исходник: api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py:44](../../../api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py#L44)

```python
deadlines(self) -> 'Plan'
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `any`, `model_validator`, `value.utcoffset`

### partial_fields

[Исходник: api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py:110](../../../api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py#L110)

```python
partial_fields(self) -> 'Receive'
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `any`, `model_validator`

### distinct_items

[Исходник: api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py:153](../../../api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py#L153)

```python
distinct_items(self) -> 'GroupReceive'
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `len`, `model_validator`

### replan_contract

[Исходник: api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py:213](../../../api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py#L213)

```python
replan_contract(self) -> 'PlacementReplan'
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `model_validator`, `self.replan_reason.strip`

### decision_contract

[Исходник: api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py:273](../../../api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py#L273)

```python
decision_contract(self) -> 'DispatchDecision'
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `model_validator`, `self.decision_reference.strip`, `self.evidence_reference.strip`, `self.expected_arrival.utcoffset`, `self.incident_detail.strip`, `self.ready_due.utcoffset`, `self.reason.strip`

### thermal_contract

[Исходник: api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py:308](../../../api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py#L308)

```python
thermal_contract(self) -> 'ThermalDecision'
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `model_validator`, `self.decision_reference.strip`, `self.observation_reference.strip`, `self.reason.strip`

### inventory_lots

[Исходник: api/wms_api_server/app/modules/inventory/api/inventory_count_routes.py:42](../../../api/wms_api_server/app/modules/inventory/api/inventory_count_routes.py#L42)

```python
inventory_lots(revision_id: int, cell: str, article: str | None=None, user: AdminUser=Depends(require_permission('stock_inventory_count')), service: InventoryObservationsPort=Depends(inventory_observations_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `len`, `require_permission`, `router.get`, `service.lots`

### inventory_count

[Исходник: api/wms_api_server/app/modules/inventory/api/inventory_count_routes.py:51](../../../api/wms_api_server/app/modules/inventory/api/inventory_count_routes.py#L51)

```python
inventory_count(request: CountRequest, user: AdminUser=Depends(require_permission('stock_inventory_count')), service: InventoryObservationsPort=Depends(inventory_observations_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CountSubmission.from_wire`, `Depends`, `HTTPException`, `ValueError`, `any`, `json.dumps`, `json.dumps(requested, ensure_ascii=True).encode`, `len`, `line.model_dump`, `request.model_dump`, `require_permission`, `router.post`, `service.count`, `set`, `str`, `sum`

### create_inventory_revision

[Исходник: api/wms_api_server/app/modules/inventory/api/inventory_count_routes.py:83](../../../api/wms_api_server/app/modules/inventory/api/inventory_count_routes.py#L83)

```python
create_inventory_revision(request: RevisionRequest, user: AdminUser=Depends(require_permission('stock_inventory_count')), service: InventoryObservationsPort=Depends(inventory_observations_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.post`, `service.create_revision`

### register_inventory_lot

[Исходник: api/wms_api_server/app/modules/inventory/api/inventory_count_routes.py:106](../../../api/wms_api_server/app/modules/inventory/api/inventory_count_routes.py#L106)

```python
register_inventory_lot(request: InventoryLotBirthRequest, user: AdminUser=Depends(require_permission('stock_inventory_count')), service: InventoryObservationsPort=Depends(inventory_observations_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `request.model_dump`, `require_permission`, `router.post`, `service.register_lot`

### investigation_view

[Исходник: api/wms_api_server/app/modules/inventory/api/investigation_routes.py:35](../../../api/wms_api_server/app/modules/inventory/api/investigation_routes.py#L35)

```python
investigation_view() -> InvestigationUser
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### investigation_edit

[Исходник: api/wms_api_server/app/modules/inventory/api/investigation_routes.py:38](../../../api/wms_api_server/app/modules/inventory/api/investigation_routes.py#L38)

```python
investigation_edit() -> InvestigationUser
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### camera_edit

[Исходник: api/wms_api_server/app/modules/inventory/api/investigation_routes.py:41](../../../api/wms_api_server/app/modules/inventory/api/investigation_routes.py#L41)

```python
camera_edit() -> InvestigationUser
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### investigation_service

[Исходник: api/wms_api_server/app/modules/inventory/api/investigation_routes.py:44](../../../api/wms_api_server/app/modules/inventory/api/investigation_routes.py#L44)

```python
investigation_service() -> InvestigationPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### read

[Исходник: api/wms_api_server/app/modules/inventory/api/investigation_routes.py:50](../../../api/wms_api_server/app/modules/inventory/api/investigation_routes.py#L50)

```python
read(short_id: int=Path(gt=0), user: InvestigationUser=Depends(investigation_view), service: InvestigationPort=Depends(investigation_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Path`, `router.get`, `service.read`

### review

[Исходник: api/wms_api_server/app/modules/inventory/api/investigation_routes.py:55](../../../api/wms_api_server/app/modules/inventory/api/investigation_routes.py#L55)

```python
review(request: InvestigationInput, short_id: int=Path(gt=0), user: InvestigationUser=Depends(investigation_edit), service: InvestigationPort=Depends(investigation_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Path`, `router.post`, `service.review`

### configure

[Исходник: api/wms_api_server/app/modules/inventory/api/investigation_routes.py:61](../../../api/wms_api_server/app/modules/inventory/api/investigation_routes.py#L61)

```python
configure(request: CameraInput, user: InvestigationUser=Depends(camera_edit), service: InvestigationPort=Depends(investigation_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `router.put`, `service.configure`

### camera_settings

[Исходник: api/wms_api_server/app/modules/inventory/api/investigation_routes.py:66](../../../api/wms_api_server/app/modules/inventory/api/investigation_routes.py#L66)

```python
camera_settings(warehouse: int=Query(gt=0), cell: str=Query(min_length=1, max_length=60), user: InvestigationUser=Depends(camera_edit), service: InvestigationPort=Depends(investigation_service)) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Query`, `router.get`, `service.camera_settings`

### camera_settings

[Исходник: api/wms_api_server/app/modules/inventory/api/investigation_routes.py:30](../../../api/wms_api_server/app/modules/inventory/api/investigation_routes.py#L30)

```python
camera_settings(self, warehouse: int, cell: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### read

[Исходник: api/wms_api_server/app/modules/inventory/api/investigation_routes.py:31](../../../api/wms_api_server/app/modules/inventory/api/investigation_routes.py#L31)

```python
read(self, short_id: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### review

[Исходник: api/wms_api_server/app/modules/inventory/api/investigation_routes.py:32](../../../api/wms_api_server/app/modules/inventory/api/investigation_routes.py#L32)

```python
review(self, short_id: int, request: InvestigationInput, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### configure

[Исходник: api/wms_api_server/app/modules/inventory/api/investigation_routes.py:33](../../../api/wms_api_server/app/modules/inventory/api/investigation_routes.py#L33)

```python
configure(self, request: CameraInput, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### minimax_view

[Исходник: api/wms_api_server/app/modules/inventory/api/minimax_routes.py:9](../../../api/wms_api_server/app/modules/inventory/api/minimax_routes.py#L9)

```python
minimax_view() -> MinimaxUser
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### minimax_edit

[Исходник: api/wms_api_server/app/modules/inventory/api/minimax_routes.py:10](../../../api/wms_api_server/app/modules/inventory/api/minimax_routes.py#L10)

```python
minimax_edit() -> MinimaxUser
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### minimax_service

[Исходник: api/wms_api_server/app/modules/inventory/api/minimax_routes.py:11](../../../api/wms_api_server/app/modules/inventory/api/minimax_routes.py#L11)

```python
minimax_service() -> MinimaxPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### preview

[Исходник: api/wms_api_server/app/modules/inventory/api/minimax_routes.py:14](../../../api/wms_api_server/app/modules/inventory/api/minimax_routes.py#L14)

```python
preview(warehouse: int=Path(gt=0), user: MinimaxUser=Depends(minimax_view), service: MinimaxPort=Depends(minimax_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Path`, `router.get`, `service.preview`

### reconcile

[Исходник: api/wms_api_server/app/modules/inventory/api/minimax_routes.py:18](../../../api/wms_api_server/app/modules/inventory/api/minimax_routes.py#L18)

```python
reconcile(warehouse: int=Path(gt=0), user: MinimaxUser=Depends(minimax_edit), service: MinimaxPort=Depends(minimax_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Path`, `router.post`, `service.reconcile`

### preview

[Исходник: api/wms_api_server/app/modules/inventory/api/minimax_routes.py:7](../../../api/wms_api_server/app/modules/inventory/api/minimax_routes.py#L7)

```python
preview(self, warehouse: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### reconcile

[Исходник: api/wms_api_server/app/modules/inventory/api/minimax_routes.py:8](../../../api/wms_api_server/app/modules/inventory/api/minimax_routes.py#L8)

```python
reconcile(self, warehouse: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### outgoing_quality_service

[Исходник: api/wms_api_server/app/modules/inventory/api/outgoing_quality_routes.py:20](../../../api/wms_api_server/app/modules/inventory/api/outgoing_quality_routes.py#L20)

```python
outgoing_quality_service() -> QualityPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### status

[Исходник: api/wms_api_server/app/modules/inventory/api/outgoing_quality_routes.py:49](../../../api/wms_api_server/app/modules/inventory/api/outgoing_quality_routes.py#L49)

```python
status(identifier: str=Path(min_length=1, max_length=150), user: AdminUser=Depends(require_permission('outgoing_pallet_check')), service: QualityPort=Depends(outgoing_quality_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Path`, `require_permission`, `router.get`, `service.status`

### control_label

[Исходник: api/wms_api_server/app/modules/inventory/api/outgoing_quality_routes.py:56](../../../api/wms_api_server/app/modules/inventory/api/outgoing_quality_routes.py#L56)

```python
control_label(identifier: str=Path(min_length=1, max_length=150), expected_signature: str | None=Query(default=None, pattern='^[A-F0-9]{64}$'), user: AdminUser=Depends(require_permission('outgoing_pallet_check')), service: QualityPort=Depends(outgoing_quality_service)) -> Response
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Path`, `Query`, `Response`, `quality_label_html`, `require_permission`, `router.get`, `service.status`, `snapshot.get`, `snapshot.get('weight_exemption', {}).get`

### scan

[Исходник: api/wms_api_server/app/modules/inventory/api/outgoing_quality_routes.py:71](../../../api/wms_api_server/app/modules/inventory/api/outgoing_quality_routes.py#L71)

```python
scan(body: ScanRequest, identifier: str=Path(min_length=1, max_length=150), user: AdminUser=Depends(require_permission('outgoing_pallet_check')), service: QualityPort=Depends(outgoing_quality_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Path`, `body.model_dump`, `require_permission`, `router.post`, `service.check`

### weight

[Исходник: api/wms_api_server/app/modules/inventory/api/outgoing_quality_routes.py:78](../../../api/wms_api_server/app/modules/inventory/api/outgoing_quality_routes.py#L78)

```python
weight(body: WeightRequest, identifier: str=Path(min_length=1, max_length=150), user: AdminUser=Depends(require_permission('outgoing_pallet_check')), service: QualityPort=Depends(outgoing_quality_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Path`, `body.model_dump`, `require_permission`, `router.post`, `service.check`

### assign_plan

[Исходник: api/wms_api_server/app/modules/inventory/api/outgoing_quality_routes.py:85](../../../api/wms_api_server/app/modules/inventory/api/outgoing_quality_routes.py#L85)

```python
assign_plan(body: QualityRequest, identifier: str=Path(min_length=1, max_length=150), user: AdminUser=Depends(require_permission('outgoing_pallet_check')), service: QualityPort=Depends(outgoing_quality_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Path`, `body.model_dump`, `require_permission`, `router.post`, `service.check`

### final_weight

[Исходник: api/wms_api_server/app/modules/inventory/api/outgoing_quality_routes.py:96](../../../api/wms_api_server/app/modules/inventory/api/outgoing_quality_routes.py#L96)

```python
final_weight(body: FinalWeightRequest, identifier: str=Path(min_length=1, max_length=150), user: AdminUser=Depends(require_permission('outgoing_pallet_check')), service: QualityPort=Depends(outgoing_quality_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Path`, `body.model_dump`, `require_permission`, `router.post`, `service.check_final`

### final_readings

[Исходник: api/wms_api_server/app/modules/inventory/api/outgoing_quality_routes.py:103](../../../api/wms_api_server/app/modules/inventory/api/outgoing_quality_routes.py#L103)

```python
final_readings(identifier: str=Path(min_length=1, max_length=150), user: AdminUser=Depends(require_permission('outgoing_pallet_check')), service: QualityPort=Depends(outgoing_quality_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Path`, `require_permission`, `router.get`, `service.final_readings`

### status

[Исходник: api/wms_api_server/app/modules/inventory/api/outgoing_quality_routes.py:11](../../../api/wms_api_server/app/modules/inventory/api/outgoing_quality_routes.py#L11)

```python
status(self, identifier: str, actor: str | None=None) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### check

[Исходник: api/wms_api_server/app/modules/inventory/api/outgoing_quality_routes.py:12](../../../api/wms_api_server/app/modules/inventory/api/outgoing_quality_routes.py#L12)

```python
check(self, identifier: str, body: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### check_final

[Исходник: api/wms_api_server/app/modules/inventory/api/outgoing_quality_routes.py:13](../../../api/wms_api_server/app/modules/inventory/api/outgoing_quality_routes.py#L13)

```python
check_final(self, identifier: str, body: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### final_readings

[Исходник: api/wms_api_server/app/modules/inventory/api/outgoing_quality_routes.py:14](../../../api/wms_api_server/app/modules/inventory/api/outgoing_quality_routes.py#L14)

```python
final_readings(self, identifier: str, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### failure

[Исходник: api/wms_api_server/app/modules/inventory/api/pallet_floor_routes.py:20](../../../api/wms_api_server/app/modules/inventory/api/pallet_floor_routes.py#L20)

```python
failure(exc: StockPostingError) -> HTTPException
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `str`

### read

[Исходник: api/wms_api_server/app/modules/inventory/api/pallet_floor_routes.py:27](../../../api/wms_api_server/app/modules/inventory/api/pallet_floor_routes.py#L27)

```python
read(identifier: str=Query(min_length=1, max_length=200), user: AdminUser=Depends(require_permission('stock_posting_shipping')), service: PalletFloorPort=Depends(pallet_floor_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Query`, `failure`, `require_permission`, `router.get`, `service.read`

### confirm

[Исходник: api/wms_api_server/app/modules/inventory/api/pallet_floor_routes.py:34](../../../api/wms_api_server/app/modules/inventory/api/pallet_floor_routes.py#L34)

```python
confirm(body: PalletFloorRequest, user: AdminUser=Depends(require_permission('stock_posting_shipping')), service: PalletFloorPort=Depends(pallet_floor_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `body.model_dump`, `failure`, `require_permission`, `router.post`, `service.confirm`, `str`, `values.items`

### partial_layout_service

[Исходник: api/wms_api_server/app/modules/inventory/api/partial_shipment_routes.py:15](../../../api/wms_api_server/app/modules/inventory/api/partial_shipment_routes.py#L15)

```python
partial_layout_service() -> PartialLayoutPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### preview

[Исходник: api/wms_api_server/app/modules/inventory/api/partial_shipment_routes.py:31](../../../api/wms_api_server/app/modules/inventory/api/partial_shipment_routes.py#L31)

```python
preview(task_id: int, pallet_identifier: str=Query(min_length=1, max_length=150), _user: AdminUser=Depends(require_permission('case_pick_short_approve')), service: PartialLayoutPort=Depends(partial_layout_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Query`, `require_permission`, `router.get`, `service.preview`, `str`

### prepare

[Исходник: api/wms_api_server/app/modules/inventory/api/partial_shipment_routes.py:43](../../../api/wms_api_server/app/modules/inventory/api/partial_shipment_routes.py#L43)

```python
prepare(task_id: int, body: PartialLayoutRequest, user: AdminUser=Depends(require_permission('case_pick_short_approve')), service: PartialLayoutPort=Depends(partial_layout_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `body.model_dump`, `require_permission`, `router.post`, `service.prepare`, `str`

### preview

[Исходник: api/wms_api_server/app/modules/inventory/api/partial_shipment_routes.py:8](../../../api/wms_api_server/app/modules/inventory/api/partial_shipment_routes.py#L8)

```python
preview(self, task_id: int, identifier: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### prepare

[Исходник: api/wms_api_server/app/modules/inventory/api/partial_shipment_routes.py:9](../../../api/wms_api_server/app/modules/inventory/api/partial_shipment_routes.py#L9)

```python
prepare(self, task_id: int, body: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### pool_view

[Исходник: api/wms_api_server/app/modules/inventory/api/pool_routes.py:13](../../../api/wms_api_server/app/modules/inventory/api/pool_routes.py#L13)

```python
pool_view() -> PoolUser
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### pool_edit

[Исходник: api/wms_api_server/app/modules/inventory/api/pool_routes.py:16](../../../api/wms_api_server/app/modules/inventory/api/pool_routes.py#L16)

```python
pool_edit() -> PoolUser
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### pool_service

[Исходник: api/wms_api_server/app/modules/inventory/api/pool_routes.py:19](../../../api/wms_api_server/app/modules/inventory/api/pool_routes.py#L19)

```python
pool_service() -> PoolPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### preview

[Исходник: api/wms_api_server/app/modules/inventory/api/pool_routes.py:29](../../../api/wms_api_server/app/modules/inventory/api/pool_routes.py#L29)

```python
preview(warehouse: int=Path(gt=0), article: str=Path(min_length=1, max_length=160), user: PoolUser=Depends(pool_view), service: PoolPort=Depends(pool_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Path`, `router.get`, `service.preview`

### allocate

[Исходник: api/wms_api_server/app/modules/inventory/api/pool_routes.py:34](../../../api/wms_api_server/app/modules/inventory/api/pool_routes.py#L34)

```python
allocate(request: PoolCommandInput, warehouse: int=Path(gt=0), article: str=Path(min_length=1, max_length=160), user: PoolUser=Depends(pool_edit), service: PoolPort=Depends(pool_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Path`, `router.post`, `service.allocate`

### preview

[Исходник: api/wms_api_server/app/modules/inventory/api/pool_routes.py:10](../../../api/wms_api_server/app/modules/inventory/api/pool_routes.py#L10)

```python
preview(self, warehouse: int, article: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### allocate

[Исходник: api/wms_api_server/app/modules/inventory/api/pool_routes.py:11](../../../api/wms_api_server/app/modules/inventory/api/pool_routes.py#L11)

```python
allocate(self, warehouse: int, article: str, operation_id: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### read

[Исходник: api/wms_api_server/app/modules/inventory/api/quality_scope_routes.py:26](../../../api/wms_api_server/app/modules/inventory/api/quality_scope_routes.py#L26)

```python
read(warehouse: int=Path(gt=0), store_addr: str=Query(default='*', min_length=1, max_length=255), place_category: Literal['ANY', 'STOCK', 'CASE']='ANY', user: AdminUser=Depends(require_permission('warehouse_settings_view')), service: QualityScopePort=Depends(quality_scope_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Path`, `Query`, `require_permission`, `router.get`, `service.read`, `str`

### save

[Исходник: api/wms_api_server/app/modules/inventory/api/quality_scope_routes.py:34](../../../api/wms_api_server/app/modules/inventory/api/quality_scope_routes.py#L34)

```python
save(body: QualityScopeInput, warehouse: int=Path(gt=0), user: AdminUser=Depends(require_permission('warehouse_settings_edit')), service: QualityScopePort=Depends(quality_scope_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Path`, `body.model_dump`, `require_permission`, `router.post`, `service.save`, `str`

### save

[Исходник: api/wms_api_server/app/modules/inventory/api/range_proposal_routes.py:29](../../../api/wms_api_server/app/modules/inventory/api/range_proposal_routes.py#L29)

```python
save(request: SaveRangeProposalInput, ware_id: int=Path(gt=0), article: str=Path(min_length=1, max_length=40), user: AdminUser=Depends(require_permission('pick_topology_edit')), service: RangeProposalPort=Depends(range_proposal_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Path`, `RangeDraft`, `article.strip`, `article.strip().upper`, `require_permission`, `router.post`, `row.model_dump`, `service.save`, `str`

### get

[Исходник: api/wms_api_server/app/modules/inventory/api/range_proposal_routes.py:39](../../../api/wms_api_server/app/modules/inventory/api/range_proposal_routes.py#L39)

```python
get(proposal_id: str=Path(min_length=8, max_length=100), ware_id: int=Path(gt=0), article: str=Path(min_length=1, max_length=40), user: AdminUser=Depends(require_permission('pick_topology_view')), service: RangeProposalPort=Depends(range_proposal_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Path`, `article.strip`, `article.strip().upper`, `require_permission`, `router.get`, `service.get`, `str`

### cancel

[Исходник: api/wms_api_server/app/modules/inventory/api/range_proposal_routes.py:46](../../../api/wms_api_server/app/modules/inventory/api/range_proposal_routes.py#L46)

```python
cancel(request: CancelRangeProposalInput, proposal_id: str=Path(min_length=8, max_length=100), ware_id: int=Path(gt=0), article: str=Path(min_length=1, max_length=40), user: AdminUser=Depends(require_permission('pick_topology_edit')), service: RangeProposalPort=Depends(range_proposal_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Path`, `article.strip`, `article.strip().upper`, `require_permission`, `router.post`, `service.cancel`, `str`

### approve

[Исходник: api/wms_api_server/app/modules/inventory/api/range_proposal_routes.py:54](../../../api/wms_api_server/app/modules/inventory/api/range_proposal_routes.py#L54)

```python
approve(request: ApproveRangeProposalInput, proposal_id: str=Path(min_length=8, max_length=100), ware_id: int=Path(gt=0), article: str=Path(min_length=1, max_length=40), user: AdminUser=Depends(require_permission('pick_topology_edit')), service: RangeProposalPort=Depends(range_proposal_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Path`, `article.strip`, `article.strip().upper`, `require_permission`, `router.post`, `service.approve`, `str`

### close_drain

[Исходник: api/wms_api_server/app/modules/inventory/api/range_proposal_routes.py:63](../../../api/wms_api_server/app/modules/inventory/api/range_proposal_routes.py#L63)

```python
close_drain(request: CloseRangeDrainInput, ware_id: int=Path(gt=0), article: str=Path(min_length=1, max_length=40), user: AdminUser=Depends(require_permission('pick_topology_edit')), service: RangeProposalPort=Depends(range_proposal_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Path`, `article.strip`, `article.strip().upper`, `require_permission`, `router.post`, `service.close`, `str`

### receiving_service

[Исходник: api/wms_api_server/app/modules/inventory/api/receiving_routes.py:61](../../../api/wms_api_server/app/modules/inventory/api/receiving_routes.py#L61)

```python
receiving_service() -> Receiving
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### label_service

[Исходник: api/wms_api_server/app/modules/inventory/api/receiving_routes.py:65](../../../api/wms_api_server/app/modules/inventory/api/receiving_routes.py#L65)

```python
label_service() -> ReceiptLabels
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### configuration_service

[Исходник: api/wms_api_server/app/modules/inventory/api/receiving_routes.py:69](../../../api/wms_api_server/app/modules/inventory/api/receiving_routes.py#L69)

```python
configuration_service() -> ReceiptConfiguration
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### reconciliation_service

[Исходник: api/wms_api_server/app/modules/inventory/api/receiving_routes.py:73](../../../api/wms_api_server/app/modules/inventory/api/receiving_routes.py#L73)

```python
reconciliation_service() -> ReceiptReconciliation
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### query_service

[Исходник: api/wms_api_server/app/modules/inventory/api/receiving_routes.py:77](../../../api/wms_api_server/app/modules/inventory/api/receiving_routes.py#L77)

```python
query_service() -> ReceivingQueries
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### pallet_composition

[Исходник: api/wms_api_server/app/modules/inventory/api/receiving_routes.py:82](../../../api/wms_api_server/app/modules/inventory/api/receiving_routes.py#L82)

```python
pallet_composition(pallet: str, after: str=Query('', max_length=64), limit: int=Query(50, ge=1, le=100), expected_signature: str | None=Query(None, min_length=64, max_length=64), user: AdminUser=Depends(require_permission('traceability_view')), service: ReceivingQueries=Depends(query_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Query`, `require_permission`, `router.get`, `service.composition`, `str`

### replan_putaway

[Исходник: api/wms_api_server/app/modules/inventory/api/receiving_routes.py:157](../../../api/wms_api_server/app/modules/inventory/api/receiving_routes.py#L157)

```python
replan_putaway(task_id: int, body: ReplanPutaway, user: AdminUser=Depends(require_permission('warehouse_task_assign')), service: Receiving=Depends(receiving_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `body.model_dump`, `require_permission`, `router.post`, `service.replan`, `str`

### issue_label

[Исходник: api/wms_api_server/app/modules/inventory/api/receiving_routes.py:168](../../../api/wms_api_server/app/modules/inventory/api/receiving_routes.py#L168)

```python
issue_label(order_id: str, body: LabelIssue, user: AdminUser=Depends(require_permission('warehouse_receipt_confirm')), service: ReceiptLabels=Depends(label_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `body.model_dump`, `require_permission`, `router.post`, `service.issue`, `str`

### read_label

[Исходник: api/wms_api_server/app/modules/inventory/api/receiving_routes.py:179](../../../api/wms_api_server/app/modules/inventory/api/receiving_routes.py#L179)

```python
read_label(label_id: str, format: Literal['html', 'zpl']='html', dpi: int=Query(203, ge=203, le=600), user: AdminUser=Depends(require_permission('warehouse_receipt_confirm')), service: ReceiptLabels=Depends(label_service)) -> Response
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Query`, `Response`, `require_permission`, `router.get`, `service.document`, `str`

### confirm_label

[Исходник: api/wms_api_server/app/modules/inventory/api/receiving_routes.py:191](../../../api/wms_api_server/app/modules/inventory/api/receiving_routes.py#L191)

```python
confirm_label(label_id: str, body: LabelScan, user: AdminUser=Depends(require_permission('warehouse_receipt_confirm')), service: ReceiptLabels=Depends(label_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.post`, `service.confirm`, `str`

### get_settings

[Исходник: api/wms_api_server/app/modules/inventory/api/receiving_routes.py:202](../../../api/wms_api_server/app/modules/inventory/api/receiving_routes.py#L202)

```python
get_settings(warehouse: int, user: AdminUser=Depends(require_permission('warehouse_settings_view')), service: ReceiptConfiguration=Depends(configuration_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `require_permission`, `router.get`, `service.get`

### save_settings

[Исходник: api/wms_api_server/app/modules/inventory/api/receiving_routes.py:208](../../../api/wms_api_server/app/modules/inventory/api/receiving_routes.py#L208)

```python
save_settings(warehouse: int, body: WarehouseReceiptSettings, user: AdminUser=Depends(require_permission('warehouse_settings_edit')), service: ReceiptConfiguration=Depends(configuration_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `body.model_dump`, `metadata.pop`, `require_permission`, `router.put`, `service.save`, `str`

### save_sku_rule

[Исходник: api/wms_api_server/app/modules/inventory/api/receiving_routes.py:221](../../../api/wms_api_server/app/modules/inventory/api/receiving_routes.py#L221)

```python
save_sku_rule(warehouse: int, articul: str, body: SkuPlacementRule, user: AdminUser=Depends(require_permission('warehouse_settings_edit')), service: ReceiptConfiguration=Depends(configuration_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `body.model_dump`, `require_permission`, `router.put`, `service.sku_rule`, `str`

### read_sku_rule

[Исходник: api/wms_api_server/app/modules/inventory/api/receiving_routes.py:230](../../../api/wms_api_server/app/modules/inventory/api/receiving_routes.py#L230)

```python
read_sku_rule(warehouse: int, articul: str, user: AdminUser=Depends(require_permission('warehouse_settings_view')), service: ReceiptConfiguration=Depends(configuration_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `require_permission`, `router.get`, `service.read_rule`

### read_cell_rule

[Исходник: api/wms_api_server/app/modules/inventory/api/receiving_routes.py:236](../../../api/wms_api_server/app/modules/inventory/api/receiving_routes.py#L236)

```python
read_cell_rule(warehouse: int, cell: str, user: AdminUser=Depends(require_permission('warehouse_settings_view')), service: ReceiptConfiguration=Depends(configuration_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `require_permission`, `router.get`, `service.read_rule`

### save_cell_rule

[Исходник: api/wms_api_server/app/modules/inventory/api/receiving_routes.py:242](../../../api/wms_api_server/app/modules/inventory/api/receiving_routes.py#L242)

```python
save_cell_rule(warehouse: int, cell: str, body: CellPlacementRule, user: AdminUser=Depends(require_permission('warehouse_settings_edit')), service: ReceiptConfiguration=Depends(configuration_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `body.model_dump`, `require_permission`, `router.put`, `service.cell_rule`, `str`

### close_supply

[Исходник: api/wms_api_server/app/modules/inventory/api/receiving_routes.py:251](../../../api/wms_api_server/app/modules/inventory/api/receiving_routes.py#L251)

```python
close_supply(order_id: str, body: CloseSupply, user: AdminUser=Depends(require_permission('warehouse_receipt_reconcile')), service: ReceiptReconciliation=Depends(reconciliation_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.post`, `service.close`, `str`

### reopen_supply

[Исходник: api/wms_api_server/app/modules/inventory/api/receiving_routes.py:260](../../../api/wms_api_server/app/modules/inventory/api/receiving_routes.py#L260)

```python
reopen_supply(order_id: str, body: CloseSupply, user: AdminUser=Depends(require_permission('warehouse_receipt_reconcile')), service: ReceiptReconciliation=Depends(reconciliation_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.post`, `service.reopen`, `str`

### receive_pallet

[Исходник: api/wms_api_server/app/modules/inventory/api/receiving_routes.py:269](../../../api/wms_api_server/app/modules/inventory/api/receiving_routes.py#L269)

```python
receive_pallet(order_id: str, request: PalletReceipt, user: AdminUser=Depends(require_permission('warehouse_receipt_confirm')), service: Receiving=Depends(receiving_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `request.model_dump`, `require_permission`, `router.post`, `service.receive`, `str`

### complete_putaway

[Исходник: api/wms_api_server/app/modules/inventory/api/receiving_routes.py:281](../../../api/wms_api_server/app/modules/inventory/api/receiving_routes.py#L281)

```python
complete_putaway(task_id: int, request: PutawayConfirmation, user: AdminUser=Depends(require_permission('warehouse_task_execute')), service: Receiving=Depends(receiving_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `request.model_dump`, `require_permission`, `router.post`, `service.complete`, `str`

### normalize_sscc

[Исходник: api/wms_api_server/app/modules/inventory/api/receiving_routes.py:42](../../../api/wms_api_server/app/modules/inventory/api/receiving_routes.py#L42)

```python
normalize_sscc(cls, value: object) -> object
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `field_validator`, `normalize_receipt_identifier`

### same_identifier

[Исходник: api/wms_api_server/app/modules/inventory/api/receiving_routes.py:48](../../../api/wms_api_server/app/modules/inventory/api/receiving_routes.py#L48)

```python
same_identifier(cls, value: object) -> object
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `isinstance`, `model_validator`, `normalize_receipt_identifier`

### ordered_temperature

[Исходник: api/wms_api_server/app/modules/inventory/api/receiving_routes.py:125](../../../api/wms_api_server/app/modules/inventory/api/receiving_routes.py#L125)

```python
ordered_temperature(self) -> 'TemperatureRule'
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `model_validator`

### inventory_task_view

[Исходник: api/wms_api_server/app/modules/inventory/api/recovery_routes.py:16](../../../api/wms_api_server/app/modules/inventory/api/recovery_routes.py#L16)

```python
inventory_task_view() -> TaskUser
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### inventory_task_execute

[Исходник: api/wms_api_server/app/modules/inventory/api/recovery_routes.py:20](../../../api/wms_api_server/app/modules/inventory/api/recovery_routes.py#L20)

```python
inventory_task_execute() -> TaskUser
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### recovery_view

[Исходник: api/wms_api_server/app/modules/inventory/api/recovery_routes.py:24](../../../api/wms_api_server/app/modules/inventory/api/recovery_routes.py#L24)

```python
recovery_view() -> TaskUser
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### recovery_tasks_service

[Исходник: api/wms_api_server/app/modules/inventory/api/recovery_routes.py:28](../../../api/wms_api_server/app/modules/inventory/api/recovery_routes.py#L28)

```python
recovery_tasks_service() -> RecoveryPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### list_inventory_tasks

[Исходник: api/wms_api_server/app/modules/inventory/api/recovery_routes.py:36](../../../api/wms_api_server/app/modules/inventory/api/recovery_routes.py#L36)

```python
list_inventory_tasks(limit: int=Query(default=50, ge=1, le=100), task_id: int | None=Query(default=None, gt=0), user: TaskUser=Depends(inventory_task_view), service: RecoveryPort=Depends(recovery_tasks_service)) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Query`, `router.get`, `service.list_inventory`

### claim_inventory_task

[Исходник: api/wms_api_server/app/modules/inventory/api/recovery_routes.py:46](../../../api/wms_api_server/app/modules/inventory/api/recovery_routes.py#L46)

```python
claim_inventory_task(task_id: int, user: TaskUser=Depends(inventory_task_execute), service: RecoveryPort=Depends(recovery_tasks_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `router.post`, `service.claim_inventory`

### list_recovery_shorts

[Исходник: api/wms_api_server/app/modules/inventory/api/recovery_routes.py:55](../../../api/wms_api_server/app/modules/inventory/api/recovery_routes.py#L55)

```python
list_recovery_shorts(limit: int=Query(default=50, ge=1, le=100), user: TaskUser=Depends(recovery_view), service: RecoveryPort=Depends(recovery_tasks_service)) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Query`, `router.get`, `service.list_recovery`

### list_inventory

[Исходник: api/wms_api_server/app/modules/inventory/api/recovery_routes.py:7](../../../api/wms_api_server/app/modules/inventory/api/recovery_routes.py#L7)

```python
list_inventory(self, limit: int, task_id: int | None=None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### list_recovery

[Исходник: api/wms_api_server/app/modules/inventory/api/recovery_routes.py:8](../../../api/wms_api_server/app/modules/inventory/api/recovery_routes.py#L8)

```python
list_recovery(self, limit: int) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### claim_inventory

[Исходник: api/wms_api_server/app/modules/inventory/api/recovery_routes.py:9](../../../api/wms_api_server/app/modules/inventory/api/recovery_routes.py#L9)

```python
claim_inventory(self, task_id: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### replenishment_view

[Исходник: api/wms_api_server/app/modules/inventory/api/replenishment_progress_routes.py:8](../../../api/wms_api_server/app/modules/inventory/api/replenishment_progress_routes.py#L8)

```python
replenishment_view() -> object
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### replenishment_progress_service

[Исходник: api/wms_api_server/app/modules/inventory/api/replenishment_progress_routes.py:11](../../../api/wms_api_server/app/modules/inventory/api/replenishment_progress_routes.py#L11)

```python
replenishment_progress_service() -> ReplenishmentProgressPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### replenishment_progress

[Исходник: api/wms_api_server/app/modules/inventory/api/replenishment_progress_routes.py:17](../../../api/wms_api_server/app/modules/inventory/api/replenishment_progress_routes.py#L17)

```python
replenishment_progress(wave_id: int=Query(gt=0), limit: int=Query(default=50, ge=1, le=100), user: object=Depends(replenishment_view), service: ReplenishmentProgressPort=Depends(replenishment_progress_service)) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Query`, `router.get`, `service.list_rows`

### list_rows

[Исходник: api/wms_api_server/app/modules/inventory/api/replenishment_progress_routes.py:6](../../../api/wms_api_server/app/modules/inventory/api/replenishment_progress_routes.py#L6)

```python
list_rows(self, wave_id: int, limit: int) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### failure

[Исходник: api/wms_api_server/app/modules/inventory/api/return_disposal_routes.py:29](../../../api/wms_api_server/app/modules/inventory/api/return_disposal_routes.py#L29)

```python
failure(exc: StoreReturnReceiveError, op: str | None=None) -> HTTPException
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `str`

### report

[Исходник: api/wms_api_server/app/modules/inventory/api/return_disposal_routes.py:33](../../../api/wms_api_server/app/modules/inventory/api/return_disposal_routes.py#L33)

```python
report(body: Report, user: AdminUser=Depends(require_permission('warehouse_return_dispatch')), service: ReturnDisposalPort=Depends(return_disposal_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `failure`, `require_permission`, `router.post`, `service.report`

### dispose

[Исходник: api/wms_api_server/app/modules/inventory/api/return_disposal_routes.py:38](../../../api/wms_api_server/app/modules/inventory/api/return_disposal_routes.py#L38)

```python
dispose(body: Dispose, user: AdminUser=Depends(require_permission('store_return_approve')), service: ReturnDisposalPort=Depends(return_disposal_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `failure`, `item.model_dump`, `require_permission`, `router.post`, `service.dispose`, `str`

### pending

[Исходник: api/wms_api_server/app/modules/inventory/api/return_disposal_routes.py:44](../../../api/wms_api_server/app/modules/inventory/api/return_disposal_routes.py#L44)

```python
pending(ware_id: int, user: AdminUser=Depends(require_permission('warehouse_return_dispatch')), service: ReturnDisposalPort=Depends(return_disposal_service)) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `failure`, `require_permission`, `router.get`, `service.pending`

### targets

[Исходник: api/wms_api_server/app/modules/inventory/api/return_putaway_routes.py:26](../../../api/wms_api_server/app/modules/inventory/api/return_putaway_routes.py#L26)

```python
targets(ware_id: int, body: ReturnTargets, user: AdminUser=Depends(require_permission('warehouse_settings_edit')), service: ReturnPutawayPort=Depends(return_putaway_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `failure`, `require_permission`, `router.put`, `service.configure`

### pending

[Исходник: api/wms_api_server/app/modules/inventory/api/return_putaway_routes.py:35](../../../api/wms_api_server/app/modules/inventory/api/return_putaway_routes.py#L35)

```python
pending(ware_id: int, receipt_operation_id: str | None=Query(default=None, min_length=1, max_length=100), user: AdminUser=Depends(require_permission('warehouse_return_place')), service: ReturnPutawayPort=Depends(return_putaway_service)) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Query`, `failure`, `require_permission`, `router.get`, `service.pending`

### plan

[Исходник: api/wms_api_server/app/modules/inventory/api/return_putaway_routes.py:44](../../../api/wms_api_server/app/modules/inventory/api/return_putaway_routes.py#L44)

```python
plan(body: ReturnTaskPlan, user: AdminUser=Depends(require_permission('warehouse_return_place')), service: ReturnPutawayPort=Depends(return_putaway_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `failure`, `require_permission`, `router.post`, `service.plan`

### preview

[Исходник: api/wms_api_server/app/modules/inventory/api/slotting_routes.py:38](../../../api/wms_api_server/app/modules/inventory/api/slotting_routes.py#L38)

```python
preview(request: SlottingScenarioInput, ware_id: int=Path(gt=0), article: str=Path(min_length=1, max_length=40), user: AdminUser=Depends(require_permission('pick_topology_view')), service: SlottingDemandPort=Depends(slotting_demand_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Path`, `article.strip`, `article.strip().upper`, `require_permission`, `router.post`, `row.model_dump`, `service.preview`, `str`

### bounded_period

[Исходник: api/wms_api_server/app/modules/inventory/api/slotting_routes.py:26](../../../api/wms_api_server/app/modules/inventory/api/slotting_routes.py#L26)

```python
bounded_period(self) -> 'SlottingScenarioInput'
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `len`, `model_validator`

### source_view_permission

[Исходник: api/wms_api_server/app/modules/inventory/api/source_routes.py:17](../../../api/wms_api_server/app/modules/inventory/api/source_routes.py#L17)

```python
source_view_permission() -> object
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### source_availability_service

[Исходник: api/wms_api_server/app/modules/inventory/api/source_routes.py:21](../../../api/wms_api_server/app/modules/inventory/api/source_routes.py#L21)

```python
source_availability_service() -> SourceAvailabilityPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### source_availability

[Исходник: api/wms_api_server/app/modules/inventory/api/source_routes.py:26](../../../api/wms_api_server/app/modules/inventory/api/source_routes.py#L26)

```python
source_availability(warehouse: int=Query(gt=0), article: str=Query(min_length=1, max_length=160), quantity: Decimal=Query(default=Decimal('0'), ge=0, max_digits=27, decimal_places=9), purpose: Literal['ALLOCATE', 'PICK', 'REPLENISH']='REPLENISH', min_days: int | None=Query(default=None, ge=0), min_percent: Decimal | None=Query(default=None, ge=0, le=100), after_uid: str=Query(default='', max_length=200), after_cell: str=Query(default='', max_length=60), limit: int=Query(default=50, ge=1, le=100), viewer: object=Depends(source_view_permission), service: SourceAvailabilityPort=Depends(source_availability_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `Depends`, `HTTPException`, `Query`, `bool`, `router.get`, `service.list_sources`

### list_sources

[Исходник: api/wms_api_server/app/modules/inventory/api/source_routes.py:9](../../../api/wms_api_server/app/modules/inventory/api/source_routes.py#L9)

```python
list_sources(self, warehouse: int, article: str, quantity: Decimal, purpose: str, min_days: int | None, min_percent: Decimal | None, after_uid: str, after_cell: str, limit: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### manual_stock_move_service

[Исходник: api/wms_api_server/app/modules/inventory/api/stock_command_routes.py:35](../../../api/wms_api_server/app/modules/inventory/api/stock_command_routes.py#L35)

```python
manual_stock_move_service() -> ManualStockMove
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### manual_move

[Исходник: api/wms_api_server/app/modules/inventory/api/stock_command_routes.py:40](../../../api/wms_api_server/app/modules/inventory/api/stock_command_routes.py#L40)

```python
manual_move(request: ManualMoveRequest, user: AdminUser=Depends(require_permission('stock_posting_manual_move')), service: ManualStockMove=Depends(manual_stock_move_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `StockLine`, `line.model_dump`, `require_permission`, `router.post`, `service.execute`, `str`, `tuple`

### set_compatibility

[Исходник: api/wms_api_server/app/modules/inventory/api/stock_command_routes.py:71](../../../api/wms_api_server/app/modules/inventory/api/stock_command_routes.py#L71)

```python
set_compatibility(request: CompatibilitySettingRequest, user: AdminUser=Depends(require_permission('stock_compatibility_admin')), service: StockCompatibilityPort=Depends(stock_compatibility_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.post`, `service.set_compatibility`, `str`

### compatibility_manual_move

[Исходник: api/wms_api_server/app/modules/inventory/api/stock_command_routes.py:82](../../../api/wms_api_server/app/modules/inventory/api/stock_command_routes.py#L82)

```python
compatibility_manual_move(request: ManualMoveRequest, user: AdminUser=Depends(require_permission('stock_posting_manual_move')), service: ManualStockMove=Depends(manual_stock_move_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `StockLine`, `line.model_dump`, `require_permission`, `router.post`, `service.execute`, `str`, `tuple`

### receipt_reverse_service

[Исходник: api/wms_api_server/app/modules/inventory/api/stock_command_routes.py:98](../../../api/wms_api_server/app/modules/inventory/api/stock_command_routes.py#L98)

```python
receipt_reverse_service() -> ReceiptReverse
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### reverse_receipt

[Исходник: api/wms_api_server/app/modules/inventory/api/stock_command_routes.py:109](../../../api/wms_api_server/app/modules/inventory/api/stock_command_routes.py#L109)

```python
reverse_receipt(document_id: int, request: ReceiptReverseRequest, user: AdminUser=Depends(require_permission('stock_receipt_reverse')), service: ReceiptReverse=Depends(receipt_reverse_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.post`, `service.execute`, `str`

### stock_queries_service

[Исходник: api/wms_api_server/app/modules/inventory/api/stock_routes.py:10](../../../api/wms_api_server/app/modules/inventory/api/stock_routes.py#L10)

```python
stock_queries_service() -> StockQueriesPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### status

[Исходник: api/wms_api_server/app/modules/inventory/api/stock_routes.py:15](../../../api/wms_api_server/app/modules/inventory/api/stock_routes.py#L15)

```python
status(user: AdminUser=Depends(require_permission(STOCK_RESERVATION_VIEW_PERMISSION)), service: StockQueriesPort=Depends(stock_queries_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `require_permission`, `router.get`, `service.status`

### operation

[Исходник: api/wms_api_server/app/modules/inventory/api/stock_routes.py:23](../../../api/wms_api_server/app/modules/inventory/api/stock_routes.py#L23)

```python
operation(operation_id: str=Path(min_length=1, max_length=100), user: AdminUser=Depends(require_permission(STOCK_RESERVATION_VIEW_PERMISSION)), service: StockQueriesPort=Depends(stock_queries_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Path`, `require_permission`, `router.get`, `service.operation`

### failure

[Исходник: api/wms_api_server/app/modules/inventory/api/store_return_receiving_routes.py:41](../../../api/wms_api_server/app/modules/inventory/api/store_return_receiving_routes.py#L41)

```python
failure(error: StoreReturnReceiveError) -> HTTPException
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `bool`, `str`

### configure

[Исходник: api/wms_api_server/app/modules/inventory/api/store_return_receiving_routes.py:47](../../../api/wms_api_server/app/modules/inventory/api/store_return_receiving_routes.py#L47)

```python
configure(ware_id: int, body: ReturnWarePolicy, user: AdminUser=Depends(require_permission('warehouse_settings_edit')), service: StoreReturnReceivePort=Depends(store_return_receive_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `failure`, `require_permission`, `router.put`, `service.configure`

### policy

[Исходник: api/wms_api_server/app/modules/inventory/api/store_return_receiving_routes.py:56](../../../api/wms_api_server/app/modules/inventory/api/store_return_receiving_routes.py#L56)

```python
policy(ware_id: int, user: AdminUser=Depends(require_permission('warehouse_settings_edit')), service: StoreReturnReceivePort=Depends(store_return_receive_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `failure`, `require_permission`, `router.get`, `service.policy`

### pending

[Исходник: api/wms_api_server/app/modules/inventory/api/store_return_receiving_routes.py:63](../../../api/wms_api_server/app/modules/inventory/api/store_return_receiving_routes.py#L63)

```python
pending(ware_id: int, user: AdminUser=Depends(require_permission('warehouse_return_receive')), service: StoreReturnReceivePort=Depends(store_return_receive_service)) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `failure`, `require_permission`, `router.get`, `service.pending`

### receive

[Исходник: api/wms_api_server/app/modules/inventory/api/store_return_receiving_routes.py:72](../../../api/wms_api_server/app/modules/inventory/api/store_return_receiving_routes.py#L72)

```python
receive(body: ReceiveStoreReturn, user: AdminUser=Depends(require_permission('warehouse_return_receive')), service: StoreReturnReceivePort=Depends(store_return_receive_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `body.model_dump`, `failure`, `require_permission`, `router.post`, `service.confirm`

### reuse_zone

[Исходник: api/wms_api_server/app/modules/inventory/api/store_return_receiving_routes.py:86](../../../api/wms_api_server/app/modules/inventory/api/store_return_receiving_routes.py#L86)

```python
reuse_zone(ware_id: int, body: ReuseZone, user: AdminUser=Depends(require_permission('warehouse_settings_edit')), service: StoreReturnReceivePort=Depends(store_return_receive_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `failure`, `require_permission`, `router.put`, `service.configure_reuse`

### pending_page

[Исходник: api/wms_api_server/app/modules/inventory/api/store_return_receiving_routes.py:91](../../../api/wms_api_server/app/modules/inventory/api/store_return_receiving_routes.py#L91)

```python
pending_page(ware_id: int, after: str=Query(default='', max_length=100), limit: int=Query(default=20, ge=1, le=100), user: AdminUser=Depends(require_permission('warehouse_return_receive')), service: StoreReturnReceivePort=Depends(store_return_receive_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Query`, `failure`, `require_permission`, `router.get`, `service.page`

### selected_source

[Исходник: api/wms_api_server/app/modules/inventory/api/store_return_receiving_routes.py:99](../../../api/wms_api_server/app/modules/inventory/api/store_return_receiving_routes.py#L99)

```python
selected_source(ware_id: int, pickup_id: str, user: AdminUser=Depends(require_permission('warehouse_return_receive')), service: StoreReturnReceivePort=Depends(store_return_receive_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `failure`, `len`, `require_permission`, `router.get`, `service.source`

### failure

[Исходник: api/wms_api_server/app/modules/inventory/api/supplier_handover_routes.py:23](../../../api/wms_api_server/app/modules/inventory/api/supplier_handover_routes.py#L23)

```python
failure(exc: StoreReturnReceiveError, op: str | None=None) -> HTTPException
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `str`

### record

[Исходник: api/wms_api_server/app/modules/inventory/api/supplier_handover_routes.py:27](../../../api/wms_api_server/app/modules/inventory/api/supplier_handover_routes.py#L27)

```python
record(body: Record, user: AdminUser=Depends(require_permission('warehouse_return_dispatch')), service: SupplierHandoverPort=Depends(supplier_handover_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `failure`, `require_permission`, `router.post`, `service.record`

### confirm

[Исходник: api/wms_api_server/app/modules/inventory/api/supplier_handover_routes.py:32](../../../api/wms_api_server/app/modules/inventory/api/supplier_handover_routes.py#L32)

```python
confirm(body: Confirm, user: AdminUser=Depends(require_permission('store_return_approve')), service: SupplierHandoverPort=Depends(supplier_handover_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `failure`, `require_permission`, `router.post`, `service.confirm`

### pending

[Исходник: api/wms_api_server/app/modules/inventory/api/supplier_handover_routes.py:37](../../../api/wms_api_server/app/modules/inventory/api/supplier_handover_routes.py#L37)

```python
pending(ware_id: int, user: AdminUser=Depends(require_permission('warehouse_return_dispatch')), service: SupplierHandoverPort=Depends(supplier_handover_service)) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `failure`, `require_permission`, `router.get`, `service.pending`

### failure

[Исходник: api/wms_api_server/app/modules/inventory/api/supplier_return_routes.py:17](../../../api/wms_api_server/app/modules/inventory/api/supplier_return_routes.py#L17)

```python
failure(exc: StoreReturnReceiveError, operation_id: str | None=None) -> HTTPException
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `str`

### prepare

[Исходник: api/wms_api_server/app/modules/inventory/api/supplier_return_routes.py:21](../../../api/wms_api_server/app/modules/inventory/api/supplier_return_routes.py#L21)

```python
prepare(body: Preparation, user: AdminUser=Depends(require_permission('store_return_approve')), service: SupplierReturnPort=Depends(supplier_return_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `failure`, `require_permission`, `router.post`, `service.prepare`

### pending

[Исходник: api/wms_api_server/app/modules/inventory/api/supplier_return_routes.py:26](../../../api/wms_api_server/app/modules/inventory/api/supplier_return_routes.py#L26)

```python
pending(ware_id: int, user: AdminUser=Depends(require_permission('warehouse_return_dispatch')), service: SupplierReturnPort=Depends(supplier_return_service)) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `failure`, `require_permission`, `router.get`, `service.pending`

### suppliers

[Исходник: api/wms_api_server/app/modules/inventory/api/supplier_return_routes.py:31](../../../api/wms_api_server/app/modules/inventory/api/supplier_return_routes.py#L31)

```python
suppliers(user: AdminUser=Depends(require_permission('store_return_approve')), service: SupplierReturnPort=Depends(supplier_return_service)) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `require_permission`, `router.get`, `service.suppliers`

### command

[Исходник: api/wms_api_server/app/modules/inventory/api/tare_assembly_routes.py:39](../../../api/wms_api_server/app/modules/inventory/api/tare_assembly_routes.py#L39)

```python
command(service: TarePort, kind: str, operation_id: str, source: dict[str, Any], metadata: dict[str, Any], user: AdminUser) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `service.post`, `str`

### book

[Исходник: api/wms_api_server/app/modules/inventory/api/tare_assembly_routes.py:44](../../../api/wms_api_server/app/modules/inventory/api/tare_assembly_routes.py#L44)

```python
book(body: Book, user: AdminUser=Depends(require_permission('tare_plan')), service: TarePort=Depends(tare_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `body.load_recovery.model_dump`, `command`, `require_permission`, `router.post`

### cancel

[Исходник: api/wms_api_server/app/modules/inventory/api/tare_assembly_routes.py:51](../../../api/wms_api_server/app/modules/inventory/api/tare_assembly_routes.py#L51)

```python
cancel(body: Cancel, user: AdminUser=Depends(require_permission('tare_plan')), service: TarePort=Depends(tare_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `command`, `require_permission`, `router.post`

### availability

[Исходник: api/wms_api_server/app/modules/inventory/api/tare_assembly_routes.py:55](../../../api/wms_api_server/app/modules/inventory/api/tare_assembly_routes.py#L55)

```python
availability(ware_id: int, user: AdminUser=Depends(require_permission('tare_view')), service: TareAssemblyPort=Depends(tare_assembly_service)) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.get`, `service.availability`, `str`

### bookings

[Исходник: api/wms_api_server/app/modules/inventory/api/tare_assembly_routes.py:60](../../../api/wms_api_server/app/modules/inventory/api/tare_assembly_routes.py#L60)

```python
bookings(ware_id: int, user: AdminUser=Depends(require_permission('tare_view')), service: TareAssemblyPort=Depends(tare_assembly_service)) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.get`, `service.bookings`, `str`

### catalog

[Исходник: api/wms_api_server/app/modules/inventory/api/tare_assembly_routes.py:65](../../../api/wms_api_server/app/modules/inventory/api/tare_assembly_routes.py#L65)

```python
catalog(user: AdminUser=Depends(require_permission('tare_view')), service: TareAssemblyPort=Depends(tare_assembly_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `require_permission`, `router.get`, `service.catalog`

### loaded_bookings

[Исходник: api/wms_api_server/app/modules/inventory/api/tare_assembly_routes.py:69](../../../api/wms_api_server/app/modules/inventory/api/tare_assembly_routes.py#L69)

```python
loaded_bookings(ware_id: int, task_id: int, user: AdminUser=Depends(require_permission('tare_view')), service: TareAssemblyPort=Depends(tare_assembly_service)) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.get`, `service.loaded_bookings`, `str`

### forecast

[Исходник: api/wms_api_server/app/modules/inventory/api/tare_assembly_routes.py:74](../../../api/wms_api_server/app/modules/inventory/api/tare_assembly_routes.py#L74)

```python
forecast(ware_id: int, wave_id: int, user: AdminUser=Depends(require_permission('tare_view')), service: TareAssemblyPort=Depends(tare_assembly_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.get`, `service.forecast`, `str`

### load_recovery_candidates

[Исходник: api/wms_api_server/app/modules/inventory/api/tare_assembly_routes.py:79](../../../api/wms_api_server/app/modules/inventory/api/tare_assembly_routes.py#L79)

```python
load_recovery_candidates(load_operation_id: str=Query(min_length=1, max_length=100), user: AdminUser=Depends(require_permission('tare_view')), service: TareAssemblyPort=Depends(tare_assembly_service)) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Query`, `require_permission`, `router.get`, `service.recovery_candidates`, `str`

### place_required

[Исходник: api/wms_api_server/app/modules/inventory/api/tare_assembly_routes.py:27](../../../api/wms_api_server/app/modules/inventory/api/tare_assembly_routes.py#L27)

```python
place_required(self) -> 'Book'
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `int`, `len`, `model_validator`, `self.place_id.encode`, `self.place_id.isascii`, `self.place_id.isdecimal`

### post

[Исходник: api/wms_api_server/app/modules/inventory/api/tare_loss_routes.py:38](../../../api/wms_api_server/app/modules/inventory/api/tare_loss_routes.py#L38)

```python
post(service: TarePort, body: Operation, kind: str, user: AdminUser) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `body.model_dump`, `isinstance`, `metadata.get`, `metadata.pop`, `service.post`, `str`

### report

[Исходник: api/wms_api_server/app/modules/inventory/api/tare_loss_routes.py:51](../../../api/wms_api_server/app/modules/inventory/api/tare_loss_routes.py#L51)

```python
report(body: Report, user: AdminUser=Depends(require_permission('tare_loss_report')), service: TarePort=Depends(tare_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `post`, `require_permission`, `router.post`

### decide

[Исходник: api/wms_api_server/app/modules/inventory/api/tare_loss_routes.py:55](../../../api/wms_api_server/app/modules/inventory/api/tare_loss_routes.py#L55)

```python
decide(body: Decision, user: AdminUser=Depends(require_permission('tare_writeoff')), service: TarePort=Depends(tare_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `post`, `require_permission`, `router.post`

### cases

[Исходник: api/wms_api_server/app/modules/inventory/api/tare_loss_routes.py:59](../../../api/wms_api_server/app/modules/inventory/api/tare_loss_routes.py#L59)

```python
cases(ware_id: int, user: AdminUser=Depends(require_permission('tare_view')), service: TareAssemblyPort=Depends(tare_assembly_service)) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.get`, `service.loss_cases`, `str`

### source_required

[Исходник: api/wms_api_server/app/modules/inventory/api/tare_loss_routes.py:28](../../../api/wms_api_server/app/modules/inventory/api/tare_loss_routes.py#L28)

```python
source_required(self) -> 'Report'
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `len`, `model_validator`, `self.custodian_id.encode`

### read

[Исходник: api/wms_api_server/app/modules/inventory/api/tare_policy_routes.py:31](../../../api/wms_api_server/app/modules/inventory/api/tare_policy_routes.py#L31)

```python
read(scope_kind: Literal['STORE', 'CUSTOMER'], scope_key: str=Query(min_length=1, max_length=255), user: AdminUser=Depends(require_permission('warehouse_settings_edit')), service: TarePolicyPort=Depends(tare_policy_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Query`, `require_permission`, `router.get`, `service.read`

### configure

[Исходник: api/wms_api_server/app/modules/inventory/api/tare_policy_routes.py:36](../../../api/wms_api_server/app/modules/inventory/api/tare_policy_routes.py#L36)

```python
configure(body: ReturnPolicy, user: AdminUser=Depends(require_permission('warehouse_settings_edit')), service: TarePolicyPort=Depends(tare_policy_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `body.model_dump`, `require_permission`, `router.put`, `service.configure`, `str`, `values.pop`

### debt

[Исходник: api/wms_api_server/app/modules/inventory/api/tare_policy_routes.py:43](../../../api/wms_api_server/app/modules/inventory/api/tare_policy_routes.py#L43)

```python
debt(ware_id: int, user: AdminUser=Depends(require_permission('tare_view')), service: TarePolicyPort=Depends(tare_policy_service)) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `require_permission`, `router.get`, `service.debt`

### bytes_limit

[Исходник: api/wms_api_server/app/modules/inventory/api/tare_policy_routes.py:20](../../../api/wms_api_server/app/modules/inventory/api/tare_policy_routes.py#L20)

```python
bytes_limit(cls, value: str) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `field_validator`, `len`, `value.encode`

### days_required

[Исходник: api/wms_api_server/app/modules/inventory/api/tare_policy_routes.py:25](../../../api/wms_api_server/app/modules/inventory/api/tare_policy_routes.py#L25)

```python
days_required(self) -> 'ReturnPolicy'
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `model_validator`

### post

[Исходник: api/wms_api_server/app/modules/inventory/api/tare_resolution_routes.py:42](../../../api/wms_api_server/app/modules/inventory/api/tare_resolution_routes.py#L42)

```python
post(service: TarePort, body: Resolution, kind: str, source_keys: tuple[str, ...], user: AdminUser) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `body.model_dump`, `service.post`, `str`, `values.get`, `values.pop`

### damage

[Исходник: api/wms_api_server/app/modules/inventory/api/tare_resolution_routes.py:50](../../../api/wms_api_server/app/modules/inventory/api/tare_resolution_routes.py#L50)

```python
damage(body: Damage, user: AdminUser=Depends(require_permission('tare_damage')), service: TarePort=Depends(tare_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `post`, `require_permission`, `router.post`

### writeoff

[Исходник: api/wms_api_server/app/modules/inventory/api/tare_resolution_routes.py:54](../../../api/wms_api_server/app/modules/inventory/api/tare_resolution_routes.py#L54)

```python
writeoff(body: Writeoff, user: AdminUser=Depends(require_permission('tare_writeoff')), service: TarePort=Depends(tare_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `post`, `require_permission`, `router.post`

### cases

[Исходник: api/wms_api_server/app/modules/inventory/api/tare_resolution_routes.py:58](../../../api/wms_api_server/app/modules/inventory/api/tare_resolution_routes.py#L58)

```python
cases(ware_id: int, user: AdminUser=Depends(require_permission('tare_view')), service: TarePort=Depends(tare_service)) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `require_permission`, `router.get`, `service.damage_cases`

### bytes_limit

[Исходник: api/wms_api_server/app/modules/inventory/api/tare_resolution_routes.py:26](../../../api/wms_api_server/app/modules/inventory/api/tare_resolution_routes.py#L26)

```python
bytes_limit(cls, value: str) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `field_validator`, `len`, `value.encode`

### source_required

[Исходник: api/wms_api_server/app/modules/inventory/api/tare_resolution_routes.py:31](../../../api/wms_api_server/app/modules/inventory/api/tare_resolution_routes.py#L31)

```python
source_required(self) -> 'Damage'
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `model_validator`

### post

[Исходник: api/wms_api_server/app/modules/inventory/api/tare_routes.py:51](../../../api/wms_api_server/app/modules/inventory/api/tare_routes.py#L51)

```python
post(service: TarePort, body: Operation, kind: str, source_fields: tuple[str, ...], user: AdminUser) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `body.model_dump`, `service.post`, `str`, `values.get`, `values.pop`

### count

[Исходник: api/wms_api_server/app/modules/inventory/api/tare_routes.py:62](../../../api/wms_api_server/app/modules/inventory/api/tare_routes.py#L62)

```python
count(body: Count, user: AdminUser=Depends(require_permission('tare_adjust')), service: TarePort=Depends(tare_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `post`, `require_permission`, `router.post`

### offer

[Исходник: api/wms_api_server/app/modules/inventory/api/tare_routes.py:66](../../../api/wms_api_server/app/modules/inventory/api/tare_routes.py#L66)

```python
offer(body: Offer, user: AdminUser=Depends(require_permission('tare_offer')), service: TarePort=Depends(tare_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `post`, `require_permission`, `router.post`

### accept

[Исходник: api/wms_api_server/app/modules/inventory/api/tare_routes.py:70](../../../api/wms_api_server/app/modules/inventory/api/tare_routes.py#L70)

```python
accept(body: Accept, user: AdminUser=Depends(require_permission('tare_accept')), service: TarePort=Depends(tare_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `post`, `require_permission`, `router.post`

### offer_cancel

[Исходник: api/wms_api_server/app/modules/inventory/api/tare_routes.py:74](../../../api/wms_api_server/app/modules/inventory/api/tare_routes.py#L74)

```python
offer_cancel(body: OfferCancel, user: AdminUser=Depends(require_permission('tare_offer')), service: TarePort=Depends(tare_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `post`, `require_permission`, `router.post`

### balances

[Исходник: api/wms_api_server/app/modules/inventory/api/tare_routes.py:78](../../../api/wms_api_server/app/modules/inventory/api/tare_routes.py#L78)

```python
balances(ware_id: int, user: AdminUser=Depends(require_permission('tare_view')), service: TarePort=Depends(tare_service)) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `require_permission`, `router.get`, `service.balances`

### offers

[Исходник: api/wms_api_server/app/modules/inventory/api/tare_routes.py:82](../../../api/wms_api_server/app/modules/inventory/api/tare_routes.py#L82)

```python
offers(task_id: int, user: AdminUser=Depends(require_permission('tare_view')), service: TarePort=Depends(tare_service)) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `require_permission`, `router.get`, `service.offers`

### context

[Исходник: api/wms_api_server/app/modules/inventory/api/tare_routes.py:86](../../../api/wms_api_server/app/modules/inventory/api/tare_routes.py#L86)

```python
context(task_id: int, user: AdminUser=Depends(require_permission('tare_view')), service: TarePort=Depends(tare_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.get`, `service.context`, `str`

### damage_custody

[Исходник: api/wms_api_server/app/modules/inventory/api/tare_routes.py:92](../../../api/wms_api_server/app/modules/inventory/api/tare_routes.py#L92)

```python
damage_custody(ware_id: int, user: AdminUser=Depends(require_permission('tare_view')), service: TarePort=Depends(tare_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.get`, `service.damage_custody`, `str`

### byte_length

[Исходник: api/wms_api_server/app/modules/inventory/api/tare_routes.py:37](../../../api/wms_api_server/app/modules/inventory/api/tare_routes.py#L37)

```python
byte_length(cls, value: str) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `field_validator`, `len`, `value.encode`

### scan_view

[Исходник: api/wms_api_server/app/modules/inventory/api/task_scan_routes.py:15](../../../api/wms_api_server/app/modules/inventory/api/task_scan_routes.py#L15)

```python
scan_view() -> ScanUser
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### scan_execute

[Исходник: api/wms_api_server/app/modules/inventory/api/task_scan_routes.py:18](../../../api/wms_api_server/app/modules/inventory/api/task_scan_routes.py#L18)

```python
scan_execute() -> ScanUser
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### scan_draft_service

[Исходник: api/wms_api_server/app/modules/inventory/api/task_scan_routes.py:21](../../../api/wms_api_server/app/modules/inventory/api/task_scan_routes.py#L21)

```python
scan_draft_service() -> ScanDraftPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### get_scan_context

[Исходник: api/wms_api_server/app/modules/inventory/api/task_scan_routes.py:40](../../../api/wms_api_server/app/modules/inventory/api/task_scan_routes.py#L40)

```python
get_scan_context(task_id: int, user: ScanUser=Depends(scan_view), service: ScanDraftPort=Depends(scan_draft_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `router.get`, `service.context`

### get_scan_draft

[Исходник: api/wms_api_server/app/modules/inventory/api/task_scan_routes.py:45](../../../api/wms_api_server/app/modules/inventory/api/task_scan_routes.py#L45)

```python
get_scan_draft(task_id: int, user: ScanUser=Depends(scan_execute), service: ScanDraftPort=Depends(scan_draft_service)) -> dict[str, Any] | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `router.get`, `service.latest`

### save_scan_draft

[Исходник: api/wms_api_server/app/modules/inventory/api/task_scan_routes.py:50](../../../api/wms_api_server/app/modules/inventory/api/task_scan_routes.py#L50)

```python
save_scan_draft(task_id: int, request: ScanDraftInput, user: ScanUser=Depends(scan_execute), service: ScanDraftPort=Depends(scan_draft_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `request.model_dump`, `router.post`, `service.save`

### context

[Исходник: api/wms_api_server/app/modules/inventory/api/task_scan_routes.py:11](../../../api/wms_api_server/app/modules/inventory/api/task_scan_routes.py#L11)

```python
context(self, task_id: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### latest

[Исходник: api/wms_api_server/app/modules/inventory/api/task_scan_routes.py:12](../../../api/wms_api_server/app/modules/inventory/api/task_scan_routes.py#L12)

```python
latest(self, task_id: int, actor: str) -> dict[str, Any] | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### save

[Исходник: api/wms_api_server/app/modules/inventory/api/task_scan_routes.py:13](../../../api/wms_api_server/app/modules/inventory/api/task_scan_routes.py#L13)

```python
save(self, task_id: int, request: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### import_manifest

[Исходник: api/wms_api_server/app/modules/inventory/api/trace_manifest_routes.py:15](../../../api/wms_api_server/app/modules/inventory/api/trace_manifest_routes.py#L15)

```python
import_manifest(body: ImportManifest, user: AdminUser=Depends(require_permission('trace_manifest_import')), service: TraceManifestPort=Depends(trace_manifest_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.post`, `service.import_manifest`, `str`

### manifests

[Исходник: api/wms_api_server/app/modules/inventory/api/trace_manifest_routes.py:22](../../../api/wms_api_server/app/modules/inventory/api/trace_manifest_routes.py#L22)

```python
manifests(ware_id: int, user: AdminUser=Depends(require_permission('trace_manifest_import')), service: TraceManifestPort=Depends(trace_manifest_service)) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.get`, `service.list`, `str`

### _context

[Исходник: api/wms_api_server/app/modules/inventory/api/trace_manifest_routes.py:35](../../../api/wms_api_server/app/modules/inventory/api/trace_manifest_routes.py#L35)

```python
_context(service: TraceManifestPort, kind: str, body: CaptureSource, user: AdminUser) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `service.capture_context`, `str`

### inventory_context

[Исходник: api/wms_api_server/app/modules/inventory/api/trace_manifest_routes.py:42](../../../api/wms_api_server/app/modules/inventory/api/trace_manifest_routes.py#L42)

```python
inventory_context(body: CaptureSource, user: AdminUser=Depends(require_permission('stock_inventory_count')), service: TraceManifestPort=Depends(trace_manifest_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `_context`, `require_permission`, `router.post`

### mes_context

[Исходник: api/wms_api_server/app/modules/inventory/api/trace_manifest_routes.py:46](../../../api/wms_api_server/app/modules/inventory/api/trace_manifest_routes.py#L46)

```python
mes_context(body: CaptureSource, user: AdminUser=Depends(require_permission('mes_wms_bridge_apply')), service: TraceManifestPort=Depends(trace_manifest_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `_context`, `require_permission`, `router.post`

### invalidate_aggregate

[Исходник: api/wms_api_server/app/modules/inventory/api/trace_manifest_routes.py:61](../../../api/wms_api_server/app/modules/inventory/api/trace_manifest_routes.py#L61)

```python
invalidate_aggregate(body: InvalidateAggregate, user: AdminUser=Depends(require_permission('trace_manifest_import')), service: TraceManifestPort=Depends(trace_manifest_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `body.model_dump`, `require_permission`, `router.post`, `service.invalidate_aggregate`, `str`

### aggregate_lifecycle

[Исходник: api/wms_api_server/app/modules/inventory/api/trace_manifest_routes.py:68](../../../api/wms_api_server/app/modules/inventory/api/trace_manifest_routes.py#L68)

```python
aggregate_lifecycle(ware_id: int, origin: str, user: AdminUser=Depends(require_permission('traceability_view')), service: TraceManifestPort=Depends(trace_manifest_service)) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.get`, `service.aggregates`, `str`

### plan_waiting

[Исходник: api/wms_api_server/app/modules/inventory/api/waiting_task_routes.py:8](../../../api/wms_api_server/app/modules/inventory/api/waiting_task_routes.py#L8)

```python
plan_waiting(request: WaitingTaskRequest, user: AdminUser=Depends(require_permission('warehouse_task_edit')), service: WaitingTaskPort=Depends(waiting_task_dependency)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.post`, `service.plan`, `str`

### read_waiting

[Исходник: api/wms_api_server/app/modules/inventory/api/waiting_task_routes.py:16](../../../api/wms_api_server/app/modules/inventory/api/waiting_task_routes.py#L16)

```python
read_waiting(decision_operation_id: str=Query(min_length=1, max_length=100, pattern='^[A-Za-z0-9_.:-]+$'), after_task_id: int=Query(default=0, ge=0), limit: int=Query(default=100, ge=1, le=200), user: AdminUser=Depends(require_permission('warehouse_task_view')), service: WaitingTaskPort=Depends(waiting_task_dependency)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Query`, `require_permission`, `router.get`, `service.read`, `str`

### repack

[Исходник: api/wms_api_server/app/modules/inventory/api/warehouse_hu_repack_routes.py:29](../../../api/wms_api_server/app/modules/inventory/api/warehouse_hu_repack_routes.py#L29)

```python
repack(body: Repack, user: AdminUser=Depends(require_permission('warehouse_task_execute')), service: WarehouseHuPort=Depends(warehouse_hu_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `execute`, `require_permission`, `router.post`

### repack_case

[Исходник: api/wms_api_server/app/modules/inventory/api/warehouse_hu_repack_routes.py:35](../../../api/wms_api_server/app/modules/inventory/api/warehouse_hu_repack_routes.py#L35)

```python
repack_case(body: CaseRepack, user: AdminUser=Depends(require_permission('warehouse_task_execute')), service: WarehouseHuPort=Depends(warehouse_hu_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `execute`, `require_permission`, `router.post`

### warehouse_hu_service

[Исходник: api/wms_api_server/app/modules/inventory/api/warehouse_hu_routes.py:18](../../../api/wms_api_server/app/modules/inventory/api/warehouse_hu_routes.py#L18)

```python
warehouse_hu_service() -> WarehouseHuPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### execute

[Исходник: api/wms_api_server/app/modules/inventory/api/warehouse_hu_routes.py:76](../../../api/wms_api_server/app/modules/inventory/api/warehouse_hu_routes.py#L76)

```python
execute(service: WarehouseHuPort, kind: str, body: Command, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `body.model_dump`, `metadata.get`, `metadata.pop`, `service.command`

### preview

[Исходник: api/wms_api_server/app/modules/inventory/api/warehouse_hu_routes.py:92](../../../api/wms_api_server/app/modules/inventory/api/warehouse_hu_routes.py#L92)

```python
preview(identifier: str=Query(min_length=1, max_length=200), _user: AdminUser=Depends(require_permission('warehouse_task_view')), service: WarehouseHuPort=Depends(warehouse_hu_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Query`, `require_permission`, `router.get`, `service.preview`

### target_slots

[Исходник: api/wms_api_server/app/modules/inventory/api/warehouse_hu_routes.py:99](../../../api/wms_api_server/app/modules/inventory/api/warehouse_hu_routes.py#L99)

```python
target_slots(cell: str=Query(min_length=1, max_length=60), warehouse: int=Query(ge=1), _user: AdminUser=Depends(require_permission('warehouse_task_view')), service: WarehouseHuPort=Depends(warehouse_hu_service)) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Query`, `require_permission`, `router.get`, `service.target_slots`

### create

[Исходник: api/wms_api_server/app/modules/inventory/api/warehouse_hu_routes.py:106](../../../api/wms_api_server/app/modules/inventory/api/warehouse_hu_routes.py#L106)

```python
create(body: Create, user: AdminUser=Depends(require_permission('warehouse_task_execute')), service: WarehouseHuPort=Depends(warehouse_hu_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `execute`, `require_permission`, `router.post`

### attach

[Исходник: api/wms_api_server/app/modules/inventory/api/warehouse_hu_routes.py:112](../../../api/wms_api_server/app/modules/inventory/api/warehouse_hu_routes.py#L112)

```python
attach(body: Link, user: AdminUser=Depends(require_permission('warehouse_task_execute')), service: WarehouseHuPort=Depends(warehouse_hu_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `execute`, `require_permission`, `router.post`

### detach

[Исходник: api/wms_api_server/app/modules/inventory/api/warehouse_hu_routes.py:118](../../../api/wms_api_server/app/modules/inventory/api/warehouse_hu_routes.py#L118)

```python
detach(body: Link, user: AdminUser=Depends(require_permission('warehouse_task_execute')), service: WarehouseHuPort=Depends(warehouse_hu_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `execute`, `require_permission`, `router.post`

### move

[Исходник: api/wms_api_server/app/modules/inventory/api/warehouse_hu_routes.py:126](../../../api/wms_api_server/app/modules/inventory/api/warehouse_hu_routes.py#L126)

```python
move(body: Move, user: AdminUser=Depends(require_permission('warehouse_task_execute')), service: WarehouseHuPort=Depends(warehouse_hu_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `execute`, `require_permission`, `router.post`

### plan_move

[Исходник: api/wms_api_server/app/modules/inventory/api/warehouse_hu_routes.py:131](../../../api/wms_api_server/app/modules/inventory/api/warehouse_hu_routes.py#L131)

```python
plan_move(body: Move, user: AdminUser=Depends(require_permission('warehouse_task_execute')), service: WarehouseHuPort=Depends(warehouse_hu_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `execute`, `require_permission`, `router.post`

### attach_case

[Исходник: api/wms_api_server/app/modules/inventory/api/warehouse_hu_routes.py:137](../../../api/wms_api_server/app/modules/inventory/api/warehouse_hu_routes.py#L137)

```python
attach_case(body: CaseLink, user: AdminUser=Depends(require_permission('warehouse_task_execute')), service: WarehouseHuPort=Depends(warehouse_hu_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `execute`, `require_permission`, `router.post`

### detach_case

[Исходник: api/wms_api_server/app/modules/inventory/api/warehouse_hu_routes.py:143](../../../api/wms_api_server/app/modules/inventory/api/warehouse_hu_routes.py#L143)

```python
detach_case(body: CaseLink, user: AdminUser=Depends(require_permission('warehouse_task_execute')), service: WarehouseHuPort=Depends(warehouse_hu_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `execute`, `require_permission`, `router.post`

### ship

[Исходник: api/wms_api_server/app/modules/inventory/api/warehouse_hu_routes.py:157](../../../api/wms_api_server/app/modules/inventory/api/warehouse_hu_routes.py#L157)

```python
ship(body: Ship, user: AdminUser=Depends(require_permission('stock_posting_shipping')), service: WarehouseHuPort=Depends(warehouse_hu_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `execute`, `require_permission`, `router.post`

### unpack

[Исходник: api/wms_api_server/app/modules/inventory/api/warehouse_hu_routes.py:173](../../../api/wms_api_server/app/modules/inventory/api/warehouse_hu_routes.py#L173)

```python
unpack(body: Unpack, user: AdminUser=Depends(require_permission('warehouse_task_execute')), service: WarehouseHuPort=Depends(warehouse_hu_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `execute`, `require_permission`, `router.post`

### relocate_slot

[Исходник: api/wms_api_server/app/modules/inventory/api/warehouse_hu_routes.py:191](../../../api/wms_api_server/app/modules/inventory/api/warehouse_hu_routes.py#L191)

```python
relocate_slot(body: RelocateSlot, user: AdminUser=Depends(require_permission('warehouse_task_execute')), service: WarehouseHuPort=Depends(warehouse_hu_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `execute`, `require_permission`, `router.post`

### unpack_case

[Исходник: api/wms_api_server/app/modules/inventory/api/warehouse_hu_routes.py:212](../../../api/wms_api_server/app/modules/inventory/api/warehouse_hu_routes.py#L212)

```python
unpack_case(body: CaseUnpack, user: AdminUser=Depends(require_permission('warehouse_task_execute')), service: WarehouseHuPort=Depends(warehouse_hu_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `execute`, `require_permission`, `router.post`

### preview

[Исходник: api/wms_api_server/app/modules/inventory/api/warehouse_hu_routes.py:10](../../../api/wms_api_server/app/modules/inventory/api/warehouse_hu_routes.py#L10)

```python
preview(self, identifier: str, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### target_slots

[Исходник: api/wms_api_server/app/modules/inventory/api/warehouse_hu_routes.py:11](../../../api/wms_api_server/app/modules/inventory/api/warehouse_hu_routes.py#L11)

```python
target_slots(self, cell: str, warehouse: int, actor: str) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### command

[Исходник: api/wms_api_server/app/modules/inventory/api/warehouse_hu_routes.py:12](../../../api/wms_api_server/app/modules/inventory/api/warehouse_hu_routes.py#L12)

```python
command(self, kind: str, uid: str, operation_id: str, metadata: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### failure

[Исходник: api/wms_api_server/app/modules/inventory/api/warehouse_scale_routes.py:13](../../../api/wms_api_server/app/modules/inventory/api/warehouse_scale_routes.py#L13)

```python
failure(exc: WarehouseScaleError) -> HTTPException
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `str`

### configure

[Исходник: api/wms_api_server/app/modules/inventory/api/warehouse_scale_routes.py:19](../../../api/wms_api_server/app/modules/inventory/api/warehouse_scale_routes.py#L19)

```python
configure(device: str, body: WarehouseScaleConfiguration, user: AdminUser=Depends(require_permission('warehouse_settings_edit')), service: WarehouseScalePort=Depends(warehouse_scale_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `failure`, `len`, `require_permission`, `router.put`, `service.configure`

### capture

[Исходник: api/wms_api_server/app/modules/inventory/api/warehouse_scale_routes.py:31](../../../api/wms_api_server/app/modules/inventory/api/warehouse_scale_routes.py#L31)

```python
capture(body: WarehouseScalePacket, user: AdminUser=Depends(require_permission('warehouse_scale_ingest')), service: WarehouseScalePort=Depends(warehouse_scale_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `error.detail.update`, `failure`, `require_permission`, `router.post`, `service.capture`

### readings

[Исходник: api/wms_api_server/app/modules/inventory/api/warehouse_scale_routes.py:42](../../../api/wms_api_server/app/modules/inventory/api/warehouse_scale_routes.py#L42)

```python
readings(task: int=Query(ge=1), line: int=Query(ge=1), user: AdminUser=Depends(require_permission('case_pick_execute')), service: WarehouseScalePort=Depends(warehouse_scale_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Query`, `failure`, `require_permission`, `router.get`, `service.readings`

### reading

[Исходник: api/wms_api_server/app/modules/inventory/api/warehouse_scale_routes.py:52](../../../api/wms_api_server/app/modules/inventory/api/warehouse_scale_routes.py#L52)

```python
reading(key: str, user: AdminUser=Depends(require_permission('case_pick_execute')), service: WarehouseScalePort=Depends(warehouse_scale_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `any`, `failure`, `len`, `require_permission`, `router.get`, `service.reading`

### final_capture

[Исходник: api/wms_api_server/app/modules/inventory/api/warehouse_scale_routes.py:63](../../../api/wms_api_server/app/modules/inventory/api/warehouse_scale_routes.py#L63)

```python
final_capture(body: WarehouseFinalScalePacket, user: AdminUser=Depends(require_permission('warehouse_scale_ingest')), service: WarehouseScalePort=Depends(warehouse_scale_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `error.detail.update`, `failure`, `require_permission`, `router.post`, `service.capture`

### final_readings

[Исходник: api/wms_api_server/app/modules/inventory/api/warehouse_scale_routes.py:70](../../../api/wms_api_server/app/modules/inventory/api/warehouse_scale_routes.py#L70)

```python
final_readings(task: int=Query(ge=1), user: AdminUser=Depends(require_permission('case_pick_execute')), service: WarehouseScalePort=Depends(warehouse_scale_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Query`, `failure`, `require_permission`, `router.get`, `service.final_readings`

### wave_execution_service

[Исходник: api/wms_api_server/app/modules/inventory/api/wave_execution_routes.py:16](../../../api/wms_api_server/app/modules/inventory/api/wave_execution_routes.py#L16)

```python
wave_execution_service() -> WaveExecutionPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### preview

[Исходник: api/wms_api_server/app/modules/inventory/api/wave_execution_routes.py:35](../../../api/wms_api_server/app/modules/inventory/api/wave_execution_routes.py#L35)

```python
preview(wave_id: int, user: AdminUser=Depends(require_permission('pick_wave_view')), service: WaveExecutionPort=Depends(wave_execution_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.get`, `service.preview`

### finish

[Исходник: api/wms_api_server/app/modules/inventory/api/wave_execution_routes.py:43](../../../api/wms_api_server/app/modules/inventory/api/wave_execution_routes.py#L43)

```python
finish(wave_id: int, body: FinishRequest, user: AdminUser=Depends(require_permission('pick_wave_launch')), service: WaveExecutionPort=Depends(wave_execution_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.post`, `service.finish`

### preview

[Исходник: api/wms_api_server/app/modules/inventory/api/wave_execution_routes.py:9](../../../api/wms_api_server/app/modules/inventory/api/wave_execution_routes.py#L9)

```python
preview(self, wave_id: int, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### finish

[Исходник: api/wms_api_server/app/modules/inventory/api/wave_execution_routes.py:10](../../../api/wms_api_server/app/modules/inventory/api/wave_execution_routes.py#L10)

```python
finish(self, wave_id: int, operation_id: str, actor: str, disposition: str | None=None, reason: str | None=None) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### require_reason

[Исходник: api/wms_api_server/app/modules/inventory/api/wave_execution_routes.py:26](../../../api/wms_api_server/app/modules/inventory/api/wave_execution_routes.py#L26)

```python
require_reason(self) -> 'FinishRequest'
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(self.reason or '').strip`, `ValueError`, `model_validator`

### wave_pick_service

[Исходник: api/wms_api_server/app/modules/inventory/api/wave_pick_routes.py:16](../../../api/wms_api_server/app/modules/inventory/api/wave_pick_routes.py#L16)

```python
wave_pick_service() -> WavePickPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### preview

[Исходник: api/wms_api_server/app/modules/inventory/api/wave_pick_routes.py:25](../../../api/wms_api_server/app/modules/inventory/api/wave_pick_routes.py#L25)

```python
preview(wave_id: int, user: AdminUser=Depends(require_permission('pick_wave_view')), service: WavePickPort=Depends(wave_pick_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.get`, `service.preview`

### release

[Исходник: api/wms_api_server/app/modules/inventory/api/wave_pick_routes.py:33](../../../api/wms_api_server/app/modules/inventory/api/wave_pick_routes.py#L33)

```python
release(wave_id: int, body: PickReleaseRequest, user: AdminUser=Depends(require_permission('pick_wave_launch')), service: WavePickPort=Depends(wave_pick_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.post`, `service.release`

### preview

[Исходник: api/wms_api_server/app/modules/inventory/api/wave_pick_routes.py:9](../../../api/wms_api_server/app/modules/inventory/api/wave_pick_routes.py#L9)

```python
preview(self, wave_id: int, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### release

[Исходник: api/wms_api_server/app/modules/inventory/api/wave_pick_routes.py:10](../../../api/wms_api_server/app/modules/inventory/api/wave_pick_routes.py#L10)

```python
release(self, wave_id: int, operation_id: str, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### confirm_weighted_box

[Исходник: api/wms_api_server/app/modules/inventory/api/weighted_case_routes.py:10](../../../api/wms_api_server/app/modules/inventory/api/weighted_case_routes.py#L10)

```python
confirm_weighted_box(task: int, line: int, body: WeightedCaseRequest, user: AdminUser=Depends(require_permission('case_pick_execute')), service: WeightedCasePort=Depends(weighted_case_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.post`, `service.confirm`, `str`

### confirm_weighed_line

[Исходник: api/wms_api_server/app/modules/inventory/api/weighted_case_routes.py:21](../../../api/wms_api_server/app/modules/inventory/api/weighted_case_routes.py#L21)

```python
confirm_weighed_line(task: int, line: int, body: WeighedLineRequest, user: AdminUser=Depends(require_permission('case_pick_execute')), service: WeightedCasePort=Depends(weighted_case_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.post`, `service.weigh_line`, `str`

### order_weight_preview

[Исходник: api/wms_api_server/app/modules/inventory/api/weighted_case_routes.py:33](../../../api/wms_api_server/app/modules/inventory/api/weighted_case_routes.py#L33)

```python
order_weight_preview(task: int, line: int, user: AdminUser=Depends(require_permission('case_pick_execute')), service: WeightedCasePort=Depends(weighted_case_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `require_permission`, `router.get`, `service.weight_preview`

### short_weight_preview

[Исходник: api/wms_api_server/app/modules/inventory/api/weighted_case_routes.py:40](../../../api/wms_api_server/app/modules/inventory/api/weighted_case_routes.py#L40)

```python
short_weight_preview(short: int, user: AdminUser=Depends(require_permission('case_pick_short_approve')), service: WeightedCasePort=Depends(weighted_case_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `require_permission`, `router.get`, `service.short_weight_preview`

### weighted_box_options

[Исходник: api/wms_api_server/app/modules/inventory/api/weighted_plan_routes.py:10](../../../api/wms_api_server/app/modules/inventory/api/weighted_plan_routes.py#L10)

```python
weighted_box_options(row: int=Path(ge=1), user: AdminUser=Depends(require_permission('pick_plan_create')), service: WeightedPlanPort=Depends(weighted_plan_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Path`, `require_permission`, `router.get`, `service.options`

### weighted_box_approval_preview

[Исходник: api/wms_api_server/app/modules/inventory/api/weighted_plan_routes.py:16](../../../api/wms_api_server/app/modules/inventory/api/weighted_plan_routes.py#L16)

```python
weighted_box_approval_preview(row: int=Path(ge=1), user: AdminUser=Depends(require_permission('case_pick_short_approve')), service: WeightedPlanPort=Depends(weighted_plan_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Path`, `require_permission`, `router.get`, `service.approval_options`

### approve_weighted_box

[Исходник: api/wms_api_server/app/modules/inventory/api/weighted_plan_routes.py:23](../../../api/wms_api_server/app/modules/inventory/api/weighted_plan_routes.py#L23)

```python
approve_weighted_box(body: WeightedBoxChoiceRequest, user: AdminUser=Depends(require_permission('case_pick_short_approve')), service: WeightedPlanPort=Depends(weighted_plan_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `require_permission`, `router.post`, `service.approve`

### cancel_weighted_box

[Исходник: api/wms_api_server/app/modules/inventory/api/weighted_plan_routes.py:30](../../../api/wms_api_server/app/modules/inventory/api/weighted_plan_routes.py#L30)

```python
cancel_weighted_box(choice: str, body: WeightedChoiceCancelRequest, user: AdminUser=Depends(require_permission('case_pick_short_approve')), service: WeightedPlanPort=Depends(weighted_plan_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `require_permission`, `router.post`, `service.cancel`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/application/case_carrier_move.py:7](../../../api/wms_api_server/app/modules/inventory/application/case_carrier_move.py#L7)

```python
__init__(self, posting: StockPostingPort) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### execute

[Исходник: api/wms_api_server/app/modules/inventory/application/case_carrier_move.py:10](../../../api/wms_api_server/app/modules/inventory/application/case_carrier_move.py#L10)

```python
execute(self, operation_id: str, actor: str, task_id: int, carrier: str, target_cell: str, expected_version: int) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockCommand`, `ValueError`, `self.posting.post`

### receive

[Исходник: api/wms_api_server/app/modules/inventory/application/ports.py:6](../../../api/wms_api_server/app/modules/inventory/application/ports.py#L6)

```python
receive(self, order_id: str, payload: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### complete

[Исходник: api/wms_api_server/app/modules/inventory/application/ports.py:7](../../../api/wms_api_server/app/modules/inventory/application/ports.py#L7)

```python
complete(self, task_id: int, scans: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### replan

[Исходник: api/wms_api_server/app/modules/inventory/application/ports.py:8](../../../api/wms_api_server/app/modules/inventory/application/ports.py#L8)

```python
replan(self, task_id: int, body: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### cancel

[Исходник: api/wms_api_server/app/modules/inventory/application/ports.py:9](../../../api/wms_api_server/app/modules/inventory/application/ports.py#L9)

```python
cancel(self, task_id: int, reason: str, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### issue

[Исходник: api/wms_api_server/app/modules/inventory/application/ports.py:13](../../../api/wms_api_server/app/modules/inventory/application/ports.py#L13)

```python
issue(self, order_id: str, payload: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### document

[Исходник: api/wms_api_server/app/modules/inventory/application/ports.py:14](../../../api/wms_api_server/app/modules/inventory/application/ports.py#L14)

```python
document(self, label_id: str, format: str, actor: str, dpi: int=203) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### confirm

[Исходник: api/wms_api_server/app/modules/inventory/application/ports.py:15](../../../api/wms_api_server/app/modules/inventory/application/ports.py#L15)

```python
confirm(self, label_id: str, scan: str, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### get

[Исходник: api/wms_api_server/app/modules/inventory/application/ports.py:19](../../../api/wms_api_server/app/modules/inventory/application/ports.py#L19)

```python
get(self, warehouse: int) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### read_rule

[Исходник: api/wms_api_server/app/modules/inventory/application/ports.py:20](../../../api/wms_api_server/app/modules/inventory/application/ports.py#L20)

```python
read_rule(self, warehouse: int, key: str, kind: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### save

[Исходник: api/wms_api_server/app/modules/inventory/application/ports.py:21](../../../api/wms_api_server/app/modules/inventory/application/ports.py#L21)

```python
save(self, warehouse: int, body: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### sku_rule

[Исходник: api/wms_api_server/app/modules/inventory/application/ports.py:22](../../../api/wms_api_server/app/modules/inventory/application/ports.py#L22)

```python
sku_rule(self, warehouse: int, articul: str, body: dict, actor: str='API') -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### cell_rule

[Исходник: api/wms_api_server/app/modules/inventory/application/ports.py:23](../../../api/wms_api_server/app/modules/inventory/application/ports.py#L23)

```python
cell_rule(self, warehouse: int, cell: str, body: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### close

[Исходник: api/wms_api_server/app/modules/inventory/application/ports.py:27](../../../api/wms_api_server/app/modules/inventory/application/ports.py#L27)

```python
close(self, order_id: str, operation: str, reason: str, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### reopen

[Исходник: api/wms_api_server/app/modules/inventory/application/ports.py:28](../../../api/wms_api_server/app/modules/inventory/application/ports.py#L28)

```python
reopen(self, order_id: str, operation: str, reason: str, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### composition

[Исходник: api/wms_api_server/app/modules/inventory/application/ports.py:32](../../../api/wms_api_server/app/modules/inventory/application/ports.py#L32)

```python
composition(self, pallet: str, after: str='', limit: int=50, expected_signature: str | None=None) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### post

[Исходник: api/wms_api_server/app/modules/inventory/application/stock_commands.py:7](../../../api/wms_api_server/app/modules/inventory/application/stock_commands.py#L7)

```python
post(self, command: StockCommand) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/application/stock_commands.py:11](../../../api/wms_api_server/app/modules/inventory/application/stock_commands.py#L11)

```python
__init__(self, posting: StockPostingPort) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### execute

[Исходник: api/wms_api_server/app/modules/inventory/application/stock_commands.py:14](../../../api/wms_api_server/app/modules/inventory/application/stock_commands.py#L14)

```python
execute(self, operation_id: str, actor: str, warehouse_id: int, reason: str, lines: tuple[StockLine, ...], *, compatibility: bool=False) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockCommand`, `ValueError`, `any`, `len`, `reason.strip`, `self.posting.post`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/application/stock_commands.py:30](../../../api/wms_api_server/app/modules/inventory/application/stock_commands.py#L30)

```python
__init__(self, posting: StockPostingPort) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### execute

[Исходник: api/wms_api_server/app/modules/inventory/application/stock_commands.py:33](../../../api/wms_api_server/app/modules/inventory/application/stock_commands.py#L33)

```python
execute(self, operation_id: str, actor: str, document_id: int, reason: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockCommand`, `ValueError`, `len`, `reason.strip`, `self.posting.post`

### status

[Исходник: api/wms_api_server/app/modules/inventory/application/stock_ports.py:6](../../../api/wms_api_server/app/modules/inventory/application/stock_ports.py#L6)

```python
status(self) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### operation

[Исходник: api/wms_api_server/app/modules/inventory/application/stock_ports.py:7](../../../api/wms_api_server/app/modules/inventory/application/stock_ports.py#L7)

```python
operation(self, operation_id: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### issue

[Исходник: api/wms_api_server/app/modules/inventory/contracts_case_labels.py:16](../../../api/wms_api_server/app/modules/inventory/contracts_case_labels.py#L16)

```python
issue(self, task: int, request: CaseSsccLabelRequest, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### current

[Исходник: api/wms_api_server/app/modules/inventory/contracts_case_labels.py:17](../../../api/wms_api_server/app/modules/inventory/contracts_case_labels.py#L17)

```python
current(self, task: int, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### confirm

[Исходник: api/wms_api_server/app/modules/inventory/contracts_case_labels.py:18](../../../api/wms_api_server/app/modules/inventory/contracts_case_labels.py#L18)

```python
confirm(self, task: int, scan: str, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### document

[Исходник: api/wms_api_server/app/modules/inventory/contracts_case_labels.py:19](../../../api/wms_api_server/app/modules/inventory/contracts_case_labels.py#L19)

```python
document(self, task: int, actor: str, format: str, dpi: int) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### validate_empty_decision

[Исходник: api/wms_api_server/app/modules/inventory/contracts_case_return.py:13](../../../api/wms_api_server/app/modules/inventory/contracts_case_return.py#L13)

```python
validate_empty_decision(self) -> 'CaseCarrierReturnRequest'
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(self.reason or '').strip`, `ValueError`, `any`, `len`, `model_validator`, `self.destinations.items`

### case_type_service

[Исходник: api/wms_api_server/app/modules/inventory/contracts_case_type.py:7](../../../api/wms_api_server/app/modules/inventory/contracts_case_type.py#L7)

```python
case_type_service() -> CaseTypePort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### read

[Исходник: api/wms_api_server/app/modules/inventory/contracts_case_type.py:4](../../../api/wms_api_server/app/modules/inventory/contracts_case_type.py#L4)

```python
read(self, task_id: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### change

[Исходник: api/wms_api_server/app/modules/inventory/contracts_case_type.py:5](../../../api/wms_api_server/app/modules/inventory/contracts_case_type.py#L5)

```python
change(self, task_id: int, operation: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/contracts_composition.py:2](../../../api/wms_api_server/app/modules/inventory/contracts_composition.py#L2)

```python
__init__(self, code: str, status: int=409) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `super`, `super().__init__`

### return_disposal_service

[Исходник: api/wms_api_server/app/modules/inventory/contracts_disposal.py:8](../../../api/wms_api_server/app/modules/inventory/contracts_disposal.py#L8)

```python
return_disposal_service() -> ReturnDisposalPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### report

[Исходник: api/wms_api_server/app/modules/inventory/contracts_disposal.py:4](../../../api/wms_api_server/app/modules/inventory/contracts_disposal.py#L4)

```python
report(self, operation_id: str, receipt_id: str, reference: str, document_hash: str, reason: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### dispose

[Исходник: api/wms_api_server/app/modules/inventory/contracts_disposal.py:5](../../../api/wms_api_server/app/modules/inventory/contracts_disposal.py#L5)

```python
dispose(self, operation_id: str, request_id: str, version: int, pallet: str, cell: str, reference: str, actor: str, scans: list[dict[str, str]] | None=None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### pending

[Исходник: api/wms_api_server/app/modules/inventory/contracts_disposal.py:6](../../../api/wms_api_server/app/modules/inventory/contracts_disposal.py#L6)

```python
pending(self, ware_id: int, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### interwarehouse_service

[Исходник: api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py:31](../../../api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py#L31)

```python
interwarehouse_service() -> InterwarehousePort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### prepare_group_onward

[Исходник: api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py:5](../../../api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py#L5)

```python
prepare_group_onward(self, operation: str, receipt: str, reason: str, reference: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### group_queue

[Исходник: api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py:6](../../../api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py#L6)

```python
group_queue(self, ware: int, actor: str, limit: int=200, after_operation_id: str | None=None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### group_detail

[Исходник: api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py:7](../../../api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py#L7)

```python
group_detail(self, plan: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### plan_group_placement

[Исходник: api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py:8](../../../api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py#L8)

```python
plan_group_placement(self, operation: str, receipt: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### plan_group

[Исходник: api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py:9](../../../api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py#L9)

```python
plan_group(self, operation: str, body: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### group_source_proof

[Исходник: api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py:10](../../../api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py#L10)

```python
group_source_proof(self, load: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### group_source

[Исходник: api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py:11](../../../api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py#L11)

```python
group_source(self, load: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### prepare_recovery_onward

[Исходник: api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py:12](../../../api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py#L12)

```python
prepare_recovery_onward(self, operation_id: str, recovery_id: str, trip_id: int, reason: str, reference: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### plan_recovery_placement

[Исходник: api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py:13](../../../api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py#L13)

```python
plan_recovery_placement(self, operation_id: str, recovery_id: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### receive_recovery

[Исходник: api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py:14](../../../api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py#L14)

```python
receive_recovery(self, operation: str, approval_id: str, metadata: dict, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### recovery_action

[Исходник: api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py:15](../../../api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py#L15)

```python
recovery_action(self, kind: str, operation: str, source_id: str, metadata: dict, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### shortage_action

[Исходник: api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py:16](../../../api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py#L16)

```python
shortage_action(self, kind: str, operation: str, source_id: str, metadata: dict, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### shortage

[Исходник: api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py:17](../../../api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py#L17)

```python
shortage(self, receipt_id: str, actor: str, selected_request: str | None=None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### close_incident

[Исходник: api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py:18](../../../api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py#L18)

```python
close_incident(self, operation: str, body: dict, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### decisions

[Исходник: api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py:19](../../../api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py#L19)

```python
decisions(self, plan_id: str, actor: str, after_revision: int=0) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### incoming

[Исходник: api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py:20](../../../api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py#L20)

```python
incoming(self, trip_id: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### record_temperature

[Исходник: api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py:21](../../../api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py#L21)

```python
record_temperature(self, operation_id: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### record_decision

[Исходник: api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py:22](../../../api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py#L22)

```python
record_decision(self, operation_id: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### plan

[Исходник: api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py:23](../../../api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py#L23)

```python
plan(self, operation_id: str, source_load: str, target_ware: int, target_trip: int, inbound_dock: str, arrival_due: datetime, ready_due: datetime, reason: str, reference: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### receive_action

[Исходник: api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py:24](../../../api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py#L24)

```python
receive_action(self, kind: str, operation_id: str, plan_id: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### plan_placement

[Исходник: api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py:25](../../../api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py#L25)

```python
plan_placement(self, operation_id: str, receipt_id: str, actor: str, superseded_task_id: int | None=None, replan_reason: str | None=None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### release_custody

[Исходник: api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py:26](../../../api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py#L26)

```python
release_custody(self, operation_id: str, receipt_id: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### prepare_onward

[Исходник: api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py:27](../../../api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py#L27)

```python
prepare_onward(self, operation_id: str, receipt_id: str, reason: str, reference: str, actor: str, accept_legacy_address: bool=False) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### unit_manifest

[Исходник: api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py:28](../../../api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py#L28)

```python
unit_manifest(self, plan_id: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### queue

[Исходник: api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py:29](../../../api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py#L29)

```python
queue(self, ware_id: int, actor: str, include_completed: bool=False) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### inventory_observations_service

[Исходник: api/wms_api_server/app/modules/inventory/contracts_observations.py:63](../../../api/wms_api_server/app/modules/inventory/contracts_observations.py#L63)

```python
inventory_observations_service() -> InventoryObservationsPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/contracts_observations.py:7](../../../api/wms_api_server/app/modules/inventory/contracts_observations.py#L7)

```python
__init__(self, code: str, status: int=409, operation_id: str='') -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `super`, `super().__init__`

### wire

[Исходник: api/wms_api_server/app/modules/inventory/contracts_observations.py:32](../../../api/wms_api_server/app/modules/inventory/contracts_observations.py#L32)

```python
wire(self, include_scans: bool=True) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `asdict`, `result.pop`

### from_wire

[Исходник: api/wms_api_server/app/modules/inventory/contracts_observations.py:48](../../../api/wms_api_server/app/modules/inventory/contracts_observations.py#L48)

```python
from_wire(cls, value: dict[str, Any]) -> 'CountSubmission'
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CountObservation`, `CountScan`, `cls`, `counts.append`, `row.get`, `value.get`

### lots

[Исходник: api/wms_api_server/app/modules/inventory/contracts_observations.py:57](../../../api/wms_api_server/app/modules/inventory/contracts_observations.py#L57)

```python
lots(self, revision_id: int, cell: str, article: str | None, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### count

[Исходник: api/wms_api_server/app/modules/inventory/contracts_observations.py:58](../../../api/wms_api_server/app/modules/inventory/contracts_observations.py#L58)

```python
count(self, request: CountSubmission, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### create_revision

[Исходник: api/wms_api_server/app/modules/inventory/contracts_observations.py:59](../../../api/wms_api_server/app/modules/inventory/contracts_observations.py#L59)

```python
create_revision(self, warehouse_id: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### register_lot

[Исходник: api/wms_api_server/app/modules/inventory/contracts_observations.py:60](../../../api/wms_api_server/app/modules/inventory/contracts_observations.py#L60)

```python
register_lot(self, operation_id: str, revision_id: int, metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### pallet_floor_service

[Исходник: api/wms_api_server/app/modules/inventory/contracts_pallet_floor.py:7](../../../api/wms_api_server/app/modules/inventory/contracts_pallet_floor.py#L7)

```python
pallet_floor_service() -> PalletFloorPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### read

[Исходник: api/wms_api_server/app/modules/inventory/contracts_pallet_floor.py:4](../../../api/wms_api_server/app/modules/inventory/contracts_pallet_floor.py#L4)

```python
read(self, identifier: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### confirm

[Исходник: api/wms_api_server/app/modules/inventory/contracts_pallet_floor.py:5](../../../api/wms_api_server/app/modules/inventory/contracts_pallet_floor.py#L5)

```python
confirm(self, operation: str, identifier: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### quality_scope_service

[Исходник: api/wms_api_server/app/modules/inventory/contracts_quality_scope.py:13](../../../api/wms_api_server/app/modules/inventory/contracts_quality_scope.py#L13)

```python
quality_scope_service() -> QualityScopePort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/contracts_quality_scope.py:5](../../../api/wms_api_server/app/modules/inventory/contracts_quality_scope.py#L5)

```python
__init__(self, message: str, status: int=409) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `super`, `super().__init__`

### read

[Исходник: api/wms_api_server/app/modules/inventory/contracts_quality_scope.py:10](../../../api/wms_api_server/app/modules/inventory/contracts_quality_scope.py#L10)

```python
read(self, warehouse: int, actor: str, address: str, category: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### save

[Исходник: api/wms_api_server/app/modules/inventory/contracts_quality_scope.py:11](../../../api/wms_api_server/app/modules/inventory/contracts_quality_scope.py#L11)

```python
save(self, warehouse: int, actor: str, body: dict[str, Any]) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### range_proposal_service

[Исходник: api/wms_api_server/app/modules/inventory/contracts_range_proposal.py:28](../../../api/wms_api_server/app/modules/inventory/contracts_range_proposal.py#L28)

```python
range_proposal_service() -> RangeProposalPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### save

[Исходник: api/wms_api_server/app/modules/inventory/contracts_range_proposal.py:21](../../../api/wms_api_server/app/modules/inventory/contracts_range_proposal.py#L21)

```python
save(self, ware: int, article: str, command: RangeDraft, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### cancel

[Исходник: api/wms_api_server/app/modules/inventory/contracts_range_proposal.py:22](../../../api/wms_api_server/app/modules/inventory/contracts_range_proposal.py#L22)

```python
cancel(self, ware: int, article: str, proposal: str, operation: str, reason: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### approve

[Исходник: api/wms_api_server/app/modules/inventory/contracts_range_proposal.py:23](../../../api/wms_api_server/app/modules/inventory/contracts_range_proposal.py#L23)

```python
approve(self, ware: int, article: str, proposal: str, operation: str, reason: str, geometry: bool, compatibility: bool, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### close

[Исходник: api/wms_api_server/app/modules/inventory/contracts_range_proposal.py:25](../../../api/wms_api_server/app/modules/inventory/contracts_range_proposal.py#L25)

```python
close(self, ware: int, article: str, mapping: int, operation: str, reason: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### get

[Исходник: api/wms_api_server/app/modules/inventory/contracts_range_proposal.py:26](../../../api/wms_api_server/app/modules/inventory/contracts_range_proposal.py#L26)

```python
get(self, ware: int, article: str, proposal: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### return_putaway_service

[Исходник: api/wms_api_server/app/modules/inventory/contracts_return_putaway.py:10](../../../api/wms_api_server/app/modules/inventory/contracts_return_putaway.py#L10)

```python
return_putaway_service() -> ReturnPutawayPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### configure

[Исходник: api/wms_api_server/app/modules/inventory/contracts_return_putaway.py:5](../../../api/wms_api_server/app/modules/inventory/contracts_return_putaway.py#L5)

```python
configure(self, ware_id: int, supplier_target: str, disposal_target: str, expected_version: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### pending

[Исходник: api/wms_api_server/app/modules/inventory/contracts_return_putaway.py:6](../../../api/wms_api_server/app/modules/inventory/contracts_return_putaway.py#L6)

```python
pending(self, ware_id: int, actor: str, receipt_operation_id: str | None=None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### plan

[Исходник: api/wms_api_server/app/modules/inventory/contracts_return_putaway.py:7](../../../api/wms_api_server/app/modules/inventory/contracts_return_putaway.py#L7)

```python
plan(self, operation_id: str, receipt_id: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### slotting_demand_service

[Исходник: api/wms_api_server/app/modules/inventory/contracts_slotting.py:12](../../../api/wms_api_server/app/modules/inventory/contracts_slotting.py#L12)

```python
slotting_demand_service() -> SlottingDemandPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/contracts_slotting.py:6](../../../api/wms_api_server/app/modules/inventory/contracts_slotting.py#L6)

```python
__init__(self, code: str, message: str, status: int=409) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `super`, `super().__init__`

### preview

[Исходник: api/wms_api_server/app/modules/inventory/contracts_slotting.py:10](../../../api/wms_api_server/app/modules/inventory/contracts_slotting.py#L10)

```python
preview(self, ware: int, article: str, start: date, end: date, forecast: Decimal | None, forecast_unit: str | None, actor: str, pallet_weight: Decimal | None=None, costs: list[dict[str, Any]] | None=None, candidate_route: int | None=None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/contracts_stock.py:10](../../../api/wms_api_server/app/modules/inventory/contracts_stock.py#L10)

```python
__init__(self, code: str, operation_id: str, oracle_code: int | None=None, rule_reason: str | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `super`, `super().__init__`

### wire

[Исходник: api/wms_api_server/app/modules/inventory/contracts_stock.py:32](../../../api/wms_api_server/app/modules/inventory/contracts_stock.py#L32)

```python
wire(self) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `any`, `isinstance`, `len`, `quantity_text`

### canonical_json

[Исходник: api/wms_api_server/app/modules/inventory/contracts_stock.py:63](../../../api/wms_api_server/app/modules/inventory/contracts_stock.py#L63)

```python
canonical_json(self) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `json.dumps`, `len`, `line.wire`, `result.encode`, `self.command_type.startswith`, `set`, `sorted`

### stock_compatibility_service

[Исходник: api/wms_api_server/app/modules/inventory/contracts_stock_settings.py:10](../../../api/wms_api_server/app/modules/inventory/contracts_stock_settings.py#L10)

```python
stock_compatibility_service() -> StockCompatibilityPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/contracts_stock_settings.py:4](../../../api/wms_api_server/app/modules/inventory/contracts_stock_settings.py#L4)

```python
__init__(self, message: str, status: int) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `super`, `super().__init__`

### set_compatibility

[Исходник: api/wms_api_server/app/modules/inventory/contracts_stock_settings.py:8](../../../api/wms_api_server/app/modules/inventory/contracts_stock_settings.py#L8)

```python
set_compatibility(self, enabled: bool, reason: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### store_return_receive_service

[Исходник: api/wms_api_server/app/modules/inventory/contracts_store_returns.py:22](../../../api/wms_api_server/app/modules/inventory/contracts_store_returns.py#L22)

```python
store_return_receive_service() -> StoreReturnReceivePort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/contracts_store_returns.py:5](../../../api/wms_api_server/app/modules/inventory/contracts_store_returns.py#L5)

```python
__init__(self, code: str, message: str, status: int=409, operation_id: str='') -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `super`, `super().__init__`

### page

[Исходник: api/wms_api_server/app/modules/inventory/contracts_store_returns.py:13](../../../api/wms_api_server/app/modules/inventory/contracts_store_returns.py#L13)

```python
page(self, ware_id: int, after: str, limit: int, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### source

[Исходник: api/wms_api_server/app/modules/inventory/contracts_store_returns.py:14](../../../api/wms_api_server/app/modules/inventory/contracts_store_returns.py#L14)

```python
source(self, ware_id: int, pickup_id: str, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### configure

[Исходник: api/wms_api_server/app/modules/inventory/contracts_store_returns.py:15](../../../api/wms_api_server/app/modules/inventory/contracts_store_returns.py#L15)

```python
configure(self, ware_id: int, supplier_cell: str, disposal_cell: str, expected_version: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### configure_reuse

[Исходник: api/wms_api_server/app/modules/inventory/contracts_store_returns.py:16](../../../api/wms_api_server/app/modules/inventory/contracts_store_returns.py#L16)

```python
configure_reuse(self, ware_id: int, receive_cell: str, expected_version: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### policy

[Исходник: api/wms_api_server/app/modules/inventory/contracts_store_returns.py:17](../../../api/wms_api_server/app/modules/inventory/contracts_store_returns.py#L17)

```python
policy(self, ware_id: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### pending

[Исходник: api/wms_api_server/app/modules/inventory/contracts_store_returns.py:18](../../../api/wms_api_server/app/modules/inventory/contracts_store_returns.py#L18)

```python
pending(self, ware_id: int, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### confirm

[Исходник: api/wms_api_server/app/modules/inventory/contracts_store_returns.py:19](../../../api/wms_api_server/app/modules/inventory/contracts_store_returns.py#L19)

```python
confirm(self, operation_id: str, pickup_id: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### supplier_handover_service

[Исходник: api/wms_api_server/app/modules/inventory/contracts_supplier_handover.py:8](../../../api/wms_api_server/app/modules/inventory/contracts_supplier_handover.py#L8)

```python
supplier_handover_service() -> SupplierHandoverPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### record

[Исходник: api/wms_api_server/app/modules/inventory/contracts_supplier_handover.py:4](../../../api/wms_api_server/app/modules/inventory/contracts_supplier_handover.py#L4)

```python
record(self, operation_id: str, dispatch_id: str, reference: str, document_hash: str, receiver: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### confirm

[Исходник: api/wms_api_server/app/modules/inventory/contracts_supplier_handover.py:5](../../../api/wms_api_server/app/modules/inventory/contracts_supplier_handover.py#L5)

```python
confirm(self, operation_id: str, handover_id: str, reference: str, reason: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### pending

[Исходник: api/wms_api_server/app/modules/inventory/contracts_supplier_handover.py:6](../../../api/wms_api_server/app/modules/inventory/contracts_supplier_handover.py#L6)

```python
pending(self, ware_id: int, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### supplier_return_service

[Исходник: api/wms_api_server/app/modules/inventory/contracts_supplier_return.py:9](../../../api/wms_api_server/app/modules/inventory/contracts_supplier_return.py#L9)

```python
supplier_return_service() -> SupplierReturnPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### prepare

[Исходник: api/wms_api_server/app/modules/inventory/contracts_supplier_return.py:5](../../../api/wms_api_server/app/modules/inventory/contracts_supplier_return.py#L5)

```python
prepare(self, operation_id: str, receipt_id: str, supplier_inn: str, reason: str, reference: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### pending

[Исходник: api/wms_api_server/app/modules/inventory/contracts_supplier_return.py:6](../../../api/wms_api_server/app/modules/inventory/contracts_supplier_return.py#L6)

```python
pending(self, ware_id: int, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### suppliers

[Исходник: api/wms_api_server/app/modules/inventory/contracts_supplier_return.py:7](../../../api/wms_api_server/app/modules/inventory/contracts_supplier_return.py#L7)

```python
suppliers(self) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### tare_service

[Исходник: api/wms_api_server/app/modules/inventory/contracts_tare.py:16](../../../api/wms_api_server/app/modules/inventory/contracts_tare.py#L16)

```python
tare_service() -> TarePort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/contracts_tare.py:4](../../../api/wms_api_server/app/modules/inventory/contracts_tare.py#L4)

```python
__init__(self, code: str, message: str, status: int=409, operation_id: str | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `super`, `super().__init__`

### post

[Исходник: api/wms_api_server/app/modules/inventory/contracts_tare.py:9](../../../api/wms_api_server/app/modules/inventory/contracts_tare.py#L9)

```python
post(self, kind: str, operation_id: str, source: dict[str, Any], metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### balances

[Исходник: api/wms_api_server/app/modules/inventory/contracts_tare.py:10](../../../api/wms_api_server/app/modules/inventory/contracts_tare.py#L10)

```python
balances(self, owner_ware_id: int, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### damage_custody

[Исходник: api/wms_api_server/app/modules/inventory/contracts_tare.py:11](../../../api/wms_api_server/app/modules/inventory/contracts_tare.py#L11)

```python
damage_custody(self, ware_id: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### damage_cases

[Исходник: api/wms_api_server/app/modules/inventory/contracts_tare.py:12](../../../api/wms_api_server/app/modules/inventory/contracts_tare.py#L12)

```python
damage_cases(self, ware_id: int, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### context

[Исходник: api/wms_api_server/app/modules/inventory/contracts_tare.py:13](../../../api/wms_api_server/app/modules/inventory/contracts_tare.py#L13)

```python
context(self, task_id: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### offers

[Исходник: api/wms_api_server/app/modules/inventory/contracts_tare.py:14](../../../api/wms_api_server/app/modules/inventory/contracts_tare.py#L14)

```python
offers(self, task_id: int, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### tare_assembly_service

[Исходник: api/wms_api_server/app/modules/inventory/contracts_tare_assembly.py:12](../../../api/wms_api_server/app/modules/inventory/contracts_tare_assembly.py#L12)

```python
tare_assembly_service() -> TareAssemblyPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### recovery_candidates

[Исходник: api/wms_api_server/app/modules/inventory/contracts_tare_assembly.py:4](../../../api/wms_api_server/app/modules/inventory/contracts_tare_assembly.py#L4)

```python
recovery_candidates(self, load_operation_id: str, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### loaded_bookings

[Исходник: api/wms_api_server/app/modules/inventory/contracts_tare_assembly.py:5](../../../api/wms_api_server/app/modules/inventory/contracts_tare_assembly.py#L5)

```python
loaded_bookings(self, ware_id: int, task_id: int, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### forecast

[Исходник: api/wms_api_server/app/modules/inventory/contracts_tare_assembly.py:6](../../../api/wms_api_server/app/modules/inventory/contracts_tare_assembly.py#L6)

```python
forecast(self, ware_id: int, wave_id: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### loss_cases

[Исходник: api/wms_api_server/app/modules/inventory/contracts_tare_assembly.py:7](../../../api/wms_api_server/app/modules/inventory/contracts_tare_assembly.py#L7)

```python
loss_cases(self, ware_id: int, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### catalog

[Исходник: api/wms_api_server/app/modules/inventory/contracts_tare_assembly.py:8](../../../api/wms_api_server/app/modules/inventory/contracts_tare_assembly.py#L8)

```python
catalog(self, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### availability

[Исходник: api/wms_api_server/app/modules/inventory/contracts_tare_assembly.py:9](../../../api/wms_api_server/app/modules/inventory/contracts_tare_assembly.py#L9)

```python
availability(self, ware_id: int, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### bookings

[Исходник: api/wms_api_server/app/modules/inventory/contracts_tare_assembly.py:10](../../../api/wms_api_server/app/modules/inventory/contracts_tare_assembly.py#L10)

```python
bookings(self, ware_id: int, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### tare_policy_service

[Исходник: api/wms_api_server/app/modules/inventory/contracts_tare_policy.py:8](../../../api/wms_api_server/app/modules/inventory/contracts_tare_policy.py#L8)

```python
tare_policy_service() -> TarePolicyPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### read

[Исходник: api/wms_api_server/app/modules/inventory/contracts_tare_policy.py:4](../../../api/wms_api_server/app/modules/inventory/contracts_tare_policy.py#L4)

```python
read(self, scope_kind: str, scope_key: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### configure

[Исходник: api/wms_api_server/app/modules/inventory/contracts_tare_policy.py:5](../../../api/wms_api_server/app/modules/inventory/contracts_tare_policy.py#L5)

```python
configure(self, scope_kind: str, scope_key: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### debt

[Исходник: api/wms_api_server/app/modules/inventory/contracts_tare_policy.py:6](../../../api/wms_api_server/app/modules/inventory/contracts_tare_policy.py#L6)

```python
debt(self, ware_id: int, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### get_task_or_404

[Исходник: api/wms_api_server/app/modules/inventory/contracts_task_actions.py:5](../../../api/wms_api_server/app/modules/inventory/contracts_task_actions.py#L5)

```python
get_task_or_404(self, task_id: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### assign_task

[Исходник: api/wms_api_server/app/modules/inventory/contracts_task_actions.py:6](../../../api/wms_api_server/app/modules/inventory/contracts_task_actions.py#L6)

```python
assign_task(self, task_id: int, request: WarehouseTaskStatusRequest) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### start_task

[Исходник: api/wms_api_server/app/modules/inventory/contracts_task_actions.py:7](../../../api/wms_api_server/app/modules/inventory/contracts_task_actions.py#L7)

```python
start_task(self, task_id: int, request: WarehouseTaskStatusRequest) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### cancel_task

[Исходник: api/wms_api_server/app/modules/inventory/contracts_task_actions.py:8](../../../api/wms_api_server/app/modules/inventory/contracts_task_actions.py#L8)

```python
cancel_task(self, task_id: int, request: WarehouseTaskStatusRequest) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/contracts_task_read.py:9](../../../api/wms_api_server/app/modules/inventory/contracts_task_read.py#L9)

```python
__init__(self, code: str, status: int=403) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `super`, `super().__init__`

### trace_manifest_service

[Исходник: api/wms_api_server/app/modules/inventory/contracts_trace_manifest.py:17](../../../api/wms_api_server/app/modules/inventory/contracts_trace_manifest.py#L17)

```python
trace_manifest_service() -> TraceManifestPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/contracts_trace_manifest.py:5](../../../api/wms_api_server/app/modules/inventory/contracts_trace_manifest.py#L5)

```python
__init__(self, code: str, message: str, status: int=409) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `super`, `super().__init__`

### import_manifest

[Исходник: api/wms_api_server/app/modules/inventory/contracts_trace_manifest.py:11](../../../api/wms_api_server/app/modules/inventory/contracts_trace_manifest.py#L11)

```python
import_manifest(self, operation_id: str, raw: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### list

[Исходник: api/wms_api_server/app/modules/inventory/contracts_trace_manifest.py:12](../../../api/wms_api_server/app/modules/inventory/contracts_trace_manifest.py#L12)

```python
list(self, ware_id: int, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### capture_context

[Исходник: api/wms_api_server/app/modules/inventory/contracts_trace_manifest.py:13](../../../api/wms_api_server/app/modules/inventory/contracts_trace_manifest.py#L13)

```python
capture_context(self, kind: str, document_id: int, article: str, cell: str, pallet: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### invalidate_aggregate

[Исходник: api/wms_api_server/app/modules/inventory/contracts_trace_manifest.py:14](../../../api/wms_api_server/app/modules/inventory/contracts_trace_manifest.py#L14)

```python
invalidate_aggregate(self, operation_id: str, request: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### aggregates

[Исходник: api/wms_api_server/app/modules/inventory/contracts_trace_manifest.py:15](../../../api/wms_api_server/app/modules/inventory/contracts_trace_manifest.py#L15)

```python
aggregates(self, origin: str, ware: int, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### waiting_task_dependency

[Исходник: api/wms_api_server/app/modules/inventory/contracts_waiting_tasks.py:20](../../../api/wms_api_server/app/modules/inventory/contracts_waiting_tasks.py#L20)

```python
waiting_task_dependency() -> WaitingTaskPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/contracts_waiting_tasks.py:11](../../../api/wms_api_server/app/modules/inventory/contracts_waiting_tasks.py#L11)

```python
__init__(self, code: str, message: str, status: int) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `super`, `super().__init__`

### plan

[Исходник: api/wms_api_server/app/modules/inventory/contracts_waiting_tasks.py:17](../../../api/wms_api_server/app/modules/inventory/contracts_waiting_tasks.py#L17)

```python
plan(self, request: WaitingTaskRequest, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### read

[Исходник: api/wms_api_server/app/modules/inventory/contracts_waiting_tasks.py:18](../../../api/wms_api_server/app/modules/inventory/contracts_waiting_tasks.py#L18)

```python
read(self, decision: str, actor: str, after: int, limit: int) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### warehouse_scale_service

[Исходник: api/wms_api_server/app/modules/inventory/contracts_warehouse_scale.py:89](../../../api/wms_api_server/app/modules/inventory/contracts_warehouse_scale.py#L89)

```python
warehouse_scale_service() -> WarehouseScalePort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/contracts_warehouse_scale.py:10](../../../api/wms_api_server/app/modules/inventory/contracts_warehouse_scale.py#L10)

```python
__init__(self, code: str, message: str, status: int=409) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `super`, `super().__init__`

### configure

[Исходник: api/wms_api_server/app/modules/inventory/contracts_warehouse_scale.py:82](../../../api/wms_api_server/app/modules/inventory/contracts_warehouse_scale.py#L82)

```python
configure(self, device: str, body: WarehouseScaleConfiguration, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### capture

[Исходник: api/wms_api_server/app/modules/inventory/contracts_warehouse_scale.py:83](../../../api/wms_api_server/app/modules/inventory/contracts_warehouse_scale.py#L83)

```python
capture(self, body: WarehouseScalePacket | WarehouseFinalScalePacket, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### readings

[Исходник: api/wms_api_server/app/modules/inventory/contracts_warehouse_scale.py:84](../../../api/wms_api_server/app/modules/inventory/contracts_warehouse_scale.py#L84)

```python
readings(self, task: int, line: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### reading

[Исходник: api/wms_api_server/app/modules/inventory/contracts_warehouse_scale.py:85](../../../api/wms_api_server/app/modules/inventory/contracts_warehouse_scale.py#L85)

```python
reading(self, key: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### final_readings

[Исходник: api/wms_api_server/app/modules/inventory/contracts_warehouse_scale.py:86](../../../api/wms_api_server/app/modules/inventory/contracts_warehouse_scale.py#L86)

```python
final_readings(self, task: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/contracts_wave_planning.py:5](../../../api/wms_api_server/app/modules/inventory/contracts_wave_planning.py#L5)

```python
__init__(self, code: str, status: int=409) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `super`, `super().__init__`

### weighted_case_service

[Исходник: api/wms_api_server/app/modules/inventory/contracts_weighted_case.py:32](../../../api/wms_api_server/app/modules/inventory/contracts_weighted_case.py#L32)

```python
weighted_case_service() -> WeightedCasePort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### short_weight_preview

[Исходник: api/wms_api_server/app/modules/inventory/contracts_weighted_case.py:26](../../../api/wms_api_server/app/modules/inventory/contracts_weighted_case.py#L26)

```python
short_weight_preview(self, short: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### weight_preview

[Исходник: api/wms_api_server/app/modules/inventory/contracts_weighted_case.py:27](../../../api/wms_api_server/app/modules/inventory/contracts_weighted_case.py#L27)

```python
weight_preview(self, task: int, line: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### weigh_line

[Исходник: api/wms_api_server/app/modules/inventory/contracts_weighted_case.py:28](../../../api/wms_api_server/app/modules/inventory/contracts_weighted_case.py#L28)

```python
weigh_line(self, task: int, line: int, request: WeighedLineRequest, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### confirm

[Исходник: api/wms_api_server/app/modules/inventory/contracts_weighted_case.py:29](../../../api/wms_api_server/app/modules/inventory/contracts_weighted_case.py#L29)

```python
confirm(self, task: int, line: int, request: WeightedCaseRequest, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### weighted_plan_service

[Исходник: api/wms_api_server/app/modules/inventory/contracts_weighted_plan.py:29](../../../api/wms_api_server/app/modules/inventory/contracts_weighted_plan.py#L29)

```python
weighted_plan_service() -> WeightedPlanPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### approval_options

[Исходник: api/wms_api_server/app/modules/inventory/contracts_weighted_plan.py:23](../../../api/wms_api_server/app/modules/inventory/contracts_weighted_plan.py#L23)

```python
approval_options(self, row: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### approve

[Исходник: api/wms_api_server/app/modules/inventory/contracts_weighted_plan.py:24](../../../api/wms_api_server/app/modules/inventory/contracts_weighted_plan.py#L24)

```python
approve(self, body: WeightedBoxChoiceRequest, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### cancel

[Исходник: api/wms_api_server/app/modules/inventory/contracts_weighted_plan.py:25](../../../api/wms_api_server/app/modules/inventory/contracts_weighted_plan.py#L25)

```python
cancel(self, choice: str, reason: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### options

[Исходник: api/wms_api_server/app/modules/inventory/contracts_weighted_plan.py:26](../../../api/wms_api_server/app/modules/inventory/contracts_weighted_plan.py#L26)

```python
options(self, row: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### assert_capture_policy

[Исходник: api/wms_api_server/app/modules/inventory/domain/capture_policy.py:4](../../../api/wms_api_server/app/modules/inventory/domain/capture_policy.py#L4)

```python
assert_capture_policy(payload: dict[str, Any], policy_version: int, profiles: dict[tuple[str, str], dict[str, Any]]) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `all`, `isinstance`, `item.values`, `len`, `payload.get`, `set`

### assert_matching_composition

[Исходник: api/wms_api_server/app/modules/inventory/domain/carrier_shipment.py:7](../../../api/wms_api_server/app/modules/inventory/domain/carrier_shipment.py#L7)

```python
assert_matching_composition(physical_rows: Sequence[tuple[Any, ...]], document_rows: Sequence[tuple[Any, ...]]) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Fraction`, `ValueError`, `any`, `convert_exact`, `int`, `len`, `physical.get`, `planned.get`, `quantity_text`

### close_transition

[Исходник: api/wms_api_server/app/modules/inventory/domain/case_close_state.py:6](../../../api/wms_api_server/app/modules/inventory/domain/case_close_state.py#L6)

```python
close_transition(status: str | None, shipped_operation: str | None) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### validate_uri

[Исходник: api/wms_api_server/app/modules/inventory/domain/cctv_archive.py:8](../../../api/wms_api_server/app/modules/inventory/domain/cctv_archive.py#L8)

```python
validate_uri(uri: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `urlsplit`

### validate_template

[Исходник: api/wms_api_server/app/modules/inventory/domain/cctv_archive.py:13](../../../api/wms_api_server/app/modules/inventory/domain/cctv_archive.py#L13)

```python
validate_template(template: str, offset: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Formatter`, `Formatter().parse`, `ValueError`, `fields.add`, `map`, `offset[1:].split`, `set`, `template.format`, `validate_uri`

### archive_uri

[Исходник: api/wms_api_server/app/modules/inventory/domain/cctv_archive.py:28](../../../api/wms_api_server/app/modules/inventory/domain/cctv_archive.py#L28)

```python
archive_uri(template: str, offset: str, created_at: datetime, cell: str, viewpoint: str, before: int, after: int) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(moment + timedelta(seconds=after)).isoformat`, `(moment - timedelta(seconds=before)).isoformat`, `created_at.replace`, `map`, `offset.startswith`, `offset[1:].split`, `quote`, `template.format`, `timedelta`, `timezone`, `validate_template`, `validate_uri`, `values.items`

### physical_composition

[Исходник: api/wms_api_server/app/modules/inventory/domain/fulfillment_fact.py:6](../../../api/wms_api_server/app/modules/inventory/domain/fulfillment_fact.py#L6)

```python
physical_composition(rows: list[tuple]) -> tuple[list[dict], str | None, str | None]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `ValueError`, `iter`, `len`, `localcontext`, `next`, `quantities.get`, `quantities.items`, `quantities.values`, `quantity_text`, `sorted`, `sum`

### departure_subtree

[Исходник: api/wms_api_server/app/modules/inventory/domain/historical_hu.py:5](../../../api/wms_api_server/app/modules/inventory/domain/historical_hu.py#L5)

```python
departure_subtree(snapshot: dict, identifier: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `all`, `ancestors.append`, `by_id.keys`, `children.get`, `children.setdefault`, `children.setdefault(edge['parent'], []).append`, `deepcopy`, `len`, `pending.extend`, `pending.pop`, `selected.add`, `set`, `snapshot.get`, `sum`

### incoming_readiness

[Исходник: api/wms_api_server/app/modules/inventory/domain/interwarehouse_readiness.py:5](../../../api/wms_api_server/app/modules/inventory/domain/interwarehouse_readiness.py#L5)

```python
incoming_readiness(trip_id: int, warehouse_id: int, rows: list[dict[str, Any]]) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `all`, `bool`, `format`, `len`, `row.get`, `sorted`, `sum`, `totals.get`, `totals.items`

### normalize_interwarehouse_scans

[Исходник: api/wms_api_server/app/modules/inventory/domain/interwarehouse_scans.py:6](../../../api/wms_api_server/app/modules/inventory/domain/interwarehouse_scans.py#L6)

```python
normalize_interwarehouse_scans(metadata: dict[str, Any]) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `code.encode`, `dict`, `isinstance`, `len`, `normalize_unit_scan_codes`, `normalized.append`, `result.get`, `result.pop`, `set`, `sha256`, `sha256(code.encode('utf-8')).hexdigest`

### phase_timing

[Исходник: api/wms_api_server/app/modules/inventory/domain/interwarehouse_timing.py:7](../../../api/wms_api_server/app/modules/inventory/domain/interwarehouse_timing.py#L7)

```python
phase_timing(due: str, actual: str | None, observed: str, reached: str) -> dict[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `ValueError`, `datetime.fromisoformat`, `deadline.utcoffset`, `fact.utcoffset`, `format`, `max`

### annotate_timing

[Исходник: api/wms_api_server/app/modules/inventory/domain/interwarehouse_timing.py:19](../../../api/wms_api_server/app/modules/inventory/domain/interwarehouse_timing.py#L19)

```python
annotate_timing(row: dict[str, Any]) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `phase_timing`

### canonical_mark

[Исходник: api/wms_api_server/app/modules/inventory/domain/mark_identity.py:5](../../../api/wms_api_server/app/modules/inventory/domain/mark_identity.py#L5)

```python
canonical_mark(system: str, profile: str, raw: str, expected_gtin: str | None=None) -> dict[str, str | None]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `any`, `enumerate`, `human.group`, `int`, `len`, `ord`, `profile.upper`, `re.fullmatch`, `reversed`, `sum`, `value.encode`, `value.startswith`, `value[18:].split`, `value[2:16].isdigit`, `value[:14].isdigit`

### normalize_unit_scan_codes

[Исходник: api/wms_api_server/app/modules/inventory/domain/mark_identity.py:42](../../../api/wms_api_server/app/modules/inventory/domain/mark_identity.py#L42)

```python
normalize_unit_scan_codes(scans: list[dict[str, str]]) -> list[dict[str, str]]
```

One canonical identity/hash contract; optional physical recipient disposition.

Вызывает: `ValueError`, `canonical_mark`, `canonical_mark(scan['system_code'], scan['profile_code'], scan['code'])['identity'].encode`, `result.append`, `scan.get`, `sha256`, `sha256(canonical_mark(scan['system_code'], scan['profile_code'], scan['code'])['identity'].encode('utf-8')).hexdigest`

### normalize_incoming_sscc

[Исходник: api/wms_api_server/app/modules/inventory/domain/pallet_identifiers.py:1](../../../api/wms_api_server/app/modules/inventory/domain/pallet_identifiers.py#L1)

```python
normalize_incoming_sscc(value: object) -> object
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `isinstance`, `len`, `value.startswith`, `value[2:].isdigit`, `value[4:].isdigit`

### normalize_receipt_identifier

[Исходник: api/wms_api_server/app/modules/inventory/domain/pallet_identifiers.py:14](../../../api/wms_api_server/app/modules/inventory/domain/pallet_identifiers.py#L14)

```python
normalize_receipt_identifier(value: object) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `any`, `character.isspace`, `isinstance`, `len`, `normalize_incoming_sscc`, `sscc_value`, `value.encode`, `value.isascii`, `value.isdigit`, `value.isprintable`

### allocate_pool

[Исходник: api/wms_api_server/app/modules/inventory/domain/pool_allocation.py:17](../../../api/wms_api_server/app/modules/inventory/domain/pool_allocation.py#L17)

```python
allocate_pool(demands: tuple[PoolDemand, ...], available: Decimal, step: Decimal) -> PoolAllocation
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `PoolAllocation`, `ValueError`, `any`, `enumerate`, `heapify`, `heappop`, `heappush`, `int`, `isinstance`, `len`, `localcontext`, `max`, `min`, `range`, `sorted`, `sum`, `units.copy`, `v.as_tuple`, `v.is_finite`, `zip`

### quality_label_html

[Исходник: api/wms_api_server/app/modules/inventory/domain/quality_label.py:8](../../../api/wms_api_server/app/modules/inventory/domain/quality_label.py#L8)

```python
quality_label_html(snapshot: Mapping[str, Any], actor: str) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `''.join`, `datetime.now`, `datetime.now(timezone.utc).isoformat`, `escape`, `exemption.get`, `fields.extend`, `isinstance`, `re.fullmatch`, `snapshot.get`, `str`

### propose_receipt_layout

[Исходник: api/wms_api_server/app/modules/inventory/domain/receipt_layout.py:8](../../../api/wms_api_server/app/modules/inventory/domain/receipt_layout.py#L8)

```python
propose_receipt_layout(remaining: str, base_uom: str, norm: str | None, pallet_count: int | None, quantities: list[str] | None, quantity_step: str | None=None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `Fraction`, `ValueError`, `base_uom.upper`, `capacity.is_finite`, `divmod`, `enumerate`, `format`, `int`, `isinstance`, `len`, `range`, `step.is_finite`, `step.normalize`, `step.normalize().as_tuple`, `sum`, `total.is_finite`, `value.is_finite`, `value.normalize`, `value.normalize().as_tuple`

### sscc_value

[Исходник: api/wms_api_server/app/modules/inventory/domain/regulatory_pallet.py:4](../../../api/wms_api_server/app/modules/inventory/domain/regulatory_pallet.py#L4)

```python
sscc_value(value: Any) -> str | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `code.isascii`, `code.isdigit`, `code.startswith`, `enumerate`, `int`, `isinstance`, `len`, `reversed`, `sum`

### receipt_sscc

[Исходник: api/wms_api_server/app/modules/inventory/domain/regulatory_pallet.py:19](../../../api/wms_api_server/app/modules/inventory/domain/regulatory_pallet.py#L19)

```python
receipt_sscc(pallet: str, declared: Any, scanned: list[dict[str, Any]]) -> str | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `iter`, `len`, `next`, `sscc_value`

### unpicked_demand

[Исходник: api/wms_api_server/app/modules/inventory/domain/slotting_demand.py:5](../../../api/wms_api_server/app/modules/inventory/domain/slotting_demand.py#L5)

```python
unpicked_demand(order: dict[str, Any]) -> Decimal
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `ValueError`, `localcontext`, `min`

### quantity_scenario

[Исходник: api/wms_api_server/app/modules/inventory/domain/slotting_demand.py:15](../../../api/wms_api_server/app/modules/inventory/domain/slotting_demand.py#L15)

```python
quantity_scenario(firm: Decimal, forecast: Decimal | None, old_credit: Decimal, inbound: Decimal, pallet_multiple: Decimal | None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(deficit / pallet_multiple).to_integral_value`, `Decimal`, `ValueError`, `format`, `localcontext`, `max`, `min`

### recommend_range

[Исходник: api/wms_api_server/app/modules/inventory/domain/slotting_recommendation.py:5](../../../api/wms_api_server/app/modules/inventory/domain/slotting_recommendation.py#L5)

```python
recommend_range(scenario: dict[str, Any], current: list[dict[str, Any]], candidates: list[dict[str, Any]], costs: list[dict[str, Any]]) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `ValueError`, `any`, `cost_by_face.get`, `format`, `int`, `len`, `localcontext`, `min`, `missing_cost.append`, `ranked.append`, `ranked.sort`, `set`, `sum`

### check_digit

[Исходник: api/wms_api_server/app/modules/inventory/domain/sscc_label.py:9](../../../api/wms_api_server/app/modules/inventory/domain/sscc_label.py#L9)

```python
check_digit(body: str) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `enumerate`, `int`, `reversed`, `str`, `sum`

### barcode_svg

[Исходник: api/wms_api_server/app/modules/inventory/domain/sscc_label.py:13](../../../api/wms_api_server/app/modules/inventory/domain/sscc_label.py#L13)

```python
barcode_svg(sscc: str) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `''.join`, `ValueError`, `bars.append`, `check_digit`, `enumerate`, `int`, `len`, `range`, `sscc.isdigit`, `sum`

### label_html

[Исходник: api/wms_api_server/app/modules/inventory/domain/sscc_label.py:28](../../../api/wms_api_server/app/modules/inventory/domain/sscc_label.py#L28)

```python
label_html(data: dict, compact: bool=False) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `''.join`, `FIELD_LABELS.get`, `barcode_svg`, `data.items`, `escape`, `html.replace`, `html.replace('size:105mm 148mm', 'size:100mm 70mm').replace`, `str`

### label_zpl

[Исходник: api/wms_api_server/app/modules/inventory/domain/sscc_label.py:35](../../../api/wms_api_server/app/modules/inventory/domain/sscc_label.py#L35)

```python
label_zpl(data: dict, dpi: int=203, compact: bool=False) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `''.join`, `'\n'.join`, `FIELD_LABELS.get`, `commands.append`, `data.items`, `enumerate`, `px`, `round`, `text.encode`

### quantity_text

[Исходник: api/wms_api_server/app/modules/inventory/domain/stock_quantity.py:8](../../../api/wms_api_server/app/modules/inventory/domain/stock_quantity.py#L8)

```python
quantity_text(value: str | Decimal, scale: int=9) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `TypeError`, `ValueError`, `digits.pop`, `format`, `isinstance`, `list`, `number.as_tuple`, `number.is_finite`, `text.rstrip`, `text.rstrip('0').rstrip`

### convert_exact

[Исходник: api/wms_api_server/app/modules/inventory/domain/stock_quantity.py:27](../../../api/wms_api_server/app/modules/inventory/domain/stock_quantity.py#L27)

```python
convert_exact(value: str | Decimal, numerator: int, denominator: int, scale: int) -> Decimal
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `Fraction`, `ValueError`, `digits.zfill`, `isinstance`, `quantity_text`, `str`

### ordered_resources

[Исходник: api/wms_api_server/app/modules/inventory/domain/stock_resources.py:30](../../../api/wms_api_server/app/modules/inventory/domain/stock_resources.py#L30)

```python
ordered_resources(resources: list[StockResource]) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `item.encoded`, `key.hex`, `key.hex().upper`, `sorted`

### encoded

[Исходник: api/wms_api_server/app/modules/inventory/domain/stock_resources.py:13](../../../api/wms_api_server/app/modules/inventory/domain/stock_resources.py#L13)

```python
encoded(self) -> bytes
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `component.encode`, `isinstance`, `len`, `str`, `str(len(raw)).encode`

### wire

[Исходник: api/wms_api_server/app/modules/inventory/domain/stock_resources.py:26](../../../api/wms_api_server/app/modules/inventory/domain/stock_resources.py#L26)

```python
wire(self) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.encoded`, `self.encoded().hex`, `self.encoded().hex().upper`

### _text

[Исходник: api/wms_api_server/app/modules/inventory/domain/trace_manifest.py:9](../../../api/wms_api_server/app/modules/inventory/domain/trace_manifest.py#L9)

```python
_text(value: Any, limit: int) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `isinstance`, `len`, `value.encode`

### _number

[Исходник: api/wms_api_server/app/modules/inventory/domain/trace_manifest.py:14](../../../api/wms_api_server/app/modules/inventory/domain/trace_manifest.py#L14)

```python
_number(value: Any) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `isinstance`

### parse_manifest

[Исходник: api/wms_api_server/app/modules/inventory/domain/trace_manifest.py:19](../../../api/wms_api_server/app/modules/inventory/domain/trace_manifest.py#L19)

```python
parse_manifest(raw: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `_number`, `_text`, `isinstance`, `json.loads`, `len`, `raw.encode`, `set`

### validate_units

[Исходник: api/wms_api_server/app/modules/inventory/domain/trace_manifest.py:36](../../../api/wms_api_server/app/modules/inventory/domain/trace_manifest.py#L36)

```python
validate_units(document: dict[str, Any], profiles: dict[tuple[str, str], dict[str, Any]], gtin: str | None) -> dict[str, dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `_text`, `canonical_mark`, `format`, `isinstance`, `len`, `profiles.items`, `set`, `unit_quantity`

### resolve_aggregates

[Исходник: api/wms_api_server/app/modules/inventory/domain/trace_manifest.py:77](../../../api/wms_api_server/app/modules/inventory/domain/trace_manifest.py#L77)

```python
resolve_aggregates(document: dict[str, Any], units: dict[str, dict[str, Any]], profiles: dict[tuple[str, str], dict[str, Any]]) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `_text`, `code.encode`, `code_keys.add`, `isinstance`, `len`, `members.add`, `nodes.items`, `pending.append`, `pending.pop`, `result.append`, `root['code'].encode`, `set`, `sha256`, `sha256(code.encode()).hexdigest`, `sha256(root['code'].encode()).hexdigest`, `sorted`

### unit_quantity

[Исходник: api/wms_api_server/app/modules/inventory/domain/unit_quantity.py:6](../../../api/wms_api_server/app/modules/inventory/domain/unit_quantity.py#L6)

```python
unit_quantity(value: object, base_uom: str, fallback: Decimal | None) -> Decimal
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `ValueError`, `base_uom.upper`, `quantity.is_finite`, `quantity.normalize`, `quantity.normalize().as_tuple`, `str`

### bind_alternative_face

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/alternative_face_binding.py:4](../../../api/wms_api_server/app/modules/inventory/infrastructure/alternative_face_binding.py#L4)

```python
bind_alternative_face(cursor: Any, wave_id: int, row_id: int, article: str, old_cell: str, face: int, cell: str, route_cell: int | None, route_sequence: int | None, sequence: int | None, unit_volume: Any, base: str, actor: str, ids: str, source_reservation: int | None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cursor.execute`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/alternative_pick_faces.py:8](../../../api/wms_api_server/app/modules/inventory/infrastructure/alternative_pick_faces.py#L8)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### route_wave

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/alternative_pick_faces.py:11](../../../api/wms_api_server/app/modules/inventory/infrastructure/alternative_pick_faces.py#L11)

```python
route_wave(self, wave_id: int, actor: str) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `ValueError`, `cursor.execute`, `cursor.fetchall`, `cursor.fetchone`, `int`, `len`, `self._release_empty`, `self._route`, `self.gateway.transaction`, `str`

### _route

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/alternative_pick_faces.py:47](../../../api/wms_api_server/app/modules/inventory/infrastructure/alternative_pick_faces.py#L47)

```python
_route(self, cursor: Any, wave_id: int, warehouse: int, route_id: int | None, row_id: int, article: str, old_cell: str, demand: Decimal, source_reservation: int | None, actor: str, pick_task: int | None, pallet: str | None) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `','.join`, `Decimal`, `ValueError`, `bind_alternative_face`, `cursor.execute`, `cursor.fetchall`, `cursor.fetchone`, `int`, `len`, `max`, `self._candidates`, `str`, `sum`

### _release_empty

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/alternative_pick_faces.py:142](../../../api/wms_api_server/app/modules/inventory/infrastructure/alternative_pick_faces.py#L142)

```python
_release_empty(cursor: Any, warehouse: int, actor: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cursor.execute`

### _candidates

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/alternative_pick_faces.py:157](../../../api/wms_api_server/app/modules/inventory/infrastructure/alternative_pick_faces.py#L157)

```python
_candidates(cursor: Any, warehouse: int, route_id: int | None, old_cell: str) -> list[tuple[Any, ...]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `cursor.execute`, `cursor.fetchall`, `len`

### plan_births

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/birth_capture.py:10](../../../api/wms_api_server/app/modules/inventory/infrastructure/birth_capture.py#L10)

```python
plan_births(cursor: Any, document: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ReceivingMarks`, `ReceivingMarks(cursor).resolve`, `ValueError`, `aliases.values`, `bindings.append`, `births.append`, `candidates.append`, `canonical_mark`, `codes.items`, `convert_exact`, `cursor.execute`, `cursor.fetchall`, `cursor.fetchone`, `format`, `identities.append`, `int`, `len`, `list`, `marks.get`, `marks['units'].items`, `meta.get`, `min`, `normalized['identity'].encode`, `physical_identity.encode`, `provided[uid].get`, `set`, `sha256`, `sha256(normalized['identity'].encode()).hexdigest`, `sha256(physical_identity.encode()).hexdigest`, `str`, `str(cursor.fetchone()[0]).zfill`, `sum`

### stage_births

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/birth_capture.py:76](../../../api/wms_api_server/app/modules/inventory/infrastructure/birth_capture.py#L76)

```python
stage_births(cursor: Any, document: dict[str, Any], captures: dict[str, Any]) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ReceivingMarks`, `ReceivingMarks(cursor).persist`, `captures[birth['uid']].get`, `cursor.execute`, `cursor.fetchone`, `hasattr`, `isinstance`, `json.loads`, `plan.get`, `raw.read`

### prepare_birth_capture

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/birth_capture_commands.py:8](../../../api/wms_api_server/app/modules/inventory/infrastructure/birth_capture_commands.py#L8)

```python
prepare_birth_capture(cursor: Any, document: dict[str, Any], operation_id: str) -> tuple[str | None, dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockPostingError`, `cursor.execute`, `cursor.fetchone`, `isinstance`, `json.dumps`, `plan_births`, `str`

### stage_checked_births

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/birth_capture_commands.py:20](../../../api/wms_api_server/app/modules/inventory/infrastructure/birth_capture_commands.py#L20)

```python
stage_checked_births(cursor: Any, document: dict[str, Any], captures: dict[str, Any]) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockPostingError`, `stage_births`, `str`

### validate_close_content

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/case_carrier_close.py:10](../../../api/wms_api_server/app/modules/inventory/infrastructure/case_carrier_close.py#L10)

```python
validate_close_content(cur: Any, task: int, actor: str, assignee: str | None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `cur.execute`, `cur.fetchone`

### close_case_carrier

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/case_carrier_close.py:37](../../../api/wms_api_server/app/modules/inventory/infrastructure/case_carrier_close.py#L37)

```python
close_case_carrier(gateway: Any, task: int, request: Any, assert_scope: Callable[[Any, int, str, str], None]) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `assert_scope`, `close_replay`, `close_transition`, `cur.execute`, `cur.fetchone`, `getattr`, `json.dumps`, `json.dumps(body, ensure_ascii=True).encode`, `len`, `receipt_task_metadata`, `record_close`, `request.model_dump`, `validate_close_content`

### close_replay

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/case_close_journal.py:8](../../../api/wms_api_server/app/modules/inventory/infrastructure/case_close_journal.py#L8)

```python
close_replay(cur: Any, operation: str | None, task: int, actor: str, body: dict[str, Any]) -> dict[str, Any] | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `cur.execute`, `cur.fetchone`, `data.get`, `hasattr`, `json.loads`, `row[3].read`

### record_close

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/case_close_journal.py:26](../../../api/wms_api_server/app/modules/inventory/infrastructure/case_close_journal.py#L26)

```python
record_close(cur: Any, operation: str | None, task: int, actor: str, body: dict[str, Any], result: dict[str, Any]) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `body.get`, `cur.execute`, `cur.var`, `json.dumps`, `result.get`, `wire.setvalue`

### write_case_event

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/case_events.py:4](../../../api/wms_api_server/app/modules/inventory/infrastructure/case_events.py#L4)

```python
write_case_event(gateway: Any, case_pick_task_id: int | None, line_id: int | None, event_type: str, request: Any, actor: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `data.get`, `gateway.execute_plsql`, `hasattr`, `request.model_dump`, `str`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/case_labels.py:13](../../../api/wms_api_server/app/modules/inventory/infrastructure/case_labels.py#L13)

```python
__init__(self, gateway: OracleGateway) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### _command

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/case_labels.py:16](../../../api/wms_api_server/app/modules/inventory/infrastructure/case_labels.py#L16)

```python
_command(self, procedure: str, task: int, value: str, actor: str, operation: str='') -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockPostingError`, `q.callproc`, `q.var`, `read_oracle_json`, `receipt_task_metadata`, `result.getvalue`, `str`, `str(error.message).split`

### issue

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/case_labels.py:26](../../../api/wms_api_server/app/modules/inventory/infrastructure/case_labels.py#L26)

```python
issue(self, task: int, request: CaseSsccLabelRequest, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `json.dumps`, `request.model_dump`, `self._command`

### confirm

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/case_labels.py:30](../../../api/wms_api_server/app/modules/inventory/infrastructure/case_labels.py#L30)

```python
confirm(self, task: int, scan: str, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockPostingError`, `normalize_incoming_sscc`, `self._command`, `str`

### current

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/case_labels.py:35](../../../api/wms_api_server/app/modules/inventory/infrastructure/case_labels.py#L35)

```python
current(self, task: int, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockPostingError`, `int`, `q.callproc`, `q.execute`, `q.fetchone`, `read_oracle_json`, `row[1].isoformat`, `self.gateway.transaction`, `str`, `str(error.message).split`

### document

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/case_labels.py:50](../../../api/wms_api_server/app/modules/inventory/infrastructure/case_labels.py#L50)

```python
document(self, task: int, actor: str, format: str, dpi: int) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockPostingError`, `current.get`, `label_html`, `label_zpl`, `self.current`, `str`

### resolve_case_codes

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/case_pick_commands.py:12](../../../api/wms_api_server/app/modules/inventory/infrastructure/case_pick_commands.py#L12)

```python
resolve_case_codes(gateway: Any, task_id: int, line_id: int, scans: Sequence[Any]) -> tuple[str, ...]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `any`, `batch.append`, `canonical_mark`, `canonical_mark(scan.system_code, scan.profile_code, scan.code)['identity'].encode`, `cursor.execute`, `cursor.var`, `enumerate`, `gateway.transaction`, `identities.add`, `int`, `json.dumps`, `len`, `range`, `result.values`, `set`, `sha256`, `sha256(canonical_mark(scan.system_code, scan.profile_code, scan.code)['identity'].encode()).hexdigest`, `sorted`, `tuple`, `wire.setvalue`

### post_case_pick

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/case_pick_commands.py:58](../../../api/wms_api_server/app/modules/inventory/infrastructure/case_pick_commands.py#L58)

```python
post_case_pick(gateway: Any, task_id: int, line_id: int, request: Any) -> dict[str, Any] | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockCommand`, `StockPosting`, `StockPosting().post`, `StockPostingError`, `ValueError`, `gateway.fetch_all`, `hasattr`, `isinstance`, `json.dumps`, `json.dumps(submitted, ensure_ascii=True).encode`, `json.loads`, `len`, `old['metadata'].get`, `quantity_text`, `request.model_dump`, `request.offline_event_id.encode`, `require_active_release`, `resolve_case_codes`, `sha256`, `sha256(request.offline_event_id.encode()).hexdigest`, `tuple`, `wire.read`

### case_pick_policy

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/case_pick_policy.py:3](../../../api/wms_api_server/app/modules/inventory/infrastructure/case_pick_policy.py#L3)

```python
case_pick_policy(gateway: Any, task_id: int, line_id: int) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LookupError`, `ValueError`, `bool`, `gateway.fetch_all`, `len`

### bind_case_shipment

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/case_shipment_binding.py:13](../../../api/wms_api_server/app/modules/inventory/infrastructure/case_shipment_binding.py#L13)

```python
bind_case_shipment(gateway: OracleGateway | TransactionGateway, task_id: int, pallet_identifier: str, scan_container: str, expected_version: int, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `LookupError`, `ValueError`, `assert_matching_composition`, `cur.execute`, `cur.fetchall`, `cur.fetchmany`, `cur.fetchone`, `cur.setinputsizes`, `hasattr`, `json.dumps`, `json.loads`, `len`, `physical_composition`, `receipt_task_metadata`, `saved.read`

### post_short_approval

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/case_short_commands.py:12](../../../api/wms_api_server/app/modules/inventory/infrastructure/case_short_commands.py#L12)

```python
post_short_approval(gateway: OracleGateway | TransactionGateway, short_id: int, request: CasePickShortDecisionRequest) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockCommand`, `StockPosting`, `StockPosting().post`, `ValueError`, `require_active_release`, `str`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/case_task_services.py:8](../../../api/wms_api_server/app/modules/inventory/infrastructure/case_task_services.py#L8)

```python
__init__(self, gateway: OracleGateway) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### marking_policy

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/case_task_services.py:9](../../../api/wms_api_server/app/modules/inventory/infrastructure/case_task_services.py#L9)

```python
marking_policy(self, task: int, line: int, actor: str, assert_scope: Callable[[Any, int, str, str], None]) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TransactionGateway`, `assert_scope`, `case_pick_policy`, `cur.execute`, `self.gateway.transaction`

### bind_shipment

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/case_task_services.py:15](../../../api/wms_api_server/app/modules/inventory/infrastructure/case_task_services.py#L15)

```python
bind_shipment(self, task: int, pallet: str, container: str, version: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `bind_case_shipment`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/case_type.py:7](../../../api/wms_api_server/app/modules/inventory/infrastructure/case_type.py#L7)

```python
__init__(self, gateway: Any, posting: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### read

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/case_type.py:10](../../../api/wms_api_server/app/modules/inventory/infrastructure/case_type.py#L10)

```python
read(self, task_id: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockPostingError`, `cur.callfunc`, `cur.execute`, `getattr`, `read_oracle_json`, `self.gateway.transaction`, `str`, `str(exc.args[0]).split`

### change

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/case_type.py:21](../../../api/wms_api_server/app/modules/inventory/infrastructure/case_type.py#L21)

```python
change(self, task_id: int, operation: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockCommand`, `self.posting.post`

### cursor_rows

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/composition_provenance.py:5](../../../api/wms_api_server/app/modules/inventory/infrastructure/composition_provenance.py#L5)

```python
cursor_rows(cur: Any) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `column[0].lower`, `cur.fetchall`, `dict`, `zip`

### birth_provenance

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/composition_provenance.py:9](../../../api/wms_api_server/app/modules/inventory/infrastructure/composition_provenance.py#L9)

```python
birth_provenance(cur: Any, pallet: str) -> tuple[list[dict[str, Any]], bool]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.execute`, `cursor_rows`, `len`, `read_oracle_json`, `row.pop`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/configuration.py:7](../../../api/wms_api_server/app/modules/inventory/infrastructure/configuration.py#L7)

```python
__init__(self, gateway: OracleGateway) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### get

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/configuration.py:10](../../../api/wms_api_server/app/modules/inventory/infrastructure/configuration.py#L10)

```python
get(self, warehouse: int) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### read_rule

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/configuration.py:14](../../../api/wms_api_server/app/modules/inventory/infrastructure/configuration.py#L14)

```python
read_rule(self, warehouse: int, key: str, kind: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### save

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/configuration.py:21](../../../api/wms_api_server/app/modules/inventory/infrastructure/configuration.py#L21)

```python
save(self, warehouse: int, body: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `LookupError`, `body.get`, `bool`, `configuration_transaction`, `cur.execute`, `cur.fetchone`, `int`, `self.get`, `str`

### sku_rule

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/configuration.py:37](../../../api/wms_api_server/app/modules/inventory/infrastructure/configuration.py#L37)

```python
sku_rule(self, warehouse: int, articul: str, body: dict, actor: str='API') -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LookupError`, `ValueError`, `body.get`, `configuration_transaction`, `cur.execute`, `cur.fetchone`, `int`

### cell_rule

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/configuration.py:48](../../../api/wms_api_server/app/modules/inventory/infrastructure/configuration.py#L48)

```python
cell_rule(self, warehouse: int, cell: str, body: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LookupError`, `ValueError`, `body.get`, `configuration_transaction`, `cur.execute`, `cur.fetchone`

### release_document_reservations

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/document_reservation_commands.py:12](../../../api/wms_api_server/app/modules/inventory/infrastructure/document_reservation_commands.py#L12)

```python
release_document_reservations(gateway: OracleGateway | TransactionGateway, document_type: str, document_id: int, actor: str, reason: str, *, only_cancelled: bool=False, reservation_kind: str | None=None) -> bool
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `StockCommand`, `StockPosting`, `StockPosting().post`, `ValueError`, `int`, `require_active_release`, `uuid4`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/fullpal_shipment.py:11](../../../api/wms_api_server/app/modules/inventory/infrastructure/fullpal_shipment.py#L11)

```python
__init__(self, gateway: OracleGateway | TransactionGateway) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### preview

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/fullpal_shipment.py:14](../../../api/wms_api_server/app/modules/inventory/infrastructure/fullpal_shipment.py#L14)

```python
preview(self, task_id: int, actor: str | None=None) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockPostingError`, `ValueError`, `getattr`, `len`, `self.gateway.execute_plsql`, `self.gateway.fetch_all`

### bind

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/fullpal_shipment.py:40](../../../api/wms_api_server/app/modules/inventory/infrastructure/fullpal_shipment.py#L40)

```python
bind(self, task_id: int, body: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockCommand`, `StockPosting`, `StockPosting().post`, `body.items`

### recorded_placement

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/hu_placement_read.py:6](../../../api/wms_api_server/app/modules/inventory/infrastructure/hu_placement_read.py#L6)

```python
recorded_placement(cur: Any, composition: dict) -> dict | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `composition.get`, `composition['nodes'][0].get`, `cur.execute`, `cur.fetchall`, `int`, `len`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py:14](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py#L14)

```python
__init__(self, gateway: Any, posting: StockPosting) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### prepare_group_onward

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py:18](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py#L18)

```python
prepare_group_onward(self, operation: str, receipt: str, reason: str, reference: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `InterwarehouseGroupOnward`, `InterwarehouseGroupOnward(self.gateway).prepare`

### group_queue

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py:22](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py#L22)

```python
group_queue(self, ware: int, actor: str, limit: int=200, after_operation_id: str | None=None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `InterwarehouseGroupRead`, `InterwarehouseGroupRead(self.gateway).queue`

### group_detail

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py:26](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py#L26)

```python
group_detail(self, plan: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `InterwarehouseGroupRead`, `InterwarehouseGroupRead(self.gateway).detail`

### plan_group_placement

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py:30](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py#L30)

```python
plan_group_placement(self, operation: str, receipt: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `InterwarehouseGroupPlacement`, `InterwarehouseGroupPlacement(self.gateway, self.posting).plan`

### plan_group

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py:34](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py#L34)

```python
plan_group(self, operation: str, body: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `InterwarehouseGroupPlan`, `InterwarehouseGroupPlan(self.gateway).plan`

### group_source_proof

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py:38](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py#L38)

```python
group_source_proof(self, load: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `InterwarehouseGroupPlan`, `InterwarehouseGroupPlan(self.gateway).source`

### group_source

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py:42](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py#L42)

```python
group_source(self, load: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `InterwarehouseGroupSource`, `InterwarehouseGroupSource(self.gateway).read`

### decisions

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py:46](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py#L46)

```python
decisions(self, plan_id: str, actor: str, after_revision: int=0) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `InterwarehouseDecisions`, `InterwarehouseDecisions(self.gateway).read`

### incoming

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py:50](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py#L50)

```python
incoming(self, trip_id: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `InterwarehouseIncoming`, `InterwarehouseIncoming(self.gateway).read`

### record_temperature

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py:54](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py#L54)

```python
record_temperature(self, operation_id: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `InterwarehouseDispatch`, `InterwarehouseDispatch(self.gateway).thermal`

### record_decision

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py:58](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py#L58)

```python
record_decision(self, operation_id: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `InterwarehouseDispatch`, `InterwarehouseDispatch(self.gateway).record`

### plan

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py:62](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py#L62)

```python
plan(self, operation_id: str, source_load: str, target_ware: int, target_trip: int, inbound_dock: str, arrival_due: datetime, ready_due: datetime, reason: str, reference: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReturnReceiveError`, `arrival.isoformat`, `arrival_due.astimezone`, `cur.callfunc`, `cur.callproc`, `cur.execute`, `cur.fetchmany`, `cur.fetchone`, `cur.setinputsizes`, `cur.var`, `getattr`, `hu_wire.getvalue`, `int`, `json.dumps`, `json.dumps([source_load, target_ware, target_trip, inbound_dock, arrival.isoformat(), ready.isoformat(), reason, reference, actor], ensure_ascii=False, separators=(',', ':')).encode`, `len`, `read_oracle_json`, `ready.isoformat`, `ready_due.astimezone`, `receipt_task_metadata`, `result.update`, `sha256`, `sha256(json.dumps([source_load, target_ware, target_trip, inbound_dock, arrival.isoformat(), ready.isoformat(), reason, reference, actor], ensure_ascii=False, separators=(',', ':')).encode()).digest`, `sorted`, `str`, `str(exc.args[0]).split`

### receive_action

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py:113](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py#L113)

```python
receive_action(self, kind: str, operation_id: str, plan_id: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockCommand`, `StockPostingError`, `StoreReturnReceiveError`, `ValueError`, `getattr`, `normalize_interwarehouse_scans`, `self.posting.post`, `str`

### plan_placement

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py:126](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py#L126)

```python
plan_placement(self, operation_id: str, receipt_id: str, actor: str, superseded_task_id: int | None=None, replan_reason: str | None=None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockCommand`, `StockPostingError`, `getattr`, `self.posting.post`

### release_custody

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py:133](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py#L133)

```python
release_custody(self, operation_id: str, receipt_id: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockCommand`, `StockPostingError`, `getattr`, `self.posting.post`

### prepare_onward

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py:139](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py#L139)

```python
prepare_onward(self, operation_id: str, receipt_id: str, reason: str, reference: str, actor: str, accept_legacy_address: bool=False) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `InterwarehouseOnward`, `InterwarehouseOnward(self.gateway).prepare`

### unit_manifest

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py:143](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py#L143)

```python
unit_manifest(self, plan_id: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReturnReceiveError`, `getattr`, `json.dumps`, `q.execute`, `q.fetchall`, `q.fetchone`, `q.var`, `read_oracle_json`, `result.get`, `self.gateway.transaction`, `str`, `str(exc.args[0]).split`, `wire.setvalue`

### queue

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py:162](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py#L162)

```python
queue(self, ware_id: int, actor: str, include_completed: bool=False) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `InterwarehouseQueue`, `InterwarehouseQueue(self.gateway).read`

### close_incident

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py:167](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py#L167)

```python
close_incident(self, operation: str, body: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `close_incident`

### shortage

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py:171](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py#L171)

```python
shortage(self, receipt_id: str, actor: str, selected_request: str | None=None) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `read_shortage`

### shortage_action

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py:175](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py#L175)

```python
shortage_action(self, kind: str, operation: str, source_id: str, metadata: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockCommand`, `self.posting.post`

### recovery_action

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py:179](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py#L179)

```python
recovery_action(self, kind: str, operation: str, source_id: str, metadata: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockCommand`, `self.posting.post`

### receive_recovery

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py:183](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py#L183)

```python
receive_recovery(self, operation: str, approval_id: str, metadata: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockCommand`, `normalize_interwarehouse_scans`, `self.posting.post`

### plan_recovery_placement

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py:188](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py#L188)

```python
plan_recovery_placement(self, operation_id: str, recovery_id: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockCommand`, `self.posting.post`

### prepare_recovery_onward

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py:191](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py#L191)

```python
prepare_recovery_onward(self, operation_id: str, recovery_id: str, trip_id: int, reason: str, reference: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `prepare_recovery_st`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_decisions.py:6](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_decisions.py#L6)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### read

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_decisions.py:9](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_decisions.py#L9)

```python
read(self, plan_id: str, actor: str, after_revision: int=0) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReturnReceiveError`, `column[0].lower`, `cur.execute`, `cur.fetchall`, `cur.fetchone`, `dict`, `int`, `len`, `self.gateway.transaction`, `zip`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_dispatch.py:11](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_dispatch.py#L11)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### record

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_dispatch.py:14](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_dispatch.py#L14)

```python
record(self, operation_id: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self._record`

### thermal

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_dispatch.py:17](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_dispatch.py#L17)

```python
thermal(self, operation_id: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self._record`

### _record

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_dispatch.py:20](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_dispatch.py#L20)

```python
_record(self, procedure: str, operation_id: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReturnReceiveError`, `cur.callproc`, `cur.setinputsizes`, `cur.var`, `dict`, `getattr`, `isinstance`, `json.dumps`, `read_oracle_json`, `receipt_task_metadata`, `request.get`, `result.getvalue`, `str`, `str(exc.args[0]).split`, `value.astimezone`, `value.astimezone(timezone.utc).isoformat`

### _scope

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_group_onward.py:13](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_group_onward.py#L13)

```python
_scope(q: Any, receipt: str, actor: str) -> tuple[Any, ...]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReturnReceiveError`, `q.execute`, `q.fetchone`

### _part

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_group_onward.py:26](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_group_onward.py#L26)

```python
_part(q: Any, operation: str, receipt: str, row: tuple[Any, ...], source: tuple[Any, ...], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `InterwarehouseOnward._create_st`, `StoreReturnReceiveError`, `any`, `dict`, `json.dumps`, `json.dumps([operation, lot], separators=(',', ':')).encode`, `q.execute`, `q.fetchone`, `read_oracle_json`, `sha256`, `sha256(json.dumps([operation, lot], separators=(',', ':')).encode()).hexdigest`, `str`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_group_onward.py:51](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_group_onward.py#L51)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### prepare

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_group_onward.py:53](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_group_onward.py#L53)

```python
prepare(self, operation: str, receipt: str, reason: str, reference: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReturnReceiveError`, `_part`, `_scope`, `dict`, `getattr`, `json.dumps`, `json.dumps([receipt, reason, reference, actor], ensure_ascii=False, separators=(',', ':')).encode`, `len`, `q.execute`, `q.fetchall`, `q.fetchone`, `q.setinputsizes`, `read_oracle_json`, `receipt_task_metadata`, `sha256`, `sha256(json.dumps([receipt, reason, reference, actor], ensure_ascii=False, separators=(',', ':')).encode()).digest`, `str`, `str(exc.args[0]).split`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_group_placement.py:9](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_group_placement.py#L9)

```python
__init__(self, gateway: Any, posting: StockPosting) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### plan

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_group_placement.py:13](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_group_placement.py#L13)

```python
plan(self, operation: str, receipt: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockCommand`, `StoreReturnReceiveError`, `dict`, `q.execute`, `q.fetchone`, `self.gateway.transaction`, `self.posting.post`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_group_plan.py:13](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_group_plan.py#L13)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### plan

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_group_plan.py:16](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_group_plan.py#L16)

```python
plan(self, operation: str, body: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReturnReceiveError`, `arrival.isoformat`, `body['arrival_due'].astimezone`, `body['ready_due'].astimezone`, `dict`, `getattr`, `hasattr`, `json.dumps`, `json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode`, `q.callproc`, `q.execute`, `q.fetchone`, `q.setinputsizes`, `read_oracle_json`, `ready.isoformat`, `receipt_task_metadata`, `sha256`, `sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).digest`, `sha256(wire.encode('utf-8')).hexdigest`, `sorted`, `str`, `str(exc.args[0]).split`, `wire.encode`, `wire.read`

### source

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_group_plan.py:70](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_group_plan.py#L70)

```python
source(self, load: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReturnReceiveError`, `dict`, `getattr`, `hasattr`, `q.execute`, `q.fetchone`, `read_oracle_json`, `self.gateway.transaction`, `sha256`, `sha256(wire.encode('utf-8')).hexdigest`, `str`, `str(exc.args[0]).split`, `wire.encode`, `wire.read`

### _scope

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_group_read.py:8](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_group_read.py#L8)

```python
_scope(q: Any, ware: int, actor: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReturnReceiveError`, `q.execute`, `q.fetchone`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_group_read.py:18](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_group_read.py#L18)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### queue

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_group_read.py:21](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_group_read.py#L21)

```python
queue(self, ware: int, actor: str, limit: int=200, after_operation_id: str | None=None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReturnReceiveError`, `_scope`, `dict`, `q.execute`, `q.fetchall`, `q.fetchone`, `self.gateway.transaction`, `zip`

### detail

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_group_read.py:51](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_group_read.py#L51)

```python
detail(self, plan: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReturnReceiveError`, `_scope`, `dict`, `json.dumps`, `len`, `q.execute`, `q.fetchall`, `q.fetchone`, `read_oracle_json`, `self.gateway.transaction`

### _archive

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_group_source.py:10](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_group_source.py#L10)

```python
_archive(q: Any, load: str, actor: str) -> tuple[Any, dict[str, Any], dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReturnReceiveError`, `len`, `q.callproc`, `q.execute`, `q.fetchone`, `read_oracle_json`, `tree.get`

### _members

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_group_source.py:28](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_group_source.py#L28)

```python
_members(q: Any, load: str, tree: dict[str, Any], domain: dict[str, Any]) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `StoreReturnReceiveError`, `bool`, `dict`, `domain.get`, `int`, `leaves.get`, `len`, `n.get`, `node.get`, `part.get`, `q.execute`, `q.fetchall`, `result.append`, `seen.add`, `set`, `sorted`

### _lot

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_group_source.py:55](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_group_source.py#L55)

```python
_lot(q: Any, load: str, archive_wire: Any, member: dict[str, Any]) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `blockers.append`, `dict`, `getattr`, `isinstance`, `json.dumps`, `len`, `q.execute`, `q.fetchall`, `q.fetchone`, `q.setinputsizes`, `read_oracle_json`, `str`, `str(exc.args[0]).split`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_group_source.py:80](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_group_source.py#L80)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### read

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_group_source.py:83](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_group_source.py#L83)

```python
read(self, load: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `StoreReturnReceiveError`, `_archive`, `_lot`, `_members`, `any`, `blockers.append`, `blockers.extend`, `dict`, `format`, `getattr`, `hasattr`, `len`, `n.get`, `q.execute`, `q.fetchone`, `row[4].read`, `self.gateway.transaction`, `sorted`, `str`, `str(exc.args[0]).split`, `totals.get`, `totals.items`

### close_incident

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_incident_close.py:8](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_incident_close.py#L8)

```python
close_incident(gateway: Any, operation: str, body: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReturnReceiveError`, `cur.callproc`, `cur.var`, `gateway.transaction`, `getattr`, `json.dumps`, `out.getvalue`, `payload.setvalue`, `read_oracle_json`, `str`, `str(exc.args[0]).split`

### read_incoming_snapshot

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_incoming.py:19](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_incoming.py#L19)

```python
read_incoming_snapshot(cur: Any, trip_id: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReturnReceiveError`, `column[0].lower`, `cur.execute`, `cur.fetchall`, `cur.fetchone`, `dict`, `incoming_readiness`, `int`, `len`, `rows.extend`, `zip`

### read_optional_incoming_snapshot

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_incoming.py:38](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_incoming.py#L38)

```python
read_optional_incoming_snapshot(cur: Any, trip_id: int, actor: str) -> dict[str, Any]
```

Current native trip scope first; absent expectations are not ready deliveries.

Вызывает: `cur.callproc`, `cur.execute`, `cur.fetchone`, `cur.var`, `read_incoming_snapshot`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_incoming.py:11](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_incoming.py#L11)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### read

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_incoming.py:14](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_incoming.py#L14)

```python
read(self, trip_id: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.execute`, `read_incoming_snapshot`, `self.gateway.transaction`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_onward.py:12](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_onward.py#L12)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### prepare

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_onward.py:15](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_onward.py#L15)

```python
prepare(self, operation_id: str, receipt_id: str, reason: str, reference: str, actor: str, accept_legacy_address: bool=False) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `StoreReturnReceiveError`, `any`, `cur.callproc`, `cur.execute`, `cur.fetchone`, `cur.setinputsizes`, `getattr`, `int`, `json.dumps`, `json.dumps([receipt_id, reason, reference, actor, accept_legacy_address], ensure_ascii=False, separators=(',', ':')).encode`, `len`, `read_oracle_json`, `receipt_task_metadata`, `self._create_st`, `sha256`, `sha256(json.dumps([receipt_id, reason, reference, actor, accept_legacy_address], ensure_ascii=False, separators=(',', ':')).encode()).digest`, `str`, `str(exc.args[0]).split`

### _create_st

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_onward.py:76](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_onward.py#L76)

```python
_create_st(cur: Any, operation_id: str, address: str, article: str, qty: str, unit: str, ware: int, actor: str) -> tuple[int, str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `StoreReturnReceiveError`, `cur.callfunc`, `cur.execute`, `cur.fetchone`, `int`, `operation_id.encode`, `sha256`, `sha256(operation_id.encode()).hexdigest`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_queue.py:11](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_queue.py#L11)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### read

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_queue.py:14](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_queue.py#L14)

```python
read(self, ware_id: int, actor: str, include_completed: bool=False) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReturnReceiveError`, `annotate_timing`, `column[0].lower`, `dict`, `int`, `q.execute`, `q.fetchall`, `q.fetchone`, `self.gateway.transaction`, `zip`

### read_recovery

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_recovery_read.py:7](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_recovery_read.py#L7)

```python
read_recovery(cur: Any, claim: tuple | None, selected_request: str | None=None) -> tuple
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReturnReceiveError`, `next`, `recovery_records`

### recovery_records

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_recovery_records.py:7](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_recovery_records.py#L7)

```python
recovery_records(cur: Any, loss_id: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReturnReceiveError`, `column[0].lower`, `cur.execute`, `cur.fetchall`, `dict`, `len`, `read_oracle_json`, `record.pop`, `seen.add`, `set`, `zip`

### prepare_recovery_st

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_recovery_st.py:13](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_recovery_st.py#L13)

```python
prepare_recovery_st(gateway: Any, operation: str, recovery_id: str, trip: int, reason: str, reference: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `InterwarehouseOnward._create_st`, `StoreReturnReceiveError`, `any`, `cur.execute`, `cur.fetchone`, `cur.setinputsizes`, `dict`, `getattr`, `int`, `json.dumps`, `json.dumps([recovery_id, trip, reason, reference, actor], ensure_ascii=False, separators=(',', ':')).encode`, `len`, `read_oracle_json`, `receipt_task_metadata`, `sha256`, `sha256(json.dumps([recovery_id, trip, reason, reference, actor], ensure_ascii=False, separators=(',', ':')).encode()).digest`, `str`, `str(exc.args[0]).split`

### read_shortage

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_shortage.py:9](../../../api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_shortage.py#L9)

```python
read_shortage(gateway: Any, receipt_id: str, actor: str, selected_request: str | None=None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `StoreReturnReceiveError`, `any`, `bool`, `claims.get`, `cur.execute`, `cur.fetchall`, `cur.fetchone`, `cur.var`, `dict`, `domain.get`, `gateway.transaction`, `int`, `json.dumps`, `len`, `next`, `read_oracle_json`, `read_recovery`, `set`, `str`, `sum`, `wire.setvalue`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/inventory_observations.py:12](../../../api/wms_api_server/app/modules/inventory/infrastructure/inventory_observations.py#L12)

```python
__init__(self, gateway: Any, posting: StockPosting) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### lots

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/inventory_observations.py:16](../../../api/wms_api_server/app/modules/inventory/infrastructure/inventory_observations.py#L16)

```python
lots(self, revision_id: int, cell: str, article: str | None, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `','.join`, `InventoryObservationError`, `assert_inventory_scope`, `enumerate`, `gateway.fetch_all`, `len`, `row.pop`, `sorted`, `str`

### count

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/inventory_observations.py:40](../../../api/wms_api_server/app/modules/inventory/infrastructure/inventory_observations.py#L40)

```python
count(self, request: CountSubmission, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `InventoryObservationError`, `StockCommand`, `assert_inventory_scope`, `enumerate`, `gateway.fetch_all`, `hasattr`, `isinstance`, `json.loads`, `line.wire`, `old.get`, `payload.read`, `resolve_count_codes`, `self.posting.post`

### create_revision

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/inventory_observations.py:65](../../../api/wms_api_server/app/modules/inventory/infrastructure/inventory_observations.py#L65)

```python
create_revision(self, warehouse_id: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `InventoryObservationError`, `assert_inventory_scope`, `gateway.call_number_plsql`, `gateway.fetch_all`

### register_lot

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/inventory_observations.py:73](../../../api/wms_api_server/app/modules/inventory/infrastructure/inventory_observations.py#L73)

```python
register_lot(self, operation_id: str, revision_id: int, metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `InventoryObservationError`, `StockCommand`, `assert_inventory_scope`, `self.posting.post`

### resolve_count_codes

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/inventory_scan_codes.py:11](../../../api/wms_api_server/app/modules/inventory/infrastructure/inventory_scan_codes.py#L11)

```python
resolve_count_codes(gateway: Any, lines: Sequence[CountObservation]) -> list[list[str]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `ValueError`, `any`, `by_line.get`, `by_line.setdefault`, `canonical_mark`, `cursor.execute`, `cursor.fetchall`, `cursor.var`, `enumerate`, `gateway.transaction`, `identity.encode`, `int`, `json.dumps`, `keys[scan['line']].append`, `len`, `list`, `payload.setvalue`, `range`, `registered.values`, `scans.append`, `set`, `sha256`, `sha256(identity.encode()).hexdigest`, `sorted`, `str`, `sum`

### assert_inventory_scope

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/inventory_scope.py:5](../../../api/wms_api_server/app/modules/inventory/infrastructure/inventory_scope.py#L5)

```python
assert_inventory_scope(gateway: Any, actor: str, *, revision: int | None=None, warehouse: int | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `InventoryObservationError`, `gateway.fetch_all`, `len`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/labels.py:14](../../../api/wms_api_server/app/modules/inventory/infrastructure/labels.py#L14)

```python
__init__(self, gateway: OracleGateway) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### _scope

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/labels.py:18](../../../api/wms_api_server/app/modules/inventory/infrastructure/labels.py#L18)

```python
_scope(cur: Any, warehouse: int, actor: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `PermissionError`, `cur.callproc`, `getattr`

### issue

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/labels.py:26](../../../api/wms_api_server/app/modules/inventory/infrastructure/labels.py#L26)

```python
issue(self, order_id: str, payload: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LookupError`, `ValueError`, `cur.execute`, `cur.fetchone`, `cur.setinputsizes`, `cur.var`, `json.dumps`, `json.dumps({'order': order_id, **payload}, sort_keys=True).encode`, `result.getvalue`, `self._scope`, `self.gateway.transaction`, `sha256`, `sha256(json.dumps({'order': order_id, **payload}, sort_keys=True).encode()).hexdigest`, `uuid4`

### document

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/labels.py:55](../../../api/wms_api_server/app/modules/inventory/infrastructure/labels.py#L55)

```python
document(self, label_id: str, format: str, actor: str, dpi: int=203) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LookupError`, `cur.execute`, `cur.fetchone`, `label_html`, `label_zpl`, `read_oracle_json`, `self._scope`, `self.gateway.transaction`

### confirm

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/labels.py:66](../../../api/wms_api_server/app/modules/inventory/infrastructure/labels.py#L66)

```python
confirm(self, label_id: str, scan: str, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LookupError`, `ValueError`, `cur.execute`, `cur.fetchone`, `normalize_incoming_sscc`, `self._scope`, `self.gateway.transaction`

### _post

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/mes_commands.py:12](../../../api/wms_api_server/app/modules/inventory/infrastructure/mes_commands.py#L12)

```python
_post(command: StockCommand) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `StockPosting`, `StockPosting().post`

### apply_mes_movements

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/mes_commands.py:24](../../../api/wms_api_server/app/modules/inventory/infrastructure/mes_commands.py#L24)

```python
apply_mes_movements(gateway: Any, production_order_id: int, request: Any, actor: str | None) -> dict[str, Any] | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `StockCommand`, `ValueError`, `_post`, `gateway.fetch_all`, `int`, `json.dumps`, `json.dumps(ids, separators=(',', ':')).encode`, `len`, `original.get`, `read_oracle_json`, `request.units_by_movement.values`, `require_active_release`, `set`, `sha256`, `sha256(json.dumps(ids, separators=(',', ':')).encode()).hexdigest`, `sorted`, `source.get`, `sum`

### release_supply

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/mes_release_commands.py:13](../../../api/wms_api_server/app/modules/inventory/infrastructure/mes_release_commands.py#L13)

```python
release_supply(gateway: OracleGateway | TransactionGateway, order_id: int, request: MesReleaseToProductionRequest) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `StockCommand`, `StockPosting`, `StockPosting().post`, `int`, `require_active_release`

### calculate_supply

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/mes_supply_commands.py:14](../../../api/wms_api_server/app/modules/inventory/infrastructure/mes_supply_commands.py#L14)

```python
calculate_supply(gateway: OracleGateway | TransactionGateway, order_id: int, request: MesRawSupplyCalculateRequest) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `StockCommand`, `StockPosting`, `StockPosting().post`, `require_active_release`, `uuid4`

### post_mes_task

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/mes_task_commands.py:16](../../../api/wms_api_server/app/modules/inventory/infrastructure/mes_task_commands.py#L16)

```python
post_mes_task(gateway: OracleGateway | TransactionGateway, action: str, task: dict, request: MesRawTransferTaskConfirmRequest | MesRawTransferTaskCancelRequest) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `HTTPException`, `StockCommand`, `StockPosting`, `StockPosting().post`, `ValueError`, `WarehouseTaskStatusRequest`, `WarehouseTaskStatusRequest(fact_qty=fact).model_dump`, `format`, `gateway.fetch_all`, `hasattr`, `int`, `json.loads`, `len`, `raw.read`, `require_active_release`, `saved_request.get`, `saved_request.get('source', {}).get`, `str`

### receipt_task_metadata

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/metadata_transactions.py:10](../../../api/wms_api_server/app/modules/inventory/infrastructure/metadata_transactions.py#L10)

```python
receipt_task_metadata(gateway: OracleGateway | TransactionGateway, purpose: str, actor: str, permission: str) -> Iterator[oracledb.Cursor]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cursor.execute`, `gateway.transaction`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/minimax_service.py:10](../../../api/wms_api_server/app/modules/inventory/infrastructure/minimax_service.py#L10)

```python
__init__(self, gateway: Any, sync_tasks: Callable[[Any, int, str], None]) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### _snapshot

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/minimax_service.py:14](../../../api/wms_api_server/app/modules/inventory/infrastructure/minimax_service.py#L14)

```python
_snapshot(self, cursor: Any, warehouse: int) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `HTTPException`, `cursor.execute`, `cursor.fetchall`, `d[0].lower`, `dict`, `format`, `len`, `localcontext`, `max`, `min`, `seen.add`, `set`, `zip`

### preview

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/minimax_service.py:80](../../../api/wms_api_server/app/modules/inventory/infrastructure/minimax_service.py#L80)

```python
preview(self, warehouse: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self._snapshot`, `self.gateway.transaction`

### reconcile

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/minimax_service.py:85](../../../api/wms_api_server/app/modules/inventory/infrastructure/minimax_service.py#L85)

```python
reconcile(self, warehouse: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `HTTPException`, `StockCommand`, `StockPosting`, `StockPosting().post`, `cursor.execute`, `cursor.fetchall`, `cursor.fetchone`, `int`, `len`, `result.append`, `self._snapshot`, `self.gateway.fetch_all`, `self.gateway.transaction`, `self.sync_tasks`, `tuple`, `uuid4`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/outgoing_quality.py:14](../../../api/wms_api_server/app/modules/inventory/infrastructure/outgoing_quality.py#L14)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### status

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/outgoing_quality.py:17](../../../api/wms_api_server/app/modules/inventory/infrastructure/outgoing_quality.py#L17)

```python
status(self, identifier: str, actor: str | None=None) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `StockPostingError`, `getattr`, `isinstance`, `json.loads`, `q.execute`, `q.fetchone`, `quality_identifier`, `quality_transport_read`, `read_oracle_json`, `rows[0].get`, `self.gateway.fetch_all`, `self.gateway.transaction`

### check

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/outgoing_quality.py:44](../../../api/wms_api_server/app/modules/inventory/infrastructure/outgoing_quality.py#L44)

```python
check(self, identifier: str, body: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `StockCommand`, `StockPosting`, `StockPosting().post`, `body.items`, `canonical_mark`, `identity.encode`, `metadata.pop`, `normalized.append`, `sha256`, `sha256(identity.encode('utf-8')).hexdigest`, `str`

### check_final

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/outgoing_quality.py:64](../../../api/wms_api_server/app/modules/inventory/infrastructure/outgoing_quality.py#L64)

```python
check_final(self, identifier: str, body: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockPostingError`, `body.items`, `metadata.update`, `q.callproc`, `q.execute`, `q.fetchone`, `read_oracle_json`, `self.check`, `self.gateway.transaction`, `str`, `str(error).split`

### final_readings

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/outgoing_quality.py:81](../../../api/wms_api_server/app/modules/inventory/infrastructure/outgoing_quality.py#L81)

```python
final_readings(self, identifier: str, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockPostingError`, `int`, `len`, `q.callproc`, `q.execute`, `q.fetchall`, `q.fetchone`, `read_oracle_json`, `self.gateway.transaction`, `str`, `str(error).split`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/pallet_floor_type.py:8](../../../api/wms_api_server/app/modules/inventory/infrastructure/pallet_floor_type.py#L8)

```python
__init__(self, gateway: Any, posting: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### read

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/pallet_floor_type.py:11](../../../api/wms_api_server/app/modules/inventory/infrastructure/pallet_floor_type.py#L11)

```python
read(self, identifier: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockPostingError`, `cur.callfunc`, `cur.execute`, `getattr`, `read_oracle_json`, `self.gateway.transaction`, `str`, `str(exc.args[0]).split`

### confirm

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/pallet_floor_type.py:22](../../../api/wms_api_server/app/modules/inventory/infrastructure/pallet_floor_type.py#L22)

```python
confirm(self, operation: str, identifier: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockCommand`, `self.posting.post`

### upsert_pallet_type

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/pallet_types.py:10](../../../api/wms_api_server/app/modules/inventory/infrastructure/pallet_types.py#L10)

```python
upsert_pallet_type(gateway: OracleGateway, request: PalletTypeUpsertRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockPostingError`, `int`, `json.dumps`, `q.callproc`, `q.var`, `receipt_task_metadata`, `request.model_dump`, `result.getvalue`

### _digest

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/partial_shipment_layout.py:13](../../../api/wms_api_server/app/modules/inventory/infrastructure/partial_shipment_layout.py#L13)

```python
_digest(value: Any) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `hashlib.sha256`, `hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest`, `json.dumps`, `json.dumps(value, sort_keys=True, separators=(',', ':')).encode`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/partial_shipment_layout.py:18](../../../api/wms_api_server/app/modules/inventory/infrastructure/partial_shipment_layout.py#L18)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### _read

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/partial_shipment_layout.py:21](../../../api/wms_api_server/app/modules/inventory/infrastructure/partial_shipment_layout.py#L21)

```python
_read(self, cursor: Any, task_id: int, identifier: str, locked: bool) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `LookupError`, `ValueError`, `_digest`, `any`, `approved.get`, `approved.items`, `by_line.get`, `cursor.execute`, `cursor.fetchall`, `cursor.fetchmany`, `cursor.fetchone`, `len`, `localcontext`, `physical_composition`, `str`

### preview

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/partial_shipment_layout.py:94](../../../api/wms_api_server/app/modules/inventory/infrastructure/partial_shipment_layout.py#L94)

```python
preview(self, task_id: int, identifier: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `Fraction`, `convert_exact`, `int`, `packages.append`, `physical.get`, `self._read`, `self.gateway.transaction`, `state.items`

### prepare

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/partial_shipment_layout.py:112](../../../api/wms_api_server/app/modules/inventory/infrastructure/partial_shipment_layout.py#L112)

```python
prepare(self, task_id: int, body: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(Decimal(weight) * actual / requested).quantize`, `Decimal`, `Fraction`, `ValueError`, `body.get`, `changes.append`, `convert_exact`, `cursor.execute`, `cursor.fetchone`, `cursor.setinputsizes`, `hasattr`, `int`, `isinstance`, `json.dumps`, `json.loads`, `len`, `localcontext`, `old[3].read`, `physical.pop`, `receipt_task_metadata`, `self._read`, `set`, `state['approved_shortages'].get`, `str`

### _base_assign

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/pickface_attributes.py:9](../../../api/wms_api_server/app/modules/inventory/infrastructure/pickface_attributes.py#L9)

```python
_base_assign(bound: TransactionGateway, request: PickFaceArticulUpsertRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `bound.call_number_plsql`

### _extended_attributes

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/pickface_attributes.py:45](../../../api/wms_api_server/app/modules/inventory/infrastructure/pickface_attributes.py#L45)

```python
_extended_attributes(bound: TransactionGateway, pick_face_articul_id: int, request: PickFaceArticulUpsertRequest) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `bound.execute`

### _identity

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/pickface_configuration.py:10](../../../api/wms_api_server/app/modules/inventory/infrastructure/pickface_configuration.py#L10)

```python
_identity(cur: Any, request: PickFaceArticulUpsertRequest, actor: str) -> tuple[int, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `cur.execute`, `cur.fetchall`, `cur.fetchone`, `int`, `len`, `request.articul.strip`, `request.articul.strip().upper`

### _preserve_occupied

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/pickface_configuration.py:32](../../../api/wms_api_server/app/modules/inventory/infrastructure/pickface_configuration.py#L32)

```python
_preserve_occupied(cur: Any, cell: str, request: PickFaceArticulUpsertRequest) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `cur.execute`, `cur.fetchone`, `cur.fetchone()[0].date`, `request.articul.upper`

### configure_existing_pick_face_article

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/pickface_configuration.py:46](../../../api/wms_api_server/app/modules/inventory/infrastructure/pickface_configuration.py#L46)

```python
configure_existing_pick_face_article(gateway: Any, request: PickFaceArticulUpsertRequest, actor: str) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `TransactionGateway`, `_base_assign`, `_extended_attributes`, `_identity`, `_preserve_occupied`, `getattr`, `request.articul.strip`, `request.articul.strip().upper`, `request.model_copy`, `stock_configuration_transaction`, `str`, `str(exc.args[0]).split`

### create_existing_plan

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/picking_plan.py:7](../../../api/wms_api_server/app/modules/inventory/infrastructure/picking_plan.py#L7)

```python
create_existing_plan(gateway: OracleGateway, request: PickingPlanCreateRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `cur.callfunc`, `gateway.call_number_plsql`, `gateway.transaction`, `getattr`, `int`, `min`, `request.model_dump`, `str`, `str(detail).split`, `str(getattr(detail, 'full_code', '')).startswith`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/placement.py:8](../../../api/wms_api_server/app/modules/inventory/infrastructure/placement.py#L8)

```python
__init__(self, cursor: oracledb.Cursor) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### choose

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/placement.py:11](../../../api/wms_api_server/app/modules/inventory/infrastructure/placement.py#L11)

```python
choose(self, warehouse: int, receiving: str, articul: str, payload: dict) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `ValueError`, `cur.execute`, `cur.fetchall`, `cur.fetchone`, `date.fromisoformat`, `date.today`, `len`, `payload.get`, `str`

### validate_target

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/placement.py:72](../../../api/wms_api_server/app/modules/inventory/infrastructure/placement.py#L72)

```python
validate_target(self, warehouse: int, cell: str, slot: int | None, receipt: dict) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `ValueError`, `cur.execute`, `cur.fetchall`, `cur.fetchone`, `date.fromisoformat`, `date.today`, `len`, `measures.get`, `receipt.get`, `self._limit`, `str`, `zip`

### _limit

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/placement.py:106](../../../api/wms_api_server/app/modules/inventory/infrastructure/placement.py#L106)

```python
_limit(value: Decimal | str | float | int | None, maximum: Decimal | float | int | None, title: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `ValueError`, `str`

### plan_pool

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/pool_plan.py:7](../../../api/wms_api_server/app/modules/inventory/infrastructure/pool_plan.py#L7)

```python
plan_pool(cursor: Any, document: dict[str, Any]) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `PoolDemand`, `allocate_pool`, `cursor.execute`, `cursor.fetchone`, `format`, `hasattr`, `int`, `json.loads`, `raw.read`, `result.quantities.items`, `str`, `tuple`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/pool_service.py:11](../../../api/wms_api_server/app/modules/inventory/infrastructure/pool_service.py#L11)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### preview

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/pool_service.py:14](../../../api/wms_api_server/app/modules/inventory/infrastructure/pool_service.py#L14)

```python
preview(self, warehouse: int, article: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `bool`, `json.loads`, `plan_pool`, `self.gateway.transaction`

### allocate

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/pool_service.py:24](../../../api/wms_api_server/app/modules/inventory/infrastructure/pool_service.py#L24)

```python
allocate(self, warehouse: int, article: str, operation_id: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `StockCommand`, `StockPosting`, `StockPosting().post`

### quality_identifier

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/quality_identifier.py:5](../../../api/wms_api_server/app/modules/inventory/infrastructure/quality_identifier.py#L5)

```python
quality_identifier(cur: oracledb.Cursor, value: str, actor: str) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockPostingError`, `cur.callproc`, `cur.execute`, `cur.fetchall`, `cur.fetchone`, `int`, `len`, `value.startswith`, `value[5:].isdigit`

### access

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/quality_scope.py:13](../../../api/wms_api_server/app/modules/inventory/infrastructure/quality_scope.py#L13)

```python
access(cur: Any, warehouse: int, actor: str, permission: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `QualityScopeError`, `cur.execute`, `cur.fetchone`

### read_rule

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/quality_scope.py:22](../../../api/wms_api_server/app/modules/inventory/infrastructure/quality_scope.py#L22)

```python
read_rule(cur: Any, warehouse: int, address: str, category: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.execute`, `cur.fetchone`, `dict`, `str`, `zip`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/quality_scope.py:35](../../../api/wms_api_server/app/modules/inventory/infrastructure/quality_scope.py#L35)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### read

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/quality_scope.py:38](../../../api/wms_api_server/app/modules/inventory/infrastructure/quality_scope.py#L38)

```python
read(self, warehouse: int, actor: str, address: str, category: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `access`, `cur.execute`, `read_rule`, `self.gateway.transaction`

### save

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/quality_scope.py:44](../../../api/wms_api_server/app/modules/inventory/infrastructure/quality_scope.py#L44)

```python
save(self, warehouse: int, actor: str, body: dict[str, Any]) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `QualityScopeError`, `access`, `cur.execute`, `cur.fetchall`, `cur.fetchone`, `hashlib.sha256`, `hashlib.sha256(wire.encode('utf-8')).hexdigest`, `int`, `json.dumps`, `len`, `read_oracle_json`, `read_rule`, `stock_configuration_transaction`, `str`, `wire.encode`

### quality_transport_read

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/quality_transport_read.py:5](../../../api/wms_api_server/app/modules/inventory/infrastructure/quality_transport_read.py#L5)

```python
quality_transport_read(cur: Any, identifier: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.execute`, `cur.fetchall`, `int`, `len`

### map_range_error

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/range_apply.py:56](../../../api/wms_api_server/app/modules/inventory/infrastructure/range_apply.py#L56)

```python
map_range_error(exc: oracledb.DatabaseError) -> SlottingError
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `SlottingError`, `getattr`, `str`, `str(exc.args[0]).split`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/range_apply.py:12](../../../api/wms_api_server/app/modules/inventory/infrastructure/range_apply.py#L12)

```python
__init__(self, gateway: Any, reader: SlottingDemand) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### approve

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/range_apply.py:15](../../../api/wms_api_server/app/modules/inventory/infrastructure/range_apply.py#L15)

```python
approve(self, ware: int, article: str, proposal: str, operation: str, reason: str, geometry: bool, compatibility: bool, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `SlottingError`, `cur.execute`, `cur.fetchone`, `date.fromisoformat`, `map_range_error`, `range_command`, `read_oracle_json`, `request.get`, `self.gateway.transaction`, `self.reader.snapshot`, `stock_configuration_transaction`

### close

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/range_apply.py:48](../../../api/wms_api_server/app/modules/inventory/infrastructure/range_apply.py#L48)

```python
close(self, ware: int, article: str, mapping: int, operation: str, reason: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `map_range_error`, `range_command`, `stock_configuration_transaction`

### range_command

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/range_command.py:7](../../../api/wms_api_server/app/modules/inventory/infrastructure/range_command.py#L7)

```python
range_command(cur: Any, ware: int, article: str, operation: str, action: str, actor: str, body: dict[str, Any], source: dict[str, Any] | None=None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.callproc`, `cur.var`, `json.dumps`, `read_oracle_json`, `request_var.setvalue`, `result.getvalue`, `source_var.setvalue`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/range_proposal.py:12](../../../api/wms_api_server/app/modules/inventory/infrastructure/range_proposal.py#L12)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RangeApply`, `SlottingDemand`

### _command

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/range_proposal.py:17](../../../api/wms_api_server/app/modules/inventory/infrastructure/range_proposal.py#L17)

```python
_command(self, ware: int, article: str, operation: str, action: str, actor: str, body: dict[str, Any], source: dict[str, Any] | None=None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `SlottingError`, `getattr`, `range_command`, `self.gateway.transaction`, `str`, `str(exc.args[0]).split`

### save

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/range_proposal.py:30](../../../api/wms_api_server/app/modules/inventory/infrastructure/range_proposal.py#L30)

```python
save(self, ware: int, article: str, command: RangeDraft, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `SlottingError`, `command.period_from.isoformat`, `command.period_to_exclusive.isoformat`, `format`, `self._command`, `self.reader.preview`

### cancel

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/range_proposal.py:49](../../../api/wms_api_server/app/modules/inventory/infrastructure/range_proposal.py#L49)

```python
cancel(self, ware: int, article: str, proposal: str, operation: str, reason: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self._command`

### approve

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/range_proposal.py:52](../../../api/wms_api_server/app/modules/inventory/infrastructure/range_proposal.py#L52)

```python
approve(self, ware: int, article: str, proposal: str, operation: str, reason: str, geometry: bool, compatibility: bool, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.apply.approve`

### close

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/range_proposal.py:56](../../../api/wms_api_server/app/modules/inventory/infrastructure/range_proposal.py#L56)

```python
close(self, ware: int, article: str, mapping: int, operation: str, reason: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.apply.close`

### get

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/range_proposal.py:59](../../../api/wms_api_server/app/modules/inventory/infrastructure/range_proposal.py#L59)

```python
get(self, ware: int, article: str, proposal: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `SlottingError`, `any`, `cur.execute`, `cur.fetchall`, `cur.fetchone`, `dict`, `len`, `read_oracle_json`, `self.gateway.transaction`, `zip`

### _book_pallet

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/receipt_booking.py:11](../../../api/wms_api_server/app/modules/inventory/infrastructure/receipt_booking.py#L11)

```python
_book_pallet(self, cur: oracledb.Cursor, order: tuple, line: tuple, payload: dict, marks: dict, placement: dict, actor: str, *, task_id: int | None=None, stock_quantity: Decimal | None=None, bindings: list | None=None, stock_base: str | None=None, receive_cell: str | None=None) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `ReceivingMarks`, `ReceivingMarks(cur).persist`, `ValueError`, `cur.callproc`, `cur.execute`, `cur.fetchone`, `date.fromisoformat`, `int`, `json.loads`, `payload.get`, `self._text`, `sscc_value`, `str`

### _text

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/receipt_booking.py:42](../../../api/wms_api_server/app/modules/inventory/infrastructure/receipt_booking.py#L42)

```python
_text(value: Any) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `hasattr`, `value.read`

### _text

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/receipt_commands.py:16](../../../api/wms_api_server/app/modules/inventory/infrastructure/receipt_commands.py#L16)

```python
_text(value: Any) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `hasattr`, `value.read`

### plan_receipt

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/receipt_commands.py:20](../../../api/wms_api_server/app/modules/inventory/infrastructure/receipt_commands.py#L20)

```python
plan_receipt(cursor: oracledb.Cursor, document: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `LookupError`, `ReceiptPlacement`, `ReceiptPlacement(cursor).choose`, `ReceivingMarks`, `ReceivingMarks(cursor).resolve`, `ValueError`, `a['code'].encode`, `aliases.values`, `bindings.append`, `canonical_mark`, `codes.items`, `cursor.execute`, `cursor.fetchone`, `format`, `identities.append`, `int`, `len`, `list`, `marks.get`, `marks['units'].items`, `min`, `normalize_receipt_identifier`, `normalized['identity'].encode`, `payload.get`, `physical_identity.encode`, `result.update`, `sha256`, `sha256(a['code'].encode()).hexdigest`, `sha256(normalized['identity'].encode()).hexdigest`, `sha256(physical_identity.encode()).hexdigest`, `sscc_value`, `str`, `str(cursor.fetchone()[0]).zfill`

### stage_receipt

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/receipt_commands.py:89](../../../api/wms_api_server/app/modules/inventory/infrastructure/receipt_commands.py#L89)

```python
stage_receipt(cursor: oracledb.Cursor, document: dict[str, Any], marks: dict[str, Any]) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `ReceiptBooking`, `ReceiptBooking()._book_pallet`, `ReceiptPlacement`, `ReceiptPlacement(cursor).validate_target`, `ValueError`, `cursor.execute`, `cursor.fetchone`, `date.fromisoformat`, `date.today`, `payload.get`, `read_oracle_json`

### receive_command

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/receipt_posting.py:7](../../../api/wms_api_server/app/modules/inventory/infrastructure/receipt_posting.py#L7)

```python
receive_command(gateway: Any, order_id: str, payload: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `StockCommand`, `StockPosting`, `StockPosting().post`, `StockPostingError`, `format`, `gateway.fetch_all`, `isinstance`, `metadata.get`, `payload.items`, `str`

### create_receipt_parent

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/receipt_regulatory_parent.py:6](../../../api/wms_api_server/app/modules/inventory/infrastructure/receipt_regulatory_parent.py#L6)

```python
create_receipt_parent(cur: Any, pallet: str, scanned: list[dict[str, Any]]) -> tuple[int | None, str | None]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `cur.callfunc`, `cur.execute`, `cur.fetchone`, `int`, `receipt_sscc`

### admit_current_source

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/receipt_replan_source.py:7](../../../api/wms_api_server/app/modules/inventory/infrastructure/receipt_replan_source.py#L7)

```python
admit_current_source(cur: oracledb.Cursor, task_id: int, task: tuple[Any, ...], receipt: dict[str, Any]) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `ValueError`, `cur.execute`, `cur.fetchall`, `cur.fetchone`, `int`, `len`, `result.update`, `str`, `str(task[7] or '').startswith`, `str(task[7]).removeprefix`

### assert_receipt_task_scope

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/receipt_task_access.py:4](../../../api/wms_api_server/app/modules/inventory/infrastructure/receipt_task_access.py#L4)

```python
assert_receipt_task_scope(cursor: oracledb.Cursor, task_id: int, actor: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `PermissionError`, `cursor.execute`, `getattr`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/receiving.py:19](../../../api/wms_api_server/app/modules/inventory/infrastructure/receiving.py#L19)

```python
__init__(self, gateway: OracleGateway) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### receive

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/receiving.py:22](../../../api/wms_api_server/app/modules/inventory/infrastructure/receiving.py#L22)

```python
receive(self, order_id: str, payload: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `receive_command`

### complete

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/receiving.py:26](../../../api/wms_api_server/app/modules/inventory/infrastructure/receiving.py#L26)

```python
complete(self, task_id: int, scans: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `WarehouseTaskStatusRequest`, `complete_existing_task`

### replan

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/receiving.py:31](../../../api/wms_api_server/app/modules/inventory/infrastructure/receiving.py#L31)

```python
replan(self, task_id: int, body: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `LookupError`, `ReceiptPlacement`, `ReceiptPlacement(cur).choose`, `ValueError`, `admit_current_source`, `assert_receipt_task_scope`, `cur.execute`, `cur.fetchone`, `json.dumps`, `json.dumps({'task_id': task_id, **body}, sort_keys=True).encode`, `normalize_incoming_sscc`, `read_oracle_json`, `receipt.get`, `receipt_task_metadata`, `self._outbox`, `sha256`, `sha256(json.dumps({'task_id': task_id, **body}, sort_keys=True).encode()).hexdigest`

### cancel

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/receiving.py:75](../../../api/wms_api_server/app/modules/inventory/infrastructure/receiving.py#L75)

```python
cancel(self, task_id: int, reason: str, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LookupError`, `ValueError`, `assert_receipt_task_scope`, `cur.execute`, `cur.fetchone`, `read_oracle_json`, `reason.strip`, `receipt_task_metadata`, `self._outbox`

### _outbox

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/receiving.py:107](../../../api/wms_api_server/app/modules/inventory/infrastructure/receiving.py#L107)

```python
_outbox(self, cur: oracledb.Cursor, event_id: str, kind: str, result: dict) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.execute`, `cur.setinputsizes`, `json.dumps`

### _text

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/receiving.py:113](../../../api/wms_api_server/app/modules/inventory/infrastructure/receiving.py#L113)

```python
_text(value: object) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `hasattr`, `value.read`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/receiving_marks.py:17](../../../api/wms_api_server/app/modules/inventory/infrastructure/receiving_marks.py#L17)

```python
__init__(self, cursor: oracledb.Cursor) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### resolve

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/receiving_marks.py:20](../../../api/wms_api_server/app/modules/inventory/infrastructure/receiving_marks.py#L20)

```python
resolve(self, order_id: str, articul: str, line_number: str, quantity: Decimal, payload: dict, base_uom: str, *, lock_policy: bool=True, birth_context: dict[str, Any] | None=None) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `ValueError`, `aggregation_members`, `assert_capture_policy`, `assert_sender_capture`, `base_uom.upper`, `cur.execute`, `cur.fetchall`, `cur.fetchone`, `hasattr`, `isinstance`, `item.get`, `iter`, `len`, `member.get`, `meta[0].read`, `next`, `payload.get`, `quantities.values`, `read_oracle_json`, `resolve_weighted_boxes`, `scanned.append`, `self._add`, `self._profile`, `self._quantity`, `self._value`, `set`, `source_header`, `sum`, `u['uom'].upper`, `unit_quantity`, `units.values`

### persist

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/receiving_marks.py:87](../../../api/wms_api_server/app/modules/inventory/infrastructure/receiving_marks.py#L87)

```python
persist(self, pallet: str, marks: dict, actor: str, *, bindings: list | None=None, base_uom: str | None=None, cell: str | None=None, source_kind: str='PHYSICAL_RECEIPT') -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `ValueError`, `any`, `assert_current_mark_policy`, `assert_current_weighted_policy`, `box.get`, `canonical_mark`, `codes.items`, `create_receipt_parent`, `cur.callfunc`, `cur.callproc`, `cur.execute`, `cur.fetchone`, `cur.setinputsizes`, `expected_gtin.isdigit`, `expected_gtin.zfill`, `identities.items`, `identities.setdefault`, `identity['profiles'].append`, `json.dumps`, `len`, `marks.get`, `marks.get('weighted_boxes', {}).get`, `marks['units'].items`, `marks['units'].values`, `normalized['identity'].encode`, `persist_scanned_aggregates`, `sha256`, `sha256(normalized['identity'].encode()).hexdigest`, `str`, `str(cur.fetchone()[0]).zfill`

### _quantity

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/receiving_marks.py:150](../../../api/wms_api_server/app/modules/inventory/infrastructure/receiving_marks.py#L150)

```python
_quantity(quantities: dict, unit_id: str, value: Decimal) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`

### _value

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/receiving_marks.py:156](../../../api/wms_api_server/app/modules/inventory/infrastructure/receiving_marks.py#L156)

```python
_value(item: dict, name: str, maximum: int) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `isinstance`, `item.get`, `len`, `value.encode`

### _profile

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/receiving_marks.py:165](../../../api/wms_api_server/app/modules/inventory/infrastructure/receiving_marks.py#L165)

```python
_profile(self, item: dict, profiles: dict) -> tuple
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `self._value`

### _add

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/receiving_marks.py:172](../../../api/wms_api_server/app/modules/inventory/infrastructure/receiving_marks.py#L172)

```python
_add(units: dict, unit_id: str, profile: tuple, code: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `code.encode`, `isinstance`, `len`, `unit_id.encode`, `units.setdefault`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/receiving_queries.py:11](../../../api/wms_api_server/app/modules/inventory/infrastructure/receiving_queries.py#L11)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### composition

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/receiving_queries.py:14](../../../api/wms_api_server/app/modules/inventory/infrastructure/receiving_queries.py#L14)

```python
composition(self, pallet: str, after: str='', limit: int=50, expected_signature: str | None=None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CompositionViewError`, `Decimal`, `LookupError`, `birth_provenance`, `cur.execute`, `cur.fetchall`, `cur.fetchone`, `cursor_rows`, `format`, `int`, `json.dumps`, `json.dumps([identity[1], locations], sort_keys=True, separators=(',', ':')).encode`, `len`, `max`, `min`, `read_oracle_json`, `self._units`, `self.gateway.transaction`, `sha256`, `sha256(json.dumps([identity[1], locations], sort_keys=True, separators=(',', ':')).encode()).hexdigest`, `sum`

### _units

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/receiving_queries.py:53](../../../api/wms_api_server/app/modules/inventory/infrastructure/receiving_queries.py#L53)

```python
_units(cur: Any, pallet: str, after: str, limit: int) -> tuple[list[dict[str, Any]], bool]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.execute`, `cursor_rows`, `hasattr`, `len`, `list`, `raw.read`, `read_oracle_json`, `unit['codes'].append`, `units.setdefault`, `units.values`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/reconciliation.py:9](../../../api/wms_api_server/app/modules/inventory/infrastructure/reconciliation.py#L9)

```python
__init__(self, gateway: OracleGateway) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### close

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/reconciliation.py:12](../../../api/wms_api_server/app/modules/inventory/infrastructure/reconciliation.py#L12)

```python
close(self, order_id: str, operation: str, reason: str, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `LookupError`, `ValueError`, `any`, `convert_exact`, `cur.execute`, `cur.fetchall`, `cur.fetchone`, `cur.setinputsizes`, `hasattr`, `int`, `json.dumps`, `json.dumps([order_id, operation, reason]).encode`, `json.dumps([order_id, operation]).encode`, `json.loads`, `len`, `lines.append`, `order[2].read`, `saved[0].read`, `self.gateway.transaction`, `sha256`, `sha256(json.dumps([order_id, operation, reason]).encode()).hexdigest`, `sha256(json.dumps([order_id, operation]).encode()).hexdigest`, `str`

### reopen

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/reconciliation.py:71](../../../api/wms_api_server/app/modules/inventory/infrastructure/reconciliation.py#L71)

```python
reopen(self, order_id: str, operation: str, reason: str, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LookupError`, `ValueError`, `cur.execute`, `cur.fetchone`, `cur.setinputsizes`, `hasattr`, `json.dumps`, `json.dumps([order_id, operation, reason]).encode`, `json.dumps([order_id, operation]).encode`, `json.loads`, `old[0].read`, `self.gateway.transaction`, `sha256`, `sha256(json.dumps([order_id, operation, reason]).encode()).hexdigest`, `sha256(json.dumps([order_id, operation]).encode()).hexdigest`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/recovery_tasks.py:7](../../../api/wms_api_server/app/modules/inventory/infrastructure/recovery_tasks.py#L7)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### list_inventory

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/recovery_tasks.py:10](../../../api/wms_api_server/app/modules/inventory/infrastructure/recovery_tasks.py#L10)

```python
list_inventory(self, limit: int, task_id: int | None=None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### list_recovery

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/recovery_tasks.py:23](../../../api/wms_api_server/app/modules/inventory/infrastructure/recovery_tasks.py#L23)

```python
list_recovery(self, limit: int) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### claim_inventory

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/recovery_tasks.py:46](../../../api/wms_api_server/app/modules/inventory/infrastructure/recovery_tasks.py#L46)

```python
claim_inventory(self, task_id: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `cursor.execute`, `cursor.fetchone`, `self.gateway.transaction`, `self.list_inventory`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/recovery_worker.py:13](../../../api/wms_api_server/app/modules/inventory/infrastructure/recovery_worker.py#L13)

```python
__init__(self, gateway: Any, actor: str, worker_id: str, assign: Callable[[Any, int, Any], None]) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### claim

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/recovery_worker.py:17](../../../api/wms_api_server/app/modules/inventory/infrastructure/recovery_worker.py#L17)

```python
claim(self) -> dict[str, Any] | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `PermissionError`, `cursor.execute`, `cursor.fetchone`, `frozen.read`, `hasattr`, `int`, `self.gateway.transaction`

### release

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/recovery_worker.py:44](../../../api/wms_api_server/app/modules/inventory/infrastructure/recovery_worker.py#L44)

```python
release(self, short_id: int, error: str | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.execute`

### prepare_source

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/recovery_worker.py:50](../../../api/wms_api_server/app/modules/inventory/infrastructure/recovery_worker.py#L50)

```python
prepare_source(self, item: dict[str, Any]) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `PickingService`, `PickingService(TransactionGateway(cursor))._enrich_replenishment_settings`, `StockCommand`, `TransactionGateway`, `command.canonical_json`, `cursor.execute`, `cursor.fetchone`, `hasattr`, `old.read`, `self.gateway.transaction`, `str`, `uuid4`

### post_frozen_source

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/recovery_worker.py:77](../../../api/wms_api_server/app/modules/inventory/infrastructure/recovery_worker.py#L77)

```python
post_frozen_source(self, item: dict[str, Any], payload: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockCommand`, `StockPosting`, `StockPosting().post`, `json.loads`, `self.gateway.execute`

### work

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/recovery_worker.py:87](../../../api/wms_api_server/app/modules/inventory/infrastructure/recovery_worker.py#L87)

```python
work(self, item: dict[str, Any]) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockCommand`, `StockPosting`, `StockPosting().post`, `any`, `assign_existing_inventory_auditor`, `dispatch_existing_urgent_replenishment`, `getattr`, `self.gateway.fetch_all`, `self.post_frozen_source`, `self.prepare_source`, `str`, `sync_existing_wave_tasks`

### process_one

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/recovery_worker.py:113](../../../api/wms_api_server/app/modules/inventory/infrastructure/recovery_worker.py#L113)

```python
process_one(self) -> dict[str, Any] | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.claim`, `self.release`, `self.work`, `str`

### require_active_release

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/release_boundary.py:5](../../../api/wms_api_server/app/modules/inventory/infrastructure/release_boundary.py#L5)

```python
require_active_release(gateway: Any, operation_id: str | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockPostingError`, `gateway.fetch_all`

### hold_unissued_capacity

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/replenishment_capacity_hold.py:5](../../../api/wms_api_server/app/modules/inventory/infrastructure/replenishment_capacity_hold.py#L5)

```python
hold_unissued_capacity(gateway: Any, wave_id: int, actor: str) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `cursor.execute`, `cursor.executemany`, `cursor.fetchall`, `gateway.transaction`, `len`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/replenishment_continuation.py:9](../../../api/wms_api_server/app/modules/inventory/infrastructure/replenishment_continuation.py#L9)

```python
__init__(self, gateway: Any, sync_tasks: Callable[[Any, int, str], None]) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### reconcile

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/replenishment_continuation.py:12](../../../api/wms_api_server/app/modules/inventory/infrastructure/replenishment_continuation.py#L12)

```python
reconcile(self, warehouse: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `AlternativePickFaces`, `AlternativePickFaces(self.gateway).route_wave`, `HTTPException`, `TransactionGateway`, `cursor.execute`, `cursor.fetchall`, `grouped.items`, `grouped.setdefault`, `grouped.setdefault(wave_id, []).append`, `int`, `len`, `reconcile_warehouse_arrivals`, `reserve_wave_sources`, `self.gateway.transaction`, `self.sync_tasks`, `set`, `sorted`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/replenishment_progress.py:5](../../../api/wms_api_server/app/modules/inventory/infrastructure/replenishment_progress.py#L5)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### list_rows

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/replenishment_progress.py:8](../../../api/wms_api_server/app/modules/inventory/infrastructure/replenishment_progress.py#L8)

```python
list_rows(self, wave_id: int, limit: int) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### post_reservation

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/reservation_commands.py:14](../../../api/wms_api_server/app/modules/inventory/infrastructure/reservation_commands.py#L14)

```python
post_reservation(gateway: OracleGateway | TransactionGateway, action: str, request: StockReservationCreateRequest | StockReservationPromoteRequest | StockReservationStatusRequest, actor: str | None, reservation_id: int | None=None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `HTTPException`, `StockCommand`, `StockPosting`, `StockPosting().post`, `ValueError`, `format`, `getattr`, `request.model_dump`, `require_active_release`, `str`, `tuple`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/return_disposal.py:13](../../../api/wms_api_server/app/modules/inventory/infrastructure/return_disposal.py#L13)

```python
__init__(self, gateway: Any, posting: StockPosting) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### report

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/return_disposal.py:17](../../../api/wms_api_server/app/modules/inventory/infrastructure/return_disposal.py#L17)

```python
report(self, operation_id: str, receipt_id: str, reference: str, document_hash: str, reason: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReturnReceiveError`, `cur.execute`, `cur.fetchone`, `cur.setinputsizes`, `getattr`, `json.dumps`, `json.dumps([receipt_id, reference, document_hash, reason, actor], ensure_ascii=False, separators=(',', ':')).encode`, `read_oracle_json`, `receipt_task_metadata`, `sha256`, `sha256(json.dumps([receipt_id, reference, document_hash, reason, actor], ensure_ascii=False, separators=(',', ':')).encode()).digest`, `str`, `str(exc.args[0]).split`

### dispose

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/return_disposal.py:37](../../../api/wms_api_server/app/modules/inventory/infrastructure/return_disposal.py#L37)

```python
dispose(self, operation_id: str, request_id: str, version: int, pallet: str, cell: str, reference: str, actor: str, scans: list[dict[str, str]] | None=None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockCommand`, `normalize_unit_scan_codes`, `self.posting.post`

### pending

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/return_disposal.py:41](../../../api/wms_api_server/app/modules/inventory/infrastructure/return_disposal.py#L41)

```python
pending(self, ware_id: int, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReturnReceiveError`, `all`, `len`, `read_oracle_json`, `row.pop`, `self.gateway.fetch_all`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/return_putaway.py:9](../../../api/wms_api_server/app/modules/inventory/infrastructure/return_putaway.py#L9)

```python
__init__(self, gateway: Any, post: Callable[[str, str, dict[str, Any], dict[str, Any], str], dict[str, Any]]) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### configure

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/return_putaway.py:13](../../../api/wms_api_server/app/modules/inventory/infrastructure/return_putaway.py#L13)

```python
configure(self, ware_id: int, supplier_target: str, disposal_target: str, expected_version: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReturnReceiveError`, `cursor.execute`, `cursor.fetchall`, `getattr`, `len`, `stock_configuration_transaction`, `str`, `str(exc.args[0]).split`

### pending

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/return_putaway.py:31](../../../api/wms_api_server/app/modules/inventory/infrastructure/return_putaway.py#L31)

```python
pending(self, ware_id: int, actor: str, receipt_operation_id: str | None=None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReturnReceiveError`, `self.gateway.fetch_all`

### plan

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/return_putaway.py:52](../../../api/wms_api_server/app/modules/inventory/infrastructure/return_putaway.py#L52)

```python
plan(self, operation_id: str, receipt_id: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.post`

### require_scope

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/return_receiving_reads.py:6](../../../api/wms_api_server/app/modules/inventory/infrastructure/return_receiving_reads.py#L6)

```python
require_scope(cur: Any, ware: int, actor: str, permission: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReturnReceiveError`, `cur.execute`, `cur.fetchone`

### policy

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/return_receiving_reads.py:11](../../../api/wms_api_server/app/modules/inventory/infrastructure/return_receiving_reads.py#L11)

```python
policy(gateway: Any, ware: int, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.execute`, `cur.fetchone`, `d[0].lower`, `dict`, `gateway.transaction`, `require_scope`, `zip`

### page

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/return_receiving_reads.py:18](../../../api/wms_api_server/app/modules/inventory/infrastructure/return_receiving_reads.py#L18)

```python
page(gateway: Any, ware: int, actor: str, after: str='', limit: int=20, pickup: str | None=None, proof: bool=False) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `cur.execute`, `cur.fetchall`, `d[0].lower`, `dict`, `gateway.transaction`, `items.append`, `len`, `read_oracle_json`, `require_scope`, `zip`

### source

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/return_receiving_reads.py:53](../../../api/wms_api_server/app/modules/inventory/infrastructure/return_receiving_reads.py#L53)

```python
source(gateway: Any, ware: int, pickup: str, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReturnReceiveError`, `page`

### convert_sap_source_quantity

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/sap_quantity.py:7](../../../api/wms_api_server/app/modules/inventory/infrastructure/sap_quantity.py#L7)

```python
convert_sap_source_quantity(cur: Any, article: str, input_unit: str, raw: str, base: str, units: list[dict]) -> Decimal
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `Fraction`, `ValueError`, `base.upper`, `cur.execute`, `cur.fetchall`, `cur.fetchone`, `format`, `getattr`, `int`, `len`, `min`, `row.get`

### reconcile_arrived_sources

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/shared_arrival_reconciliation.py:7](../../../api/wms_api_server/app/modules/inventory/infrastructure/shared_arrival_reconciliation.py#L7)

```python
reconcile_arrived_sources(gateway: TransactionGateway, wave_id: int, actor: str, row_ids: list[int] | None=None) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `gateway.execute`, `json.dumps`, `requeue_partial_sources`

### reconcile_warehouse_arrivals

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/shared_arrival_reconciliation.py:36](../../../api/wms_api_server/app/modules/inventory/infrastructure/shared_arrival_reconciliation.py#L36)

```python
reconcile_warehouse_arrivals(gateway: TransactionGateway, warehouse: int, actor: str) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `gateway.fetch_all`, `grouped.items`, `grouped.setdefault`, `grouped.setdefault(int(row['pick_wave_id']), []).append`, `int`, `len`, `reconcile_arrived_sources`, `sum`

### requeue_partial_sources

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/shared_arrival_reconciliation.py:62](../../../api/wms_api_server/app/modules/inventory/infrastructure/shared_arrival_reconciliation.py#L62)

```python
requeue_partial_sources(gateway: TransactionGateway, wave_id: int, actor: str, row_ids: list[int] | None=None) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `gateway.execute`, `json.dumps`

### read_shipping_temperature_requirements

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/shipping_temperature_read.py:5](../../../api/wms_api_server/app/modules/inventory/infrastructure/shipping_temperature_read.py#L5)

```python
read_shipping_temperature_requirements(cur: oracledb.Cursor, member_ids: list[int], actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `','.join`, `Decimal`, `PermissionError`, `ValueError`, `all`, `any`, `bool`, `cur.execute`, `cur.fetchall`, `cur.fetchone`, `enumerate`, `int`, `isinstance`, `items.append`, `len`, `lower.append`, `max`, `min`, `range`, `rows.update`, `set`, `sorted`, `str`, `str(user[1] or '').strip`, `str(user[1] or '').strip().upper`, `upper.append`

### payload

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/short_investigation.py:9](../../../api/wms_api_server/app/modules/inventory/infrastructure/short_investigation.py#L9)

```python
payload(value: Any) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `isinstance`, `json.loads`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/short_investigation.py:13](../../../api/wms_api_server/app/modules/inventory/infrastructure/short_investigation.py#L13)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### read

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/short_investigation.py:16](../../../api/wms_api_server/app/modules/inventory/infrastructure/short_investigation.py#L16)

```python
read(self, short_id: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `archive_uri`, `data.get`, `datetime.fromisoformat`, `datetime.fromisoformat(instant).astimezone`, `event.pop`, `history.append`, `len`, `links.append`, `payload`, `result.pop`, `self.gateway.fetch_all`

### camera_settings

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/short_investigation.py:61](../../../api/wms_api_server/app/modules/inventory/infrastructure/short_investigation.py#L61)

```python
camera_settings(self, warehouse: int, cell: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `len`, `self.gateway.fetch_all`

### configure

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/short_investigation.py:68](../../../api/wms_api_server/app/modules/inventory/infrastructure/short_investigation.py#L68)

```python
configure(self, request: Any, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `ValueError`, `cursor.execute`, `cursor.fetchone`, `int`, `len`, `request.archive_uri_template.encode`, `stock_configuration_transaction`, `str`, `validate_template`

### review

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/short_investigation.py:101](../../../api/wms_api_server/app/modules/inventory/infrastructure/short_investigation.py#L101)

```python
review(self, short_id: int, request: Any, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `cursor.execute`, `cursor.fetchone`, `hasattr`, `int`, `json.dumps`, `len`, `old[2].read`, `payload`, `request.model_dump`, `saved.get`, `self.gateway.transaction`, `str`, `validate_uri`, `wire.encode`

### short_report_replay

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/short_report_replay.py:6](../../../api/wms_api_server/app/modules/inventory/infrastructure/short_report_replay.py#L6)

```python
short_report_replay(gateway: Any, task_id: int, line_id: int, request: Any) -> dict[str, Any] | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `gateway.fetch_all`, `len`, `request.model_dump`, `str`

### native_template_volumes

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/slotting_candidates.py:9](../../../api/wms_api_server/app/modules/inventory/infrastructure/slotting_candidates.py#L9)

```python
native_template_volumes(cur: Any, article: str, templates: list[tuple[Any, ...]]) -> tuple[Decimal | None, list[dict[str, Any]]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `cur.execute`, `cur.fetchone`, `format`, `getattr`, `iter`, `len`, `next`, `set`, `str`, `str(exc.args[0]).split`, `volume_evidence.append`, `volumes.add`

### recommendation_sources

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/slotting_candidates.py:36](../../../api/wms_api_server/app/modules/inventory/infrastructure/slotting_candidates.py#L36)

```python
recommendation_sources(cur: Any, ware: int, article: str, scenario: dict[str, Any], layout: dict[str, Any], pallet_weight: Decimal | None, costs: list[dict[str, Any]], candidate_route: int | None=None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `SlottingError`, `add`, `candidates.append`, `cur.execute`, `cur.fetchall`, `cur.fetchone`, `format`, `hasattr`, `int`, `json.dumps`, `len`, `localcontext`, `native_template_volumes`, `raw.read`, `reasons.append`, `recommend_range`

### add

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/slotting_candidates.py:89](../../../api/wms_api_server/app/modules/inventory/infrastructure/slotting_candidates.py#L89)

```python
add(face: int, cell: str, volume: str | None, weight: str | None, route: int | None, route_cell: int | None, old: bool, budget: str | None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `candidates.append`, `format`, `int`, `reasons.append`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/slotting_demand_reader.py:16](../../../api/wms_api_server/app/modules/inventory/infrastructure/slotting_demand_reader.py#L16)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### preview

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/slotting_demand_reader.py:18](../../../api/wms_api_server/app/modules/inventory/infrastructure/slotting_demand_reader.py#L18)

```python
preview(self, ware: int, article: str, start: date, end: date, forecast: Decimal | None, forecast_unit: str | None, actor: str, pallet_weight: Decimal | None=None, costs: list[dict[str, Any]] | None=None, candidate_route: int | None=None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `SlottingError`, `cur.execute`, `getattr`, `self.gateway.transaction`, `self.snapshot`, `str`, `str(exc.args[0]).split`

### snapshot

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/slotting_demand_reader.py:30](../../../api/wms_api_server/app/modules/inventory/infrastructure/slotting_demand_reader.py#L30)

```python
snapshot(self, cur: Any, ware: int, article: str, start: date, end: date, forecast: Decimal | None, forecast_unit: str | None, actor: str, pallet_weight: Decimal | None=None, costs: list[dict[str, Any]] | None=None, candidate_route: int | None=None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `SlottingError`, `cur.execute`, `cur.fetchone`, `end.isoformat`, `format`, `incoming_stock_credit`, `int`, `json.dumps`, `json.dumps(sources, sort_keys=True, separators=(',', ':')).encode`, `localcontext`, `old_stock_credit`, `quantity_scenario`, `range_capacity`, `read_oracle_json`, `recommendation_sources`, `self._orders`, `sha256`, `sha256(json.dumps(sources, sort_keys=True, separators=(',', ':')).encode()).hexdigest`, `start.isoformat`, `sum`, `unpicked_demand`

### _orders

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/slotting_demand_reader.py:61](../../../api/wms_api_server/app/modules/inventory/infrastructure/slotting_demand_reader.py#L61)

```python
_orders(cur: Any, orders: list[dict[str, Any]], start: date, end: date) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.execute`, `cur.fetchall`, `days.get`, `end.isoformat`, `format`, `int`, `json.dumps`, `selected.append`, `start.isoformat`, `undated.append`, `unpicked_demand`

### range_capacity

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/slotting_layout.py:8](../../../api/wms_api_server/app/modules/inventory/infrastructure/slotting_layout.py#L8)

```python
range_capacity(cur: Any, ware: int, article: str, additional: str | None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `SlottingError`, `blockers.append`, `cells.count`, `cur.execute`, `cur.fetchall`, `cur.fetchone`, `format`, `getattr`, `len`, `localcontext`, `max`, `rows.append`, `set`, `str`, `str(exc.args[0]).split`

### old_stock_credit

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/slotting_stock.py:11](../../../api/wms_api_server/app/modules/inventory/infrastructure/slotting_stock.py#L11)

```python
old_stock_credit(cur: Any, ware: int, article: str, line_ids: list[int]) -> tuple[Decimal, list[dict[str, Any]]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `SlottingError`, `cur.execute`, `cur.fetchall`, `detail.append`, `format`, `json.dumps`, `len`, `map`, `min`

### incoming_stock_credit

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/slotting_stock.py:39](../../../api/wms_api_server/app/modules/inventory/infrastructure/slotting_stock.py#L39)

```python
incoming_stock_credit(cur: Any, ware: int, article: str) -> tuple[Decimal, list[dict[str, Any]]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `SlottingError`, `cur.execute`, `cur.fetchall`, `detail.append`, `format`, `identities.count`, `len`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/source_availability.py:8](../../../api/wms_api_server/app/modules/inventory/infrastructure/source_availability.py#L8)

```python
__init__(self, gateway: OracleGateway) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### list_sources

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/source_availability.py:11](../../../api/wms_api_server/app/modules/inventory/infrastructure/source_availability.py#L11)

```python
list_sources(self, warehouse: int, article: str, quantity: Decimal, purpose: str, min_days: int | None, min_percent: Decimal | None, after_uid: str, after_cell: str, limit: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `format`, `len`, `self.gateway.fetch_all`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/st_defer_waiting.py:10](../../../api/wms_api_server/app/modules/inventory/infrastructure/st_defer_waiting.py#L10)

```python
__init__(self, gateway: OracleGateway) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### plan

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/st_defer_waiting.py:13](../../../api/wms_api_server/app/modules/inventory/infrastructure/st_defer_waiting.py#L13)

```python
plan(self, request: WaitingTaskRequest, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `WaitingTaskError`, `_logger.warning`, `cur.callproc`, `cur.var`, `getattr`, `out.getvalue`, `read_oracle_json`, `self.gateway.transaction`, `str`, `str(exc.args[0]).split`

### read

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/st_defer_waiting.py:31](../../../api/wms_api_server/app/modules/inventory/infrastructure/st_defer_waiting.py#L31)

```python
read(self, decision: str, actor: str, after: int, limit: int) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `WaitingTaskError`, `cur.callproc`, `cur.execute`, `cur.fetchall`, `cur.fetchone`, `cur.var`, `dict`, `len`, `places.get`, `places_out.getvalue`, `read_oracle_json`, `self.gateway.transaction`, `str`, `zip`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/stock_posting_queries.py:7](../../../api/wms_api_server/app/modules/inventory/infrastructure/stock_posting_queries.py#L7)

```python
__init__(self, gateway: OracleGateway | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`

### status

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/stock_posting_queries.py:10](../../../api/wms_api_server/app/modules/inventory/infrastructure/stock_posting_queries.py#L10)

```python
status(self) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### operation

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/stock_posting_queries.py:16](../../../api/wms_api_server/app/modules/inventory/infrastructure/stock_posting_queries.py#L16)

```python
operation(self, operation_id: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### _oracle_code

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/stock_posting_uow.py:26](../../../api/wms_api_server/app/modules/inventory/infrastructure/stock_posting_uow.py#L26)

```python
_oracle_code(exc: Exception) -> int | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `getattr`

### _discard

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/stock_posting_uow.py:31](../../../api/wms_api_server/app/modules/inventory/infrastructure/stock_posting_uow.py#L31)

```python
_discard(pool: Any, connection: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_LOG.error`, `connection.close`, `pool.drop`

### _attempt

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/stock_posting_uow.py:41](../../../api/wms_api_server/app/modules/inventory/infrastructure/stock_posting_uow.py#L41)

```python
_attempt(lease: _Lease, payload: str, actor: str, operation_id: str, deadline: float) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockPostingError`, `connection.commit`, `connection.cursor`, `connection.rollback`, `cursor.close`, `cursor.execute`, `cursor.fetchone`, `cursor.var`, `hasattr`, `int`, `json.loads`, `max`, `min`, `monotonic`, `payload_bind.setvalue`, `prepare_staging_inputs`, `resolution_bind.setvalue`, `result.getvalue`, `stage_checked_births`, `stage_receipt`, `value.read`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/stock_posting_uow.py:117](../../../api/wms_api_server/app/modules/inventory/infrastructure/stock_posting_uow.py#L117)

```python
__init__(self, wait: Callable[[float], None] | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### post

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/stock_posting_uow.py:121](../../../api/wms_api_server/app/modules/inventory/infrastructure/stock_posting_uow.py#L121)

```python
post(self, command: StockCommand) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `': '.join`, `StockPostingError`, `_Lease`, `_attempt`, `_discard`, `_oracle_code`, `_oracle_pool`, `command.canonical_json`, `getattr`, `match.groups`, `monotonic`, `pool.acquire`, `pool.release`, `random.uniform`, `range`, `re.search`, `self.wait`, `str`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/stock_settings.py:6](../../../api/wms_api_server/app/modules/inventory/infrastructure/stock_settings.py#L6)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### set_compatibility

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/stock_settings.py:7](../../../api/wms_api_server/app/modules/inventory/infrastructure/stock_settings.py#L7)

```python
set_compatibility(self, enabled: bool, reason: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockSettingError`, `cur.callproc`, `getattr`, `self.gateway.transaction`, `str`, `str(exc.args[0]).split`

### prepare_staging_inputs

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/stock_staging_inputs.py:6](../../../api/wms_api_server/app/modules/inventory/infrastructure/stock_staging_inputs.py#L6)

```python
prepare_staging_inputs(cursor: oracledb.Cursor, command_document: dict[str, Any], operation_id: str) -> tuple[str | None, dict[str, Any], dict[str, Any] | None]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cursor.execute`, `cursor.fetchone`, `json.dumps`, `plan_pool`, `plan_receipt`, `prepare_birth_capture`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/store_return_receiving.py:11](../../../api/wms_api_server/app/modules/inventory/infrastructure/store_return_receiving.py#L11)

```python
__init__(self, gateway: Any, post: Callable[[str, str, dict[str, Any], dict[str, Any], str], dict[str, Any]]) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### configure

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/store_return_receiving.py:15](../../../api/wms_api_server/app/modules/inventory/infrastructure/store_return_receiving.py#L15)

```python
configure(self, ware_id: int, supplier_cell: str, disposal_cell: str, expected_version: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReturnReceiveError`, `cursor.execute`, `cursor.fetchall`, `getattr`, `reads.require_scope`, `stock_configuration_transaction`, `str`, `str(exc.args[0]).split`

### configure_reuse

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/store_return_receiving.py:37](../../../api/wms_api_server/app/modules/inventory/infrastructure/store_return_receiving.py#L37)

```python
configure_reuse(self, ware_id: int, receive_cell: str, expected_version: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReturnReceiveError`, `cursor.execute`, `getattr`, `reads.require_scope`, `self.policy`, `stock_configuration_transaction`, `str`, `str(exc.args[0]).split`

### policy

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/store_return_receiving.py:49](../../../api/wms_api_server/app/modules/inventory/infrastructure/store_return_receiving.py#L49)

```python
policy(self, ware_id: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `reads.policy`

### page

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/store_return_receiving.py:52](../../../api/wms_api_server/app/modules/inventory/infrastructure/store_return_receiving.py#L52)

```python
page(self, ware_id: int, after: str, limit: int, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `reads.page`

### source

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/store_return_receiving.py:55](../../../api/wms_api_server/app/modules/inventory/infrastructure/store_return_receiving.py#L55)

```python
source(self, ware_id: int, pickup_id: str, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `reads.source`

### pending

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/store_return_receiving.py:58](../../../api/wms_api_server/app/modules/inventory/infrastructure/store_return_receiving.py#L58)

```python
pending(self, ware_id: int, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReturnReceiveError`, `reads.page`

### confirm

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/store_return_receiving.py:63](../../../api/wms_api_server/app/modules/inventory/infrastructure/store_return_receiving.py#L63)

```python
confirm(self, operation_id: str, pickup_id: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReturnReceiveError`, `normalize_interwarehouse_scans`, `self.post`, `str`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/supplier_handover.py:10](../../../api/wms_api_server/app/modules/inventory/infrastructure/supplier_handover.py#L10)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### record

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/supplier_handover.py:13](../../../api/wms_api_server/app/modules/inventory/infrastructure/supplier_handover.py#L13)

```python
record(self, operation_id: str, dispatch_id: str, reference: str, document_hash: str, receiver: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self._write`

### confirm

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/supplier_handover.py:16](../../../api/wms_api_server/app/modules/inventory/infrastructure/supplier_handover.py#L16)

```python
confirm(self, operation_id: str, handover_id: str, reference: str, reason: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self._write`

### _write

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/supplier_handover.py:19](../../../api/wms_api_server/app/modules/inventory/infrastructure/supplier_handover.py#L19)

```python
_write(self, op: str, kind: str, values: list[str], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReturnReceiveError`, `cur.execute`, `cur.fetchone`, `cur.setinputsizes`, `dict`, `getattr`, `json.dumps`, `json.dumps([kind, values, actor], ensure_ascii=False, separators=(',', ':')).encode`, `op.encode`, `params.update`, `payload.update`, `read_oracle_json`, `receipt_task_metadata`, `sha256`, `sha256(json.dumps([kind, values, actor], ensure_ascii=False, separators=(',', ':')).encode()).digest`, `sha256(op.encode()).hexdigest`, `str`, `str(exc.args[0]).split`, `zip`

### pending

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/supplier_handover.py:59](../../../api/wms_api_server/app/modules/inventory/infrastructure/supplier_handover.py#L59)

```python
pending(self, ware_id: int, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReturnReceiveError`, `self.gateway.fetch_all`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/supplier_return.py:10](../../../api/wms_api_server/app/modules/inventory/infrastructure/supplier_return.py#L10)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### prepare

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/supplier_return.py:13](../../../api/wms_api_server/app/modules/inventory/infrastructure/supplier_return.py#L13)

```python
prepare(self, operation_id: str, receipt_id: str, supplier_inn: str, reason: str, reference: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReturnReceiveError`, `cur.callfunc`, `cur.execute`, `cur.fetchmany`, `cur.fetchone`, `cur.setinputsizes`, `getattr`, `int`, `json.dumps`, `json.dumps([receipt_id, supplier_inn, reason, reference, actor], ensure_ascii=False, separators=(',', ':')).encode`, `len`, `operation_id.encode`, `read_oracle_json`, `receipt_task_metadata`, `sha256`, `sha256(json.dumps([receipt_id, supplier_inn, reason, reference, actor], ensure_ascii=False, separators=(',', ':')).encode()).digest`, `sha256(operation_id.encode()).hexdigest`, `str`, `str(exc.args[0]).split`

### pending

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/supplier_return.py:55](../../../api/wms_api_server/app/modules/inventory/infrastructure/supplier_return.py#L55)

```python
pending(self, ware_id: int, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReturnReceiveError`, `self.gateway.fetch_all`

### suppliers

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/supplier_return.py:70](../../../api/wms_api_server/app/modules/inventory/infrastructure/supplier_return.py#L70)

```python
suppliers(self) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/tare.py:8](../../../api/wms_api_server/app/modules/inventory/infrastructure/tare.py#L8)

```python
__init__(self, gateway: Any, post: Callable[..., dict[str, Any]]) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### post

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/tare.py:11](../../../api/wms_api_server/app/modules/inventory/infrastructure/tare.py#L11)

```python
post(self, kind: str, operation_id: str, source: dict[str, Any], metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.poster`

### balances

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/tare.py:14](../../../api/wms_api_server/app/modules/inventory/infrastructure/tare.py#L14)

```python
balances(self, owner_ware_id: int, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### offers

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/tare.py:30](../../../api/wms_api_server/app/modules/inventory/infrastructure/tare.py#L30)

```python
offers(self, task_id: int, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### context

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/tare.py:49](../../../api/wms_api_server/app/modules/inventory/infrastructure/tare.py#L49)

```python
context(self, task_id: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TareError`, `len`, `participant_holders`, `self.gateway.fetch_all`

### damage_custody

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/tare.py:66](../../../api/wms_api_server/app/modules/inventory/infrastructure/tare.py#L66)

```python
damage_custody(self, ware_id: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `damage_custody`

### damage_cases

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/tare.py:69](../../../api/wms_api_server/app/modules/inventory/infrastructure/tare.py#L69)

```python
damage_cases(self, ware_id: int, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### case_snapshot

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/tare_assembly.py:110](../../../api/wms_api_server/app/modules/inventory/infrastructure/tare_assembly.py#L110)

```python
case_snapshot(gateway: Any, task_id: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `gateway.fetch_all`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/tare_assembly.py:6](../../../api/wms_api_server/app/modules/inventory/infrastructure/tare_assembly.py#L6)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### _warehouse

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/tare_assembly.py:9](../../../api/wms_api_server/app/modules/inventory/infrastructure/tare_assembly.py#L9)

```python
_warehouse(self, ware_id: int, actor: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TareError`, `self.gateway.fetch_all`

### recovery_candidates

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/tare_assembly.py:15](../../../api/wms_api_server/app/modules/inventory/infrastructure/tare_assembly.py#L15)

```python
recovery_candidates(self, load_operation_id: str, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `recovery_candidates`

### loaded_bookings

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/tare_assembly.py:18](../../../api/wms_api_server/app/modules/inventory/infrastructure/tare_assembly.py#L18)

```python
loaded_bookings(self, ware_id: int, task_id: int, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self._warehouse`, `self.gateway.fetch_all`

### forecast

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/tare_assembly.py:31](../../../api/wms_api_server/app/modules/inventory/infrastructure/tare_assembly.py#L31)

```python
forecast(self, ware_id: int, wave_id: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TareError`, `self._warehouse`, `self.gateway.fetch_all`

### loss_cases

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/tare_assembly.py:68](../../../api/wms_api_server/app/modules/inventory/infrastructure/tare_assembly.py#L68)

```python
loss_cases(self, ware_id: int, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self._warehouse`, `self.gateway.fetch_all`

### catalog

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/tare_assembly.py:79](../../../api/wms_api_server/app/modules/inventory/infrastructure/tare_assembly.py#L79)

```python
catalog(self, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### availability

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/tare_assembly.py:89](../../../api/wms_api_server/app/modules/inventory/infrastructure/tare_assembly.py#L89)

```python
availability(self, ware_id: int, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self._warehouse`, `self.gateway.fetch_all`

### bookings

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/tare_assembly.py:101](../../../api/wms_api_server/app/modules/inventory/infrastructure/tare_assembly.py#L101)

```python
bookings(self, ware_id: int, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self._warehouse`, `self.gateway.fetch_all`

### damage_custody

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/tare_damage_custody.py:5](../../../api/wms_api_server/app/modules/inventory/infrastructure/tare_damage_custody.py#L5)

```python
damage_custody(gateway: Any, ware: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `gateway.fetch_all`, `len`

### recovery_candidates

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/tare_load_recovery.py:6](../../../api/wms_api_server/app/modules/inventory/infrastructure/tare_load_recovery.py#L6)

```python
recovery_candidates(gateway: Any, load_operation_id: str, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TareError`, `gateway.fetch_all`, `len`

### participant_holders

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/tare_participant_read.py:5](../../../api/wms_api_server/app/modules/inventory/infrastructure/tare_participant_read.py#L5)

```python
participant_holders(gateway: Any, trip: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `bool`, `gateway.fetch_all`, `len`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/tare_policy.py:7](../../../api/wms_api_server/app/modules/inventory/infrastructure/tare_policy.py#L7)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### read

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/tare_policy.py:10](../../../api/wms_api_server/app/modules/inventory/infrastructure/tare_policy.py#L10)

```python
read(self, scope_kind: str, scope_key: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### configure

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/tare_policy.py:14](../../../api/wms_api_server/app/modules/inventory/infrastructure/tare_policy.py#L14)

```python
configure(self, scope_kind: str, scope_key: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TareError`, `cursor.execute`, `cursor.fetchall`, `getattr`, `self.read`, `stock_configuration_transaction`, `str`, `str(exc.args[0]).split`

### debt

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/tare_policy.py:36](../../../api/wms_api_server/app/modules/inventory/infrastructure/tare_policy.py#L36)

```python
debt(self, ware_id: int, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### complete_existing_task

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/task_completion.py:15](../../../api/wms_api_server/app/modules/inventory/infrastructure/task_completion.py#L15)

```python
complete_existing_task(gateway: OracleGateway | TransactionGateway, task_id: int, request: WarehouseTaskStatusRequest, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `HTTPException`, `StockCommand`, `_post_completion`, `format`, `gateway.fetch_all`, `int`, `json.loads`, `metadata.get`, `metadata.pop`, `metadata.update`, `normalize_incoming_sscc`, `request.model_dump`, `str`

### _post_completion

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/task_completion.py:61](../../../api/wms_api_server/app/modules/inventory/infrastructure/task_completion.py#L61)

```python
_post_completion(command: StockCommand) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `StockPosting`, `StockPosting().post`

### lock_domain

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/task_completion.py:73](../../../api/wms_api_server/app/modules/inventory/infrastructure/task_completion.py#L73)

```python
lock_domain(gateway: OracleGateway | TransactionGateway, task: dict[str, Any]) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `gateway.fetch_all`, `rows[0].get`, `task.get`

### run_existing_task_action

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/task_completion.py:90](../../../api/wms_api_server/app/modules/inventory/infrastructure/task_completion.py#L90)

```python
run_existing_task_action(gateway: OracleGateway | TransactionGateway, task_id: int, action: str, request: WarehouseTaskStatusRequest, service_factory: Callable[[TransactionGateway], TaskActionHandler]) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `TransactionGateway`, `ValueError`, `bound.fetch_all`, `cursor.execute`, `gateway.transaction`, `getattr`, `getattr(service, action)`, `lock_domain`, `service.get_task_or_404`, `service_factory`

### task_progress

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/task_progress.py:7](../../../api/wms_api_server/app/modules/inventory/infrastructure/task_progress.py#L7)

```python
task_progress(gateway: Any, task_id: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `HTTPException`, `any`, `format`, `gateway.fetch_all`, `iter`, `len`, `localcontext`, `max`, `next`, `pending.sort`, `sum`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/task_queue_read.py:48](../../../api/wms_api_server/app/modules/inventory/infrastructure/task_queue_read.py#L48)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### list

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/task_queue_read.py:51](../../../api/wms_api_server/app/modules/inventory/infrastructure/task_queue_read.py#L51)

```python
list(self, status: str | None=None, task_type: str | None=None, task_source: str | None=None, assigned_to: str | None=None, production_order_id: int | None=None, source_doc_type: str | None=None, source_doc_id: int | None=None, limit: int=100, scope_warehouse_id: int | None=None, scope_global: bool=True, queue_group: str | None=None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `HTTPException`, `_LIST_SQL.format`, `assigned_to.upper`, `conditions.append`, `max`, `min`, `self.gateway.fetch_all`, `source_doc_type.upper`, `status.upper`, `task_source.upper`, `task_type.upper`

### get

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/task_queue_read.py:101](../../../api/wms_api_server/app/modules/inventory/infrastructure/task_queue_read.py#L101)

```python
get(self, task_id: int) -> dict[str, Any] | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### read_task_snapshot

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/task_read_scope.py:11](../../../api/wms_api_server/app/modules/inventory/infrastructure/task_read_scope.py#L11)

```python
read_task_snapshot(gateway: OracleGateway, actor: str, loader: Callable[[TransactionGateway, TaskViewScope], Result], task_id: int | None=None) -> Result
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TaskReadError`, `TaskViewScope`, `TransactionGateway`, `bool`, `bound.fetch_all`, `cursor.callproc`, `cursor.execute`, `gateway.transaction`, `getattr`, `int`, `loader`

### read_task_progress_snapshot

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/task_read_scope.py:36](../../../api/wms_api_server/app/modules/inventory/infrastructure/task_read_scope.py#L36)

```python
read_task_progress_snapshot(gateway: OracleGateway, task_id: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TaskReadError`, `bound.cursor.callproc`, `getattr`, `read_task_snapshot`, `task_progress`

### load

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/task_read_scope.py:38](../../../api/wms_api_server/app/modules/inventory/infrastructure/task_read_scope.py#L38)

```python
load(bound: TransactionGateway, scope: TaskViewScope) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TaskReadError`, `bound.cursor.callproc`, `getattr`, `task_progress`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/task_scan_drafts.py:12](../../../api/wms_api_server/app/modules/inventory/infrastructure/task_scan_drafts.py#L12)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### context

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/task_scan_drafts.py:15](../../../api/wms_api_server/app/modules/inventory/infrastructure/task_scan_drafts.py#L15)

```python
context(self, task_id: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `len`, `result.pop`, `self.gateway.fetch_all`

### latest

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/task_scan_drafts.py:35](../../../api/wms_api_server/app/modules/inventory/infrastructure/task_scan_drafts.py#L35)

```python
latest(self, task_id: int, actor: str) -> dict[str, Any] | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `json.loads`, `row.pop`, `self.gateway.fetch_all`

### save

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/task_scan_drafts.py:47](../../../api/wms_api_server/app/modules/inventory/infrastructure/task_scan_drafts.py#L47)

```python
save(self, task_id: int, request: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `TaskScanDrafts`, `TaskScanDrafts(bound).context`, `TransactionGateway`, `bound.fetch_all`, `cursor.execute`, `cursor.setinputsizes`, `format`, `json.dumps`, `len`, `self.gateway.transaction`, `self.resolve`, `wire.encode`

### resolve

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/task_scan_drafts.py:79](../../../api/wms_api_server/app/modules/inventory/infrastructure/task_scan_drafts.py#L79)

```python
resolve(cursor: Any, context: dict[str, Any], scans: list[dict[str, str]]) -> tuple[list[str], Decimal]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `HTTPException`, `any`, `batch.append`, `canonical_mark`, `cursor.execute`, `cursor.var`, `enumerate`, `identity.encode`, `int`, `json.dumps`, `len`, `localcontext`, `payload.setvalue`, `physical.values`, `range`, `resolved.values`, `seen.add`, `set`, `sha256`, `sha256(identity.encode('utf-8')).hexdigest`, `sorted`, `str`, `sum`

### post_terminal_quality

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/terminal_quality_commands.py:14](../../../api/wms_api_server/app/modules/inventory/infrastructure/terminal_quality_commands.py#L14)

```python
post_terminal_quality(gateway: OracleGateway | TransactionGateway, pallet: str, request: LotCheckRequest) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockCommand`, `StockPosting`, `StockPosting().post`, `ValueError`, `checked.append`, `datetime.fromisoformat`, `datetime.strptime`, `errors.append`, `isinstance`, `quantity_text`, `require_active_release`, `stamp.strftime`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/trace_aggregation_lifecycle.py:11](../../../api/wms_api_server/app/modules/inventory/infrastructure/trace_aggregation_lifecycle.py#L11)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### invalidate

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/trace_aggregation_lifecycle.py:14](../../../api/wms_api_server/app/modules/inventory/infrastructure/trace_aggregation_lifecycle.py#L14)

```python
invalidate(self, operation_id: str, request: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TraceManifestError`, `getattr`, `json.dumps`, `q.execute`, `q.setinputsizes`, `q.var`, `read_oracle_json`, `receipt_task_metadata`, `result.getvalue`, `str`, `str(exc.args[0]).split`

### list

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/trace_aggregation_lifecycle.py:29](../../../api/wms_api_server/app/modules/inventory/infrastructure/trace_aggregation_lifecycle.py#L29)

```python
list(self, origin: str, ware: int, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TraceManifestError`, `dict`, `item.update`, `len`, `q.execute`, `q.fetchmany`, `q.fetchone`, `result.append`, `self.gateway.transaction`, `zip`

### source_header

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/trace_aggregation_source.py:9](../../../api/wms_api_server/app/modules/inventory/infrastructure/trace_aggregation_source.py#L9)

```python
source_header(cur: Any, manifest_id: str, uid: str, article: str, base: str, cell: str, source_kind: str, source_doc: int, actor: str, policy_version: int, profiles: dict[tuple[str, str], dict[str, Any]]) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `ValueError`, `cur.execute`, `cur.fetchone`, `read_oracle_json`, `str`, `str(row[3]).zfill`

### aggregation_members

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/trace_aggregation_source.py:19](../../../api/wms_api_server/app/modules/inventory/infrastructure/trace_aggregation_source.py#L19)

```python
aggregation_members(cur: Any, order_id: str, line_number: str, profile: tuple[str, str], code: str, agg_level: str, manifest_id: str | None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `code.encode`, `cur.execute`, `cur.fetchone`, `read_oracle_json`, `sha256`, `sha256(code.encode()).hexdigest`

### assert_sender_capture

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/trace_aggregation_source.py:30](../../../api/wms_api_server/app/modules/inventory/infrastructure/trace_aggregation_source.py#L30)

```python
assert_sender_capture(header: dict[str, Any], units: dict[str, dict[tuple[str, str], str]], quantities: dict[str, Decimal], base: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `canonical_mark`, `set`, `unit_quantity`, `units[uid].items`

### assert_current_mark_policy

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/trace_aggregation_source.py:43](../../../api/wms_api_server/app/modules/inventory/infrastructure/trace_aggregation_source.py#L43)

```python
assert_current_mark_policy(cur: Any, pallet: str, marks: dict[str, Any]) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `cur.execute`, `cur.fetchmany`, `cur.fetchone`

### persist_scanned_aggregates

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/trace_aggregation_source.py:52](../../../api/wms_api_server/app/modules/inventory/infrastructure/trace_aggregation_source.py#L52)

```python
persist_scanned_aggregates(cur: Any, pallet: str, scanned: list[dict[str, Any]]) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `aggregation['code'].encode`, `cur.execute`, `cur.setinputsizes`, `seen.add`, `set`, `sha256`, `sha256(aggregation['code'].encode()).hexdigest`

### capture_context

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/trace_capture_context.py:5](../../../api/wms_api_server/app/modules/inventory/infrastructure/trace_capture_context.py#L5)

```python
capture_context(gateway: Any, kind: str, document_id: int, article: str, cell: str, pallet: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TraceManifestError`, `cur.execute`, `cur.fetchmany`, `cur.fetchone`, `gateway.transaction`, `int`, `len`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/trace_sender_manifest.py:14](../../../api/wms_api_server/app/modules/inventory/infrastructure/trace_sender_manifest.py#L14)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### import_manifest

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/trace_sender_manifest.py:17](../../../api/wms_api_server/app/modules/inventory/infrastructure/trace_sender_manifest.py#L17)

```python
import_manifest(self, operation_id: str, raw: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `TraceManifestError`, `cur.execute`, `cur.fetchmany`, `cur.fetchone`, `format`, `getattr`, `json.dumps`, `json.dumps([raw, actor], ensure_ascii=False, separators=(',', ':')).encode`, `len`, `parse_manifest`, `raw.encode`, `read_oracle_json`, `receipt_task_metadata`, `resolve_aggregates`, `self._persist`, `self._scope`, `sha256`, `sha256(json.dumps([raw, actor], ensure_ascii=False, separators=(',', ':')).encode()).digest`, `sha256(raw.encode()).hexdigest`, `str`, `str(article_row[0]).zfill`, `str(exc.args[0]).split`, `sum`, `units.values`, `validate_units`

### _scope

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/trace_sender_manifest.py:56](../../../api/wms_api_server/app/modules/inventory/infrastructure/trace_sender_manifest.py#L56)

```python
_scope(cur: Any, ware: int, actor: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TraceManifestError`, `cur.execute`, `cur.fetchone`

### _persist

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/trace_sender_manifest.py:62](../../../api/wms_api_server/app/modules/inventory/infrastructure/trace_sender_manifest.py#L62)

```python
_persist(cur: Any, op: str, digest: bytes, raw: str, document: dict[str, Any], profiles: dict[tuple[str, str], dict[str, Any]], aggregates: list[dict[str, Any]], quantity: Decimal, result: dict[str, Any], actor: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.execute`, `cur.setinputsizes`, `json.dumps`, `profiles.items`, `sorted`

### list

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/trace_sender_manifest.py:69](../../../api/wms_api_server/app/modules/inventory/infrastructure/trace_sender_manifest.py#L69)

```python
list(self, ware_id: int, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `column[0].lower`, `cur.execute`, `cur.fetchall`, `dict`, `self._scope`, `self.gateway.transaction`, `zip`

### capture_context

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/trace_sender_manifest.py:76](../../../api/wms_api_server/app/modules/inventory/infrastructure/trace_sender_manifest.py#L76)

```python
capture_context(self, kind: str, document_id: int, article: str, cell: str, pallet: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `capture_context`

### invalidate_aggregate

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/trace_sender_manifest.py:80](../../../api/wms_api_server/app/modules/inventory/infrastructure/trace_sender_manifest.py#L80)

```python
invalidate_aggregate(self, operation_id: str, request: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TraceAggregationLifecycle`, `TraceAggregationLifecycle(self.gateway).invalidate`

### aggregates

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/trace_sender_manifest.py:84](../../../api/wms_api_server/app/modules/inventory/infrastructure/trace_sender_manifest.py#L84)

```python
aggregates(self, origin: str, ware: int, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TraceAggregationLifecycle`, `TraceAggregationLifecycle(self.gateway).list`

### assert_hu_view

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/warehouse_hu.py:163](../../../api/wms_api_server/app/modules/inventory/infrastructure/warehouse_hu.py#L163)

```python
assert_hu_view(cur: Any, actor: str, warehouse: int) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `cur.execute`, `cur.fetchone`, `str`, `str(row[1] or '').strip`, `str(row[1] or '').strip().upper`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/warehouse_hu.py:16](../../../api/wms_api_server/app/modules/inventory/infrastructure/warehouse_hu.py#L16)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### preview

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/warehouse_hu.py:19](../../../api/wms_api_server/app/modules/inventory/infrastructure/warehouse_hu.py#L19)

```python
preview(self, identifier: str, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `TransactionGateway`, `WarehouseHu`, `assert_hu_view`, `bound._preview`, `cur.execute`, `cur.fetchall`, `data.get`, `getattr`, `int`, `len`, `recorded_placement`, `self.gateway.transaction`, `str`

### _preview

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/warehouse_hu.py:37](../../../api/wms_api_server/app/modules/inventory/infrastructure/warehouse_hu.py#L37)

```python
_preview(self, identifier: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `HTTPException`, `abs`, `case_number.isascii`, `case_number.isdigit`, `departure_subtree`, `format`, `getattr`, `identifier.startswith`, `int`, `isinstance`, `json.dumps`, `json.loads`, `len`, `node.get`, `normalize_incoming_sscc`, `rows[0].get`, `self.gateway.fetch_all`, `sorted`, `str`, `str(getattr(error, 'message', exc)).split`, `totals.get`, `totals.items`

### target_slots

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/warehouse_hu.py:109](../../../api/wms_api_server/app/modules/inventory/infrastructure/warehouse_hu.py#L109)

```python
target_slots(self, cell: str, warehouse: int, actor: str) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TransactionGateway`, `WarehouseHu`, `WarehouseHu(TransactionGateway(cur))._target_slots`, `assert_hu_view`, `cur.execute`, `getattr`, `self.gateway.transaction`

### _target_slots

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/warehouse_hu.py:116](../../../api/wms_api_server/app/modules/inventory/infrastructure/warehouse_hu.py#L116)

```python
_target_slots(self, cell: str, warehouse: int) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### command

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/warehouse_hu.py:147](../../../api/wms_api_server/app/modules/inventory/infrastructure/warehouse_hu.py#L147)

```python
command(self, kind: str, uid: str, operation_id: str, metadata: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockCommand`, `StockPosting`, `StockPosting().post`, `dict`, `metadata.get`, `normalize_incoming_sscc`, `self.gateway.fetch_all`

### scale_error

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/warehouse_scales.py:11](../../../api/wms_api_server/app/modules/inventory/infrastructure/warehouse_scales.py#L11)

```python
scale_error(exc: oracledb.DatabaseError) -> WarehouseScaleError
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `WarehouseScaleError`, `str`, `str(exc.args[0]).split`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/warehouse_scales.py:19](../../../api/wms_api_server/app/modules/inventory/infrastructure/warehouse_scales.py#L19)

```python
__init__(self, gateway: OracleGateway) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### configure

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/warehouse_scales.py:22](../../../api/wms_api_server/app/modules/inventory/infrastructure/warehouse_scales.py#L22)

```python
configure(self, device: str, body: WarehouseScaleConfiguration, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `WarehouseScaleError`, `int`, `q.execute`, `q.fetchone`, `scale_error`, `stock_configuration_transaction`

### capture

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/warehouse_scales.py:49](../../../api/wms_api_server/app/modules/inventory/infrastructure/warehouse_scales.py#L49)

```python
capture(self, body: WarehouseScalePacket | WarehouseFinalScalePacket, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `body.model_dump`, `json.dumps`, `out.getvalue`, `q.callproc`, `q.var`, `read_oracle_json`, `scale_error`, `self.gateway.transaction`

### readings

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/warehouse_scales.py:59](../../../api/wms_api_server/app/modules/inventory/infrastructure/warehouse_scales.py#L59)

```python
readings(self, task: int, line: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `len`, `q.callproc`, `q.execute`, `q.fetchall`, `read_oracle_json`, `scale_error`, `self.gateway.transaction`

### reading

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/warehouse_scales.py:76](../../../api/wms_api_server/app/modules/inventory/infrastructure/warehouse_scales.py#L76)

```python
reading(self, key: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `WarehouseScaleError`, `int`, `len`, `q.callproc`, `q.execute`, `q.fetchmany`, `q.fetchone`, `read_oracle_json`, `scale_error`, `self.gateway.transaction`

### final_readings

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/warehouse_scales.py:96](../../../api/wms_api_server/app/modules/inventory/infrastructure/warehouse_scales.py#L96)

```python
final_readings(self, task: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `len`, `q.callproc`, `q.execute`, `q.fetchall`, `read_oracle_json`, `scale_error`, `self.gateway.transaction`

### reserve_wave_sources

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/wave_commands.py:13](../../../api/wms_api_server/app/modules/inventory/infrastructure/wave_commands.py#L13)

```python
reserve_wave_sources(gateway: OracleGateway | TransactionGateway, wave_id: int, actor: str, row_ids: list[int] | None=None) -> bool
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `StockCommand`, `StockPosting`, `StockPosting().post`, `command.canonical_json`, `cursor.execute`, `cursor.fetchall`, `cursor.fetchone`, `gateway.transaction`, `hasattr`, `int`, `json.dumps`, `json.loads`, `len`, `pending.append`, `require_active_release`, `saved.read`, `uuid4`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/wave_execution.py:11](../../../api/wms_api_server/app/modules/inventory/infrastructure/wave_execution.py#L11)

```python
__init__(self, gateway: OracleGateway | TransactionGateway) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### preview

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/wave_execution.py:14](../../../api/wms_api_server/app/modules/inventory/infrastructure/wave_execution.py#L14)

```python
preview(self, wave_id: int, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `execution_snapshot`

### finish

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/wave_execution.py:17](../../../api/wms_api_server/app/modules/inventory/infrastructure/wave_execution.py#L17)

```python
finish(self, wave_id: int, operation_id: str, actor: str, disposition: str | None=None, reason: str | None=None) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockCommand`, `StockPosting`, `StockPosting().post`

### assert_wave_view

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/wave_execution_reader.py:7](../../../api/wms_api_server/app/modules/inventory/infrastructure/wave_execution_reader.py#L7)

```python
assert_wave_view(cur: Any, wave: int, actor: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `cur.callproc`, `getattr`, `str`

### execution_snapshot

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/wave_execution_reader.py:21](../../../api/wms_api_server/app/modules/inventory/infrastructure/wave_execution_reader.py#L21)

```python
execution_snapshot(gateway: Any, wave: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `assert_wave_view`, `cases.get`, `cur.execute`, `cur.fetchall`, `cur.fetchone`, `gateway.transaction`, `getattr`, `hasattr`, `int`, `json.loads`, `len`, `raw.read`, `str`

### read_wave_header

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/wave_header.py:4](../../../api/wms_api_server/app/modules/inventory/infrastructure/wave_header.py#L4)

```python
read_wave_header(gateway: Any, pick_wave_id: int) -> dict[str, Any] | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `gateway.fetch_all`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/wave_pick_release.py:13](../../../api/wms_api_server/app/modules/inventory/infrastructure/wave_pick_release.py#L13)

```python
__init__(self, gateway: OracleGateway | TransactionGateway) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### preview

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/wave_pick_release.py:16](../../../api/wms_api_server/app/modules/inventory/infrastructure/wave_pick_release.py#L16)

```python
preview(self, wave_id: int, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `assert_wave_view`, `cursor.execute`, `cursor.fetchone`, `getattr`, `hasattr`, `json.loads`, `raw.read`, `self.gateway.transaction`

### release

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/wave_pick_release.py:25](../../../api/wms_api_server/app/modules/inventory/infrastructure/wave_pick_release.py#L25)

```python
release(self, wave_id: int, operation_id: str, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockCommand`, `StockPosting`, `StockPosting().post`

### _scope

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/wave_planning.py:7](../../../api/wms_api_server/app/modules/inventory/infrastructure/wave_planning.py#L7)

```python
_scope(cursor: Any, warehouse: int | None, actor: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `WavePlanningError`, `cursor.execute`, `cursor.fetchone`

### create_wave

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/wave_planning.py:18](../../../api/wms_api_server/app/modules/inventory/infrastructure/wave_planning.py#L18)

```python
create_wave(gateway: Any, request: Any) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_scope`, `cursor.callfunc`, `gateway.transaction`, `int`, `request.model_dump`, `request.model_dump().items`

### add_plan

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/wave_planning.py:25](../../../api/wms_api_server/app/modules/inventory/infrastructure/wave_planning.py#L25)

```python
add_plan(gateway: Any, wave: int, request: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `WavePlanningError`, `_scope`, `cursor.callproc`, `cursor.execute`, `cursor.fetchone`, `gateway.transaction`, `getattr`, `str`, `str(exc.args[0]).split`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/wave_queue_reads.py:9](../../../api/wms_api_server/app/modules/inventory/infrastructure/wave_queue_reads.py#L9)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### wave

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/wave_queue_reads.py:12](../../../api/wms_api_server/app/modules/inventory/infrastructure/wave_queue_reads.py#L12)

```python
wave(self, wave_id: int, actor: str, reader: Callable[[Any], Any]) -> Any
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `TransactionGateway`, `assert_wave_view`, `cursor.execute`, `getattr`, `reader`, `self.gateway.transaction`

### waves

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/wave_queue_reads.py:21](../../../api/wms_api_server/app/modules/inventory/infrastructure/wave_queue_reads.py#L21)

```python
waves(self, actor: str, warehouse: int | None, reader: Callable[[Any, int | None], Any]) -> Any
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `TransactionGateway`, `cursor.execute`, `cursor.fetchone`, `getattr`, `reader`, `self.gateway.transaction`

### _target

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/wave_staging.py:7](../../../api/wms_api_server/app/modules/inventory/infrastructure/wave_staging.py#L7)

```python
_target(cursor: Any, wave: int, cell: str, actor: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `WavePlanningError`, `cursor.execute`, `cursor.fetchone`

### _release

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/wave_staging.py:25](../../../api/wms_api_server/app/modules/inventory/infrastructure/wave_staging.py#L25)

```python
_release(cursor: Any, wave: int, cell: str, actor: str) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `WavePlanningError`, `cursor.execute`, `cursor.fetchmany`, `len`

### release_staging

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/wave_staging.py:63](../../../api/wms_api_server/app/modules/inventory/infrastructure/wave_staging.py#L63)

```python
release_staging(gateway: Any, wave: int, request: Any) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `WavePlanningError`, `_release`, `_target`, `gateway.transaction`, `getattr`, `str`, `str(request.to_cell or '').strip`

### decode_box

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/weighted_box_capture.py:9](../../../api/wms_api_server/app/modules/inventory/infrastructure/weighted_box_capture.py#L9)

```python
decode_box(cur: Any, raw: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.callfunc`, `hasattr`, `json.loads`, `value.read`

### resolve_weighted_boxes

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/weighted_box_capture.py:14](../../../api/wms_api_server/app/modules/inventory/infrastructure/weighted_box_capture.py#L14)

```python
resolve_weighted_boxes(cur: Any, article: str, quantity: Decimal, payload: dict, base: str, policy: tuple) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `ValueError`, `bool`, `box_dimensions`, `canonical_mark`, `cur.callproc`, `cur.execute`, `cur.fetchall`, `decode_box`, `int`, `isinstance`, `item.get`, `len`, `payload.get`, `quantities.values`, `set`, `sum`

### assert_current_weighted_policy

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/weighted_box_capture.py:61](../../../api/wms_api_server/app/modules/inventory/infrastructure/weighted_box_capture.py#L61)

```python
assert_current_weighted_policy(cur: Any, pallet: str, marks: dict) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `cur.callproc`, `cur.execute`, `cur.fetchmany`, `cur.fetchone`, `marks['weighted_boxes'].values`

### box_dimensions

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/weighted_box_capture.py:78](../../../api/wms_api_server/app/modules/inventory/infrastructure/weighted_box_capture.py#L78)

```python
box_dimensions(item: dict, net: Decimal) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `ValueError`, `any`, `dimensions.values`, `format`, `isinstance`, `item.get`, `len`, `measurement.as_tuple`, `measurement.is_finite`, `reference.strip`

### prepare_weighted_case

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/weighted_case_pick.py:107](../../../api/wms_api_server/app/modules/inventory/infrastructure/weighted_case_pick.py#L107)

```python
prepare_weighted_case(gateway: OracleGateway, task: int, line: int, request: WeightedCaseRequest, actor: str) -> tuple[dict[str, Any], tuple[str, ...]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `ValueError`, `bool`, `cur.callproc`, `cur.execute`, `cur.fetchall`, `decode_box`, `format`, `gateway.transaction`, `int`, `len`, `request.model_dump`, `resolve_case_codes`, `set`, `str`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/weighted_case_pick.py:15](../../../api/wms_api_server/app/modules/inventory/infrastructure/weighted_case_pick.py#L15)

```python
__init__(self, gateway: OracleGateway) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### short_weight_preview

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/weighted_case_pick.py:18](../../../api/wms_api_server/app/modules/inventory/infrastructure/weighted_case_pick.py#L18)

```python
short_weight_preview(self, short: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockPostingError`, `int`, `q.callfunc`, `q.callproc`, `q.execute`, `q.fetchone`, `read_oracle_json`, `self.gateway.transaction`

### weight_preview

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/weighted_case_pick.py:34](../../../api/wms_api_server/app/modules/inventory/infrastructure/weighted_case_pick.py#L34)

```python
weight_preview(self, task: int, line: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockPostingError`, `q.callfunc`, `q.execute`, `read_oracle_json`, `self.gateway.transaction`

### weigh_line

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/weighted_case_pick.py:45](../../../api/wms_api_server/app/modules/inventory/infrastructure/weighted_case_pick.py#L45)

```python
weigh_line(self, task: int, line: int, request: WeighedLineRequest, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `StockCommand`, `StockPosting`, `StockPosting().post`, `StockPostingError`, `ValueError`, `format`, `old['metadata'].get`, `q.callproc`, `q.execute`, `q.fetchone`, `read_oracle_json`, `request.model_dump`, `self.gateway.fetch_all`, `self.gateway.transaction`, `str`

### confirm

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/weighted_case_pick.py:84](../../../api/wms_api_server/app/modules/inventory/infrastructure/weighted_case_pick.py#L84)

```python
confirm(self, task: int, line: int, request: WeightedCaseRequest, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockCommand`, `StockPosting`, `StockPosting().post`, `StockPostingError`, `old['metadata'].get`, `prepare_weighted_case`, `read_oracle_json`, `request.model_dump`, `self.gateway.fetch_all`, `tuple`

### choice_error

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/weighted_planning.py:63](../../../api/wms_api_server/app/modules/inventory/infrastructure/weighted_planning.py#L63)

```python
choice_error(exc: oracledb.DatabaseError, choice: str) -> StockPostingError
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockPostingError`, `str`, `str(exc).split`

### __init__

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/weighted_planning.py:13](../../../api/wms_api_server/app/modules/inventory/infrastructure/weighted_planning.py#L13)

```python
__init__(self, gateway: OracleGateway) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### options

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/weighted_planning.py:16](../../../api/wms_api_server/app/modules/inventory/infrastructure/weighted_planning.py#L16)

```python
options(self, row: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self._options`

### approval_options

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/weighted_planning.py:19](../../../api/wms_api_server/app/modules/inventory/infrastructure/weighted_planning.py#L19)

```python
approval_options(self, row: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self._options`

### _options

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/weighted_planning.py:22](../../../api/wms_api_server/app/modules/inventory/infrastructure/weighted_planning.py#L22)

```python
_options(self, row: int, actor: str, permission: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockPostingError`, `len`, `q.callfunc`, `q.execute`, `q.fetchall`, `read_oracle_json`, `self.gateway.transaction`

### approve

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/weighted_planning.py:41](../../../api/wms_api_server/app/modules/inventory/infrastructure/weighted_planning.py#L41)

```python
approve(self, body: WeightedBoxChoiceRequest, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `body.model_dump`, `choice_error`, `json.dumps`, `out.getvalue`, `q.callproc`, `q.var`, `read_oracle_json`, `receipt_task_metadata`

### cancel

[Исходник: api/wms_api_server/app/modules/inventory/infrastructure/weighted_planning.py:53](../../../api/wms_api_server/app/modules/inventory/infrastructure/weighted_planning.py#L53)

```python
cancel(self, choice: str, reason: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `choice_error`, `out.getvalue`, `q.callproc`, `q.var`, `read_oracle_json`, `receipt_task_metadata`

### build_receiving_service

[Исходник: api/wms_api_server/app/modules/inventory/public.py:20](../../../api/wms_api_server/app/modules/inventory/public.py#L20)

```python
build_receiving_service() -> Receiving
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `Receiving`

### build_label_service

[Исходник: api/wms_api_server/app/modules/inventory/public.py:23](../../../api/wms_api_server/app/modules/inventory/public.py#L23)

```python
build_label_service() -> ReceiptLabels
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `ReceiptLabels`

### build_configuration_service

[Исходник: api/wms_api_server/app/modules/inventory/public.py:26](../../../api/wms_api_server/app/modules/inventory/public.py#L26)

```python
build_configuration_service() -> ReceiptConfiguration
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `ReceiptConfiguration`

### build_reconciliation_service

[Исходник: api/wms_api_server/app/modules/inventory/public.py:29](../../../api/wms_api_server/app/modules/inventory/public.py#L29)

```python
build_reconciliation_service() -> ReceiptReconciliation
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `ReceiptReconciliation`

### pallet_composition

[Исходник: api/wms_api_server/app/modules/inventory/public.py:32](../../../api/wms_api_server/app/modules/inventory/public.py#L32)

```python
pallet_composition(pallet: str, after: str='', limit: int=50, expected_signature: str | None=None) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `ReceivingQueries`, `ReceivingQueries(OracleGateway()).composition`, `max`, `min`

### build_query_service

[Исходник: api/wms_api_server/app/modules/inventory/public.py:35](../../../api/wms_api_server/app/modules/inventory/public.py#L35)

```python
build_query_service() -> ReceivingQueries
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `ReceivingQueries`

### complete_existing_warehouse_task

[Исходник: api/wms_api_server/app/modules/inventory/public.py:38](../../../api/wms_api_server/app/modules/inventory/public.py#L38)

```python
complete_existing_warehouse_task(gateway: OracleGateway | TransactionGateway, task_id: int, request: WarehouseTaskStatusRequest, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `complete_existing_task`

### run_existing_warehouse_task_action

[Исходник: api/wms_api_server/app/modules/inventory/public.py:42](../../../api/wms_api_server/app/modules/inventory/public.py#L42)

```python
run_existing_warehouse_task_action(gateway: OracleGateway | TransactionGateway, task_id: int, action: str, request: WarehouseTaskStatusRequest, service_factory: Callable[[TransactionGateway], TaskActionHandler]) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `run_existing_task_action`

### build_stock_queries_service

[Исходник: api/wms_api_server/app/modules/inventory/public.py:57](../../../api/wms_api_server/app/modules/inventory/public.py#L57)

```python
build_stock_queries_service() -> StockPostingQueries
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `StockPostingQueries`

### build_stock_posting_service

[Исходник: api/wms_api_server/app/modules/inventory/public.py:60](../../../api/wms_api_server/app/modules/inventory/public.py#L60)

```python
build_stock_posting_service() -> StockPosting
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockPosting`

### build_manual_stock_move_service

[Исходник: api/wms_api_server/app/modules/inventory/public.py:68](../../../api/wms_api_server/app/modules/inventory/public.py#L68)

```python
build_manual_stock_move_service() -> ManualStockMove
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ManualStockMove`, `build_stock_posting_service`

### inventory_configuration_transaction

[Исходник: api/wms_api_server/app/modules/inventory/public.py:73](../../../api/wms_api_server/app/modules/inventory/public.py#L73)

```python
inventory_configuration_transaction(gateway: OracleGateway | TransactionGateway, label: str, actor: str, permission: str) -> AbstractContextManager[oracledb.Cursor]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `configuration_transaction`

### reserve_existing_wave_sources

[Исходник: api/wms_api_server/app/modules/inventory/public.py:77](../../../api/wms_api_server/app/modules/inventory/public.py#L77)

```python
reserve_existing_wave_sources(gateway: OracleGateway | TransactionGateway, wave_id: int, actor: str) -> bool
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `reserve_wave_sources`

### release_existing_document_reservations

[Исходник: api/wms_api_server/app/modules/inventory/public.py:81](../../../api/wms_api_server/app/modules/inventory/public.py#L81)

```python
release_existing_document_reservations(gateway: OracleGateway | TransactionGateway, document_type: str, document_id: int, actor: str, reason: str, **scope: bool | str | None) -> bool
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `release_document_reservations`

### post_existing_mes_task

[Исходник: api/wms_api_server/app/modules/inventory/public.py:85](../../../api/wms_api_server/app/modules/inventory/public.py#L85)

```python
post_existing_mes_task(gateway: OracleGateway | TransactionGateway, action: str, task: dict, request: MesRawTransferTaskConfirmRequest | MesRawTransferTaskCancelRequest) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `post_mes_task`

### calculate_existing_mes_supply

[Исходник: api/wms_api_server/app/modules/inventory/public.py:89](../../../api/wms_api_server/app/modules/inventory/public.py#L89)

```python
calculate_existing_mes_supply(gateway: OracleGateway | TransactionGateway, order_id: int, request: MesRawSupplyCalculateRequest) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `calculate_supply`

### build_receipt_reverse_service

[Исходник: api/wms_api_server/app/modules/inventory/public.py:99](../../../api/wms_api_server/app/modules/inventory/public.py#L99)

```python
build_receipt_reverse_service() -> ReceiptReverse
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ReceiptReverse`, `build_stock_posting_service`

### post_existing_case_pick

[Исходник: api/wms_api_server/app/modules/inventory/public.py:104](../../../api/wms_api_server/app/modules/inventory/public.py#L104)

```python
post_existing_case_pick(gateway: OracleGateway | TransactionGateway, task_id: int, line_id: int, request: CasePickLineConfirmRequest) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `post_case_pick`

### warehouse_metadata_transaction

[Исходник: api/wms_api_server/app/modules/inventory/public.py:108](../../../api/wms_api_server/app/modules/inventory/public.py#L108)

```python
warehouse_metadata_transaction(gateway: OracleGateway | TransactionGateway, purpose: str, actor: str, permission: str) -> AbstractContextManager[oracledb.Cursor]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `receipt_task_metadata`

### existing_case_pick_policy

[Исходник: api/wms_api_server/app/modules/inventory/public.py:112](../../../api/wms_api_server/app/modules/inventory/public.py#L112)

```python
existing_case_pick_policy(gateway: OracleGateway | TransactionGateway, task_id: int, line_id: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `case_pick_policy`

### build_case_carrier_move_service

[Исходник: api/wms_api_server/app/modules/inventory/public.py:116](../../../api/wms_api_server/app/modules/inventory/public.py#L116)

```python
build_case_carrier_move_service() -> CaseCarrierMove
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CaseCarrierMove`, `build_stock_posting_service`

### post_existing_case_short_approval

[Исходник: api/wms_api_server/app/modules/inventory/public.py:120](../../../api/wms_api_server/app/modules/inventory/public.py#L120)

```python
post_existing_case_short_approval(gateway: OracleGateway | TransactionGateway, short_id: int, request: CasePickShortDecisionRequest) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `post_short_approval`

### post_existing_terminal_quality

[Исходник: api/wms_api_server/app/modules/inventory/public.py:126](../../../api/wms_api_server/app/modules/inventory/public.py#L126)

```python
post_existing_terminal_quality(gateway: OracleGateway | TransactionGateway, pallet: str, request: LotCheckRequest) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `post_terminal_quality`

### bind_existing_case_shipment

[Исходник: api/wms_api_server/app/modules/inventory/public.py:130](../../../api/wms_api_server/app/modules/inventory/public.py#L130)

```python
bind_existing_case_shipment(gateway: OracleGateway | TransactionGateway, task_id: int, pallet_identifier: str, scan_container: str, expected_version: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `bind_case_shipment`

### return_existing_case_carrier

[Исходник: api/wms_api_server/app/modules/inventory/public.py:135](../../../api/wms_api_server/app/modules/inventory/public.py#L135)

```python
return_existing_case_carrier(task_id: int, request: CaseCarrierReturnRequest, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockCommand`, `StockPosting`, `StockPosting().post`, `ValueError`, `any`, `len`, `request.destinations.items`, `request.model_dump`

### build_source_availability_service

[Исходник: api/wms_api_server/app/modules/inventory/public.py:148](../../../api/wms_api_server/app/modules/inventory/public.py#L148)

```python
build_source_availability_service() -> SourceAvailability
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `SourceAvailability`

### get_existing_task_progress

[Исходник: api/wms_api_server/app/modules/inventory/public.py:155](../../../api/wms_api_server/app/modules/inventory/public.py#L155)

```python
get_existing_task_progress(gateway: _Any, task_id: int) -> dict[str, _Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `task_progress`

### build_recovery_tasks_service

[Исходник: api/wms_api_server/app/modules/inventory/public.py:161](../../../api/wms_api_server/app/modules/inventory/public.py#L161)

```python
build_recovery_tasks_service() -> RecoveryTasks
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `RecoveryTasks`

### build_task_scan_drafts

[Исходник: api/wms_api_server/app/modules/inventory/public.py:167](../../../api/wms_api_server/app/modules/inventory/public.py#L167)

```python
build_task_scan_drafts() -> TaskScanDrafts
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `TaskScanDrafts`

### build_replenishment_progress

[Исходник: api/wms_api_server/app/modules/inventory/public.py:174](../../../api/wms_api_server/app/modules/inventory/public.py#L174)

```python
build_replenishment_progress() -> ReplenishmentProgress
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `ReplenishmentProgress`

### build_pool_service

[Исходник: api/wms_api_server/app/modules/inventory/public.py:184](../../../api/wms_api_server/app/modules/inventory/public.py#L184)

```python
build_pool_service() -> PoolService
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `PoolService`

### build_short_investigation

[Исходник: api/wms_api_server/app/modules/inventory/public.py:193](../../../api/wms_api_server/app/modules/inventory/public.py#L193)

```python
build_short_investigation() -> ShortInvestigation
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `ShortInvestigation`

### build_partial_layout_service

[Исходник: api/wms_api_server/app/modules/inventory/public.py:201](../../../api/wms_api_server/app/modules/inventory/public.py#L201)

```python
build_partial_layout_service() -> PartialShipmentLayout
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `PartialShipmentLayout`

### build_wave_pick_service

[Исходник: api/wms_api_server/app/modules/inventory/public.py:207](../../../api/wms_api_server/app/modules/inventory/public.py#L207)

```python
build_wave_pick_service() -> WavePickRelease
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `WavePickRelease`

### route_existing_alternative_pick_faces

[Исходник: api/wms_api_server/app/modules/inventory/public.py:212](../../../api/wms_api_server/app/modules/inventory/public.py#L212)

```python
route_existing_alternative_pick_faces(gateway: OracleGateway | TransactionGateway, wave_id: int, actor: str) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `AlternativePickFaces`, `AlternativePickFaces(gateway).route_wave`

### build_fullpal_shipment_service

[Исходник: api/wms_api_server/app/modules/inventory/public.py:218](../../../api/wms_api_server/app/modules/inventory/public.py#L218)

```python
build_fullpal_shipment_service() -> FullPalletShipment
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `FullPalletShipment`, `OracleGateway`

### build_wave_execution_service

[Исходник: api/wms_api_server/app/modules/inventory/public.py:226](../../../api/wms_api_server/app/modules/inventory/public.py#L226)

```python
build_wave_execution_service() -> WaveExecution
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `WaveExecution`

### build_warehouse_hu_service

[Исходник: api/wms_api_server/app/modules/inventory/public.py:232](../../../api/wms_api_server/app/modules/inventory/public.py#L232)

```python
build_warehouse_hu_service() -> WarehouseHu
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `WarehouseHu`

### build_outgoing_quality_service

[Исходник: api/wms_api_server/app/modules/inventory/public.py:238](../../../api/wms_api_server/app/modules/inventory/public.py#L238)

```python
build_outgoing_quality_service() -> OutgoingQuality
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `OutgoingQuality`

### build_inventory_observations_service

[Исходник: api/wms_api_server/app/modules/inventory/public.py:245](../../../api/wms_api_server/app/modules/inventory/public.py#L245)

```python
build_inventory_observations_service() -> InventoryObservationsPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `InventoryObservations`, `OracleGateway`, `build_stock_posting_service`

### build_store_return_receiving

[Исходник: api/wms_api_server/app/modules/inventory/public.py:252](../../../api/wms_api_server/app/modules/inventory/public.py#L252)

```python
build_store_return_receiving(gateway: Any, post: Callable[[str, str, dict[str, Any], dict[str, Any], str], dict[str, Any]]) -> StoreReturnReceivePort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReturnReceiving`

### build_return_putaway

[Исходник: api/wms_api_server/app/modules/inventory/public.py:259](../../../api/wms_api_server/app/modules/inventory/public.py#L259)

```python
build_return_putaway(gateway: Any, post: Callable[[str, str, dict[str, Any], dict[str, Any], str], dict[str, Any]]) -> ReturnPutawayPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ReturnPutaway`

### build_tare

[Исходник: api/wms_api_server/app/modules/inventory/public.py:266](../../../api/wms_api_server/app/modules/inventory/public.py#L266)

```python
build_tare(gateway: Any, post: Callable[..., dict[str, Any]]) -> TarePort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Tare`

### build_tare_policy

[Исходник: api/wms_api_server/app/modules/inventory/public.py:273](../../../api/wms_api_server/app/modules/inventory/public.py#L273)

```python
build_tare_policy(gateway: Any) -> TarePolicyPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TarePolicy`

### build_tare_assembly

[Исходник: api/wms_api_server/app/modules/inventory/public.py:282](../../../api/wms_api_server/app/modules/inventory/public.py#L282)

```python
build_tare_assembly(gateway: Any) -> TareAssemblyPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TareAssembly`

### build_supplier_return

[Исходник: api/wms_api_server/app/modules/inventory/public.py:291](../../../api/wms_api_server/app/modules/inventory/public.py#L291)

```python
build_supplier_return(gateway: Any) -> SupplierReturnPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `SupplierReturn`

### build_supplier_handover

[Исходник: api/wms_api_server/app/modules/inventory/public.py:298](../../../api/wms_api_server/app/modules/inventory/public.py#L298)

```python
build_supplier_handover(gateway: Any) -> SupplierHandoverPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `SupplierHandover`

### build_return_disposal

[Исходник: api/wms_api_server/app/modules/inventory/public.py:305](../../../api/wms_api_server/app/modules/inventory/public.py#L305)

```python
build_return_disposal(gateway: Any) -> ReturnDisposalPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ReturnDisposal`, `StockPosting`

### build_interwarehouse

[Исходник: api/wms_api_server/app/modules/inventory/public.py:312](../../../api/wms_api_server/app/modules/inventory/public.py#L312)

```python
build_interwarehouse(gateway: Any) -> InterwarehousePort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Interwarehouse`, `StockPosting`

### build_trace_manifest

[Исходник: api/wms_api_server/app/modules/inventory/public.py:319](../../../api/wms_api_server/app/modules/inventory/public.py#L319)

```python
build_trace_manifest(gateway: Any) -> TraceManifestPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TraceSenderManifest`

### build_stock_compatibility

[Исходник: api/wms_api_server/app/modules/inventory/public.py:325](../../../api/wms_api_server/app/modules/inventory/public.py#L325)

```python
build_stock_compatibility(gateway: Any) -> StockCompatibilityPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockCompatibility`

### build_slotting_demand

[Исходник: api/wms_api_server/app/modules/inventory/public.py:334](../../../api/wms_api_server/app/modules/inventory/public.py#L334)

```python
build_slotting_demand(gateway: Any) -> SlottingDemandPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `SlottingDemand`

### build_case_task_services

[Исходник: api/wms_api_server/app/modules/inventory/public.py:344](../../../api/wms_api_server/app/modules/inventory/public.py#L344)

```python
build_case_task_services() -> CaseTaskServices
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CaseTaskServices`, `OracleGateway`

### build_range_proposal

[Исходник: api/wms_api_server/app/modules/inventory/public.py:351](../../../api/wms_api_server/app/modules/inventory/public.py#L351)

```python
build_range_proposal(gateway: Any) -> RangeProposalPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RangeProposal`

### create_existing_pick_plan

[Исходник: api/wms_api_server/app/modules/inventory/public.py:357](../../../api/wms_api_server/app/modules/inventory/public.py#L357)

```python
create_existing_pick_plan(gateway: OracleGateway, request: PickingPlanCreateRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `create_existing_plan`

### build_weighted_case

[Исходник: api/wms_api_server/app/modules/inventory/public.py:367](../../../api/wms_api_server/app/modules/inventory/public.py#L367)

```python
build_weighted_case() -> WeightedCasePort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `WeightedCasePick`

### build_warehouse_scales

[Исходник: api/wms_api_server/app/modules/inventory/public.py:374](../../../api/wms_api_server/app/modules/inventory/public.py#L374)

```python
build_warehouse_scales() -> WarehouseScalePort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `WarehouseScales`

### build_weighted_plan

[Исходник: api/wms_api_server/app/modules/inventory/public.py:381](../../../api/wms_api_server/app/modules/inventory/public.py#L381)

```python
build_weighted_plan() -> WeightedPlanPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `WeightedPlanning`

### upsert_existing_pallet_type

[Исходник: api/wms_api_server/app/modules/inventory/public.py:386](../../../api/wms_api_server/app/modules/inventory/public.py#L386)

```python
upsert_existing_pallet_type(gateway: OracleGateway, request: PalletTypeUpsertRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `upsert_pallet_type`

### case_label_service

[Исходник: api/wms_api_server/app/modules/inventory/public.py:394](../../../api/wms_api_server/app/modules/inventory/public.py#L394)

```python
case_label_service() -> CaseLabelPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CaseLabels`, `OracleGateway`

### normalize_unit_scan_codes

[Исходник: api/wms_api_server/app/modules/inventory/public.py:396](../../../api/wms_api_server/app/modules/inventory/public.py#L396)

```python
normalize_unit_scan_codes(scans: list[dict[str, str]]) -> list[dict[str, str]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `normalize`

### waiting_task_service

[Исходник: api/wms_api_server/app/modules/inventory/public.py:422](../../../api/wms_api_server/app/modules/inventory/public.py#L422)

```python
waiting_task_service() -> WaitingTaskPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `StDeferWaiting`

### build_wave_queue_reads

[Исходник: api/wms_api_server/app/modules/inventory/public.py:429](../../../api/wms_api_server/app/modules/inventory/public.py#L429)

```python
build_wave_queue_reads() -> WaveQueueReads
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `WaveQueueReads`

### build_task_queue_read

[Исходник: api/wms_api_server/app/modules/inventory/public.py:438](../../../api/wms_api_server/app/modules/inventory/public.py#L438)

```python
build_task_queue_read(gateway: Any) -> TaskQueueRead
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TaskQueueRead`

### build_pallet_floor_type

[Исходник: api/wms_api_server/app/modules/inventory/public.py:448](../../../api/wms_api_server/app/modules/inventory/public.py#L448)

```python
build_pallet_floor_type(gateway: Any, posting: Any) -> PalletFloorPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `PalletFloorType`

### build_case_type

[Исходник: api/wms_api_server/app/modules/inventory/public.py:455](../../../api/wms_api_server/app/modules/inventory/public.py#L455)

```python
build_case_type(gateway: Any, posting: Any) -> CaseTypePort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CaseType`

### build_quality_scope

[Исходник: api/wms_api_server/app/modules/inventory/public.py:468](../../../api/wms_api_server/app/modules/inventory/public.py#L468)

```python
build_quality_scope(gateway: Any) -> QualityScopePort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `QualityScope`
