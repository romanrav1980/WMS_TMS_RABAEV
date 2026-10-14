# Методы: oracle_gateway.py

### _truncate

[Исходник: api/wms_api_server/app/oracle_gateway.py:375](../../../api/wms_api_server/app/oracle_gateway.py#L375)

```python
_truncate(value: Any, max_length: int) -> str | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `str`

### _json_dumps_limited

[Исходник: api/wms_api_server/app/oracle_gateway.py:382](../../../api/wms_api_server/app/oracle_gateway.py#L382)

```python
_json_dumps_limited(value: Any, max_length: int) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `json.dumps`, `str`

### ping

[Исходник: api/wms_api_server/app/oracle_gateway.py:15](../../../api/wms_api_server/app/oracle_gateway.py#L15)

```python
ping(self) -> dict[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `connection.cursor`, `cursor.execute`, `cursor.fetchone`, `oracle_connection`, `scalar_to_text`

### fetch_all

[Исходник: api/wms_api_server/app/oracle_gateway.py:33](../../../api/wms_api_server/app/oracle_gateway.py#L33)

```python
fetch_all(self, sql: str, params: dict[str, Any] | None=None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `connection.cursor`, `cursor.execute`, `len`, `oracle_connection`, `rows_as_dicts`, `self._apply_session_context`, `self._log_slow_sql`, `str`, `time.perf_counter`

### execute

[Исходник: api/wms_api_server/app/oracle_gateway.py:59](../../../api/wms_api_server/app/oracle_gateway.py#L59)

```python
execute(self, sql: str, params: dict[str, Any] | None=None) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `connection.commit`, `connection.cursor`, `connection.rollback`, `cursor.execute`, `oracle_connection`, `self._apply_session_context`, `self._log_slow_sql`, `str`, `time.perf_counter`

### execute_many

[Исходник: api/wms_api_server/app/oracle_gateway.py:86](../../../api/wms_api_server/app/oracle_gateway.py#L86)

```python
execute_many(self, statements: list[tuple[str, dict[str, Any]]]) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `connection.commit`, `connection.cursor`, `connection.rollback`, `cursor.executemany`, `grouped.items`, `grouped.setdefault`, `grouped.setdefault(sql, []).append`, `len`, `max`, `oracle_connection`, `self._apply_session_context`, `self._log_slow_sql`, `set`, `str`, `time.perf_counter`

### transaction

[Исходник: api/wms_api_server/app/oracle_gateway.py:119](../../../api/wms_api_server/app/oracle_gateway.py#L119)

```python
transaction(self, operation_name: str)
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `connection.commit`, `connection.cursor`, `connection.rollback`, `oracle_connection`, `self._apply_session_context`, `self._log_slow_sql`, `str`, `time.perf_counter`

### call_varchar_function

[Исходник: api/wms_api_server/app/oracle_gateway.py:143](../../../api/wms_api_server/app/oracle_gateway.py#L143)

```python
call_varchar_function(self, function_name: str, params: dict[str, Any]) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `connection.commit`, `connection.cursor`, `connection.rollback`, `cursor.callfunc`, `oracle_connection`, `scalar_to_text`, `self._apply_session_context`, `self._log_slow_sql`, `str`, `time.perf_counter`

### call_varchar_plsql

[Исходник: api/wms_api_server/app/oracle_gateway.py:168](../../../api/wms_api_server/app/oracle_gateway.py#L168)

```python
call_varchar_plsql(self, block: str, params: dict[str, Any]) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `connection.commit`, `connection.cursor`, `connection.rollback`, `cursor.execute`, `cursor.var`, `oracle_connection`, `result.getvalue`, `scalar_to_text`, `self._apply_session_context`, `self._log_slow_sql`, `str`, `time.perf_counter`

### call_number_plsql

[Исходник: api/wms_api_server/app/oracle_gateway.py:194](../../../api/wms_api_server/app/oracle_gateway.py#L194)

```python
call_number_plsql(self, block: str, params: dict[str, Any]) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `connection.commit`, `connection.cursor`, `connection.rollback`, `cursor.execute`, `cursor.var`, `int`, `oracle_connection`, `result.getvalue`, `self._apply_session_context`, `self._log_slow_sql`, `str`, `time.perf_counter`

### call_optional_number_plsql

[Исходник: api/wms_api_server/app/oracle_gateway.py:221](../../../api/wms_api_server/app/oracle_gateway.py#L221)

```python
call_optional_number_plsql(self, block: str, params: dict[str, Any]) -> int | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `connection.commit`, `connection.cursor`, `connection.rollback`, `cursor.execute`, `cursor.var`, `int`, `oracle_connection`, `result.getvalue`, `self._apply_session_context`, `self._log_slow_sql`, `str`, `time.perf_counter`

### execute_plsql

[Исходник: api/wms_api_server/app/oracle_gateway.py:248](../../../api/wms_api_server/app/oracle_gateway.py#L248)

```python
execute_plsql(self, block: str, params: dict[str, Any]) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `connection.commit`, `connection.cursor`, `connection.rollback`, `cursor.execute`, `oracle_connection`, `self._apply_session_context`, `self._log_slow_sql`, `str`, `time.perf_counter`

### _apply_session_context

[Исходник: api/wms_api_server/app/oracle_gateway.py:272](../../../api/wms_api_server/app/oracle_gateway.py#L272)

```python
_apply_session_context(self, cursor: oracledb.Cursor) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_truncate`, `context.method.upper`, `cursor.execute`, `get_request_context`

### _log_slow_sql

[Исходник: api/wms_api_server/app/oracle_gateway.py:302](../../../api/wms_api_server/app/oracle_gateway.py#L302)

```python
_log_slow_sql(self, connection: oracledb.Connection, sql: str, params: dict[str, Any] | None, started: float, row_count: int | None, error_text: str | None, operation_kind: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(sql or '').strip`, `_json_dumps_limited`, `_truncate`, `connection.commit`, `connection.cursor`, `connection.rollback`, `context.method.upper`, `cursor.execute`, `get_request_context`, `get_settings`, `hashlib.sha256`, `hashlib.sha256(sql_text.encode('utf-8', errors='replace')).hexdigest`, `int`, `sql_text.encode`, `time.perf_counter`
