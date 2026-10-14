# Методы: delivery

### send

[Исходник: api/wms_api_server/app/modules/delivery/api/case_work_routes.py:34](../../../api/wms_api_server/app/modules/delivery/api/case_work_routes.py#L34)

```python
send(service: CaseWorkPort, case_id: str, body: CaseCommand, action: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `body.model_dump`, `failure`, `len`, `service.command`

### assign

[Исходник: api/wms_api_server/app/modules/delivery/api/case_work_routes.py:45](../../../api/wms_api_server/app/modules/delivery/api/case_work_routes.py#L45)

```python
assign(case_id: str, body: Assignment, user: AdminUser=Depends(require_permission('store_case_manage')), service: CaseWorkPort=Depends(case_work_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `require_permission`, `router.post`, `send`

### finding

[Исходник: api/wms_api_server/app/modules/delivery/api/case_work_routes.py:51](../../../api/wms_api_server/app/modules/delivery/api/case_work_routes.py#L51)

```python
finding(case_id: str, body: Finding, user: AdminUser=Depends(require_permission('store_case_investigate')), service: CaseWorkPort=Depends(case_work_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `require_permission`, `router.post`, `send`

### loss

[Исходник: api/wms_api_server/app/modules/delivery/api/case_work_routes.py:57](../../../api/wms_api_server/app/modules/delivery/api/case_work_routes.py#L57)

```python
loss(case_id: str, body: Loss, user: AdminUser=Depends(require_permission('store_loss_confirm')), service: CaseWorkPort=Depends(case_work_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `require_permission`, `router.post`, `send`

### mine

[Исходник: api/wms_api_server/app/modules/delivery/api/case_work_routes.py:63](../../../api/wms_api_server/app/modules/delivery/api/case_work_routes.py#L63)

```python
mine(user: AdminUser=Depends(require_permission('store_case_investigate')), service: CaseWorkPort=Depends(case_work_service)) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `require_permission`, `router.get`, `service.assigned`

### investigation

[Исходник: api/wms_api_server/app/modules/delivery/api/case_work_routes.py:69](../../../api/wms_api_server/app/modules/delivery/api/case_work_routes.py#L69)

```python
investigation(case_id: str, user: AdminUser=Depends(require_permission('store_case_investigate')), service: CaseWorkPort=Depends(case_work_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `failure`, `require_permission`, `router.get`, `service.investigation`

### review

[Исходник: api/wms_api_server/app/modules/delivery/api/case_work_routes.py:78](../../../api/wms_api_server/app/modules/delivery/api/case_work_routes.py#L78)

```python
review(case_id: str, user: AdminUser=Depends(require_permission('store_loss_confirm')), service: CaseWorkPort=Depends(case_work_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `failure`, `require_permission`, `router.get`, `service.review`

### management

[Исходник: api/wms_api_server/app/modules/delivery/api/case_work_routes.py:87](../../../api/wms_api_server/app/modules/delivery/api/case_work_routes.py#L87)

```python
management(case_id: str, user: AdminUser=Depends(require_permission('store_case_manage')), service: CaseWorkPort=Depends(case_work_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `failure`, `require_permission`, `router.get`, `service.review`

### close

[Исходник: api/wms_api_server/app/modules/delivery/api/case_work_routes.py:99](../../../api/wms_api_server/app/modules/delivery/api/case_work_routes.py#L99)

```python
close(case_id: str, body: Closure, user: AdminUser=Depends(require_permission('store_loss_confirm')), service: CaseWorkPort=Depends(case_work_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `require_permission`, `router.post`, `send`

### delivery

[Исходник: api/wms_api_server/app/modules/delivery/api/order_delivery_routes.py:10](../../../api/wms_api_server/app/modules/delivery/api/order_delivery_routes.py#L10)

```python
delivery(order_id: int, user: AdminUser=Depends(require_permission('customer_fulfillment_view')), service: OrderDeliveryPort=Depends(order_delivery_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.get`, `service.get`, `str`

### handover

[Исходник: api/wms_api_server/app/modules/delivery/api/return_custody_routes.py:36](../../../api/wms_api_server/app/modules/delivery/api/return_custody_routes.py#L36)

```python
handover(body: Handover, user: AdminUser=Depends(require_permission('store_return_handover')), service: ReturnCustodyPort=Depends(return_custody_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `body.model_dump`, `failure`, `require_permission`, `router.post`, `service.handover`

### pickup

[Исходник: api/wms_api_server/app/modules/delivery/api/return_custody_routes.py:45](../../../api/wms_api_server/app/modules/delivery/api/return_custody_routes.py#L45)

```python
pickup(body: Pickup, user: AdminUser=Depends(require_permission('driver_return_accept')), service: ReturnCustodyPort=Depends(return_custody_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `body.model_dump`, `failure`, `require_permission`, `router.post`, `service.pickup`

### store

[Исходник: api/wms_api_server/app/modules/delivery/api/return_custody_routes.py:54](../../../api/wms_api_server/app/modules/delivery/api/return_custody_routes.py#L54)

```python
store(store_address: str=Query(min_length=1, max_length=255), task_id: int | None=Query(default=None, ge=1), user: AdminUser=Depends(require_permission('store_return_handover')), service: ReturnCustodyPort=Depends(return_custody_service)) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Query`, `failure`, `require_permission`, `router.get`, `service.store_pending`

### driver

[Исходник: api/wms_api_server/app/modules/delivery/api/return_custody_routes.py:63](../../../api/wms_api_server/app/modules/delivery/api/return_custody_routes.py#L63)

```python
driver(task_id: int | None=Query(default=None, ge=1), user: AdminUser=Depends(require_permission('driver_return_accept')), service: ReturnCustodyPort=Depends(return_custody_service)) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Query`, `require_permission`, `router.get`, `service.driver_pending`

### plan

[Исходник: api/wms_api_server/app/modules/delivery/api/return_transport_routes.py:22](../../../api/wms_api_server/app/modules/delivery/api/return_transport_routes.py#L22)

```python
plan(body: ReturnPlan, user: AdminUser=Depends(require_permission('store_return_transport')), service: ReturnTransportPort=Depends(return_transport_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `body.model_dump`, `failure`, `require_permission`, `router.post`, `service.plan`

### eligible

[Исходник: api/wms_api_server/app/modules/delivery/api/return_transport_routes.py:31](../../../api/wms_api_server/app/modules/delivery/api/return_transport_routes.py#L31)

```python
eligible(user: AdminUser=Depends(require_permission('store_return_transport')), service: ReturnTransportPort=Depends(return_transport_service)) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `require_permission`, `router.get`, `service.eligible`

### trip

[Исходник: api/wms_api_server/app/modules/delivery/api/return_transport_routes.py:37](../../../api/wms_api_server/app/modules/delivery/api/return_transport_routes.py#L37)

```python
trip(task_id: int, user: AdminUser=Depends(require_permission('store_return_transport')), service: ReturnTransportPort=Depends(return_transport_service)) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `failure`, `require_permission`, `router.get`, `service.trip`

### failure

[Исходник: api/wms_api_server/app/modules/delivery/api/store_evidence_routes.py:13](../../../api/wms_api_server/app/modules/delivery/api/store_evidence_routes.py#L13)

```python
failure(error: StoreReceiptError) -> HTTPException
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `str`

### upload

[Исходник: api/wms_api_server/app/modules/delivery/api/store_evidence_routes.py:18](../../../api/wms_api_server/app/modules/delivery/api/store_evidence_routes.py#L18)

```python
upload(load_operation_id: str, store_address: str, view: Literal['FRONT', 'LEFT', 'RIGHT', 'BACK', 'TOP'], request: Request, user: AdminUser=Depends(require_permission('store_receipt_confirm')), service: StoreEvidencePort=Depends(store_evidence_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `bytearray`, `bytes`, `failure`, `len`, `payload.extend`, `request.headers.get`, `request.headers.get('content-type', '').split`, `request.headers.get('content-type', '').split(';', 1)[0].lower`, `request.stream`, `require_permission`, `router.post`, `run_in_threadpool`

### photos

[Исходник: api/wms_api_server/app/modules/delivery/api/store_evidence_routes.py:38](../../../api/wms_api_server/app/modules/delivery/api/store_evidence_routes.py#L38)

```python
photos(load_operation_id: str, store_address: str, user: AdminUser=Depends(require_permission('store_receipt_confirm')), service: StoreEvidencePort=Depends(store_evidence_service)) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `failure`, `len`, `require_permission`, `router.get`, `service.photos`

### content

[Исходник: api/wms_api_server/app/modules/delivery/api/store_evidence_routes.py:50](../../../api/wms_api_server/app/modules/delivery/api/store_evidence_routes.py#L50)

```python
content(photo_id: str, user: AdminUser=Depends(require_permission('store_receipt_confirm')), service: StoreEvidencePort=Depends(store_evidence_service)) -> Response
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Response`, `any`, `failure`, `len`, `require_permission`, `router.get`, `service.content`

### failure

[Исходник: api/wms_api_server/app/modules/delivery/api/store_receipt_routes.py:83](../../../api/wms_api_server/app/modules/delivery/api/store_receipt_routes.py#L83)

```python
failure(error: StoreReceiptError) -> HTTPException
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `bool`, `str`

### preview

[Исходник: api/wms_api_server/app/modules/delivery/api/store_receipt_routes.py:90](../../../api/wms_api_server/app/modules/delivery/api/store_receipt_routes.py#L90)

```python
preview(load_operation_id: str, store_address: str, user: AdminUser=Depends(require_permission('store_receipt_confirm')), service: StoreReceiptPort=Depends(store_receipt_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `failure`, `len`, `require_permission`, `router.get`, `service.preview`

### places

[Исходник: api/wms_api_server/app/modules/delivery/api/store_receipt_routes.py:102](../../../api/wms_api_server/app/modules/delivery/api/store_receipt_routes.py#L102)

```python
places(trip_id: int, store_address: str, after: str=Query('', max_length=100), limit: int=Query(200, ge=1, le=200), user: AdminUser=Depends(require_permission('store_receipt_confirm')), service: StoreReceiptPort=Depends(store_receipt_service)) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Query`, `failure`, `len`, `require_permission`, `router.get`, `service.places`

### confirm

[Исходник: api/wms_api_server/app/modules/delivery/api/store_receipt_routes.py:114](../../../api/wms_api_server/app/modules/delivery/api/store_receipt_routes.py#L114)

```python
confirm(body: StoreReceiptRequest, user: AdminUser=Depends(require_permission('store_receipt_confirm')), service: StoreReceiptPort=Depends(store_receipt_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `body.case_note.encode`, `body.model_dump`, `failure`, `len`, `require_permission`, `router.post`, `row.model_dump`, `scan.model_dump`, `service.confirm`

### configure

[Исходник: api/wms_api_server/app/modules/delivery/api/store_receipt_routes.py:139](../../../api/wms_api_server/app/modules/delivery/api/store_receipt_routes.py#L139)

```python
configure(body: PolicyRequest, user: AdminUser=Depends(require_permission('warehouse_settings_edit')), service: StoreReceiptPort=Depends(store_receipt_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `failure`, `require_permission`, `router.put`, `service.configure`

### assign_receiver

[Исходник: api/wms_api_server/app/modules/delivery/api/store_receipt_routes.py:149](../../../api/wms_api_server/app/modules/delivery/api/store_receipt_routes.py#L149)

```python
assign_receiver(body: ReceiverRequest, user: AdminUser=Depends(require_permission('warehouse_settings_edit')), service: StoreReceiptPort=Depends(store_receipt_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `failure`, `require_permission`, `router.post`, `service.assign_receiver`

### cases

[Исходник: api/wms_api_server/app/modules/delivery/api/store_receipt_routes.py:159](../../../api/wms_api_server/app/modules/delivery/api/store_receipt_routes.py#L159)

```python
cases(store_address: str, after: str='', limit: int=50, user: AdminUser=Depends(require_permission('transport_dispatch_view')), service: StoreReceiptPort=Depends(store_receipt_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `failure`, `len`, `require_permission`, `router.get`, `service.cases`

### case_detail

[Исходник: api/wms_api_server/app/modules/delivery/api/store_receipt_routes.py:171](../../../api/wms_api_server/app/modules/delivery/api/store_receipt_routes.py#L171)

```python
case_detail(case_id: str, user: AdminUser=Depends(require_permission('transport_dispatch_view')), service: StoreReceiptPort=Depends(store_receipt_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `failure`, `len`, `require_permission`, `router.get`, `service.case_detail`

### release_custody

[Исходник: api/wms_api_server/app/modules/delivery/api/store_receipt_routes.py:187](../../../api/wms_api_server/app/modules/delivery/api/store_receipt_routes.py#L187)

```python
release_custody(body: StoreCustodyRelease, user: AdminUser=Depends(require_permission('transport_dispatch_close')), service: StoreReceiptPort=Depends(store_receipt_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `failure`, `require_permission`, `router.post`, `service.release_custody`

### start_unloading

[Исходник: api/wms_api_server/app/modules/delivery/api/store_receipt_routes.py:194](../../../api/wms_api_server/app/modules/delivery/api/store_receipt_routes.py#L194)

```python
start_unloading(body: UnloadingStart, user: AdminUser=Depends(require_permission('store_receipt_confirm')), service: StoreReceiptPort=Depends(store_receipt_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `body.model_dump`, `failure`, `require_permission`, `router.post`, `service.start_unloading`

### unloading

[Исходник: api/wms_api_server/app/modules/delivery/api/store_receipt_routes.py:201](../../../api/wms_api_server/app/modules/delivery/api/store_receipt_routes.py#L201)

```python
unloading(load_operation_id: Annotated[str, Query(min_length=1, max_length=100)], store_address: Annotated[str, Query(min_length=1, max_length=255)], user: AdminUser=Depends(require_permission('store_receipt_confirm')), service: StoreReceiptPort=Depends(store_receipt_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Query`, `failure`, `require_permission`, `router.get`, `service.unloading`

### approve

[Исходник: api/wms_api_server/app/modules/delivery/api/store_return_routes.py:26](../../../api/wms_api_server/app/modules/delivery/api/store_return_routes.py#L26)

```python
approve(receipt_id: str, body: ReturnApproval, user: AdminUser=Depends(require_permission('store_return_approve')), service: StoreReturnsPort=Depends(store_returns_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `body.model_dump`, `failure`, `len`, `require_permission`, `router.post`, `service.approve`

### original

[Исходник: api/wms_api_server/app/modules/delivery/api/store_return_routes.py:37](../../../api/wms_api_server/app/modules/delivery/api/store_return_routes.py#L37)

```python
original(receipt_id: str, user: AdminUser=Depends(require_permission('store_return_approve')), service: StoreReturnsPort=Depends(store_returns_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `failure`, `require_permission`, `router.get`, `service.original`

### reuse_preview

[Исходник: api/wms_api_server/app/modules/delivery/api/store_return_routes.py:46](../../../api/wms_api_server/app/modules/delivery/api/store_return_routes.py#L46)

```python
reuse_preview(receipt_id: str, line_no: int=Query(ge=1, le=200), quantity: str=Query(pattern='^[0-9]{1,18}(\\.[0-9]{1,9})?$'), user: AdminUser=Depends(require_permission('store_return_approve')), service: StoreReturnsPort=Depends(store_returns_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Query`, `failure`, `len`, `require_permission`, `router.get`, `service.reuse_preview`

### configure

[Исходник: api/wms_api_server/app/modules/delivery/api/store_scale_routes.py:52](../../../api/wms_api_server/app/modules/delivery/api/store_scale_routes.py#L52)

```python
configure(device_id: str, body: ScaleConfiguration, user: AdminUser=Depends(require_permission('warehouse_settings_edit')), service: StoreScalesPort=Depends(store_scales_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `body.model_dump`, `failure`, `len`, `require_permission`, `router.put`, `service.configure`

### capture

[Исходник: api/wms_api_server/app/modules/delivery/api/store_scale_routes.py:64](../../../api/wms_api_server/app/modules/delivery/api/store_scale_routes.py#L64)

```python
capture(body: ScalePacket, user: AdminUser=Depends(require_permission('store_scale_ingest')), service: StoreScalesPort=Depends(store_scales_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `body.model_dump`, `error.detail.update`, `failure`, `require_permission`, `router.post`, `service.capture`

### reading

[Исходник: api/wms_api_server/app/modules/delivery/api/store_scale_routes.py:76](../../../api/wms_api_server/app/modules/delivery/api/store_scale_routes.py#L76)

```python
reading(capture_key: str, user: AdminUser=Depends(require_permission('store_receipt_confirm')), service: StoreScalesPort=Depends(store_scales_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `any`, `failure`, `len`, `require_permission`, `router.get`, `service.reading`

### readings

[Исходник: api/wms_api_server/app/modules/delivery/api/store_scale_routes.py:88](../../../api/wms_api_server/app/modules/delivery/api/store_scale_routes.py#L88)

```python
readings(load_operation_id: str, store_address: str, user: AdminUser=Depends(require_permission('store_receipt_confirm')), service: StoreScalesPort=Depends(store_scales_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `failure`, `len`, `require_permission`, `router.get`, `service.readings`

### store_receipt_service

[Исходник: api/wms_api_server/app/modules/delivery/contracts.py:26](../../../api/wms_api_server/app/modules/delivery/contracts.py#L26)

```python
store_receipt_service() -> StoreReceiptPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### __init__

[Исходник: api/wms_api_server/app/modules/delivery/contracts.py:6](../../../api/wms_api_server/app/modules/delivery/contracts.py#L6)

```python
__init__(self, code: str, message: str, status: int=409, operation_id: str='') -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `super`, `super().__init__`

### start_unloading

[Исходник: api/wms_api_server/app/modules/delivery/contracts.py:14](../../../api/wms_api_server/app/modules/delivery/contracts.py#L14)

```python
start_unloading(self, body: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### unloading

[Исходник: api/wms_api_server/app/modules/delivery/contracts.py:15](../../../api/wms_api_server/app/modules/delivery/contracts.py#L15)

```python
unloading(self, load: str, address: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### release_custody

[Исходник: api/wms_api_server/app/modules/delivery/contracts.py:16](../../../api/wms_api_server/app/modules/delivery/contracts.py#L16)

```python
release_custody(self, operation_id: str, receipt_id: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### cases

[Исходник: api/wms_api_server/app/modules/delivery/contracts.py:17](../../../api/wms_api_server/app/modules/delivery/contracts.py#L17)

```python
cases(self, address: str, after: str, limit: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### case_detail

[Исходник: api/wms_api_server/app/modules/delivery/contracts.py:18](../../../api/wms_api_server/app/modules/delivery/contracts.py#L18)

```python
case_detail(self, case_id: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### preview

[Исходник: api/wms_api_server/app/modules/delivery/contracts.py:19](../../../api/wms_api_server/app/modules/delivery/contracts.py#L19)

```python
preview(self, load_operation_id: str, store_address: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### places

[Исходник: api/wms_api_server/app/modules/delivery/contracts.py:20](../../../api/wms_api_server/app/modules/delivery/contracts.py#L20)

```python
places(self, trip_id: int, store_address: str, actor: str, after: str='', limit: int=200) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### confirm

[Исходник: api/wms_api_server/app/modules/delivery/contracts.py:21](../../../api/wms_api_server/app/modules/delivery/contracts.py#L21)

```python
confirm(self, operation_id: str, load_operation_id: str, store_address: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### configure

[Исходник: api/wms_api_server/app/modules/delivery/contracts.py:22](../../../api/wms_api_server/app/modules/delivery/contracts.py#L22)

```python
configure(self, store_address: str, mode: str, expected_version: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### assign_receiver

[Исходник: api/wms_api_server/app/modules/delivery/contracts.py:23](../../../api/wms_api_server/app/modules/delivery/contracts.py#L23)

```python
assign_receiver(self, store_address: str, username: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### case_work_service

[Исходник: api/wms_api_server/app/modules/delivery/contracts_case_work.py:11](../../../api/wms_api_server/app/modules/delivery/contracts_case_work.py#L11)

```python
case_work_service() -> CaseWorkPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### command

[Исходник: api/wms_api_server/app/modules/delivery/contracts_case_work.py:5](../../../api/wms_api_server/app/modules/delivery/contracts_case_work.py#L5)

```python
command(self, operation_id: str, case_id: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### assigned

[Исходник: api/wms_api_server/app/modules/delivery/contracts_case_work.py:6](../../../api/wms_api_server/app/modules/delivery/contracts_case_work.py#L6)

```python
assigned(self, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### investigation

[Исходник: api/wms_api_server/app/modules/delivery/contracts_case_work.py:7](../../../api/wms_api_server/app/modules/delivery/contracts_case_work.py#L7)

```python
investigation(self, case_id: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### review

[Исходник: api/wms_api_server/app/modules/delivery/contracts_case_work.py:8](../../../api/wms_api_server/app/modules/delivery/contracts_case_work.py#L8)

```python
review(self, case_id: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### store_evidence_service

[Исходник: api/wms_api_server/app/modules/delivery/contracts_evidence.py:19](../../../api/wms_api_server/app/modules/delivery/contracts_evidence.py#L19)

```python
store_evidence_service() -> StoreEvidencePort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### upload

[Исходник: api/wms_api_server/app/modules/delivery/contracts_evidence.py:14](../../../api/wms_api_server/app/modules/delivery/contracts_evidence.py#L14)

```python
upload(self, load_operation_id: str, store_address: str, view: str, mime_type: str, contents: bytes, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### photos

[Исходник: api/wms_api_server/app/modules/delivery/contracts_evidence.py:15](../../../api/wms_api_server/app/modules/delivery/contracts_evidence.py#L15)

```python
photos(self, load_operation_id: str, store_address: str, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### content

[Исходник: api/wms_api_server/app/modules/delivery/contracts_evidence.py:16](../../../api/wms_api_server/app/modules/delivery/contracts_evidence.py#L16)

```python
content(self, photo_id: str, actor: str) -> ArchivedPhoto
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### order_delivery_service

[Исходник: api/wms_api_server/app/modules/delivery/contracts_orders.py:8](../../../api/wms_api_server/app/modules/delivery/contracts_orders.py#L8)

```python
order_delivery_service() -> OrderDeliveryPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### get

[Исходник: api/wms_api_server/app/modules/delivery/contracts_orders.py:5](../../../api/wms_api_server/app/modules/delivery/contracts_orders.py#L5)

```python
get(self, order_id: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### return_custody_service

[Исходник: api/wms_api_server/app/modules/delivery/contracts_return_custody.py:11](../../../api/wms_api_server/app/modules/delivery/contracts_return_custody.py#L11)

```python
return_custody_service() -> ReturnCustodyPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### handover

[Исходник: api/wms_api_server/app/modules/delivery/contracts_return_custody.py:5](../../../api/wms_api_server/app/modules/delivery/contracts_return_custody.py#L5)

```python
handover(self, operation_id: str, transport_id: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### pickup

[Исходник: api/wms_api_server/app/modules/delivery/contracts_return_custody.py:6](../../../api/wms_api_server/app/modules/delivery/contracts_return_custody.py#L6)

```python
pickup(self, operation_id: str, handover_id: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### store_pending

[Исходник: api/wms_api_server/app/modules/delivery/contracts_return_custody.py:7](../../../api/wms_api_server/app/modules/delivery/contracts_return_custody.py#L7)

```python
store_pending(self, store_address: str, actor: str, task_id: int | None=None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### driver_pending

[Исходник: api/wms_api_server/app/modules/delivery/contracts_return_custody.py:8](../../../api/wms_api_server/app/modules/delivery/contracts_return_custody.py#L8)

```python
driver_pending(self, actor: str, task_id: int | None=None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### return_transport_service

[Исходник: api/wms_api_server/app/modules/delivery/contracts_return_transport.py:10](../../../api/wms_api_server/app/modules/delivery/contracts_return_transport.py#L10)

```python
return_transport_service() -> ReturnTransportPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### plan

[Исходник: api/wms_api_server/app/modules/delivery/contracts_return_transport.py:5](../../../api/wms_api_server/app/modules/delivery/contracts_return_transport.py#L5)

```python
plan(self, operation_id: str, approval_id: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### eligible

[Исходник: api/wms_api_server/app/modules/delivery/contracts_return_transport.py:6](../../../api/wms_api_server/app/modules/delivery/contracts_return_transport.py#L6)

```python
eligible(self) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### trip

[Исходник: api/wms_api_server/app/modules/delivery/contracts_return_transport.py:7](../../../api/wms_api_server/app/modules/delivery/contracts_return_transport.py#L7)

```python
trip(self, task_id: int) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### store_returns_service

[Исходник: api/wms_api_server/app/modules/delivery/contracts_returns.py:10](../../../api/wms_api_server/app/modules/delivery/contracts_returns.py#L10)

```python
store_returns_service() -> StoreReturnsPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### reuse_preview

[Исходник: api/wms_api_server/app/modules/delivery/contracts_returns.py:5](../../../api/wms_api_server/app/modules/delivery/contracts_returns.py#L5)

```python
reuse_preview(self, receipt_id: str, line_no: int, quantity: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### approve

[Исходник: api/wms_api_server/app/modules/delivery/contracts_returns.py:6](../../../api/wms_api_server/app/modules/delivery/contracts_returns.py#L6)

```python
approve(self, operation_id: str, receipt_id: str, line_no: int, metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### original

[Исходник: api/wms_api_server/app/modules/delivery/contracts_returns.py:7](../../../api/wms_api_server/app/modules/delivery/contracts_returns.py#L7)

```python
original(self, receipt_id: str, actor: str | None=None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### store_scales_service

[Исходник: api/wms_api_server/app/modules/delivery/contracts_scales.py:12](../../../api/wms_api_server/app/modules/delivery/contracts_scales.py#L12)

```python
store_scales_service() -> StoreScalesPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### readings

[Исходник: api/wms_api_server/app/modules/delivery/contracts_scales.py:6](../../../api/wms_api_server/app/modules/delivery/contracts_scales.py#L6)

```python
readings(self, load_operation_id: str, store_address: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### configure

[Исходник: api/wms_api_server/app/modules/delivery/contracts_scales.py:7](../../../api/wms_api_server/app/modules/delivery/contracts_scales.py#L7)

```python
configure(self, device_id: str, body: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### capture

[Исходник: api/wms_api_server/app/modules/delivery/contracts_scales.py:8](../../../api/wms_api_server/app/modules/delivery/contracts_scales.py#L8)

```python
capture(self, body: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### reading

[Исходник: api/wms_api_server/app/modules/delivery/contracts_scales.py:9](../../../api/wms_api_server/app/modules/delivery/contracts_scales.py#L9)

```python
reading(self, key: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### text

[Исходник: api/wms_api_server/app/modules/delivery/domain/order_delivery.py:8](../../../api/wms_api_server/app/modules/delivery/domain/order_delivery.py#L8)

```python
text(value: Decimal) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `format`, `format(value, 'f').rstrip`, `format(value, 'f').rstrip('0').rstrip`

### project_delivery

[Исходник: api/wms_api_server/app/modules/delivery/domain/order_delivery.py:12](../../../api/wms_api_server/app/modules/delivery/domain/order_delivery.py#L12)

```python
project_delivery(order_id: int, legs: list[dict[str, Any]], fulfillments: list[dict[str, Any]], receipts: list[dict[str, Any]]) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `ValueError`, `any`, `by_load_uid.get`, `by_load_uid[row['load_operation_id'], row.get('original_lot_uid', row['lot_uid'])].append`, `combine_receipts`, `contexts.get`, `counter.items`, `defaultdict`, `grouped.items`, `grouped[leg['shipping_operation'], leg['lot_uid']].append`, `iter`, `len`, `next`, `open_cases.update`, `places.add`, `row.get`, `set`, `sorted`, `sum`, `text`, `totals.items`, `totals.setdefault`, `totals.values`, `unresolved.append`

### combine_receipts

[Исходник: api/wms_api_server/app/modules/delivery/domain/receipt_totals.py:6](../../../api/wms_api_server/app/modules/delivery/domain/receipt_totals.py#L6)

```python
combine_receipts(receipts: list[dict[str, Any]], total: Decimal) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `ValueError`, `any`, `iter`, `len`, `next`, `r.get`, `result.update`, `result.values`, `sum`

### __init__

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/case_work.py:8](../../../api/wms_api_server/app/modules/delivery/infrastructure/case_work.py#L8)

```python
__init__(self, gateway: Any, post: Callable[[str, str, dict[str, Any], dict[str, Any], str], dict[str, Any]]) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### command

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/case_work.py:12](../../../api/wms_api_server/app/modules/delivery/infrastructure/case_work.py#L12)

```python
command(self, operation_id: str, case_id: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.post`

### assigned

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/case_work.py:15](../../../api/wms_api_server/app/modules/delivery/infrastructure/case_work.py#L15)

```python
assigned(self, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReceiptError`, `len`, `self.gateway.fetch_all`

### investigation

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/case_work.py:25](../../../api/wms_api_server/app/modules/delivery/infrastructure/case_work.py#L25)

```python
investigation(self, case_id: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreCases`, `StoreCases(self.gateway).detail`, `StoreReceiptError`, `self.gateway.fetch_all`

### review

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/case_work.py:32](../../../api/wms_api_server/app/modules/delivery/infrastructure/case_work.py#L32)

```python
review(self, case_id: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreCases`, `StoreCases(self.gateway).detail`, `StoreReceiptError`, `self.gateway.fetch_all`

### rows

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/order_delivery.py:9](../../../api/wms_api_server/app/modules/delivery/infrastructure/order_delivery.py#L9)

```python
rows(cursor: Any) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `column[0].lower`, `cursor.fetchall`, `dict`, `zip`

### __init__

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/order_delivery.py:15](../../../api/wms_api_server/app/modules/delivery/infrastructure/order_delivery.py#L15)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### get

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/order_delivery.py:18](../../../api/wms_api_server/app/modules/delivery/infrastructure/order_delivery.py#L18)

```python
get(self, order_id: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LookupError`, `ValueError`, `assert_customer_order_warehouse`, `bool`, `len`, `project_delivery`, `q.execute`, `q.fetchone`, `result.update`, `row.get`, `rows`, `self._legs`, `self._receipts`, `self.gateway.transaction`, `sorted`

### _legs

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/order_delivery.py:47](../../../api/wms_api_server/app/modules/delivery/infrastructure/order_delivery.py#L47)

```python
_legs(self, q: Any, operations: list[str]) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' union all '.join`, `ValueError`, `json.dumps`, `len`, `q.execute`, `rows`, `selects.append`, `set`

### _receipts

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/order_delivery.py:68](../../../api/wms_api_server/app/modules/delivery/infrastructure/order_delivery.py#L68)

```python
_receipts(self, q: Any, loads: list[str]) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Path`, `Path(__file__).with_name`, `Path(__file__).with_name('order_delivery_receipts.sql').read_text`, `ValueError`, `json.dumps`, `len`, `q.execute`, `rows`

### verify_photo

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/photo_validation.py:10](../../../api/wms_api_server/app/modules/delivery/infrastructure/photo_validation.py#L10)

```python
verify_photo(contents: bytes, mime_type: str) -> tuple[int, int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `BytesIO`, `Image.open`, `StoreReceiptError`, `getattr`, `image.load`, `image.verify`, `len`, `min`, `{'JPEG': 'image/jpeg', 'PNG': 'image/png'}.get`

### __init__

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/return_custody.py:10](../../../api/wms_api_server/app/modules/delivery/infrastructure/return_custody.py#L10)

```python
__init__(self, gateway: Any, post: Callable[[str, str, dict[str, Any], dict[str, Any], str], dict[str, Any]]) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### handover

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/return_custody.py:14](../../../api/wms_api_server/app/modules/delivery/infrastructure/return_custody.py#L14)

```python
handover(self, operation_id: str, transport_id: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReceiptError`, `normalize_interwarehouse_scans`, `self.post`, `str`

### pickup

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/return_custody.py:19](../../../api/wms_api_server/app/modules/delivery/infrastructure/return_custody.py#L19)

```python
pickup(self, operation_id: str, handover_id: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReceiptError`, `normalize_interwarehouse_scans`, `self.post`, `str`

### store_pending

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/return_custody.py:24](../../../api/wms_api_server/app/modules/delivery/infrastructure/return_custody.py#L24)

```python
store_pending(self, store_address: str, actor: str, task_id: int | None=None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReceiptError`, `cursor.execute`, `getattr`, `read_oracle_json`, `row.get`, `self.gateway.fetch_all`, `self.gateway.transaction`

### driver_pending

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/return_custody.py:44](../../../api/wms_api_server/app/modules/delivery/infrastructure/return_custody.py#L44)

```python
driver_pending(self, actor: str, task_id: int | None=None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `read_oracle_json`, `row.get`, `self.gateway.fetch_all`

### return_progress

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/return_progress.py:8](../../../api/wms_api_server/app/modules/delivery/infrastructure/return_progress.py#L8)

```python
return_progress(cursor: Any, approval_ids: list[str], actor: str | None) -> dict[str, dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Path`, `Path(__file__).with_suffix`, `Path(__file__).with_suffix('.sql').read_text`, `StoreReceiptError`, `ValueError`, `cursor.execute`, `cursor.fetchmany`, `d[0].lower`, `dict`, `json.dumps`, `len`, `zip`

### __init__

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/return_transport.py:7](../../../api/wms_api_server/app/modules/delivery/infrastructure/return_transport.py#L7)

```python
__init__(self, gateway: Any, post: Callable[[str, str, dict[str, Any], dict[str, Any], str], dict[str, Any]]) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### plan

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/return_transport.py:11](../../../api/wms_api_server/app/modules/delivery/infrastructure/return_transport.py#L11)

```python
plan(self, operation_id: str, approval_id: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.post`

### eligible

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/return_transport.py:14](../../../api/wms_api_server/app/modules/delivery/infrastructure/return_transport.py#L14)

```python
eligible(self) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### trip

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/return_transport.py:25](../../../api/wms_api_server/app/modules/delivery/infrastructure/return_transport.py#L25)

```python
trip(self, task_id: int) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReceiptError`, `len`, `self.gateway.fetch_all`

### __init__

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/store_cases.py:7](../../../api/wms_api_server/app/modules/delivery/infrastructure/store_cases.py#L7)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### list

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/store_cases.py:10](../../../api/wms_api_server/app/modules/delivery/infrastructure/store_cases.py#L10)

```python
list(self, address: str, after: str, limit: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `len`, `self.gateway.fetch_all`

### detail

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/store_cases.py:22](../../../api/wms_api_server/app/modules/delivery/infrastructure/store_cases.py#L22)

```python
detail(self, case_id: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReceiptError`, `any`, `bool`, `len`, `self.gateway.fetch_all`

### evidence_failure

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/store_evidence.py:11](../../../api/wms_api_server/app/modules/delivery/infrastructure/store_evidence.py#L11)

```python
evidence_failure(error: oracledb.DatabaseError) -> StoreReceiptError
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReceiptError`, `getattr`, `str`, `str(error.args[0]).split`

### __init__

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/store_evidence.py:18](../../../api/wms_api_server/app/modules/delivery/infrastructure/store_evidence.py#L18)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### upload

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/store_evidence.py:21](../../../api/wms_api_server/app/modules/delivery/infrastructure/store_evidence.py#L21)

```python
upload(self, load_operation_id: str, store_address: str, view: str, mime_type: str, contents: bytes, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReceiptError`, `abs`, `blob.setvalue`, `cursor.callproc`, `cursor.var`, `evidence_failure`, `getattr`, `hasattr`, `json.loads`, `result.getvalue`, `self.gateway.transaction`, `sha256`, `sha256(contents).hexdigest`, `sha256(contents).hexdigest().upper`, `value.read`, `verify_photo`

### photos

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/store_evidence.py:38](../../../api/wms_api_server/app/modules/delivery/infrastructure/store_evidence.py#L38)

```python
photos(self, load_operation_id: str, store_address: str, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `abs`, `evidence_failure`, `getattr`, `isinstance`, `json.loads`, `self.gateway.fetch_all`

### content

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/store_evidence.py:49](../../../api/wms_api_server/app/modules/delivery/infrastructure/store_evidence.py#L49)

```python
content(self, photo_id: str, actor: str) -> ArchivedPhoto
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ArchivedPhoto`, `StoreReceiptError`, `isinstance`, `len`, `self.gateway.fetch_all`, `self.photos`, `sha256`, `sha256(contents).hexdigest`, `sha256(contents).hexdigest().upper`

### __init__

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/store_receipt.py:13](../../../api/wms_api_server/app/modules/delivery/infrastructure/store_receipt.py#L13)

```python
__init__(self, gateway: Any, post: Callable[[str, str, dict[str, Any], dict[str, Any], str], dict[str, Any]]) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### start_unloading

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/store_receipt.py:17](../../../api/wms_api_server/app/modules/delivery/infrastructure/store_receipt.py#L17)

```python
start_unloading(self, body: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `start_unloading`

### unloading

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/store_receipt.py:21](../../../api/wms_api_server/app/modules/delivery/infrastructure/store_receipt.py#L21)

```python
unloading(self, load: str, address: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `read_unloading`

### release_custody

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/store_receipt.py:25](../../../api/wms_api_server/app/modules/delivery/infrastructure/store_receipt.py#L25)

```python
release_custody(self, operation_id: str, receipt_id: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.post`

### cases

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/store_receipt.py:28](../../../api/wms_api_server/app/modules/delivery/infrastructure/store_receipt.py#L28)

```python
cases(self, address: str, after: str, limit: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreCases`, `StoreCases(self.gateway).list`

### case_detail

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/store_receipt.py:31](../../../api/wms_api_server/app/modules/delivery/infrastructure/store_receipt.py#L31)

```python
case_detail(self, case_id: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreCases`, `StoreCases(self.gateway).detail`

### preview

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/store_receipt.py:34](../../../api/wms_api_server/app/modules/delivery/infrastructure/store_receipt.py#L34)

```python
preview(self, load_operation_id: str, store_address: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `read_store_preview`

### places

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/store_receipt.py:37](../../../api/wms_api_server/app/modules/delivery/infrastructure/store_receipt.py#L37)

```python
places(self, trip_id: int, store_address: str, actor: str, after: str='', limit: int=200) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReceiptError`, `cur.callproc`, `getattr`, `len`, `params.items`, `self.gateway.fetch_all`, `self.gateway.transaction`

### confirm

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/store_receipt.py:67](../../../api/wms_api_server/app/modules/delivery/infrastructure/store_receipt.py#L67)

```python
confirm(self, operation_id: str, load_operation_id: str, store_address: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReceiptError`, `ValueError`, `dict`, `entry.get`, `entry.items`, `metadata.get`, `metadata.pop`, `normalize_interwarehouse_scans`, `normalize_unit_scan_codes`, `normalized.append`, `self.post`, `str`

### configure

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/store_receipt.py:94](../../../api/wms_api_server/app/modules/delivery/infrastructure/store_receipt.py#L94)

```python
configure(self, store_address: str, mode: str, expected_version: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReceiptError`, `cursor.execute`, `cursor.fetchall`, `cursor.fetchone`, `stock_configuration_transaction`

### assign_receiver

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/store_receipt.py:110](../../../api/wms_api_server/app/modules/delivery/infrastructure/store_receipt.py#L110)

```python
assign_receiver(self, store_address: str, username: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReceiptError`, `cursor.execute`, `cursor.fetchone`, `stock_configuration_transaction`

### read_store_preview

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/store_receipt_read.py:9](../../../api/wms_api_server/app/modules/delivery/infrastructure/store_receipt_read.py#L9)

```python
read_store_preview(gateway: Any, load_operation_id: str, store_address: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReceiptError`, `abs`, `cursor.execute`, `cursor.fetchone`, `gateway.transaction`, `getattr`, `read_oracle_json`, `str`, `str(exc.args[0]).split`, `unloading_fact`

### __init__

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/store_returns.py:9](../../../api/wms_api_server/app/modules/delivery/infrastructure/store_returns.py#L9)

```python
__init__(self, gateway: Any, post: Callable[[str, str, dict[str, Any], dict[str, Any], str], dict[str, Any]]) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### approve

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/store_returns.py:13](../../../api/wms_api_server/app/modules/delivery/infrastructure/store_returns.py#L13)

```python
approve(self, operation_id: str, receipt_id: str, line_no: int, metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.post`

### original

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/store_returns.py:16](../../../api/wms_api_server/app/modules/delivery/infrastructure/store_returns.py#L16)

```python
original(self, receipt_id: str, actor: str | None=None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReceiptError`, `dict`, `item[0].lower`, `len`, `progress.get`, `q.execute`, `q.fetchall`, `q.fetchone`, `read_oracle_json`, `return_progress`, `rows`, `self.gateway.transaction`, `units.extend`, `zip`

### reuse_preview

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/store_returns.py:86](../../../api/wms_api_server/app/modules/delivery/infrastructure/store_returns.py#L86)

```python
reuse_preview(self, receipt_id: str, line_no: int, quantity: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReceiptError`, `getattr`, `out.getvalue`, `q.callproc`, `q.execute`, `q.var`, `read_oracle_json`, `self.gateway.transaction`, `str`, `str(exc.args[0]).split`

### rows

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/store_returns.py:23](../../../api/wms_api_server/app/modules/delivery/infrastructure/store_returns.py#L23)

```python
rows(sql: str, binds: dict) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `dict`, `item[0].lower`, `q.execute`, `q.fetchall`, `zip`

### scale_failure

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/store_scales.py:11](../../../api/wms_api_server/app/modules/delivery/infrastructure/store_scales.py#L11)

```python
scale_failure(exc: oracledb.DatabaseError) -> StoreReceiptError
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReceiptError`, `abs`, `getattr`, `str`, `str(error).split`

### __init__

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/store_scales.py:19](../../../api/wms_api_server/app/modules/delivery/infrastructure/store_scales.py#L19)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### configure

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/store_scales.py:22](../../../api/wms_api_server/app/modules/delivery/infrastructure/store_scales.py#L22)

```python
configure(self, device_id: str, body: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `StoreReceiptError`, `int`, `q.execute`, `q.fetchone`, `scale_failure`, `stock_configuration_transaction`

### capture

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/store_scales.py:48](../../../api/wms_api_server/app/modules/delivery/infrastructure/store_scales.py#L48)

```python
capture(self, body: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `hasattr`, `inp.setvalue`, `json.dumps`, `json.loads`, `out.getvalue`, `q.callproc`, `q.var`, `raw.read`, `scale_failure`, `self.gateway.transaction`

### readings

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/store_scales.py:59](../../../api/wms_api_server/app/modules/delivery/infrastructure/store_scales.py#L59)

```python
readings(self, load_operation_id: str, store_address: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `isinstance`, `json.loads`, `len`, `read_store_preview`, `self.gateway.fetch_all`

### reading

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/store_scales.py:64](../../../api/wms_api_server/app/modules/delivery/infrastructure/store_scales.py#L64)

```python
reading(self, key: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReceiptError`, `isinstance`, `json.loads`, `read_store_preview`, `self.gateway.fetch_all`

### start_unloading

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/store_unloading.py:9](../../../api/wms_api_server/app/modules/delivery/infrastructure/store_unloading.py#L9)

```python
start_unloading(gateway: Any, body: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReceiptError`, `cursor.callproc`, `cursor.var`, `gateway.transaction`, `getattr`, `json.dumps`, `read_oracle_json`, `result.getvalue`, `str`, `str(exc.args[0]).split`

### unloading_fact

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/store_unloading.py:25](../../../api/wms_api_server/app/modules/delivery/infrastructure/store_unloading.py#L25)

```python
unloading_fact(cursor: Any, load: str, address: str) -> dict[str, Any] | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cursor.execute`, `cursor.fetchone`, `read_oracle_json`

### read_unloading

[Исходник: api/wms_api_server/app/modules/delivery/infrastructure/store_unloading.py:37](../../../api/wms_api_server/app/modules/delivery/infrastructure/store_unloading.py#L37)

```python
read_unloading(gateway: Any, load: str, address: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReceiptError`, `cursor.callproc`, `cursor.execute`, `cursor.var`, `gateway.transaction`, `getattr`, `str`, `str(exc.args[0]).split`, `unloading_fact`

### build_store_receipt

[Исходник: api/wms_api_server/app/modules/delivery/public.py:9](../../../api/wms_api_server/app/modules/delivery/public.py#L9)

```python
build_store_receipt(gateway: Any, post: Callable[[str, str, dict[str, Any], dict[str, Any], str], dict[str, Any]]) -> StoreReceiptPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReceipt`

### build_store_evidence

[Исходник: api/wms_api_server/app/modules/delivery/public.py:16](../../../api/wms_api_server/app/modules/delivery/public.py#L16)

```python
build_store_evidence(gateway: Any) -> StoreEvidencePort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreEvidence`

### build_store_scales

[Исходник: api/wms_api_server/app/modules/delivery/public.py:24](../../../api/wms_api_server/app/modules/delivery/public.py#L24)

```python
build_store_scales(gateway: Any) -> StoreScalesPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreScales`

### build_order_delivery

[Исходник: api/wms_api_server/app/modules/delivery/public.py:32](../../../api/wms_api_server/app/modules/delivery/public.py#L32)

```python
build_order_delivery(gateway: Any) -> OrderDeliveryPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OrderDelivery`

### build_case_work

[Исходник: api/wms_api_server/app/modules/delivery/public.py:40](../../../api/wms_api_server/app/modules/delivery/public.py#L40)

```python
build_case_work(gateway: Any, post: Callable[[str, str, dict[str, Any], dict[str, Any], str], dict[str, Any]]) -> CaseWorkPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CaseWork`

### build_store_returns

[Исходник: api/wms_api_server/app/modules/delivery/public.py:47](../../../api/wms_api_server/app/modules/delivery/public.py#L47)

```python
build_store_returns(gateway: Any, post: Callable[[str, str, dict[str, Any], dict[str, Any], str], dict[str, Any]]) -> StoreReturnsPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreReturns`

### build_return_transport

[Исходник: api/wms_api_server/app/modules/delivery/public.py:54](../../../api/wms_api_server/app/modules/delivery/public.py#L54)

```python
build_return_transport(gateway: Any, post: Callable[[str, str, dict[str, Any], dict[str, Any], str], dict[str, Any]]) -> ReturnTransportPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ReturnTransport`

### build_return_custody

[Исходник: api/wms_api_server/app/modules/delivery/public.py:61](../../../api/wms_api_server/app/modules/delivery/public.py#L61)

```python
build_return_custody(gateway: Any, post: Callable[[str, str, dict[str, Any], dict[str, Any], str], dict[str, Any]]) -> ReturnCustodyPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ReturnCustody`
