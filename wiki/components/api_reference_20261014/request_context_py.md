# Методы: request_context.py

### set_request_context

[Исходник: api/wms_api_server/app/request_context.py:21](../../../api/wms_api_server/app/request_context.py#L21)

```python
set_request_context(context: RequestContext) -> Token[RequestContext | None]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_request_context.set`

### update_request_context

[Исходник: api/wms_api_server/app/request_context.py:25](../../../api/wms_api_server/app/request_context.py#L25)

```python
update_request_context(**changes) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_request_context.get`, `_request_context.set`, `replace`

### reset_request_context

[Исходник: api/wms_api_server/app/request_context.py:32](../../../api/wms_api_server/app/request_context.py#L32)

```python
reset_request_context(token: Token[RequestContext | None]) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_request_context.reset`

### get_request_context

[Исходник: api/wms_api_server/app/request_context.py:36](../../../api/wms_api_server/app/request_context.py#L36)

```python
get_request_context() -> RequestContext | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_request_context.get`
