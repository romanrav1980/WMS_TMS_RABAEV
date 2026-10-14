# Методы: platform

### stock_configuration_transaction

[Исходник: api/wms_api_server/app/modules/platform/infrastructure/configuration.py:6](../../../api/wms_api_server/app/modules/platform/infrastructure/configuration.py#L6)

```python
stock_configuration_transaction(gateway: Any, label: str, actor: str, permission: str) -> Iterator[Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cursor.execute`, `gateway.transaction`

### read_oracle_json

[Исходник: api/wms_api_server/app/modules/platform/infrastructure/oracle_json.py:5](../../../api/wms_api_server/app/modules/platform/infrastructure/oracle_json.py#L5)

```python
read_oracle_json(value: Any) -> Any
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TypeError`, `hasattr`, `isinstance`, `json.loads`, `value.read`
