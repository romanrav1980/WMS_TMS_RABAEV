# Методы: finance

### report

[Исходник: api/wms_api_server/app/modules/finance/api/day_reconciliation_routes.py:10](../../../api/wms_api_server/app/modules/finance/api/day_reconciliation_routes.py#L10)

```python
report(ware_id: int, business_date: date, timezone_region: str=Query(default='Asia/Tbilisi', min_length=1, max_length=64), user: AdminUser=Depends(require_permission('transport_dispatch_view')), service: DayReconciliationPort=Depends(day_reconciliation_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Query`, `require_permission`, `router.get`, `service.report`, `str`

### stock_conflicts

[Исходник: api/wms_api_server/app/modules/finance/api/day_reconciliation_routes.py:16](../../../api/wms_api_server/app/modules/finance/api/day_reconciliation_routes.py#L16)

```python
stock_conflicts(ware_id: int=Path(gt=0), metric: Literal['stock_quantity_invariants', 'physical_unit_composition']=Query(...), after: str | None=Query(None, max_length=2048), limit: int=Query(50, ge=1, le=100), user: AdminUser=Depends(require_permission('transport_dispatch_view')), service: DayReconciliationPort=Depends(day_reconciliation_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Path`, `Query`, `require_permission`, `router.get`, `service.stock_conflicts`, `str`

### context

[Исходник: api/wms_api_server/app/modules/finance/api/day_review_routes.py:22](../../../api/wms_api_server/app/modules/finance/api/day_review_routes.py#L22)

```python
context(ware_id: int, business_date: date, timezone_region: str=Query(min_length=1, max_length=64), user: AdminUser=Depends(require_permission('transport_dispatch_view')), service: DayReviewsPort=Depends(day_reviews_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Query`, `require_permission`, `router.get`, `service.context`, `str`

### record

[Исходник: api/wms_api_server/app/modules/finance/api/day_review_routes.py:29](../../../api/wms_api_server/app/modules/finance/api/day_review_routes.py#L29)

```python
record(body: ReviewBody, user: AdminUser=Depends(require_permission('transport_dispatch_edit')), service: DayReviewsPort=Depends(day_reviews_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `body.model_dump`, `require_permission`, `router.post`, `service.record`, `str`

### resolve

[Исходник: api/wms_api_server/app/modules/finance/api/day_review_routes.py:36](../../../api/wms_api_server/app/modules/finance/api/day_review_routes.py#L36)

```python
resolve(body: ReviewBody, user: AdminUser=Depends(require_permission('transport_dispatch_edit')), service: DayReviewsPort=Depends(day_reviews_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `body.model_dump`, `require_permission`, `router.post`, `service.resolve`, `str`

### history

[Исходник: api/wms_api_server/app/modules/finance/api/day_review_routes.py:43](../../../api/wms_api_server/app/modules/finance/api/day_review_routes.py#L43)

```python
history(ware_id: int, business_date: date, timezone_region: str=Query(min_length=1, max_length=64), after_version: int=Query(default=0, ge=0), limit: int=Query(default=20, ge=1, le=50), user: AdminUser=Depends(require_permission('transport_dispatch_view')), service: DayReviewsPort=Depends(day_reviews_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Query`, `require_permission`, `router.get`, `service.history`, `str`

### detail

[Исходник: api/wms_api_server/app/modules/finance/api/day_review_routes.py:51](../../../api/wms_api_server/app/modules/finance/api/day_review_routes.py#L51)

```python
detail(operation: str, user: AdminUser=Depends(require_permission('transport_dispatch_view')), service: DayReviewsPort=Depends(day_reviews_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.get`, `service.get`, `str`

### shipping_register

[Исходник: api/wms_api_server/app/modules/finance/api/day_review_routes.py:58](../../../api/wms_api_server/app/modules/finance/api/day_review_routes.py#L58)

```python
shipping_register(ware_id: int, business_date: date, after_id: int=Query(default=0, ge=0), limit: int=Query(default=20, ge=1, le=50), user: AdminUser=Depends(require_permission('transport_dispatch_view')), service: DayReviewsPort=Depends(day_reviews_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Query`, `require_permission`, `router.get`, `service.shipping_register`, `str`

### inspection

[Исходник: api/wms_api_server/app/modules/finance/api/day_review_routes.py:76](../../../api/wms_api_server/app/modules/finance/api/day_review_routes.py#L76)

```python
inspection(review_id: str, user: AdminUser=Depends(require_permission('transport_dispatch_view')), service: DayReviewsPort=Depends(day_reviews_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.get`, `service.inspection`, `str`

### inspect

[Исходник: api/wms_api_server/app/modules/finance/api/day_review_routes.py:83](../../../api/wms_api_server/app/modules/finance/api/day_review_routes.py#L83)

```python
inspect(body: InspectionBody, user: AdminUser=Depends(require_permission('transport_dispatch_view')), service: DayReviewsPort=Depends(day_reviews_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `body.model_dump`, `require_permission`, `router.post`, `service.inspect`, `str`

### resolve_inspection

[Исходник: api/wms_api_server/app/modules/finance/api/day_review_routes.py:90](../../../api/wms_api_server/app/modules/finance/api/day_review_routes.py#L90)

```python
resolve_inspection(body: InspectionBody, user: AdminUser=Depends(require_permission('transport_dispatch_view')), service: DayReviewsPort=Depends(day_reviews_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `body.model_dump`, `require_permission`, `router.post`, `service.resolve_inspection`, `str`

### allocate

[Исходник: api/wms_api_server/app/modules/finance/api/expense_allocation_routes.py:15](../../../api/wms_api_server/app/modules/finance/api/expense_allocation_routes.py#L15)

```python
allocate(body: Allocate, user: AdminUser=Depends(require_permission('calc_tt_price')), service: ExpenseAllocationPort=Depends(expense_allocation_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.post`, `service.allocate`, `str`

### invoice

[Исходник: api/wms_api_server/app/modules/finance/api/expense_allocation_routes.py:20](../../../api/wms_api_server/app/modules/finance/api/expense_allocation_routes.py#L20)

```python
invoice(invoice_id: int, user: AdminUser=Depends(require_permission('transport_dispatch_view')), service: ExpenseAllocationPort=Depends(expense_allocation_service)) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `require_permission`, `router.get`, `service.invoice`

### failure

[Исходник: api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py:38](../../../api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py#L38)

```python
failure(exc: LogisticsCostError, op: str | None=None) -> HTTPException
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `str`

### rate

[Исходник: api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py:42](../../../api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py#L42)

```python
rate(body: Rate, user: AdminUser=Depends(require_permission('create_tt_price')), service: LogisticsCostPort=Depends(logistics_cost_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `body.effective_from.isoformat`, `failure`, `require_permission`, `router.post`, `service.rate`

### monthly_rate

[Исходник: api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py:47](../../../api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py#L47)

```python
monthly_rate(body: MonthlyRate, user: AdminUser=Depends(require_permission('create_tt_price')), service: LogisticsCostPort=Depends(logistics_cost_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `failure`, `require_permission`, `router.post`, `service.monthly_rate`

### rates

[Исходник: api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py:52](../../../api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py#L52)

```python
rates(ware_id: int, user: AdminUser=Depends(require_permission('transport_dispatch_view')), service: LogisticsCostPort=Depends(logistics_cost_service)) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `failure`, `require_permission`, `router.get`, `service.rates`

### rate_history

[Исходник: api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py:57](../../../api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py#L57)

```python
rate_history(ware_id: int, currency: str=Query(pattern='^[A-Z]{3}$'), before_version: int=Query(default=0, ge=0), limit: int=Query(default=25, ge=1, le=100), user: AdminUser=Depends(require_permission('transport_dispatch_view')), service: LogisticsCostPort=Depends(logistics_cost_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Query`, `failure`, `require_permission`, `router.get`, `service.rate_history`

### calculate

[Исходник: api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py:62](../../../api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py#L62)

```python
calculate(body: Calculate, user: AdminUser=Depends(require_permission('calc_tt_price')), service: LogisticsCostPort=Depends(logistics_cost_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `failure`, `require_permission`, `router.post`, `service.calculate`

### trip

[Исходник: api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py:67](../../../api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py#L67)

```python
trip(trip_id: int, user: AdminUser=Depends(require_permission('transport_dispatch_view')), service: LogisticsCostPort=Depends(logistics_cost_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `failure`, `require_permission`, `router.get`, `service.trip`

### invoice

[Исходник: api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py:72](../../../api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py#L72)

```python
invoice(invoice_id: int, user: AdminUser=Depends(require_permission('transport_dispatch_view')), service: LogisticsCostPort=Depends(logistics_cost_service)) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `failure`, `require_permission`, `router.get`, `service.invoice`

### assembly_period

[Исходник: api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py:78](../../../api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py#L78)

```python
assembly_period(trip_id: int, warehouse_id: int=Query(gt=0), timezone_region: str=Query(min_length=1, max_length=64, pattern='^[A-Za-z0-9_/+:-]+$'), user: AdminUser=Depends(require_permission('transport_dispatch_view')), service: LogisticsCostPort=Depends(logistics_cost_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Query`, `failure`, `require_permission`, `router.get`, `service.assembly_period`

### period_policy

[Исходник: api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py:93](../../../api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py#L93)

```python
period_policy(ware_id: int, user: AdminUser=Depends(require_permission('transport_dispatch_view')), service: LogisticsCostPort=Depends(logistics_cost_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `failure`, `require_permission`, `router.get`, `service.period_policy`

### configure_period

[Исходник: api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py:98](../../../api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py#L98)

```python
configure_period(ware_id: int, body: PeriodPolicy, user: AdminUser=Depends(require_permission('create_tt_price')), service: LogisticsCostPort=Depends(logistics_cost_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `failure`, `require_permission`, `router.post`, `service.configure_period`

### invoice_summary

[Исходник: api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py:103](../../../api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py#L103)

```python
invoice_summary(invoice_id: int, user: AdminUser=Depends(require_permission('transport_dispatch_view')), service: LogisticsCostPort=Depends(logistics_cost_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `failure`, `require_permission`, `router.get`, `service.invoice_summary`

### transport_tariff_sources

[Исходник: api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py:108](../../../api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py#L108)

```python
transport_tariff_sources(trip_id: int, warehouse_id: int=Query(gt=0), user: AdminUser=Depends(require_permission('transport_dispatch_view')), service: LogisticsCostPort=Depends(logistics_cost_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Query`, `failure`, `require_permission`, `router.get`, `service.transport_tariff_sources`

### publish_transport_norm

[Исходник: api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py:135](../../../api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py#L135)

```python
publish_transport_norm(body: TransportNorm, user: AdminUser=Depends(require_permission('create_tt_price')), service: LogisticsCostPort=Depends(logistics_cost_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `body.model_dump`, `failure`, `require_permission`, `router.post`, `service.publish_transport_norm`

### transport_norm_history

[Исходник: api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py:142](../../../api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py#L142)

```python
transport_norm_history(ware_id: int, source_price_id: int, before_version: int | None=Query(default=None, gt=0), limit: int=Query(default=30, ge=1, le=100), user: AdminUser=Depends(require_permission('transport_dispatch_view')), service: LogisticsCostPort=Depends(logistics_cost_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Query`, `failure`, `require_permission`, `router.get`, `service.transport_norm_history`

### transport_cost_facts

[Исходник: api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py:151](../../../api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py#L151)

```python
transport_cost_facts(trip_id: int, warehouse_id: int=Query(gt=0), user: AdminUser=Depends(require_permission('transport_dispatch_view')), service: LogisticsCostPort=Depends(logistics_cost_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Query`, `failure`, `require_permission`, `router.get`, `service.transport_facts`

### transport_cost_preview

[Исходник: api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py:160](../../../api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py#L160)

```python
transport_cost_preview(trip_id: int, warehouse_id: int=Query(gt=0), source_price_id: int=Query(gt=0), user: AdminUser=Depends(require_permission('transport_dispatch_view')), service: LogisticsCostPort=Depends(logistics_cost_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Query`, `failure`, `require_permission`, `router.get`, `service.transport_cost_preview`

### conduct_transport_cost

[Исходник: api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py:178](../../../api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py#L178)

```python
conduct_transport_cost(body: TransportCostConduct, user: AdminUser=Depends(require_permission('calc_tt_price')), service: LogisticsCostPort=Depends(logistics_cost_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `body.model_dump`, `failure`, `require_permission`, `router.post`, `service.conduct_transport_cost`

### transport_costs

[Исходник: api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py:186](../../../api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py#L186)

```python
transport_costs(trip_id: int, warehouse_id: int=Query(gt=0), user: AdminUser=Depends(require_permission('transport_dispatch_view')), service: LogisticsCostPort=Depends(logistics_cost_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Query`, `failure`, `require_permission`, `router.get`, `service.transport_costs`

### invoice_transport_costs

[Исходник: api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py:195](../../../api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py#L195)

```python
invoice_transport_costs(invoice_id: int, user: AdminUser=Depends(require_permission('transport_dispatch_view')), service: LogisticsCostPort=Depends(logistics_cost_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `failure`, `require_permission`, `router.get`, `service.invoice_transport_costs`

### failure

[Исходник: api/wms_api_server/app/modules/finance/api/logistics_expense_routes.py:45](../../../api/wms_api_server/app/modules/finance/api/logistics_expense_routes.py#L45)

```python
failure(exc: LogisticsCostError, op: str | None=None) -> HTTPException
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `str`

### articles

[Исходник: api/wms_api_server/app/modules/finance/api/logistics_expense_routes.py:49](../../../api/wms_api_server/app/modules/finance/api/logistics_expense_routes.py#L49)

```python
articles(user: AdminUser=Depends(require_permission('transport_dispatch_view')), service: LogisticsExpensePort=Depends(logistics_expense_service)) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `require_permission`, `router.get`, `service.articles`

### article

[Исходник: api/wms_api_server/app/modules/finance/api/logistics_expense_routes.py:53](../../../api/wms_api_server/app/modules/finance/api/logistics_expense_routes.py#L53)

```python
article(body: Article, user: AdminUser=Depends(require_permission('create_tt_price')), service: LogisticsExpensePort=Depends(logistics_expense_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `failure`, `require_permission`, `router.post`, `service.article`

### report

[Исходник: api/wms_api_server/app/modules/finance/api/logistics_expense_routes.py:58](../../../api/wms_api_server/app/modules/finance/api/logistics_expense_routes.py#L58)

```python
report(body: Report, user: AdminUser=Depends(require_permission('edit_bill_tt')), service: LogisticsExpensePort=Depends(logistics_expense_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `body.expense_date.isoformat`, `failure`, `require_permission`, `router.post`, `service.report`

### decide

[Исходник: api/wms_api_server/app/modules/finance/api/logistics_expense_routes.py:63](../../../api/wms_api_server/app/modules/finance/api/logistics_expense_routes.py#L63)

```python
decide(body: Decision, user: AdminUser=Depends(require_permission('transport_dispatch_view')), service: LogisticsExpensePort=Depends(logistics_expense_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `failure`, `require_permission`, `router.post`, `service.decide`

### pending

[Исходник: api/wms_api_server/app/modules/finance/api/logistics_expense_routes.py:68](../../../api/wms_api_server/app/modules/finance/api/logistics_expense_routes.py#L68)

```python
pending(ware_id: int, operation_id: str | None=Query(default=None, min_length=1, max_length=100), user: AdminUser=Depends(require_permission('transport_dispatch_view')), service: LogisticsExpensePort=Depends(logistics_expense_service)) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Query`, `failure`, `require_permission`, `router.get`, `service.pending`

### normative_cost_sources

[Исходник: api/wms_api_server/app/modules/finance/api/logistics_expense_routes.py:74](../../../api/wms_api_server/app/modules/finance/api/logistics_expense_routes.py#L74)

```python
normative_cost_sources(ware_id: int, cost_operation_id: str | None=Query(default=None, min_length=1, max_length=100), user: AdminUser=Depends(require_permission('transport_dispatch_view')), service: LogisticsExpensePort=Depends(logistics_expense_service)) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Query`, `failure`, `require_permission`, `router.get`, `service.normative_cost_sources`

### logistics_cost_service

[Исходник: api/wms_api_server/app/modules/finance/contracts.py:29](../../../api/wms_api_server/app/modules/finance/contracts.py#L29)

```python
logistics_cost_service() -> LogisticsCostPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### __init__

[Исходник: api/wms_api_server/app/modules/finance/contracts.py:4](../../../api/wms_api_server/app/modules/finance/contracts.py#L4)

```python
__init__(self, code: str, message: str, status: int=409) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `super`, `super().__init__`

### publish_transport_norm

[Исходник: api/wms_api_server/app/modules/finance/contracts.py:9](../../../api/wms_api_server/app/modules/finance/contracts.py#L9)

```python
publish_transport_norm(self, body: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### transport_norm_history

[Исходник: api/wms_api_server/app/modules/finance/contracts.py:10](../../../api/wms_api_server/app/modules/finance/contracts.py#L10)

```python
transport_norm_history(self, ware: int, price_id: int, before: int | None, limit: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### rate

[Исходник: api/wms_api_server/app/modules/finance/contracts.py:11](../../../api/wms_api_server/app/modules/finance/contracts.py#L11)

```python
rate(self, ware: int, currency: str, value: str, effective: str, version: int, reason: str, reference: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### monthly_rate

[Исходник: api/wms_api_server/app/modules/finance/contracts.py:12](../../../api/wms_api_server/app/modules/finance/contracts.py#L12)

```python
monthly_rate(self, ware: int, currency: str, month: str, picking: str, common: str, boxes: str, version: int, reason: str, reference: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### calculate

[Исходник: api/wms_api_server/app/modules/finance/contracts.py:13](../../../api/wms_api_server/app/modules/finance/contracts.py#L13)

```python
calculate(self, op: str, trip: int, ware: int, currency: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### rate_history

[Исходник: api/wms_api_server/app/modules/finance/contracts.py:14](../../../api/wms_api_server/app/modules/finance/contracts.py#L14)

```python
rate_history(self, ware: int, currency: str, before: int, limit: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### assembly_period

[Исходник: api/wms_api_server/app/modules/finance/contracts.py:15](../../../api/wms_api_server/app/modules/finance/contracts.py#L15)

```python
assembly_period(self, trip: int, ware: int, region: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### period_policy

[Исходник: api/wms_api_server/app/modules/finance/contracts.py:16](../../../api/wms_api_server/app/modules/finance/contracts.py#L16)

```python
period_policy(self, ware: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### configure_period

[Исходник: api/wms_api_server/app/modules/finance/contracts.py:17](../../../api/wms_api_server/app/modules/finance/contracts.py#L17)

```python
configure_period(self, op: str, ware: int, mode: str, region: str | None, version: int, reason: str, reference: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### rates

[Исходник: api/wms_api_server/app/modules/finance/contracts.py:18](../../../api/wms_api_server/app/modules/finance/contracts.py#L18)

```python
rates(self, ware: int, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### trip

[Исходник: api/wms_api_server/app/modules/finance/contracts.py:19](../../../api/wms_api_server/app/modules/finance/contracts.py#L19)

```python
trip(self, trip: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### invoice

[Исходник: api/wms_api_server/app/modules/finance/contracts.py:20](../../../api/wms_api_server/app/modules/finance/contracts.py#L20)

```python
invoice(self, invoice: int, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### invoice_transport_costs

[Исходник: api/wms_api_server/app/modules/finance/contracts.py:21](../../../api/wms_api_server/app/modules/finance/contracts.py#L21)

```python
invoice_transport_costs(self, invoice: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### transport_costs

[Исходник: api/wms_api_server/app/modules/finance/contracts.py:22](../../../api/wms_api_server/app/modules/finance/contracts.py#L22)

```python
transport_costs(self, trip: int, ware: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### conduct_transport_cost

[Исходник: api/wms_api_server/app/modules/finance/contracts.py:23](../../../api/wms_api_server/app/modules/finance/contracts.py#L23)

```python
conduct_transport_cost(self, body: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### transport_cost_preview

[Исходник: api/wms_api_server/app/modules/finance/contracts.py:24](../../../api/wms_api_server/app/modules/finance/contracts.py#L24)

```python
transport_cost_preview(self, trip: int, ware: int, price_id: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### transport_facts

[Исходник: api/wms_api_server/app/modules/finance/contracts.py:25](../../../api/wms_api_server/app/modules/finance/contracts.py#L25)

```python
transport_facts(self, trip: int, ware: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### transport_tariff_sources

[Исходник: api/wms_api_server/app/modules/finance/contracts.py:26](../../../api/wms_api_server/app/modules/finance/contracts.py#L26)

```python
transport_tariff_sources(self, trip: int, ware: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### invoice_summary

[Исходник: api/wms_api_server/app/modules/finance/contracts.py:27](../../../api/wms_api_server/app/modules/finance/contracts.py#L27)

```python
invoice_summary(self, invoice: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### expense_allocation_service

[Исходник: api/wms_api_server/app/modules/finance/contracts_allocation.py:7](../../../api/wms_api_server/app/modules/finance/contracts_allocation.py#L7)

```python
expense_allocation_service() -> ExpenseAllocationPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### allocate

[Исходник: api/wms_api_server/app/modules/finance/contracts_allocation.py:4](../../../api/wms_api_server/app/modules/finance/contracts_allocation.py#L4)

```python
allocate(self, operation_id: str, expense_id: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### invoice

[Исходник: api/wms_api_server/app/modules/finance/contracts_allocation.py:5](../../../api/wms_api_server/app/modules/finance/contracts_allocation.py#L5)

```python
invoice(self, invoice_id: int, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### day_reviews_service

[Исходник: api/wms_api_server/app/modules/finance/contracts_day_reviews.py:15](../../../api/wms_api_server/app/modules/finance/contracts_day_reviews.py#L15)

```python
day_reviews_service() -> DayReviewsPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### resolve_inspection

[Исходник: api/wms_api_server/app/modules/finance/contracts_day_reviews.py:5](../../../api/wms_api_server/app/modules/finance/contracts_day_reviews.py#L5)

```python
resolve_inspection(self, operation: str, body: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### inspection

[Исходник: api/wms_api_server/app/modules/finance/contracts_day_reviews.py:6](../../../api/wms_api_server/app/modules/finance/contracts_day_reviews.py#L6)

```python
inspection(self, review: str, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### inspect

[Исходник: api/wms_api_server/app/modules/finance/contracts_day_reviews.py:7](../../../api/wms_api_server/app/modules/finance/contracts_day_reviews.py#L7)

```python
inspect(self, operation: str, body: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### shipping_register

[Исходник: api/wms_api_server/app/modules/finance/contracts_day_reviews.py:8](../../../api/wms_api_server/app/modules/finance/contracts_day_reviews.py#L8)

```python
shipping_register(self, ware: int, day: date, after: int, limit: int, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### history

[Исходник: api/wms_api_server/app/modules/finance/contracts_day_reviews.py:9](../../../api/wms_api_server/app/modules/finance/contracts_day_reviews.py#L9)

```python
history(self, ware: int, day: date, region: str, after: int, limit: int, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### get

[Исходник: api/wms_api_server/app/modules/finance/contracts_day_reviews.py:10](../../../api/wms_api_server/app/modules/finance/contracts_day_reviews.py#L10)

```python
get(self, operation: str, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### context

[Исходник: api/wms_api_server/app/modules/finance/contracts_day_reviews.py:11](../../../api/wms_api_server/app/modules/finance/contracts_day_reviews.py#L11)

```python
context(self, ware: int, day: date, region: str, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### resolve

[Исходник: api/wms_api_server/app/modules/finance/contracts_day_reviews.py:12](../../../api/wms_api_server/app/modules/finance/contracts_day_reviews.py#L12)

```python
resolve(self, operation: str, body: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### record

[Исходник: api/wms_api_server/app/modules/finance/contracts_day_reviews.py:13](../../../api/wms_api_server/app/modules/finance/contracts_day_reviews.py#L13)

```python
record(self, operation: str, body: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### logistics_expense_service

[Исходник: api/wms_api_server/app/modules/finance/contracts_expenses.py:11](../../../api/wms_api_server/app/modules/finance/contracts_expenses.py#L11)

```python
logistics_expense_service() -> LogisticsExpensePort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### article

[Исходник: api/wms_api_server/app/modules/finance/contracts_expenses.py:4](../../../api/wms_api_server/app/modules/finance/contracts_expenses.py#L4)

```python
article(self, code: str, name: str, scope: str, included: bool, active: bool, version: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### normative_cost_sources

[Исходник: api/wms_api_server/app/modules/finance/contracts_expenses.py:5](../../../api/wms_api_server/app/modules/finance/contracts_expenses.py#L5)

```python
normative_cost_sources(self, ware: int, actor: str, cost_operation_id: str | None=None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### articles

[Исходник: api/wms_api_server/app/modules/finance/contracts_expenses.py:6](../../../api/wms_api_server/app/modules/finance/contracts_expenses.py#L6)

```python
articles(self) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### report

[Исходник: api/wms_api_server/app/modules/finance/contracts_expenses.py:7](../../../api/wms_api_server/app/modules/finance/contracts_expenses.py#L7)

```python
report(self, op: str, ware: int, code: str, kind: str, object_id: int, amount: str, currency: str, day: str, reference: str, reason: str, actor: str, correction: str | None=None, expected: str | None=None, cost_correction: str | None=None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### decide

[Исходник: api/wms_api_server/app/modules/finance/contracts_expenses.py:8](../../../api/wms_api_server/app/modules/finance/contracts_expenses.py#L8)

```python
decide(self, op: str, expense: str, phase: str, outcome: str, basis: str, reference: str, reason: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### pending

[Исходник: api/wms_api_server/app/modules/finance/contracts_expenses.py:9](../../../api/wms_api_server/app/modules/finance/contracts_expenses.py#L9)

```python
pending(self, ware: int, actor: str, operation_id: str | None=None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### day_reconciliation_service

[Исходник: api/wms_api_server/app/modules/finance/contracts_reconciliation.py:8](../../../api/wms_api_server/app/modules/finance/contracts_reconciliation.py#L8)

```python
day_reconciliation_service() -> DayReconciliationPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### stock_conflicts

[Исходник: api/wms_api_server/app/modules/finance/contracts_reconciliation.py:5](../../../api/wms_api_server/app/modules/finance/contracts_reconciliation.py#L5)

```python
stock_conflicts(self, ware: int, metric: str, after: str | None, limit: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### report

[Исходник: api/wms_api_server/app/modules/finance/contracts_reconciliation.py:6](../../../api/wms_api_server/app/modules/finance/contracts_reconciliation.py#L6)

```python
report(self, ware: int, day: date, region: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### allocate_cents

[Исходник: api/wms_api_server/app/modules/finance/domain/allocation.py:3](../../../api/wms_api_server/app/modules/finance/domain/allocation.py#L3)

```python
allocate_cents(amount: Decimal, weights: list[tuple[str, Decimal]]) -> dict[str, Decimal]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `ValueError`, `amount.quantize`, `any`, `floors.values`, `int`, `len`, `localcontext`, `shares.items`, `sorted`, `sum`, `value.quantize`, `weight.is_finite`

### rate_value

[Исходник: api/wms_api_server/app/modules/finance/domain/amount.py:3](../../../api/wms_api_server/app/modules/finance/domain/amount.py#L3)

```python
rate_value(value: str) -> Decimal
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `ValueError`, `amount.as_tuple`, `amount.is_finite`

### cost_amount

[Исходник: api/wms_api_server/app/modules/finance/domain/amount.py:10](../../../api/wms_api_server/app/modules/finance/domain/amount.py#L10)

```python
cost_amount(quantity: int, value: Decimal) -> Decimal
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(quantity * value).quantize`, `Decimal`

### recognized_cost_summary

[Исходник: api/wms_api_server/app/modules/finance/domain/cost_summary.py:6](../../../api/wms_api_server/app/modules/finance/domain/cost_summary.py#L6)

```python
recognized_cost_summary(lines: list[dict[str, Any]]) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `ValueError`, `amount.is_finite`, `amount.quantize`, `format`, `group['trips'].add`, `groups[key].update`, `len`, `localcontext`, `quantity.is_finite`, `result.append`, `row.get`, `seen.add`, `set`, `sorted`, `str`, `totals.get`, `totals.items`, `tuple`

### canonical

[Исходник: api/wms_api_server/app/modules/finance/domain/day_review_material.py:6](../../../api/wms_api_server/app/modules/finance/domain/day_review_material.py#L6)

```python
canonical(value: dict) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `json.dumps`

### material

[Исходник: api/wms_api_server/app/modules/finance/domain/day_review_material.py:9](../../../api/wms_api_server/app/modules/finance/domain/day_review_material.py#L9)

```python
material(report: dict) -> tuple[str, str, datetime]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `canonical`, `datetime.fromisoformat`, `dict`, `raw.encode`, `sha256`, `sha256(raw.encode('utf-8')).hexdigest`, `value.pop`

### day_window

[Исходник: api/wms_api_server/app/modules/finance/domain/day_window.py:3](../../../api/wms_api_server/app/modules/finance/domain/day_window.py#L3)

```python
day_window(day: date) -> tuple[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(day + timedelta(days=1)).isoformat`, `day.isoformat`, `timedelta`

### signed_amount

[Исходник: api/wms_api_server/app/modules/finance/domain/expense_value.py:4](../../../api/wms_api_server/app/modules/finance/domain/expense_value.py#L4)

```python
signed_amount(value: str, correction: bool) -> Decimal
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `ValueError`, `abs`, `amount.is_finite`, `amount.quantize`, `rate_value`, `str`

### monthly_components

[Исходник: api/wms_api_server/app/modules/finance/domain/monthly_rate.py:7](../../../api/wms_api_server/app/modules/finance/domain/monthly_rate.py#L7)

```python
monthly_components(month: str, picking: str, common: str, boxes: str) -> dict[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(total / count).quantize`, `Decimal`, `ValueError`, `canonical`, `count.is_finite`, `count.to_integral_value`, `date.fromisoformat`, `first.strftime`, `format`, `localcontext`, `rate_value`, `total.as_tuple`, `value.normalize`

### canonical

[Исходник: api/wms_api_server/app/modules/finance/domain/monthly_rate.py:22](../../../api/wms_api_server/app/modules/finance/domain/monthly_rate.py#L22)

```python
canonical(value: Decimal) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `format`, `value.normalize`

### physical_box_count

[Исходник: api/wms_api_server/app/modules/finance/domain/physical_boxes.py:5](../../../api/wms_api_server/app/modules/finance/domain/physical_boxes.py#L5)

```python
physical_box_count(tree: dict, proofs: list[dict]) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `ValueError`, `actual.keys`, `expected.items`, `expected.keys`, `len`, `node.get`, `str`, `tree.get`

### read_assembly_period

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/assembly_period.py:10](../../../api/wms_api_server/app/modules/finance/infrastructure/assembly_period.py#L10)

```python
read_assembly_period(gateway: Any, trip: int, ware: int, region: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LogisticsCostError`, `all`, `bool`, `box_assembly_clocks`, `cursor.execute`, `cursor.fetchall`, `cursor.fetchone`, `gateway.transaction`, `getattr`, `len`, `line.get`, `lines.append`, `n.get`, `read_oracle_json`, `require_warehouse`, `sorted`, `tree.get`

### box_assembly_clocks

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/box_assembly_clocks.py:8](../../../api/wms_api_server/app/modules/finance/infrastructure/box_assembly_clocks.py#L8)

```python
box_assembly_clocks(cursor: Any, tree: dict[str, Any], ware: int, region: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cursor.execute`, `cursor.fetchone`, `cursor.setinputsizes`, `json.dumps`, `read_oracle_json`

### calculate_box_cost

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/box_costs.py:13](../../../api/wms_api_server/app/modules/finance/infrastructure/box_costs.py#L13)

```python
calculate_box_cost(gateway: Any, op: str, trip: int, ware: int, currency: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `LogisticsCostError`, `cur.execute`, `cur.fetchall`, `cur.fetchone`, `cur.setinputsizes`, `current_policy`, `dict`, `enqueue`, `gateway.transaction`, `getattr`, `int`, `json.dumps`, `json.dumps([trip, ware, currency, actor], separators=(',', ':')).encode`, `len`, `lines.extend`, `load_period_lines`, `physical_box_count`, `read_oracle_json`, `require_warehouse`, `sha256`, `sha256(json.dumps([trip, ware, currency, actor], separators=(',', ':')).encode()).digest`, `sorted`, `str`, `str(exc.args[0]).split`, `sum`, `x[0].lower`, `zip`

### set_box_rate

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/box_rates.py:10](../../../api/wms_api_server/app/modules/finance/infrastructure/box_rates.py#L10)

```python
set_box_rate(gateway: Any, ware: int, currency: str, value: str, effective: str, version: int, reason: str, reference: str, actor: str, *, components: dict[str, str] | None=None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `LogisticsCostError`, `cur.execute`, `cur.fetchone`, `cur.setinputsizes`, `f'{ware}:WAREHOUSE_PICKING:{currency}'.encode`, `gateway.transaction`, `getattr`, `json.dumps`, `rate_value`, `read_oracle_json`, `require_warehouse`, `result`, `sha256`, `sha256(f'{ware}:WAREHOUSE_PICKING:{currency}'.encode()).hexdigest`, `str`, `str(exc.args[0]).split`

### result

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/box_rates.py:13](../../../api/wms_api_server/app/modules/finance/infrastructure/box_rates.py#L13)

```python
result() -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `str`

### require_warehouse

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/cost_access.py:4](../../../api/wms_api_server/app/modules/finance/infrastructure/cost_access.py#L4)

```python
require_warehouse(cursor: Any, ware: int, actor: str, permission: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LogisticsCostError`, `cursor.execute`, `cursor.fetchone`

### load_period_lines

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/cost_period_lines.py:10](../../../api/wms_api_server/app/modules/finance/infrastructure/cost_period_lines.py#L10)

```python
load_period_lines(cursor: Any, tree: dict[str, Any], boxes: int, load: str, loaded_day: str, ware: int, currency: str, policy: dict[str, Any]) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Counter`, `Decimal`, `LogisticsCostError`, `any`, `box_assembly_clocks`, `cost_amount`, `counts.items`, `cursor.execute`, `cursor.fetchone`, `int`, `len`, `lines.append`, `sorted`, `str`

### __init__

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/day_inspections.py:12](../../../api/wms_api_server/app/modules/finance/infrastructure/day_inspections.py#L12)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### get

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/day_inspections.py:15](../../../api/wms_api_server/app/modules/finance/infrastructure/day_inspections.py#L15)

```python
get(self, review: str, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LogisticsCostError`, `all`, `cur.execute`, `cur.fetchone`, `len`, `read_oracle_json`, `report.get`, `report.get('shipping_register', {}).get`, `require_warehouse`, `self.gateway.transaction`

### resolve

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/day_inspections.py:34](../../../api/wms_api_server/app/modules/finance/infrastructure/day_inspections.py#L34)

```python
resolve(self, operation: str, body: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LogisticsCostError`, `canonical`, `cur.callproc`, `cur.var`, `getattr`, `read_oracle_json`, `result.getvalue`, `self.gateway.transaction`, `str`, `str(exc.args[0]).split`

### record

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/day_inspections.py:46](../../../api/wms_api_server/app/modules/finance/infrastructure/day_inspections.py#L46)

```python
record(self, operation: str, body: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `DayReconciliation`, `DayReconciliation(self.gateway).report`, `LogisticsCostError`, `business_day.date`, `canonical`, `captured.isoformat`, `cur.callproc`, `cur.execute`, `cur.fetchone`, `cur.var`, `getattr`, `hasattr`, `material`, `read_oracle_json`, `result.getvalue`, `self.gateway.transaction`, `str`, `str(exc.args[0]).split`

### __init__

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/day_reconciliation.py:17](../../../api/wms_api_server/app/modules/finance/infrastructure/day_reconciliation.py#L17)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### stock_conflicts

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/day_reconciliation.py:20](../../../api/wms_api_server/app/modules/finance/infrastructure/day_reconciliation.py#L20)

```python
stock_conflicts(self, ware: int, metric: str, after: str | None, limit: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `stock_conflict_page`

### report

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/day_reconciliation.py:24](../../../api/wms_api_server/app/modules/finance/infrastructure/day_reconciliation.py#L24)

```python
report(self, ware: int, day: date, region: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LogisticsCostError`, `backlog.items`, `backlog_documents`, `blockers.append`, `cur.execute`, `cur.fetchone`, `cur.setinputsizes`, `daily_counts`, `datetime.now`, `datetime.now(timezone.utc).isoformat`, `day.isoformat`, `day_window`, `end.isoformat`, `erp_snapshot`, `external.update`, `external_documents`, `getattr`, `int`, `item.setdefault`, `raw_end.replace`, `raw_start.replace`, `read_snapshot`, `regulatory_snapshot`, `require_warehouse`, `self.gateway.transaction`, `start.isoformat`, `stock_documents`, `stock_snapshot`, `sum`, `task_time_coverage`

### history

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/day_review_history.py:8](../../../api/wms_api_server/app/modules/finance/infrastructure/day_review_history.py#L8)

```python
history(gateway: Any, ware: int, day: date, region: str, after: int, limit: int, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LogisticsCostError`, `cur.execute`, `cur.fetchall`, `day.isoformat`, `dict`, `gateway.transaction`, `len`, `require_warehouse`, `zip`

### detail

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/day_review_history.py:22](../../../api/wms_api_server/app/modules/finance/infrastructure/day_review_history.py#L22)

```python
detail(gateway: Any, operation: str, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LogisticsCostError`, `cur.execute`, `cur.fetchone`, `gateway.transaction`, `read_oracle_json`, `require_warehouse`

### __init__

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/day_reviews.py:12](../../../api/wms_api_server/app/modules/finance/infrastructure/day_reviews.py#L12)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `DayReconciliation`

### resolve_inspection

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/day_reviews.py:16](../../../api/wms_api_server/app/modules/finance/infrastructure/day_reviews.py#L16)

```python
resolve_inspection(self, operation: str, body: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `DayInspections`, `DayInspections(self.gateway).resolve`

### inspection

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/day_reviews.py:20](../../../api/wms_api_server/app/modules/finance/infrastructure/day_reviews.py#L20)

```python
inspection(self, review: str, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `DayInspections`, `DayInspections(self.gateway).get`

### inspect

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/day_reviews.py:24](../../../api/wms_api_server/app/modules/finance/infrastructure/day_reviews.py#L24)

```python
inspect(self, operation: str, body: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `DayInspections`, `DayInspections(self.gateway).record`

### shipping_register

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/day_reviews.py:28](../../../api/wms_api_server/app/modules/finance/infrastructure/day_reviews.py#L28)

```python
shipping_register(self, ware: int, day: date, after: int, limit: int, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `report`

### history

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/day_reviews.py:32](../../../api/wms_api_server/app/modules/finance/infrastructure/day_reviews.py#L32)

```python
history(self, ware: int, day: date, region: str, after: int, limit: int, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `history`

### get

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/day_reviews.py:36](../../../api/wms_api_server/app/modules/finance/infrastructure/day_reviews.py#L36)

```python
get(self, operation: str, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `detail`

### context

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/day_reviews.py:40](../../../api/wms_api_server/app/modules/finance/infrastructure/day_reviews.py#L40)

```python
context(self, ware: int, day: date, region: str, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.callproc`, `cur.execute`, `cur.var`, `material`, `read_oracle_json`, `require_warehouse`, `result.getvalue`, `self.gateway.transaction`, `self.reconciliation.report`

### resolve

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/day_reviews.py:51](../../../api/wms_api_server/app/modules/finance/infrastructure/day_reviews.py#L51)

```python
resolve(self, operation: str, body: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LogisticsCostError`, `canonical`, `cur.callproc`, `cur.var`, `getattr`, `payload.setvalue`, `read_oracle_json`, `require_warehouse`, `result.getvalue`, `self.gateway.transaction`, `str`

### record

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/day_reviews.py:65](../../../api/wms_api_server/app/modules/finance/infrastructure/day_reviews.py#L65)

```python
record(self, operation: str, body: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LogisticsCostError`, `canonical`, `capture.setvalue`, `cur.callproc`, `cur.var`, `date.fromisoformat`, `getattr`, `material`, `payload.setvalue`, `read_oracle_json`, `require_warehouse`, `result.getvalue`, `self.gateway.transaction`, `self.reconciliation.report`, `str`

### __init__

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/expense_allocation.py:13](../../../api/wms_api_server/app/modules/finance/infrastructure/expense_allocation.py#L13)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### allocate

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/expense_allocation.py:16](../../../api/wms_api_server/app/modules/finance/infrastructure/expense_allocation.py#L16)

```python
allocate(self, operation_id: str, expense_id: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LogisticsCostError`, `getattr`, `self._allocate`, `str`, `str(exc.args[0]).split`

### _allocate

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/expense_allocation.py:26](../../../api/wms_api_server/app/modules/finance/infrastructure/expense_allocation.py#L26)

```python
_allocate(self, op: str, expense: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `LogisticsCostError`, `actual_goods`, `allocate_cents`, `cur.execute`, `cur.fetchone`, `cur.setinputsizes`, `enqueue`, `format`, `int`, `json.dumps`, `json.dumps([expense, actor], separators=(',', ':')).encode`, `read_oracle_json`, `require_warehouse`, `self.gateway.transaction`, `sha256`, `sha256(json.dumps([expense, actor], separators=(',', ':')).encode()).digest`, `str`

### invoice

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/expense_allocation.py:54](../../../api/wms_api_server/app/modules/finance/infrastructure/expense_allocation.py#L54)

```python
invoice(self, invoice_id: int, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `invoice_expenses`

### invoice_expenses

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/expense_basis_read.py:23](../../../api/wms_api_server/app/modules/finance/infrastructure/expense_basis_read.py#L23)

```python
invoice_expenses(gateway: Any, invoice_id: int, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `gateway.fetch_all`

### missing_leaf_weight

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/expense_box_weight.py:5](../../../api/wms_api_server/app/modules/finance/infrastructure/expense_box_weight.py#L5)

```python
missing_leaf_weight(node: dict[str, Any], tree: dict[str, Any], proofs: dict[str, Decimal]) -> tuple[Decimal, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `LogisticsCostError`, `any`, `children.get`, `children.setdefault`, `children.setdefault(link['parent'], []).append`, `descendants.append`, `len`, `n.get`, `net.is_finite`, `nodes[box].get`, `nodes[current].get`, `seen.add`, `set`, `stack.extend`, `stack.pop`, `sum`, `tree.get`

### set_article

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/expense_catalog.py:5](../../../api/wms_api_server/app/modules/finance/infrastructure/expense_catalog.py#L5)

```python
set_article(gateway: Any, code: str, name: str, scope: str, included: bool, active: bool, version: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LogisticsCostError`, `cur.execute`, `cur.fetchone`, `gateway.transaction`, `int`

### confirmed_total

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/expense_correction.py:5](../../../api/wms_api_server/app/modules/finance/infrastructure/expense_correction.py#L5)

```python
confirmed_total(cursor: Any, expense: str) -> Decimal
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `LogisticsCostError`, `cursor.execute`, `cursor.fetchone`

### correction_source

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/expense_correction.py:14](../../../api/wms_api_server/app/modules/finance/infrastructure/expense_correction.py#L14)

```python
correction_source(cursor: Any, expense: str, expected: Decimal, delta: Decimal, ware: int, code: str, kind: str, object_id: int, currency: str) -> tuple[str, int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LogisticsCostError`, `confirmed_total`, `cursor.execute`, `cursor.fetchone`, `int`

### lock_correction_root

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/expense_correction.py:24](../../../api/wms_api_server/app/modules/finance/infrastructure/expense_correction.py#L24)

```python
lock_correction_root(cursor: Any, expense: str) -> str | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cursor.execute`, `cursor.fetchone`

### assert_correction_decision

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/expense_correction.py:31](../../../api/wms_api_server/app/modules/finance/infrastructure/expense_correction.py#L31)

```python
assert_correction_decision(cursor: Any, expense: str, root: str, phase: str, outcome: str, basis: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `LogisticsCostError`, `confirmed_total`, `cursor.execute`, `cursor.fetchone`

### decide_expense

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/expense_decisions.py:10](../../../api/wms_api_server/app/modules/finance/infrastructure/expense_decisions.py#L10)

```python
decide_expense(gateway: Any, op: str, expense: str, phase: str, outcome: str, basis: str, reference: str, reason: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LogisticsCostError`, `assert_correction_decision`, `cur.execute`, `cur.fetchone`, `cur.setinputsizes`, `enqueue`, `expense_payload`, `gateway.transaction`, `json.dumps`, `json.dumps([expense, phase, outcome, basis, reference, reason, actor], ensure_ascii=False, separators=(',', ':')).encode`, `lock_correction_root`, `lock_root`, `read_oracle_json`, `require_warehouse`, `sha256`, `sha256(json.dumps([expense, phase, outcome, basis, reference, reason, actor], ensure_ascii=False, separators=(',', ':')).encode()).digest`

### actual_goods

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/expense_manifest.py:8](../../../api/wms_api_server/app/modules/finance/infrastructure/expense_manifest.py#L8)

```python
actual_goods(cursor: Any, trip: int, ware: int, basis: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `LogisticsCostError`, `any`, `cursor.execute`, `cursor.fetchall`, `dict`, `full_proofs.get`, `full_proofs.setdefault`, `full_proofs.setdefault(load, []).append`, `keys.add`, `len`, `missing_leaf_weight`, `n.get`, `node.get`, `physical_box_count`, `proofs.get`, `proofs.setdefault`, `quantity.is_finite`, `read_oracle_json`, `rows.append`, `set`, `str`, `tree.get`, `units.add`, `value.is_finite`, `x.get`, `x[0].lower`, `zip`

### warehouse_expenses

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/expense_register_read.py:21](../../../api/wms_api_server/app/modules/finance/infrastructure/expense_register_read.py#L21)

```python
warehouse_expenses(gateway: Any, ware: int, operation_id: str | None=None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `gateway.fetch_all`

### report_expense

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/expense_reports.py:12](../../../api/wms_api_server/app/modules/finance/infrastructure/expense_reports.py#L12)

```python
report_expense(gateway: Any, op: str, ware: int, code: str, kind: str, object_id: int, value: str, currency: str, day: str, reference: str, reason: str, actor: str, correction: str | None=None, expected: str | None=None, cost_correction: str | None=None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LogisticsCostError`, `abs`, `correction_source`, `cur.execute`, `cur.fetchone`, `cur.setinputsizes`, `format`, `gateway.transaction`, `json.dumps`, `json.dumps(source_values, ensure_ascii=False, separators=(',', ':')).encode`, `rate_value`, `read_oracle_json`, `require_warehouse`, `result.update`, `sha256`, `sha256(json.dumps(source_values, ensure_ascii=False, separators=(',', ':')).encode()).digest`, `signed_amount`, `source_values.extend`, `str`, `validate_report`

### enqueue

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/finance_outbox.py:5](../../../api/wms_api_server/app/modules/finance/infrastructure/finance_outbox.py#L5)

```python
enqueue(cursor: Any, event_type: str, operation_id: str, payload: dict[str, Any], semantics: str) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(event_type + ':' + operation_id).encode`, `cursor.execute`, `cursor.setinputsizes`, `json.dumps`, `sha256`, `sha256((event_type + ':' + operation_id).encode()).hexdigest`

### expense_payload

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/finance_outbox.py:12](../../../api/wms_api_server/app/modules/finance/infrastructure/finance_outbox.py#L12)

```python
expense_payload(cursor: Any, expense: str, result: dict[str, Any]) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cursor.execute`, `cursor.fetchone`, `dict`, `zip`

### __init__

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py:9](../../../api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py#L9)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### invoice_transport_costs

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py:12](../../../api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py#L12)

```python
invoice_transport_costs(self, invoice: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `invoice_transport_costs`

### transport_costs

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py:16](../../../api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py#L16)

```python
transport_costs(self, trip: int, ware: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `transport_costs`

### conduct_transport_cost

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py:20](../../../api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py#L20)

```python
conduct_transport_cost(self, body: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `conduct_transport_cost`

### transport_cost_preview

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py:24](../../../api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py#L24)

```python
transport_cost_preview(self, trip: int, ware: int, price_id: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cursor.execute`, `preview_transport_cost`, `self.gateway.transaction`

### transport_facts

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py:30](../../../api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py#L30)

```python
transport_facts(self, trip: int, ware: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cursor.execute`, `self.gateway.transaction`, `transport_facts`

### transport_tariff_sources

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py:36](../../../api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py#L36)

```python
transport_tariff_sources(self, trip: int, ware: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `transport_tariff_sources`

### publish_transport_norm

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py:40](../../../api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py#L40)

```python
publish_transport_norm(self, body: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `publish_transport_norm`

### transport_norm_history

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py:44](../../../api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py#L44)

```python
transport_norm_history(self, ware: int, price_id: int, before: int | None, limit: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `transport_norm_history`

### rate

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py:48](../../../api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py#L48)

```python
rate(self, ware: int, currency: str, value: str, effective: str, version: int, reason: str, reference: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `set_box_rate`

### monthly_rate

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py:51](../../../api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py#L51)

```python
monthly_rate(self, ware: int, currency: str, month: str, picking: str, common: str, boxes: str, version: int, reason: str, reference: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `set_monthly_rate`

### calculate

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py:54](../../../api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py#L54)

```python
calculate(self, op: str, trip: int, ware: int, currency: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `calculate_box_cost`

### rate_history

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py:57](../../../api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py#L57)

```python
rate_history(self, ware: int, currency: str, before: int, limit: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `read_rate_history`

### assembly_period

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py:61](../../../api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py#L61)

```python
assembly_period(self, trip: int, ware: int, region: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `read_assembly_period`

### period_policy

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py:65](../../../api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py#L65)

```python
period_policy(self, ware: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `read_policy`

### configure_period

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py:69](../../../api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py#L69)

```python
configure_period(self, op: str, ware: int, mode: str, region: str | None, version: int, reason: str, reference: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `set_policy`

### rates

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py:73](../../../api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py#L73)

```python
rates(self, ware: int, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.execute`, `cur.fetchall`, `dict`, `read_oracle_json`, `require_warehouse`, `row.pop`, `rows.append`, `self.gateway.transaction`, `x[0].lower`, `zip`

### trip

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py:88](../../../api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py#L88)

```python
trip(self, trip: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LogisticsCostError`, `recognized_cost_summary`, `self._lines`, `str`

### invoice

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py:96](../../../api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py#L96)

```python
invoice(self, invoice: int, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LogisticsCostError`, `self._lines`, `self.gateway.fetch_all`

### invoice_summary

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py:101](../../../api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py#L101)

```python
invoice_summary(self, invoice: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LogisticsCostError`, `recognized_cost_summary`, `self.invoice`, `str`

### _lines

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py:109](../../../api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py#L109)

```python
_lines(self, clause: str, object_id: int, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LogisticsCostError`, `len`, `read_oracle_json`, `self.gateway.fetch_all`

### __init__

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/logistics_expenses.py:11](../../../api/wms_api_server/app/modules/finance/infrastructure/logistics_expenses.py#L11)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### _action

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/logistics_expenses.py:14](../../../api/wms_api_server/app/modules/finance/infrastructure/logistics_expenses.py#L14)

```python
_action(self, fn: Callable[..., dict[str, Any]], *args: Any) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LogisticsCostError`, `fn`, `getattr`, `range`, `str`, `str(exc.args[0]).split`

### article

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/logistics_expenses.py:25](../../../api/wms_api_server/app/modules/finance/infrastructure/logistics_expenses.py#L25)

```python
article(self, code: str, name: str, scope: str, included: bool, active: bool, version: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self._action`

### normative_cost_sources

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/logistics_expenses.py:28](../../../api/wms_api_server/app/modules/finance/infrastructure/logistics_expenses.py#L28)

```python
normative_cost_sources(self, ware: int, actor: str, cost_operation_id: str | None=None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `normative_cost_sources`

### articles

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/logistics_expenses.py:32](../../../api/wms_api_server/app/modules/finance/infrastructure/logistics_expenses.py#L32)

```python
articles(self) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### report

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/logistics_expenses.py:35](../../../api/wms_api_server/app/modules/finance/infrastructure/logistics_expenses.py#L35)

```python
report(self, op: str, ware: int, code: str, kind: str, object_id: int, amount: str, currency: str, day: str, reference: str, reason: str, actor: str, correction: str | None=None, expected: str | None=None, cost_correction: str | None=None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self._action`

### decide

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/logistics_expenses.py:38](../../../api/wms_api_server/app/modules/finance/infrastructure/logistics_expenses.py#L38)

```python
decide(self, op: str, expense: str, phase: str, outcome: str, basis: str, reference: str, reason: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self._action`

### pending

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/logistics_expenses.py:41](../../../api/wms_api_server/app/modules/finance/infrastructure/logistics_expenses.py#L41)

```python
pending(self, ware: int, actor: str, operation_id: str | None=None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `require_warehouse`, `self.gateway.transaction`, `warehouse_expenses`

### set_monthly_rate

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/monthly_rates.py:8](../../../api/wms_api_server/app/modules/finance/infrastructure/monthly_rates.py#L8)

```python
set_monthly_rate(gateway: Any, ware: int, currency: str, month: str, picking: str, common: str, boxes: str, version: int, reason: str, reference: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LogisticsCostError`, `monthly_components`, `set_box_rate`, `str`

### validate_report

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/normative_correction.py:6](../../../api/wms_api_server/app/modules/finance/infrastructure/normative_correction.py#L6)

```python
validate_report(cursor: Any, cost: str, ware: int, kind: str, object_id: int, currency: str, delta: Decimal, expected: Decimal) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cursor.callproc`

### lock_root

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/normative_correction.py:11](../../../api/wms_api_server/app/modules/finance/infrastructure/normative_correction.py#L11)

```python
lock_root(cursor: Any, expense: str) -> str | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cursor.execute`, `cursor.fetchone`, `str`

### confirmed_total

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/normative_correction.py:21](../../../api/wms_api_server/app/modules/finance/infrastructure/normative_correction.py#L21)

```python
confirmed_total(cursor: Any, cost: str) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cursor.execute`, `cursor.fetchone`, `str`

### confirmed_totals

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/normative_totals_read.py:7](../../../api/wms_api_server/app/modules/finance/infrastructure/normative_totals_read.py#L7)

```python
confirmed_totals(cursor: Any, originals: dict[str, str]) -> dict[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `','.join`, `Decimal`, `LogisticsCostError`, `adjustments.get`, `cursor.execute`, `cursor.fetchall`, `dict`, `enumerate`, `format`, `len`, `localcontext`, `originals.items`, `str`, `total.is_finite`, `total.normalize`

### current_policy

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/period_policy.py:11](../../../api/wms_api_server/app/modules/finance/infrastructure/period_policy.py#L11)

```python
current_policy(cursor: Any, ware: int, *, lock: bool=False) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LogisticsCostError`, `cursor.execute`, `cursor.fetchone`, `getattr`, `read_oracle_json`

### read_policy

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/period_policy.py:25](../../../api/wms_api_server/app/modules/finance/infrastructure/period_policy.py#L25)

```python
read_policy(gateway: Any, ware: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `current_policy`, `cursor.execute`, `gateway.transaction`, `require_warehouse`

### set_policy

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/period_policy.py:32](../../../api/wms_api_server/app/modules/finance/infrastructure/period_policy.py#L32)

```python
set_policy(gateway: Any, op: str, ware: int, mode: str, region: str | None, version: int, reason: str, reference: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LogisticsCostError`, `current_policy`, `cursor.execute`, `cursor.fetchone`, `cursor.setinputsizes`, `gateway.transaction`, `getattr`, `json.dumps`, `json.dumps([ware, mode, region, version, reason, reference, actor], ensure_ascii=False, separators=(',', ':')).encode`, `read_oracle_json`, `require_warehouse`, `sha256`, `sha256(json.dumps([ware, mode, region, version, reason, reference, actor], ensure_ascii=False, separators=(',', ':')).encode()).digest`, `str`, `str(exc.args[0]).split`

### read_rate_history

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/rate_history.py:8](../../../api/wms_api_server/app/modules/finance/infrastructure/rate_history.py#L8)

```python
read_rate_history(gateway: Any, ware: int, currency: str, before: int, limit: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.execute`, `cur.fetchall`, `dict`, `f'{ware}:WAREHOUSE_PICKING:{currency}'.encode`, `gateway.transaction`, `len`, `read_oracle_json`, `require_warehouse`, `row.pop`, `rows.append`, `sha256`, `sha256(f'{ware}:WAREHOUSE_PICKING:{currency}'.encode()).hexdigest`, `x[0].lower`, `zip`

### daily_counts

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/reconciliation_documents.py:24](../../../api/wms_api_server/app/modules/finance/infrastructure/reconciliation_documents.py#L24)

```python
daily_counts(cursor: Any, params: dict[str, Any]) -> dict[str, int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' union all '.join`, `cursor.execute`, `cursor.fetchall`, `int`

### backlog_documents

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/reconciliation_documents.py:30](../../../api/wms_api_server/app/modules/finance/infrastructure/reconciliation_documents.py#L30)

```python
backlog_documents(cursor: Any, warehouse: int) -> tuple[dict[str, int], dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' union all '.join`, `ValueError`, `cursor.execute`, `cursor.fetchall`, `details[key]['document_ids'].append`, `int`, `len`, `parts.append`, `query.startswith`

### erp_snapshot

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/reconciliation_erp.py:9](../../../api/wms_api_server/app/modules/finance/infrastructure/reconciliation_erp.py#L9)

```python
erp_snapshot(cursor: Any, ware: int) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cursor.execute`, `cursor.fetchall`

### external_documents

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/reconciliation_external_documents.py:13](../../../api/wms_api_server/app/modules/finance/infrastructure/reconciliation_external_documents.py#L13)

```python
external_documents(cursor: Any, ware: int, counts: dict[str, int]) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' union all '.join`, `SOURCES.items`, `counts.get`, `cursor.execute`, `cursor.fetchall`, `parts.append`, `result[key]['document_ids'].append`

### regulatory_snapshot

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/reconciliation_regulatory.py:13](../../../api/wms_api_server/app/modules/finance/infrastructure/reconciliation_regulatory.py#L13)

```python
regulatory_snapshot(cursor: Any, ware: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LogisticsCostError`, `cursor.execute`, `cursor.fetchall`, `int`, `len`, `sum`

### stock_snapshot

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/reconciliation_stock.py:9](../../../api/wms_api_server/app/modules/finance/infrastructure/reconciliation_stock.py#L9)

```python
stock_snapshot(cursor: Any, ware: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cursor.execute`, `cursor.fetchall`, `cursor.fetchone`

### stock_documents

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/reconciliation_stock_documents.py:13](../../../api/wms_api_server/app/modules/finance/infrastructure/reconciliation_stock_documents.py#L13)

```python
stock_documents(cursor: Any, ware: int, counts: dict[str, int]) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' union all '.join`, `SOURCES.items`, `counts.get`, `cursor.execute`, `cursor.fetchall`, `json.dumps`, `parts.append`, `result[key]['document_ids'].append`, `result[key]['stock_rows'].append`

### task_time_coverage

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/reconciliation_task_times.py:4](../../../api/wms_api_server/app/modules/finance/infrastructure/reconciliation_task_times.py#L4)

```python
task_time_coverage(cursor: Any, ware: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cursor.execute`, `cursor.fetchone`, `int`

### report

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/shipping_register.py:11](../../../api/wms_api_server/app/modules/finance/infrastructure/shipping_register.py#L11)

```python
report(gateway: Any, ware: int, day: date, after: int, limit: int, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LogisticsCostError`, `cur.execute`, `gateway.transaction`, `read_snapshot`, `require_warehouse`

### read_snapshot

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/shipping_register.py:18](../../../api/wms_api_server/app/modules/finance/infrastructure/shipping_register.py#L18)

```python
read_snapshot(cur: Any, ware: int, day: date, after: int, limit: int) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LogisticsCostError`, `any`, `bool`, `cur.execute`, `cur.fetchall`, `cur.var`, `day.isoformat`, `json.dumps`, `len`, `payload.setvalue`, `published_cell_coverage`, `rows.append`, `timedelta`

### decode_cursor

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/stock_conflict_page.py:11](../../../api/wms_api_server/app/modules/finance/infrastructure/stock_conflict_page.py#L11)

```python
decode_cursor(value: str | None, ware: int, metric: str) -> tuple[str, str] | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LogisticsCostError`, `ValueError`, `base64.b64decode`, `isinstance`, `json.loads`, `len`, `raw.decode`, `value.encode`

### stock_conflict_page

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/stock_conflict_page.py:24](../../../api/wms_api_server/app/modules/finance/infrastructure/stock_conflict_page.py#L24)

```python
stock_conflict_page(gateway: Any, ware: int, metric: str, after: str | None, limit: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LogisticsCostError`, `base64.urlsafe_b64encode`, `base64.urlsafe_b64encode(json.dumps([ware, metric, last['uid_pallet'], last['cell']], ensure_ascii=False, separators=(',', ':')).encode('utf-8')).decode`, `cur.execute`, `cur.fetchall`, `decode_cursor`, `gateway.transaction`, `json.dumps`, `json.dumps([ware, metric, last['uid_pallet'], last['cell']], ensure_ascii=False, separators=(',', ':')).encode`, `len`, `params.update`, `require_warehouse`

### transport_facts

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/transport_cost_facts.py:8](../../../api/wms_api_server/app/modules/finance/infrastructure/transport_cost_facts.py#L8)

```python
transport_facts(cursor: Any, trip: int, ware: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LogisticsCostError`, `any`, `bool`, `cursor.execute`, `cursor.fetchall`, `details.append`, `int`, `len`, `missing.append`, `read_oracle_json`, `received.get`, `require_warehouse`, `set`, `sorted`

### native_failure

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/transport_cost_preview.py:8](../../../api/wms_api_server/app/modules/finance/infrastructure/transport_cost_preview.py#L8)

```python
native_failure(exc: oracledb.DatabaseError) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LogisticsCostError`, `getattr`, `str`, `str(exc.args[0]).split`

### preview_transport_cost

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/transport_cost_preview.py:18](../../../api/wms_api_server/app/modules/finance/infrastructure/transport_cost_preview.py#L18)

```python
preview_transport_cost(cursor: Any, trip: int, ware: int, price_id: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cursor.callproc`, `cursor.var`, `native_failure`, `out.getvalue`, `read_oracle_json`

### conduct_transport_cost

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/transport_cost_preview.py:28](../../../api/wms_api_server/app/modules/finance/infrastructure/transport_cost_preview.py#L28)

```python
conduct_transport_cost(gateway: Any, body: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cursor.callproc`, `cursor.var`, `gateway.transaction`, `json.dumps`, `native_failure`, `out.getvalue`, `read_oracle_json`

### transport_costs

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/transport_cost_read.py:9](../../../api/wms_api_server/app/modules/finance/infrastructure/transport_cost_read.py#L9)

```python
transport_costs(gateway: Any, trip: int, ware: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LogisticsCostError`, `confirmed_total`, `cursor.execute`, `cursor.fetchall`, `gateway.transaction`, `len`, `read_oracle_json`, `require_warehouse`

### invoice_snapshot

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/transport_cost_read.py:28](../../../api/wms_api_server/app/modules/finance/infrastructure/transport_cost_read.py#L28)

```python
invoice_snapshot(cursor: Any, invoice: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `LogisticsCostError`, `confirmed.is_finite`, `confirmed_currency_totals.get`, `confirmed_totals`, `cursor.execute`, `cursor.fetchall`, `format`, `len`, `localcontext`, `read_oracle_json`, `sorted`, `totals.get`, `totals.items`, `value.is_finite`

### invoice_transport_costs

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/transport_cost_read.py:67](../../../api/wms_api_server/app/modules/finance/infrastructure/transport_cost_read.py#L67)

```python
invoice_transport_costs(gateway: Any, invoice: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cursor.execute`, `gateway.transaction`, `invoice_snapshot`

### normative_cost_sources

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/transport_cost_read.py:73](../../../api/wms_api_server/app/modules/finance/infrastructure/transport_cost_read.py#L73)

```python
normative_cost_sources(gateway: Any, ware: int, actor: str, cost_operation_id: str | None=None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `confirmed_totals`, `cursor.execute`, `cursor.fetchall`, `gateway.transaction`, `require_warehouse`

### publish_transport_norm

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/transport_norms.py:10](../../../api/wms_api_server/app/modules/finance/infrastructure/transport_norms.py#L10)

```python
publish_transport_norm(gateway: Any, body: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LogisticsCostError`, `cursor.callproc`, `cursor.var`, `gateway.transaction`, `getattr`, `json.dumps`, `read_oracle_json`, `result.getvalue`, `str`, `str(exc.args[0]).split`

### transport_norm_history

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/transport_norms.py:26](../../../api/wms_api_server/app/modules/finance/infrastructure/transport_norms.py#L26)

```python
transport_norm_history(gateway: Any, ware: int, price_id: int, before: int | None, limit: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LogisticsCostError`, `cursor.execute`, `cursor.fetchall`, `gateway.transaction`, `items.append`, `len`, `read_oracle_json`, `require_warehouse`

### transport_tariff_sources

[Исходник: api/wms_api_server/app/modules/finance/infrastructure/transport_tariff_sources.py:10](../../../api/wms_api_server/app/modules/finance/infrastructure/transport_tariff_sources.py#L10)

```python
transport_tariff_sources(gateway: Any, trip: int, ware: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LogisticsCostError`, `cursor.execute`, `cursor.fetchall`, `cursor.fetchone`, `dict`, `gateway.transaction`, `int`, `json.dumps`, `json.dumps(row, sort_keys=True, separators=(',', ':')).encode`, `len`, `read_oracle_json`, `require_warehouse`, `result.append`, `sha256`, `sha256(json.dumps(row, sort_keys=True, separators=(',', ':')).encode()).hexdigest`, `sorted`, `str`, `zip`

### build_logistics_costs

[Исходник: api/wms_api_server/app/modules/finance/public.py:6](../../../api/wms_api_server/app/modules/finance/public.py#L6)

```python
build_logistics_costs(gateway: Any) -> LogisticsCostPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LogisticsCosts`

### build_logistics_expenses

[Исходник: api/wms_api_server/app/modules/finance/public.py:13](../../../api/wms_api_server/app/modules/finance/public.py#L13)

```python
build_logistics_expenses(gateway: Any) -> LogisticsExpensePort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LogisticsExpenses`

### build_expense_allocation

[Исходник: api/wms_api_server/app/modules/finance/public.py:20](../../../api/wms_api_server/app/modules/finance/public.py#L20)

```python
build_expense_allocation(gateway: Any) -> ExpenseAllocationPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ExpenseAllocation`

### build_day_reconciliation

[Исходник: api/wms_api_server/app/modules/finance/public.py:27](../../../api/wms_api_server/app/modules/finance/public.py#L27)

```python
build_day_reconciliation(gateway: Any) -> DayReconciliationPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `DayReconciliation`

### build_day_reviews

[Исходник: api/wms_api_server/app/modules/finance/public.py:34](../../../api/wms_api_server/app/modules/finance/public.py#L34)

```python
build_day_reviews(gateway: Any) -> DayReviewsPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `DayReviews`
