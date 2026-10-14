# Методы: transport_composition.py

### build_transport_loading

[Исходник: api/wms_api_server/app/transport_composition.py:8](../../../api/wms_api_server/app/transport_composition.py#L8)

```python
build_transport_loading() -> TransportLoadingPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `StockCommand`, `TransportLoadingError`, `build_loading_service`, `build_stock_posting_service`, `posting.post`, `str`

### build_transport_driver_binding

[Исходник: api/wms_api_server/app/transport_composition.py:26](../../../api/wms_api_server/app/transport_composition.py#L26)

```python
build_transport_driver_binding() -> DriverBindingPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `build_driver_binding`

### post

[Исходник: api/wms_api_server/app/transport_composition.py:11](../../../api/wms_api_server/app/transport_composition.py#L11)

```python
post(kind: str, operation_id: str, source: dict[str, Any], metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StockCommand`, `TransportLoadingError`, `posting.post`, `str`
