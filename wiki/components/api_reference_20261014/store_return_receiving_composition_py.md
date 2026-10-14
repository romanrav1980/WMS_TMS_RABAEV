# Методы: store_return_receiving_composition.py

### _return_poster

[Исходник: api/wms_api_server/app/store_return_receiving_composition.py:8](../../../api/wms_api_server/app/store_return_receiving_composition.py#L8)

```python
_return_poster() -> Callable[[str, str, dict[str, Any], dict[str, Any], str], dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockCommand`, `StoreReturnReceiveError`, `abs`, `build_stock_posting_service`, `posting.post`, `str`

### build_return_receiving

[Исходник: api/wms_api_server/app/store_return_receiving_composition.py:22](../../../api/wms_api_server/app/store_return_receiving_composition.py#L22)

```python
build_return_receiving() -> StoreReturnReceivePort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `_return_poster`, `build_store_return_receiving`

### build_store_return_putaway

[Исходник: api/wms_api_server/app/store_return_receiving_composition.py:27](../../../api/wms_api_server/app/store_return_receiving_composition.py#L27)

```python
build_store_return_putaway() -> ReturnPutawayPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `_return_poster`, `build_return_putaway`

### post

[Исходник: api/wms_api_server/app/store_return_receiving_composition.py:11](../../../api/wms_api_server/app/store_return_receiving_composition.py#L11)

```python
post(kind: str, operation_id: str, source: dict[str, Any], metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockCommand`, `StoreReturnReceiveError`, `abs`, `posting.post`, `str`
