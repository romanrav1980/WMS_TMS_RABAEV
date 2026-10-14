# Методы: transaction_gateway.py

### __init__

[Исходник: api/wms_api_server/app/transaction_gateway.py:11](../../../api/wms_api_server/app/transaction_gateway.py#L11)

```python
__init__(self, cursor: oracledb.Cursor)
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### fetch_all

[Исходник: api/wms_api_server/app/transaction_gateway.py:14](../../../api/wms_api_server/app/transaction_gateway.py#L14)

```python
fetch_all(self, sql: str, params: dict[str, Any] | None=None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `rows_as_dicts`, `self.cursor.execute`

### execute

[Исходник: api/wms_api_server/app/transaction_gateway.py:18](../../../api/wms_api_server/app/transaction_gateway.py#L18)

```python
execute(self, sql: str, params: dict[str, Any] | None=None) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.cursor.execute`

### execute_many

[Исходник: api/wms_api_server/app/transaction_gateway.py:22](../../../api/wms_api_server/app/transaction_gateway.py#L22)

```python
execute_many(self, statements: list[tuple[str, dict[str, Any]]]) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.execute`

### execute_plsql

[Исходник: api/wms_api_server/app/transaction_gateway.py:27](../../../api/wms_api_server/app/transaction_gateway.py#L27)

```python
execute_plsql(self, block: str, params: dict[str, Any]) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.execute`

### call_number_plsql

[Исходник: api/wms_api_server/app/transaction_gateway.py:30](../../../api/wms_api_server/app/transaction_gateway.py#L30)

```python
call_number_plsql(self, block: str, params: dict[str, Any]) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `int`, `result.getvalue`, `self.cursor.execute`, `self.cursor.var`

### transaction

[Исходник: api/wms_api_server/app/transaction_gateway.py:36](../../../api/wms_api_server/app/transaction_gateway.py#L36)

```python
transaction(self, operation_name: str)
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 
