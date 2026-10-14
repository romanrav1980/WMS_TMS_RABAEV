# Методы: db.py

### _oracle_pool

[Исходник: api/wms_api_server/app/db.py:28](../../../api/wms_api_server/app/db.py#L28)

```python
_oracle_pool() -> oracledb.ConnectionPool
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `get_settings`, `oracledb.create_pool`

### oracle_connection

[Исходник: api/wms_api_server/app/db.py:49](../../../api/wms_api_server/app/db.py#L49)

```python
oracle_connection() -> Iterator[oracledb.Connection]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_LOG.warning`, `_oracle_pool`, `connection.close`, `connection.cursor`, `connection.rollback`, `cursor.callproc`, `int`, `max`, `min`, `os.environ.get`, `pool.acquire`, `pool.drop`, `pool.release`, `type`

### scalar_to_text

[Исходник: api/wms_api_server/app/db.py:76](../../../api/wms_api_server/app/db.py#L76)

```python
scalar_to_text(value: Any) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `str`

### rows_as_dicts

[Исходник: api/wms_api_server/app/db.py:82](../../../api/wms_api_server/app/db.py#L82)

```python
rows_as_dicts(cursor: oracledb.Cursor) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `column[0].lower`, `cursor.fetchall`, `dict`, `oracle_value`, `zip`

### oracle_value

[Исходник: api/wms_api_server/app/db.py:87](../../../api/wms_api_server/app/db.py#L87)

```python
oracle_value(value: Any) -> Any
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `isinstance`, `value.read`
