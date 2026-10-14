# Методы: delivery_composition.py

### _delivery_post

[Исходник: api/wms_api_server/app/delivery_composition.py:9](../../../api/wms_api_server/app/delivery_composition.py#L9)

```python
_delivery_post() -> Callable[[str, str, dict[str, Any], dict[str, Any], str], dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockCommand`, `StoreReceiptError`, `abs`, `build_stock_posting_service`, `posting.post`, `str`

### build_delivery_receipt

[Исходник: api/wms_api_server/app/delivery_composition.py:25](../../../api/wms_api_server/app/delivery_composition.py#L25)

```python
build_delivery_receipt() -> StoreReceiptPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `_delivery_post`, `build_store_receipt`

### build_delivery_evidence

[Исходник: api/wms_api_server/app/delivery_composition.py:30](../../../api/wms_api_server/app/delivery_composition.py#L30)

```python
build_delivery_evidence() -> StoreEvidencePort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `build_store_evidence`

### build_delivery_scales

[Исходник: api/wms_api_server/app/delivery_composition.py:36](../../../api/wms_api_server/app/delivery_composition.py#L36)

```python
build_delivery_scales() -> StoreScalesPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `build_store_scales`

### build_delivery_progress

[Исходник: api/wms_api_server/app/delivery_composition.py:42](../../../api/wms_api_server/app/delivery_composition.py#L42)

```python
build_delivery_progress() -> OrderDeliveryPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `build_order_delivery`

### build_delivery_case_work

[Исходник: api/wms_api_server/app/delivery_composition.py:48](../../../api/wms_api_server/app/delivery_composition.py#L48)

```python
build_delivery_case_work() -> CaseWorkPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `_delivery_post`, `build_case_work`

### build_delivery_returns

[Исходник: api/wms_api_server/app/delivery_composition.py:53](../../../api/wms_api_server/app/delivery_composition.py#L53)

```python
build_delivery_returns() -> StoreReturnsPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `_delivery_post`, `build_store_returns`

### build_sap_store_returns

[Исходник: api/wms_api_server/app/delivery_composition.py:58](../../../api/wms_api_server/app/delivery_composition.py#L58)

```python
build_sap_store_returns() -> SapStoreReturnsPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_delivery_post`, `compose_sap_store_returns`

### build_delivery_return_transport

[Исходник: api/wms_api_server/app/delivery_composition.py:63](../../../api/wms_api_server/app/delivery_composition.py#L63)

```python
build_delivery_return_transport() -> ReturnTransportPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `_delivery_post`, `build_return_transport`

### build_delivery_return_custody

[Исходник: api/wms_api_server/app/delivery_composition.py:68](../../../api/wms_api_server/app/delivery_composition.py#L68)

```python
build_delivery_return_custody() -> ReturnCustodyPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `_delivery_post`, `build_return_custody`

### post

[Исходник: api/wms_api_server/app/delivery_composition.py:12](../../../api/wms_api_server/app/delivery_composition.py#L12)

```python
post(kind: str, operation_id: str, source: dict[str, Any], metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockCommand`, `StoreReceiptError`, `abs`, `posting.post`, `str`
