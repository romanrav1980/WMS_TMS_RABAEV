# Методы: tare_composition.py

### build_tare_ledger

[Исходник: api/wms_api_server/app/tare_composition.py:5](../../../api/wms_api_server/app/tare_composition.py#L5)

```python
build_tare_ledger() -> TarePort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `StockCommand`, `TareError`, `abs`, `build_stock_posting_service`, `build_tare`, `posting.post`, `str`

### build_tare_return_policy

[Исходник: api/wms_api_server/app/tare_composition.py:17](../../../api/wms_api_server/app/tare_composition.py#L17)

```python
build_tare_return_policy() -> TarePolicyPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `build_tare_policy`

### build_tare_for_assembly

[Исходник: api/wms_api_server/app/tare_composition.py:22](../../../api/wms_api_server/app/tare_composition.py#L22)

```python
build_tare_for_assembly() -> TareAssemblyPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `build_tare_assembly`

### post

[Исходник: api/wms_api_server/app/tare_composition.py:7](../../../api/wms_api_server/app/tare_composition.py#L7)

```python
post(kind: str, operation_id: str, source: dict[str, Any], metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockCommand`, `TareError`, `abs`, `posting.post`, `str`
