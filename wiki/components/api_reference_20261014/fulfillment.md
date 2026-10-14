# Методы: fulfillment

### execution_service

[Исходник: api/wms_api_server/app/modules/fulfillment/api/execution_routes.py:13](../../../api/wms_api_server/app/modules/fulfillment/api/execution_routes.py#L13)

```python
execution_service() -> OrderExecutionPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### execution

[Исходник: api/wms_api_server/app/modules/fulfillment/api/execution_routes.py:18](../../../api/wms_api_server/app/modules/fulfillment/api/execution_routes.py#L18)

```python
execution(order_id: int, _user: AdminUser=Depends(require_permission('customer_fulfillment_view')), service: OrderExecutionPort=Depends(execution_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.get`, `service.get`, `str`

### get

[Исходник: api/wms_api_server/app/modules/fulfillment/api/execution_routes.py:7](../../../api/wms_api_server/app/modules/fulfillment/api/execution_routes.py#L7)

```python
get(self, order_id: int, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### readiness

[Исходник: api/wms_api_server/app/modules/fulfillment/api/preparation_read_routes.py:9](../../../api/wms_api_server/app/modules/fulfillment/api/preparation_read_routes.py#L9)

```python
readiness(order_id: int, user: AdminUser=Depends(require_permission('customer_order_view')), service: PreparationPort=Depends(preparation_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.get`, `service.readiness`, `str`

### layout

[Исходник: api/wms_api_server/app/modules/fulfillment/api/preparation_read_routes.py:27](../../../api/wms_api_server/app/modules/fulfillment/api/preparation_read_routes.py#L27)

```python
layout(order_id: int, body: LayoutProposal, user: AdminUser=Depends(require_permission('customer_order_view')), service: PreparationPort=Depends(preparation_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.post`, `service.layout`, `str`

### auto_call

[Исходник: api/wms_api_server/app/modules/fulfillment/api/preparation_read_routes.py:51](../../../api/wms_api_server/app/modules/fulfillment/api/preparation_read_routes.py#L51)

```python
auto_call(method: Callable[[int, dict, str], dict], order_id: int, body: dict, user: AdminUser) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `getattr`, `method`, `str`

### auto_preview

[Исходник: api/wms_api_server/app/modules/fulfillment/api/preparation_read_routes.py:66](../../../api/wms_api_server/app/modules/fulfillment/api/preparation_read_routes.py#L66)

```python
auto_preview(order_id: int, body: AutoLimits, user: AdminUser=Depends(require_permission('customer_order_view')), service: PreparationPort=Depends(preparation_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `auto_call`, `body.model_dump`, `require_permission`, `router.post`

### auto_prepare

[Исходник: api/wms_api_server/app/modules/fulfillment/api/preparation_read_routes.py:72](../../../api/wms_api_server/app/modules/fulfillment/api/preparation_read_routes.py#L72)

```python
auto_prepare(order_id: int, body: AutoPreparationRequest, user: AdminUser=Depends(require_permission('customer_order_import')), service: PreparationPort=Depends(preparation_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `auto_call`, `body.model_dump`, `require_permission`, `router.post`

### auto_resolve

[Исходник: api/wms_api_server/app/modules/fulfillment/api/preparation_read_routes.py:78](../../../api/wms_api_server/app/modules/fulfillment/api/preparation_read_routes.py#L78)

```python
auto_resolve(order_id: int, body: AutoPreparationRequest, user: AdminUser=Depends(require_permission('customer_order_import')), service: PreparationPort=Depends(preparation_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `auto_call`, `body.model_dump`, `require_permission`, `router.post`

### failure

[Исходник: api/wms_api_server/app/modules/fulfillment/api/prepared_layout_routes.py:23](../../../api/wms_api_server/app/modules/fulfillment/api/prepared_layout_routes.py#L23)

```python
failure(exc: StockPostingError) -> HTTPException
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `str`

### read

[Исходник: api/wms_api_server/app/modules/fulfillment/api/prepared_layout_routes.py:31](../../../api/wms_api_server/app/modules/fulfillment/api/prepared_layout_routes.py#L31)

```python
read(order_id: int=Path(ge=1), user: AdminUser=Depends(require_permission('customer_order_view')), service: PreparedLayoutPort=Depends(prepared_layout_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Path`, `failure`, `require_permission`, `router.get`, `service.read`

### preview

[Исходник: api/wms_api_server/app/modules/fulfillment/api/prepared_layout_routes.py:40](../../../api/wms_api_server/app/modules/fulfillment/api/prepared_layout_routes.py#L40)

```python
preview(body: LayoutPreview, order_id: int=Path(ge=1), user: AdminUser=Depends(require_permission('customer_order_view')), service: PreparedLayoutPort=Depends(prepared_layout_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Path`, `failure`, `require_permission`, `router.post`, `service.preview`

### move

[Исходник: api/wms_api_server/app/modules/fulfillment/api/prepared_layout_routes.py:50](../../../api/wms_api_server/app/modules/fulfillment/api/prepared_layout_routes.py#L50)

```python
move(body: LayoutMove, order_id: int=Path(ge=1), user: AdminUser=Depends(require_permission('outgoing_pallet_edit')), service: PreparedLayoutPort=Depends(prepared_layout_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Path`, `body.model_dump`, `failure`, `require_permission`, `router.post`, `service.move`

### store_admission_service

[Исходник: api/wms_api_server/app/modules/fulfillment/api/store_decision_routes.py:16](../../../api/wms_api_server/app/modules/fulfillment/api/store_decision_routes.py#L16)

```python
store_admission_service() -> StoreAdmissionPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### receive_decision

[Исходник: api/wms_api_server/app/modules/fulfillment/api/store_decision_routes.py:21](../../../api/wms_api_server/app/modules/fulfillment/api/store_decision_routes.py#L21)

```python
receive_decision(request: Request, user: AdminUser=Depends(require_permission('sap_store_decision_import')), service: StoreAdmissionPort=Depends(store_admission_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `bytearray`, `bytes`, `len`, `raw.extend`, `request.stream`, `require_permission`, `router.post`, `run_in_threadpool`, `str`

### receive

[Исходник: api/wms_api_server/app/modules/fulfillment/api/store_decision_routes.py:13](../../../api/wms_api_server/app/modules/fulfillment/api/store_decision_routes.py#L13)

```python
receive(self, raw: bytes, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### store_order_service

[Исходник: api/wms_api_server/app/modules/fulfillment/api/store_order_routes.py:16](../../../api/wms_api_server/app/modules/fulfillment/api/store_order_routes.py#L16)

```python
store_order_service() -> StoreOrdersPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### preparation_service

[Исходник: api/wms_api_server/app/modules/fulfillment/api/store_order_routes.py:20](../../../api/wms_api_server/app/modules/fulfillment/api/store_order_routes.py#L20)

```python
preparation_service() -> PreparationPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### prepare_st

[Исходник: api/wms_api_server/app/modules/fulfillment/api/store_order_routes.py:39](../../../api/wms_api_server/app/modules/fulfillment/api/store_order_routes.py#L39)

```python
prepare_st(order_id: int, body: PreparationRequest, user: AdminUser=Depends(require_permission('customer_order_import')), service: PreparationPort=Depends(preparation_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `body.model_dump`, `len`, `require_permission`, `router.post`, `service.prepare`, `str`, `sum`

### receive_order

[Исходник: api/wms_api_server/app/modules/fulfillment/api/store_order_routes.py:62](../../../api/wms_api_server/app/modules/fulfillment/api/store_order_routes.py#L62)

```python
receive_order(request: Request, user: AdminUser=Depends(require_permission('sap_store_order_import')), service: StoreOrdersPort=Depends(store_order_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `bytearray`, `bytes`, `len`, `raw.extend`, `request.stream`, `require_permission`, `router.post`, `run_in_threadpool`, `str`

### list_orders

[Исходник: api/wms_api_server/app/modules/fulfillment/api/store_order_routes.py:80](../../../api/wms_api_server/app/modules/fulfillment/api/store_order_routes.py#L80)

```python
list_orders(warehouse_id: int | None=None, limit: int=Query(100, ge=1, le=200), user: AdminUser=Depends(require_permission('customer_order_view')), service: StoreOrdersPort=Depends(store_order_service)) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Query`, `require_permission`, `router.get`, `service.list`, `str`

### configure_calendar

[Исходник: api/wms_api_server/app/modules/fulfillment/api/store_order_routes.py:90](../../../api/wms_api_server/app/modules/fulfillment/api/store_order_routes.py#L90)

```python
configure_calendar(warehouse: int, store_code: str, body: StoreCalendar, user: AdminUser=Depends(require_permission('customer_rule_edit')), service: StoreOrdersPort=Depends(store_order_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `body.model_dump`, `require_permission`, `router.put`, `service.configure`, `str`

### get_order

[Исходник: api/wms_api_server/app/modules/fulfillment/api/store_order_routes.py:102](../../../api/wms_api_server/app/modules/fulfillment/api/store_order_routes.py#L102)

```python
get_order(order_id: int, user: AdminUser=Depends(require_permission('customer_order_view')), service: StoreOrdersPort=Depends(store_order_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.get`, `service.get`, `str`

### calendar_context

[Исходник: api/wms_api_server/app/modules/fulfillment/api/store_order_routes.py:124](../../../api/wms_api_server/app/modules/fulfillment/api/store_order_routes.py#L124)

```python
calendar_context(warehouse: int, store_code: str, delivery_date: date, user: AdminUser=Depends(require_permission('customer_rule_edit')), service: StoreOrdersPort=Depends(store_order_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `delivery_date.isoformat`, `require_permission`, `router.get`, `service.calendar_context`, `str`

### calendar_exception

[Исходник: api/wms_api_server/app/modules/fulfillment/api/store_order_routes.py:136](../../../api/wms_api_server/app/modules/fulfillment/api/store_order_routes.py#L136)

```python
calendar_exception(body: CalendarException, user: AdminUser=Depends(require_permission('customer_rule_edit')), service: StoreOrdersPort=Depends(store_order_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `body.model_dump`, `require_permission`, `router.post`, `service.set_calendar_exception`, `str`

### resolve_preparation

[Исходник: api/wms_api_server/app/modules/fulfillment/api/store_order_routes.py:146](../../../api/wms_api_server/app/modules/fulfillment/api/store_order_routes.py#L146)

```python
resolve_preparation(order_id: int, body: PreparationRequest, user: AdminUser=Depends(require_permission('customer_order_import')), service: PreparationPort=Depends(preparation_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `body.model_dump`, `len`, `require_permission`, `router.post`, `service.resolve`, `str`, `sum`

### receive

[Исходник: api/wms_api_server/app/modules/fulfillment/application/ports.py:9](../../../api/wms_api_server/app/modules/fulfillment/application/ports.py#L9)

```python
receive(self, raw: bytes, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### list

[Исходник: api/wms_api_server/app/modules/fulfillment/application/ports.py:10](../../../api/wms_api_server/app/modules/fulfillment/application/ports.py#L10)

```python
list(self, warehouse: int | None, limit: int, actor: str) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### get

[Исходник: api/wms_api_server/app/modules/fulfillment/application/ports.py:11](../../../api/wms_api_server/app/modules/fulfillment/application/ports.py#L11)

```python
get(self, order_id: int, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### configure

[Исходник: api/wms_api_server/app/modules/fulfillment/application/ports.py:12](../../../api/wms_api_server/app/modules/fulfillment/application/ports.py#L12)

```python
configure(self, warehouse: int, store_code: str, body: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### calendar_context

[Исходник: api/wms_api_server/app/modules/fulfillment/application/ports.py:13](../../../api/wms_api_server/app/modules/fulfillment/application/ports.py#L13)

```python
calendar_context(self, warehouse: int, store_code: str, day: str, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### set_calendar_exception

[Исходник: api/wms_api_server/app/modules/fulfillment/application/ports.py:14](../../../api/wms_api_server/app/modules/fulfillment/application/ports.py#L14)

```python
set_calendar_exception(self, operation: str, body: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### auto_preview

[Исходник: api/wms_api_server/app/modules/fulfillment/application/ports.py:18](../../../api/wms_api_server/app/modules/fulfillment/application/ports.py#L18)

```python
auto_preview(self, order_id: int, limits: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### auto_prepare

[Исходник: api/wms_api_server/app/modules/fulfillment/application/ports.py:19](../../../api/wms_api_server/app/modules/fulfillment/application/ports.py#L19)

```python
auto_prepare(self, order_id: int, payload: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### auto_resolve

[Исходник: api/wms_api_server/app/modules/fulfillment/application/ports.py:20](../../../api/wms_api_server/app/modules/fulfillment/application/ports.py#L20)

```python
auto_resolve(self, order_id: int, payload: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### resolve

[Исходник: api/wms_api_server/app/modules/fulfillment/application/ports.py:21](../../../api/wms_api_server/app/modules/fulfillment/application/ports.py#L21)

```python
resolve(self, order_id: int, payload: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### layout

[Исходник: api/wms_api_server/app/modules/fulfillment/application/ports.py:22](../../../api/wms_api_server/app/modules/fulfillment/application/ports.py#L22)

```python
layout(self, order_id: int, counts: dict[str, int], actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### readiness

[Исходник: api/wms_api_server/app/modules/fulfillment/application/ports.py:23](../../../api/wms_api_server/app/modules/fulfillment/application/ports.py#L23)

```python
readiness(self, order_id: int, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### prepare

[Исходник: api/wms_api_server/app/modules/fulfillment/application/ports.py:24](../../../api/wms_api_server/app/modules/fulfillment/application/ports.py#L24)

```python
prepare(self, order_id: int, payload: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### prepared_layout_service

[Исходник: api/wms_api_server/app/modules/fulfillment/contracts_prepared_layout.py:10](../../../api/wms_api_server/app/modules/fulfillment/contracts_prepared_layout.py#L10)

```python
prepared_layout_service() -> PreparedLayoutPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### read

[Исходник: api/wms_api_server/app/modules/fulfillment/contracts_prepared_layout.py:5](../../../api/wms_api_server/app/modules/fulfillment/contracts_prepared_layout.py#L5)

```python
read(self, order: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### preview

[Исходник: api/wms_api_server/app/modules/fulfillment/contracts_prepared_layout.py:6](../../../api/wms_api_server/app/modules/fulfillment/contracts_prepared_layout.py#L6)

```python
preview(self, order: int, row: int, target: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### move

[Исходник: api/wms_api_server/app/modules/fulfillment/contracts_prepared_layout.py:7](../../../api/wms_api_server/app/modules/fulfillment/contracts_prepared_layout.py#L7)

```python
move(self, order: int, body: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### positive

[Исходник: api/wms_api_server/app/modules/fulfillment/domain/automatic_layout.py:8](../../../api/wms_api_server/app/modules/fulfillment/domain/automatic_layout.py#L8)

```python
positive(value: str) -> Fraction
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `Fraction`, `ValueError`, `number.is_finite`, `str`

### temperature

[Исходник: api/wms_api_server/app/modules/fulfillment/domain/automatic_layout.py:18](../../../api/wms_api_server/app/modules/fulfillment/domain/automatic_layout.py#L18)

```python
temperature(line: dict) -> tuple[Decimal | None, Decimal | None]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `ValueError`, `any`, `line.get`, `str`, `x.is_finite`

### merged_temperature

[Исходник: api/wms_api_server/app/modules/fulfillment/domain/automatic_layout.py:28](../../../api/wms_api_server/app/modules/fulfillment/domain/automatic_layout.py#L28)

```python
merged_temperature(current: dict, lo: Decimal | None, hi: Decimal | None) -> tuple[Decimal | None, Decimal | None] | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `bool`, `max`, `min`

### automatic_layout

[Исходник: api/wms_api_server/app/modules/fulfillment/domain/automatic_layout.py:39](../../../api/wms_api_server/app/modules/fulfillment/domain/automatic_layout.py#L39)

```python
automatic_layout(lines: list[dict], sequence: dict[str, tuple], limits: dict) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Fraction`, `ValueError`, `current['lines'].append`, `enumerate`, `exact_decimal`, `format`, `isinstance`, `len`, `merged_temperature`, `min`, `pallets.append`, `positive`, `sequence.get`, `sorted`, `statistics.append`, `str`, `temperature`

### _text

[Исходник: api/wms_api_server/app/modules/fulfillment/domain/execution_progress.py:7](../../../api/wms_api_server/app/modules/fulfillment/domain/execution_progress.py#L7)

```python
_text(number: Decimal) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `format`, `value.rstrip`, `value.rstrip('0').rstrip`

### line_progress

[Исходник: api/wms_api_server/app/modules/fulfillment/domain/execution_progress.py:12](../../../api/wms_api_server/app/modules/fulfillment/domain/execution_progress.py#L12)

```python
line_progress(row: dict[str, Any]) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `Decimal(scaled.numerator).scaleb`, `Fraction`, `ValueError`, `_text`, `int`, `localcontext`, `max`, `result.update`

### line_is_cancelled

[Исходник: api/wms_api_server/app/modules/fulfillment/domain/execution_progress.py:54](../../../api/wms_api_server/app/modules/fulfillment/domain/execution_progress.py#L54)

```python
line_is_cancelled(line: dict[str, Any]) -> bool
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `line.get`

### order_progress_status

[Исходник: api/wms_api_server/app/modules/fulfillment/domain/execution_progress.py:58](../../../api/wms_api_server/app/modules/fulfillment/domain/execution_progress.py#L58)

```python
order_progress_status(lines: list[dict[str, Any]]) -> str
```

Never hide excess, unresolved units or closed shortage behind PARTIAL.

Вызывает: `Decimal`, `all`, `any`, `line_is_cancelled`

### exact_decimal

[Исходник: api/wms_api_server/app/modules/fulfillment/domain/preparation_quantities.py:5](../../../api/wms_api_server/app/modules/fulfillment/domain/preparation_quantities.py#L5)

```python
exact_decimal(value: Fraction, scale: int=9) -> Decimal
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `ValueError`, `abs`, `str`, `str(abs(ticks.numerator)).zfill`

### pallet_share

[Исходник: api/wms_api_server/app/modules/fulfillment/domain/preparation_quantities.py:14](../../../api/wms_api_server/app/modules/fulfillment/domain/preparation_quantities.py#L14)

```python
pallet_share(quantity: Decimal, total: Decimal, total_packs: Decimal, total_weight: Decimal) -> tuple[int, Decimal]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Fraction`, `ValueError`, `any`, `exact_decimal`, `v.is_finite`

### read_store_decision

[Исходник: api/wms_api_server/app/modules/fulfillment/domain/store_decision.py:8](../../../api/wms_api_server/app/modules/fulfillment/domain/store_decision.py#L8)

```python
read_store_decision(raw: bytes) -> dict[str, object]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ET.fromstring`, `ValueError`, `any`, `int`, `len`, `min`, `node.tag.split`, `raw.decode`, `re.fullmatch`, `root.get`, `root.tag.split`, `scalar`, `sha256`, `sha256(raw).hexdigest`, `text.upper`, `version.isascii`, `version.isdigit`

### scalar

[Исходник: api/wms_api_server/app/modules/fulfillment/domain/store_order.py:9](../../../api/wms_api_server/app/modules/fulfillment/domain/store_order.py#L9)

```python
scalar(node: ET.Element, name: str, maximum: int=100) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(found[0].text or '').strip`, `ValueError`, `len`, `n.tag.split`, `value.encode`

### positive

[Исходник: api/wms_api_server/app/modules/fulfillment/domain/store_order.py:19](../../../api/wms_api_server/app/modules/fulfillment/domain/store_order.py#L19)

```python
positive(value: str) -> Decimal
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `ValueError`, `number.is_finite`, `number.normalize`, `number.normalize().as_tuple`

### read_order

[Исходник: api/wms_api_server/app/modules/fulfillment/domain/store_order.py:29](../../../api/wms_api_server/app/modules/fulfillment/domain/store_order.py#L29)

```python
read_order(raw: bytes) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ET.fromstring`, `ValueError`, `any`, `data.items`, `data['WarehouseId'].isascii`, `data['WarehouseId'].isdigit`, `date.fromisoformat`, `date.fromisoformat(data[name]).isoformat`, `datetime.fromisoformat`, `datetime.fromisoformat(data[name]).utcoffset`, `int`, `json.dumps`, `json.dumps(content, sort_keys=True).encode`, `len`, `lines.append`, `n.tag.split`, `next`, `node.tag.split`, `number.isascii`, `number.isdigit`, `positive`, `qnode.get`, `qnode.get('unit', '').strip`, `raw.decode`, `root.get`, `root.tag.split`, `scalar`, `seen.add`, `set`, `sha256`, `sha256(json.dumps(content, sort_keys=True).encode()).hexdigest`, `sha256(raw).hexdigest`, `sorted`, `str`, `text.upper` (остальные вызовы — в исходнике)

### calendar

[Исходник: api/wms_api_server/app/modules/fulfillment/domain/store_order.py:77](../../../api/wms_api_server/app/modules/fulfillment/domain/store_order.py#L77)

```python
calendar(data: dict, offset_minutes: int, weekdays: str, same_day: bool, received: datetime, delivery_exception: bool | None=None) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `date.fromisoformat`, `datetime.combine`, `datetime.fromisoformat`, `datetime.fromisoformat(data[n]).astimezone`, `delivery.isoweekday`, `finish.replace`, `received.astimezone`, `shipment.date`, `shipment.replace`, `start.date`, `start.replace`, `str`, `time`, `timedelta`, `timezone`, `weekdays.split`

### digest

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/automatic_preparation.py:13](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/automatic_preparation.py#L13)

```python
digest(value: dict) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `json.dumps`, `json.dumps(value, sort_keys=True, separators=(',', ':'), default=str).encode`, `sha256`, `sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), default=str).encode()).hexdigest`

### lock_layout_inputs

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/automatic_preparation.py:16](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/automatic_preparation.py#L16)

```python
lock_layout_inputs(cur: oracledb.Cursor, order: int) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.execute`, `cur.fetchall`

### __init__

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/automatic_preparation.py:26](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/automatic_preparation.py#L26)

```python
__init__(self, legacy: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### _layout

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/automatic_preparation.py:29](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/automatic_preparation.py#L29)

```python
_layout(self, cur: oracledb.Cursor, order: int, limits: dict, actor: str, permission: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `','.join`, `TransactionGateway`, `ValueError`, `automatic_layout`, `cur.execute`, `cur.fetchall`, `digest`, `int`, `len`, `preparation_readiness`

### preview

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/automatic_preparation.py:53](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/automatic_preparation.py#L53)

```python
preview(self, order: int, limits: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.execute`, `self._layout`, `self.legacy.gateway.transaction`

### _saved

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/automatic_preparation.py:58](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/automatic_preparation.py#L58)

```python
_saved(self, cur: oracledb.Cursor, order: int, request: dict, actor: str) -> dict | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LookupError`, `StoreOrderConflict`, `assert_store_scope`, `cur.execute`, `cur.fetchone`, `digest`, `read_oracle_json`, `saved.get`

### prepare

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/automatic_preparation.py:73](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/automatic_preparation.py#L73)

```python
prepare(self, order: int, request: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreOrderConflict`, `digest`, `lock_layout_inputs`, `self._layout`, `self._saved`, `self.legacy._prepare_locked`, `source_transaction`

### resolve

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/automatic_preparation.py:89](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/automatic_preparation.py#L89)

```python
resolve(self, order: int, request: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self._saved`, `source_transaction`

### __init__

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/customer_order_read.py:9](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/customer_order_read.py#L9)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### list

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/customer_order_read.py:12](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/customer_order_read.py#L12)

```python
list(self, actor: str, status: str | None=None, order_no: str | None=None, legacy_order_id: int | None=None, limit: int=200, before_id: int | None=None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CustomerOrderRead`, `CustomerOrderRead(TransactionGateway(cur)).list_rows`, `TransactionGateway`, `ValueError`, `actor_warehouse`, `cur.execute`, `getattr`, `self.gateway.transaction`

### get

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/customer_order_read.py:24](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/customer_order_read.py#L24)

```python
get(self, order_id: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CustomerOrderRead`, `CustomerOrderRead(TransactionGateway(cur)).detail_rows`, `LookupError`, `TransactionGateway`, `ValueError`, `assert_store_scope`, `cur.execute`, `cur.fetchone`, `getattr`, `self.gateway.transaction`

### list_rows

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/customer_order_read.py:40](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/customer_order_read.py#L40)

```python
list_rows(self, status: str | None=None, order_no: str | None=None, legacy_order_id: int | None=None, limit: int=200, warehouse: int | None=None, before_id: int | None=None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `conditions.append`, `max`, `min`, `order_no.upper`, `self.gateway.fetch_all`, `status.upper`

### detail_rows

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/customer_order_read.py:111](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/customer_order_read.py#L111)

```python
detail_rows(self, customer_order_id: int) -> dict[str, Any] | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `len`, `self.gateway.fetch_all`

### __init__

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/execution_progress.py:10](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/execution_progress.py#L10)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### get

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/execution_progress.py:13](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/execution_progress.py#L13)

```python
get(self, order_id: int, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LookupError`, `OrderExecution`, `OrderExecution(TransactionGateway(cursor))._snapshot`, `TransactionGateway`, `ValueError`, `assert_store_scope`, `cursor.execute`, `cursor.fetchone`, `getattr`, `result.update`, `self.gateway.transaction`

### _snapshot

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/execution_progress.py:28](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/execution_progress.py#L28)

```python
_snapshot(self, order_id: int) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `LookupError`, `len`, `line_is_cancelled`, `line_progress`, `order_progress_status`, `self.gateway.fetch_all`, `sum`

### __init__

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/legacy_preparation.py:15](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/legacy_preparation.py#L15)

```python
__init__(self, gateway: OracleGateway) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### readiness

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/legacy_preparation.py:18](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/legacy_preparation.py#L18)

```python
readiness(self, order_id: int, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `preparation_readiness`

### layout

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/legacy_preparation.py:22](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/legacy_preparation.py#L22)

```python
layout(self, order_id: int, counts: dict[str, int], actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `preparation_layout`

### resolve

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/legacy_preparation.py:26](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/legacy_preparation.py#L26)

```python
resolve(self, order_id: int, payload: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LookupError`, `StoreOrderConflict`, `assert_store_scope`, `cur.execute`, `cur.fetchone`, `json.dumps`, `json.dumps(payload, sort_keys=True).encode`, `read_oracle_json`, `sha256`, `sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest`, `source_transaction`

### prepare

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/legacy_preparation.py:38](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/legacy_preparation.py#L38)

```python
prepare(self, order_id: int, payload: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self._prepare_locked`, `source_transaction`

### auto_preview

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/legacy_preparation.py:42](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/legacy_preparation.py#L42)

```python
auto_preview(self, order_id: int, limits: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `AutomaticPreparation`, `AutomaticPreparation(self).preview`

### auto_prepare

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/legacy_preparation.py:46](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/legacy_preparation.py#L46)

```python
auto_prepare(self, order_id: int, payload: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `AutomaticPreparation`, `AutomaticPreparation(self).prepare`

### auto_resolve

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/legacy_preparation.py:50](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/legacy_preparation.py#L50)

```python
auto_resolve(self, order_id: int, payload: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `AutomaticPreparation`, `AutomaticPreparation(self).resolve`

### _prepare_locked

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/legacy_preparation.py:54](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/legacy_preparation.py#L54)

```python
_prepare_locked(self, cur: oracledb.Cursor, order_id: int, payload: dict, actor: str, result_metadata: dict | None=None) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LookupError`, `StoreOrderConflict`, `ValueError`, `assert_current_order_calendar`, `assert_store_scope`, `cur.callfunc`, `cur.execute`, `cur.fetchone`, `cur.setinputsizes`, `enumerate`, `identifiers.append`, `int`, `json.dumps`, `json.dumps(payload, sort_keys=True).encode`, `lock_layout_inputs`, `read_oracle_json`, `result.update`, `self._demand`, `self._legacy_rows`, `self._pallet_rows`, `sha256`, `sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest`, `str`

### _demand

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/legacy_preparation.py:112](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/legacy_preparation.py#L112)

```python
_demand(self, cur: oracledb.Cursor, order_id: int, payload: dict) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `ValueError`, `cur.execute`, `cur.fetchall`, `defaultdict`, `demand.items`, `dict`, `seen.add`, `set`

### _legacy_rows

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/legacy_preparation.py:126](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/legacy_preparation.py#L126)

```python
_legacy_rows(self, cur: oracledb.Cursor, legacy_id: int, warehouse: int, demand: dict) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `ValueError`, `cur.callfunc`, `cur.execute`, `cur.fetchall`, `demand.items`, `len`

### _pallet_rows

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/legacy_preparation.py:148](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/legacy_preparation.py#L148)

```python
_pallet_rows(self, cur: oracledb.Cursor, uid: str, lines: list[dict], articles: dict, warehouse: int, st_number: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `ValueError`, `cur.callfunc`, `int`, `pallet_share`

### _text

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/legacy_preparation.py:158](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/legacy_preparation.py#L158)

```python
_text(value: object) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `hasattr`, `str`, `value.read`

### __init__

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/order_fulfillment_read.py:10](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/order_fulfillment_read.py#L10)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### get

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/order_fulfillment_read.py:13](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/order_fulfillment_read.py#L13)

```python
get(self, customer_order_id: int, actor: str) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LookupError`, `OrderFulfillmentRead`, `OrderFulfillmentRead(TransactionGateway(cur))._rows`, `TransactionGateway`, `ValueError`, `assert_store_scope`, `cur.execute`, `cur.fetchone`, `getattr`, `self.gateway.transaction`

### _rows

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/order_fulfillment_read.py:26](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/order_fulfillment_read.py#L26)

```python
_rows(self, customer_order_id: int, warehouse: int) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `hasattr`, `isinstance`, `json.loads`, `len`, `payload.read`, `row.get`, `row.pop`, `self.gateway.fetch_all`

### preparation_layout

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/preparation_layout.py:11](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/preparation_layout.py#L11)

```python
preparation_layout(gateway: Any, order: int, counts: dict[str, int], actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `','.join`, `Decimal`, `Fraction`, `ValueError`, `counts.get`, `exact_decimal`, `format`, `json.dumps`, `json.dumps(source, sort_keys=True, separators=(',', ':'), default=str).encode`, `len`, `pallets.append`, `preparation_readiness`, `propose_receipt_layout`, `set`, `sha256`, `sha256(json.dumps(source, sort_keys=True, separators=(',', ':'), default=str).encode()).hexdigest`, `str`, `summary.append`

### preparation_readiness

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/preparation_readiness.py:9](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/preparation_readiness.py#L9)

```python
preparation_readiness(gateway: Any, order: int, actor: str, permission: str='customer_order_view') -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(Decimal(quantity) / values[0]).to_integral_value`, `Decimal`, `LookupError`, `ValueError`, `actor_warehouse`, `address.strip`, `all`, `any`, `assert_store_scope`, `blockers.append`, `bool`, `cur.execute`, `cur.fetchall`, `cur.fetchone`, `delivery_rule`, `errors.append`, `finish.isoformat`, `gateway.transaction`, `getattr`, `len`, `lines.append`, `shipment.isoformat`

### __init__

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/prepared_layout.py:9](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/prepared_layout.py#L9)

```python
__init__(self, gateway: Any, posting: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### read

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/prepared_layout.py:12](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/prepared_layout.py#L12)

```python
read(self, order: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.callfunc`, `cur.execute`, `cur.fetchall`, `dict`, `int`, `len`, `self._failure`, `self.gateway.transaction`, `zip`

### preview

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/prepared_layout.py:32](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/prepared_layout.py#L32)

```python
preview(self, order: int, row: int, target: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.callfunc`, `cur.execute`, `read_oracle_json`, `self._failure`, `self.gateway.transaction`

### move

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/prepared_layout.py:41](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/prepared_layout.py#L41)

```python
move(self, order: int, body: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockCommand`, `self.posting.post`

### _failure

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/prepared_layout.py:48](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/prepared_layout.py#L48)

```python
_failure(exc: Exception) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockPostingError`, `getattr`, `str`, `str(exc.args[0]).split`

### admission_error

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/store_admission.py:10](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/store_admission.py#L10)

```python
admission_error(exc: oracledb.DatabaseError) -> Exception
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LookupError`, `PermissionError`, `StoreOrderConflict`, `ValueError`, `getattr`, `str`, `str(exc.args[0]).split`

### read_admission

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/store_admission.py:40](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/store_admission.py#L40)

```python
read_admission(cur: Any, order: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `admission_error`, `cur.callproc`, `cur.var`, `read_oracle_json`, `result.getvalue`

### __init__

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/store_admission.py:24](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/store_admission.py#L24)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### receive

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/store_admission.py:27](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/store_admission.py#L27)

```python
receive(self, raw: bytes, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `admission_error`, `cur.callproc`, `cur.var`, `json.dumps`, `payload.setvalue`, `read_oracle_json`, `read_store_decision`, `result.getvalue`, `self.gateway.transaction`

### call_calendar

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/store_calendar.py:8](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/store_calendar.py#L8)

```python
call_calendar(gateway: Any, procedure: str, arguments: list[Any], read_only: bool=False) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `PermissionError`, `ValueError`, `bound.append`, `cur.callproc`, `cur.execute`, `cur.var`, `gateway.transaction`, `getattr`, `isinstance`, `json.dumps`, `payload.setvalue`, `read_oracle_json`, `result.getvalue`, `str`, `str(exc.args[0]).split`

### configure_calendar

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/store_calendar.py:33](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/store_calendar.py#L33)

```python
configure_calendar(gateway: Any, warehouse: int, store: str, body: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `call_calendar`

### calendar_context

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/store_calendar.py:37](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/store_calendar.py#L37)

```python
calendar_context(gateway: Any, warehouse: int, store: str, day: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `call_calendar`

### set_exception

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/store_calendar.py:41](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/store_calendar.py#L41)

```python
set_exception(gateway: Any, operation: str, body: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `call_calendar`

### delivery_rule

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/store_calendar_rule.py:9](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/store_calendar_rule.py#L9)

```python
delivery_rule(cur: Any, warehouse: int, store: int, day: date) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.callproc`, `cur.var`, `proof.getvalue`, `read_oracle_json`

### assert_current_order_calendar

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/store_calendar_rule.py:17](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/store_calendar_rule.py#L17)

```python
assert_current_order_calendar(cur: Any, order: int) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LookupError`, `StoreOrderConflict`, `cur.execute`, `cur.fetchone`, `delivery_rule`

### rows

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/store_order_reads.py:7](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/store_order_reads.py#L7)

```python
rows(cur: Any) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `column[0].lower`, `cur.fetchall`, `dict`, `zip`

### list_store_orders

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/store_order_reads.py:12](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/store_order_reads.py#L12)

```python
list_store_orders(gateway: Any, warehouse: int | None, limit: int, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `actor_warehouse`, `assert_store_scope`, `cur.execute`, `gateway.transaction`, `rows`

### store_order_detail

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/store_order_reads.py:31](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/store_order_reads.py#L31)

```python
store_order_detail(gateway: Any, order: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LookupError`, `actor_warehouse`, `assert_store_scope`, `cur.execute`, `gateway.transaction`, `hasattr`, `read_admission`, `read_oracle_json`, `result.get`, `result['raw_xml'].read`, `rows`

### __init__

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/store_orders.py:14](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/store_orders.py#L14)

```python
__init__(self, gateway: OracleGateway) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### receive

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/store_orders.py:17](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/store_orders.py#L17)

```python
receive(self, raw: bytes, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreOrderConflict`, `assert_store_scope`, `cur.execute`, `cur.fetchone`, `cur.setinputsizes`, `datetime.fromisoformat`, `datetime.now`, `int`, `json.dumps`, `raw.decode`, `read_oracle_json`, `read_order`, `self._destination`, `self._lines`, `source_transaction`, `times.get`, `times['picking_finish'].isoformat`, `times['picking_start'].isoformat`, `times['shipment'].isoformat`

### _destination

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/store_orders.py:63](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/store_orders.py#L63)

```python
_destination(self, cur: oracledb.Cursor, data: dict, received: datetime) -> tuple
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(received + timedelta(minutes=settings[0])).date`, `ValueError`, `bool`, `calendar`, `cur.execute`, `cur.fetchall`, `cur.fetchone`, `datetime.fromisoformat`, `delivery_rule`, `int`, `len`, `proof.get`, `store[2].date`, `timedelta`

### _lines

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/store_orders.py:85](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/store_orders.py#L85)

```python
_lines(self, cur: oracledb.Cursor, order_id: int, data: dict, actor: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `ValueError`, `base.upper`, `convert_sap_source_quantity`, `cur.execute`, `cur.fetchall`, `int`, `len`, `read_oracle_json`

### configure

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/store_orders.py:99](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/store_orders.py#L99)

```python
configure(self, warehouse: int, store_code: str, body: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `configure_calendar`

### calendar_context

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/store_orders.py:103](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/store_orders.py#L103)

```python
calendar_context(self, warehouse: int, store_code: str, day: str, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `calendar_context`

### set_calendar_exception

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/store_orders.py:107](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/store_orders.py#L107)

```python
set_calendar_exception(self, operation: str, body: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `set_exception`

### list

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/store_orders.py:111](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/store_orders.py#L111)

```python
list(self, warehouse: int | None, limit: int, actor: str) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `list_store_orders`

### get

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/store_orders.py:115](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/store_orders.py#L115)

```python
get(self, order_id: int, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `store_order_detail`

### assert_store_scope

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/store_source_scope.py:7](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/store_source_scope.py#L7)

```python
assert_store_scope(cur: Any, actor: str, permission: str, warehouse: int) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `PermissionError`, `cur.callproc`, `getattr`

### actor_warehouse

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/store_source_scope.py:16](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/store_source_scope.py#L16)

```python
actor_warehouse(cur: Any, actor: str, permission: str) -> tuple[int | None, bool]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `PermissionError`, `cur.callproc`, `cur.var`, `getattr`, `global_admin.getvalue`, `own.getvalue`

### source_transaction

[Исходник: api/wms_api_server/app/modules/fulfillment/infrastructure/store_source_scope.py:29](../../../api/wms_api_server/app/modules/fulfillment/infrastructure/store_source_scope.py#L29)

```python
source_transaction(gateway: Any, label: str, actor: str, permission: str, warehouse: int | None=None, order: int | None=None) -> Iterator[Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LookupError`, `PermissionError`, `cur.callproc`, `cur.execute`, `cur.fetchone`, `gateway.transaction`, `getattr`

### build_store_order_service

[Исходник: api/wms_api_server/app/modules/fulfillment/public.py:8](../../../api/wms_api_server/app/modules/fulfillment/public.py#L8)

```python
build_store_order_service() -> StoreOrders
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `StoreOrders`

### build_preparation_service

[Исходник: api/wms_api_server/app/modules/fulfillment/public.py:12](../../../api/wms_api_server/app/modules/fulfillment/public.py#L12)

```python
build_preparation_service() -> LegacyPreparation
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LegacyPreparation`, `OracleGateway`

### build_execution_service

[Исходник: api/wms_api_server/app/modules/fulfillment/public.py:22](../../../api/wms_api_server/app/modules/fulfillment/public.py#L22)

```python
build_execution_service() -> OrderExecution
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `OrderExecution`

### build_store_admission_service

[Исходник: api/wms_api_server/app/modules/fulfillment/public.py:29](../../../api/wms_api_server/app/modules/fulfillment/public.py#L29)

```python
build_store_admission_service() -> StoreAdmission
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `StoreAdmission`

### build_fulfillment_read_service

[Исходник: api/wms_api_server/app/modules/fulfillment/public.py:37](../../../api/wms_api_server/app/modules/fulfillment/public.py#L37)

```python
build_fulfillment_read_service(gateway: Any | None=None) -> OrderFulfillmentRead
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `OrderFulfillmentRead`

### build_customer_order_read_service

[Исходник: api/wms_api_server/app/modules/fulfillment/public.py:47](../../../api/wms_api_server/app/modules/fulfillment/public.py#L47)

```python
build_customer_order_read_service(gateway: Any | None=None) -> CustomerOrderRead
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CustomerOrderRead`, `OracleGateway`

### build_prepared_layout

[Исходник: api/wms_api_server/app/modules/fulfillment/public.py:58](../../../api/wms_api_server/app/modules/fulfillment/public.py#L58)

```python
build_prepared_layout(gateway: Any, posting: Any) -> PreparedLayoutPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `PreparedLayout`
