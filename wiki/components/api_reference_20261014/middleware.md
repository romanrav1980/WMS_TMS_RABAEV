# Методы: middleware

### is_replayable

[Исходник: api/wms_api_server/app/middleware/api_audit.py:172](../../../api/wms_api_server/app/middleware/api_audit.py#L172)

```python
is_replayable(request: Request) -> bool
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `path.startswith`, `request.method.upper`

### is_lightweight_transport_read

[Исходник: api/wms_api_server/app/middleware/api_audit.py:183](../../../api/wms_api_server/app/middleware/api_audit.py#L183)

```python
is_lightweight_transport_read(request: Request) -> bool
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `request.method.upper`, `request.url.path.endswith`, `request.url.path.startswith`

### _int_header

[Исходник: api/wms_api_server/app/middleware/api_audit.py:212](../../../api/wms_api_server/app/middleware/api_audit.py#L212)

```python
_int_header(value: str | None) -> int | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `int`

### dispatch

[Исходник: api/wms_api_server/app/middleware/api_audit.py:24](../../../api/wms_api_server/app/middleware/api_audit.py#L24)

```python
dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ApiAuditService`, `JSONResponse`, `RequestContext`, `Response`, `_int_header`, `audit.append_local`, `audit.finish_call`, `audit.start_call`, `body_digest`, `call_next`, `capture_request`, `capture_response`, `dict`, `get_settings`, `int`, `is_lightweight_transport_read`, `is_replayable`, `json_dumps`, `redact_headers`, `request.headers.get`, `reset_request_context`, `set_request_context`, `str`, `time.perf_counter`, `update_request_context`, `uuid.uuid4`

### receive

[Исходник: api/wms_api_server/app/middleware/api_audit.py:103](../../../api/wms_api_server/app/middleware/api_audit.py#L103)

```python
receive() -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### is_photo_upload

[Исходник: api/wms_api_server/app/middleware/audit_body.py:18](../../../api/wms_api_server/app/middleware/audit_body.py#L18)

```python
is_photo_upload(request: Request) -> bool
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `request.method.upper`, `request.url.path.rstrip`

### capture_request

[Исходник: api/wms_api_server/app/middleware/audit_body.py:22](../../../api/wms_api_server/app/middleware/audit_body.py#L22)

```python
capture_request(request: Request, max_chars: int) -> AuditedRequestBody
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `AuditedRequestBody`, `body_digest`, `bytearray`, `bytes`, `collected.extend`, `decode_limited`, `int`, `is_photo_upload`, `json_dumps`, `len`, `request.body`, `request.method.upper`, `request.stream`, `request.url.path.rstrip`

### capture_response

[Исходник: api/wms_api_server/app/middleware/audit_body.py:46](../../../api/wms_api_server/app/middleware/audit_body.py#L46)

```python
capture_response(response: Response, max_chars: int, capture: bool) -> tuple[bytes, str, int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `body_digest`, `bytearray`, `bytes`, `collected.extend`, `decode_limited`, `getattr`, `json_dumps`, `len`, `response.headers.get`, `response.headers.get('content-type', '').split`
