# Методы: services

### is_available

[Исходник: api/wms_api_server/app/services/am_solver.py:19](../../../api/wms_api_server/app/services/am_solver.py#L19)

```python
is_available() -> bool
```

Проверить доступность модели и PyTorch.

Вызывает: `os.path.exists`

### solve_am

[Исходник: api/wms_api_server/app/services/am_solver.py:28](../../../api/wms_api_server/app/services/am_solver.py#L28)

```python
solve_am(lats: list[float], lons: list[float], pallets: list[int], max_stops: int=30) -> list[int] | None
```

Запустить AM-инференс. Возвращает список индексов в порядке объезда,
или None если модель недоступна.

Вызывает: `AMDecoder`, `AMEncoder`, `checkpoint.get`, `decoder`, `decoder(h, query).view`, `decoder.eval`, `decoder.load_state_dict`, `encoder`, `encoder.eval`, `encoder.load_state_dict`, `int`, `is_available`, `len`, `log.debug`, `log.warning`, `logits.argmax`, `logits.argmax().item`, `max`, `min`, `nn.Linear`, `nn.MultiheadAttention`, `nn.TransformerEncoder`, `nn.TransformerEncoderLayer`, `range`, `route.append`, `self.attn`, `self.embed`, `self.ptr`, `self.ptr(attn_out).squeeze`, `self.query_proj`, `self.transformer`, `set`, `super`, `super().__init__`, `torch.load` (остальные вызовы — в исходнике)

### __init__

[Исходник: api/wms_api_server/app/services/am_solver.py:51](../../../api/wms_api_server/app/services/am_solver.py#L51)

```python
__init__(self) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `nn.Linear`, `nn.TransformerEncoder`, `nn.TransformerEncoderLayer`, `super`, `super().__init__`

### forward

[Исходник: api/wms_api_server/app/services/am_solver.py:57](../../../api/wms_api_server/app/services/am_solver.py#L57)

```python
forward(self, x: 'torch.Tensor') -> 'torch.Tensor'
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.embed`, `self.transformer`

### __init__

[Исходник: api/wms_api_server/app/services/am_solver.py:61](../../../api/wms_api_server/app/services/am_solver.py#L61)

```python
__init__(self) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `nn.Linear`, `nn.MultiheadAttention`, `super`, `super().__init__`

### forward

[Исходник: api/wms_api_server/app/services/am_solver.py:67](../../../api/wms_api_server/app/services/am_solver.py#L67)

```python
forward(self, h: 'torch.Tensor', query: 'torch.Tensor') -> 'torch.Tensor'
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.attn`, `self.ptr`, `self.ptr(attn_out).squeeze`, `self.query_proj`

### json_dumps

[Исходник: api/wms_api_server/app/services/api_audit_service.py:372](../../../api/wms_api_server/app/services/api_audit_service.py#L372)

```python
json_dumps(value: Any) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `json.dumps`

### json_loads

[Исходник: api/wms_api_server/app/services/api_audit_service.py:376](../../../api/wms_api_server/app/services/api_audit_service.py#L376)

```python
json_loads(value: str | None) -> dict[str, str] | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `isinstance`, `json.loads`

### utc_now_iso

[Исходник: api/wms_api_server/app/services/api_audit_service.py:386](../../../api/wms_api_server/app/services/api_audit_service.py#L386)

```python
utc_now_iso() -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `datetime.now`, `datetime.now(timezone.utc).isoformat`

### body_digest

[Исходник: api/wms_api_server/app/services/api_audit_service.py:390](../../../api/wms_api_server/app/services/api_audit_service.py#L390)

```python
body_digest(body: bytes) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `hashlib.sha256`, `hashlib.sha256(body).hexdigest`

### decode_limited

[Исходник: api/wms_api_server/app/services/api_audit_service.py:394](../../../api/wms_api_server/app/services/api_audit_service.py#L394)

```python
decode_limited(body: bytes, max_chars: int) -> tuple[str, int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `body.decode`, `len`

### redact_headers

[Исходник: api/wms_api_server/app/services/api_audit_service.py:401](../../../api/wms_api_server/app/services/api_audit_service.py#L401)

```python
redact_headers(headers: dict[str, str]) -> dict[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `headers.items`, `key.lower`

### normalize_date_filter

[Исходник: api/wms_api_server/app/services/api_audit_service.py:408](../../../api/wms_api_server/app/services/api_audit_service.py#L408)

```python
normalize_date_filter(value: str) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `len`, `value.strip`, `value.strip().replace`

### __init__

[Исходник: api/wms_api_server/app/services/api_audit_service.py:33](../../../api/wms_api_server/app/services/api_audit_service.py#L33)

```python
__init__(self, gateway: OracleGateway | None=None, settings: Settings | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `Path`, `Path.cwd`, `get_settings`, `self.local_dir.is_absolute`

### start_call

[Исходник: api/wms_api_server/app/services/api_audit_service.py:44](../../../api/wms_api_server/app/services/api_audit_service.py#L44)

```python
start_call(self, entry: dict[str, Any]) -> int | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.call_number_plsql`

### finish_call

[Исходник: api/wms_api_server/app/services/api_audit_service.py:73](../../../api/wms_api_server/app/services/api_audit_service.py#L73)

```python
finish_call(self, api_call_id: int | None, entry: dict[str, Any]) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.execute_plsql`

### append_local

[Исходник: api/wms_api_server/app/services/api_audit_service.py:98](../../../api/wms_api_server/app/services/api_audit_service.py#L98)

```python
append_local(self, record: dict[str, Any]) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `datetime.now`, `handle.write`, `json.dumps`, `path.open`, `self.local_dir.mkdir`, `str`, `utc_now_iso`

### list_calls

[Исходник: api/wms_api_server/app/services/api_audit_service.py:107](../../../api/wms_api_server/app/services/api_audit_service.py#L107)

```python
list_calls(self, from_call_id: int | None=None, to_call_id: int | None=None, from_at: str | None=None, to_at: str | None=None, method: str | None=None, path_like: str | None=None, status: str | None=None, replayable: int | None=None, limit: int=100, offset: int=0) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `max`, `min`, `self._build_call_filters`, `self.gateway.fetch_all`

### get_call

[Исходник: api/wms_api_server/app/services/api_audit_service.py:154](../../../api/wms_api_server/app/services/api_audit_service.py#L154)

```python
get_call(self, api_call_id: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### replay_calls

[Исходник: api/wms_api_server/app/services/api_audit_service.py:171](../../../api/wms_api_server/app/services/api_audit_service.py#L171)

```python
replay_calls(self, request: dict[str, Any]) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `', '.join`, `bool`, `enumerate`, `int`, `len`, `max`, `min`, `range`, `replay_result.get`, `request.get`, `results.append`, `self._build_call_filters`, `self._mark_replay`, `self._replay_one`, `self.gateway.fetch_all`, `str`, `time.perf_counter`, `uuid.uuid4`

### _replay_one

[Исходник: api/wms_api_server/app/services/api_audit_service.py:265](../../../api/wms_api_server/app/services/api_audit_service.py#L265)

```python
_replay_one(self, row: dict[str, Any], replay_run_id: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Request`, `RuntimeError`, `body.encode`, `exc.headers.get`, `exc.read`, `exc.read().decode`, `headers.items`, `int`, `json_loads`, `key.lower`, `response.headers.get`, `response.read`, `response.read().decode`, `row.get`, `self.settings.audit_replay_base_url.rstrip`, `str`, `urlopen`

### _mark_replay

[Исходник: api/wms_api_server/app/services/api_audit_service.py:309](../../../api/wms_api_server/app/services/api_audit_service.py#L309)

```python
_mark_replay(self, source_call_id: int, replay_call_id: int | None, error_text: str | None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.execute_plsql`

### _build_call_filters

[Исходник: api/wms_api_server/app/services/api_audit_service.py:332](../../../api/wms_api_server/app/services/api_audit_service.py#L332)

```python
_build_call_filters(self, from_call_id: int | None=None, to_call_id: int | None=None, from_at: str | None=None, to_at: str | None=None, method: str | None=None, path_like: str | None=None, status: str | None=None, replayable: int | None=None) -> tuple[str, dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `conditions.append`, `method.upper`, `normalize_date_filter`

### clamp_limit

[Исходник: api/wms_api_server/app/services/bom_service.py:450](../../../api/wms_api_server/app/services/bom_service.py#L450)

```python
clamp_limit(value: int) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `max`, `min`

### to_float

[Исходник: api/wms_api_server/app/services/bom_service.py:454](../../../api/wms_api_server/app/services/bom_service.py#L454)

```python
to_float(value: Any) -> float
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `float`

### apply_tolerance

[Исходник: api/wms_api_server/app/services/bom_service.py:460](../../../api/wms_api_server/app/services/bom_service.py#L460)

```python
apply_tolerance(value: float, pct: Any, sign: int) -> float | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `round`, `to_float`

### _model_dict

[Исходник: api/wms_api_server/app/services/bom_service.py:466](../../../api/wms_api_server/app/services/bom_service.py#L466)

```python
_model_dict(model) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `hasattr`, `model.dict`, `model.model_dump`

### __init__

[Исходник: api/wms_api_server/app/services/bom_service.py:17](../../../api/wms_api_server/app/services/bom_service.py#L17)

```python
__init__(self, gateway: OracleGateway | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`

### list_boms

[Исходник: api/wms_api_server/app/services/bom_service.py:20](../../../api/wms_api_server/app/services/bom_service.py#L20)

```python
list_boms(self, target_articul: str | None=None, status: str | None=None, is_primary: int | None=None, active_on: date | None=None, limit: int=100) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `clamp_limit`, `conditions.append`, `int`, `self.gateway.fetch_all`, `status.upper`, `target_articul.upper`

### get_bom

[Исходник: api/wms_api_server/app/services/bom_service.py:83](../../../api/wms_api_server/app/services/bom_service.py#L83)

```python
get_bom(self, bom_id: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`, `self.list_audit`, `self.list_lines`

### list_lines

[Исходник: api/wms_api_server/app/services/bom_service.py:122](../../../api/wms_api_server/app/services/bom_service.py#L122)

```python
list_lines(self, bom_id: int) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### list_audit

[Исходник: api/wms_api_server/app/services/bom_service.py:152](../../../api/wms_api_server/app/services/bom_service.py#L152)

```python
list_audit(self, bom_id: int) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### create_bom

[Исходник: api/wms_api_server/app/services/bom_service.py:171](../../../api/wms_api_server/app/services/bom_service.py#L171)

```python
create_bom(self, request: BomCreateRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_model_dict`, `self.gateway.call_number_plsql`

### update_bom

[Исходник: api/wms_api_server/app/services/bom_service.py:197](../../../api/wms_api_server/app/services/bom_service.py#L197)

```python
update_bom(self, bom_id: int, request: BomUpdateRequest) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_model_dict`, `self.gateway.execute_plsql`

### add_line

[Исходник: api/wms_api_server/app/services/bom_service.py:224](../../../api/wms_api_server/app/services/bom_service.py#L224)

```python
add_line(self, bom_id: int, request: BomLineRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_model_dict`, `params.pop`, `self.gateway.call_number_plsql`

### update_line

[Исходник: api/wms_api_server/app/services/bom_service.py:253](../../../api/wms_api_server/app/services/bom_service.py#L253)

```python
update_line(self, line_id: int, request: BomLineRequest) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_model_dict`, `params.pop`, `self.gateway.execute_plsql`

### delete_line

[Исходник: api/wms_api_server/app/services/bom_service.py:282](../../../api/wms_api_server/app/services/bom_service.py#L282)

```python
delete_line(self, line_id: int, deleted_by: str | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.execute_plsql`

### approve_bom

[Исходник: api/wms_api_server/app/services/bom_service.py:295](../../../api/wms_api_server/app/services/bom_service.py#L295)

```python
approve_bom(self, bom_id: int, user_name: str | None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.execute_plsql`

### block_bom

[Исходник: api/wms_api_server/app/services/bom_service.py:308](../../../api/wms_api_server/app/services/bom_service.py#L308)

```python
block_bom(self, bom_id: int, reason: str | None, user_name: str | None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.execute_plsql`

### archive_bom

[Исходник: api/wms_api_server/app/services/bom_service.py:322](../../../api/wms_api_server/app/services/bom_service.py#L322)

```python
archive_bom(self, bom_id: int, reason: str | None, user_name: str | None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.execute_plsql`

### make_primary

[Исходник: api/wms_api_server/app/services/bom_service.py:336](../../../api/wms_api_server/app/services/bom_service.py#L336)

```python
make_primary(self, bom_id: int, user_name: str | None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.execute_plsql`

### clone_bom

[Исходник: api/wms_api_server/app/services/bom_service.py:349](../../../api/wms_api_server/app/services/bom_service.py#L349)

```python
clone_bom(self, source_bom_id: int, request: BomCloneRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_model_dict`, `self.gateway.call_number_plsql`

### find_primary

[Исходник: api/wms_api_server/app/services/bom_service.py:365](../../../api/wms_api_server/app/services/bom_service.py#L365)

```python
find_primary(self, target_articul: str, planned_date: date | None=None, target_mod_id: int | None=None, ware_id: int | None=None, production_line: str | None=None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.call_optional_number_plsql`, `self.get_bom`

### calculate

[Исходник: api/wms_api_server/app/services/bom_service.py:395](../../../api/wms_api_server/app/services/bom_service.py#L395)

```python
calculate(self, bom_id: int, request: BomCalculateRequest) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `apply_tolerance`, `bom.get`, `float`, `line.get`, `lines.append`, `round`, `self.get_bom`, `to_float`

### _trim

[Исходник: api/wms_api_server/app/services/case_pick_service.py:16](../../../api/wms_api_server/app/services/case_pick_service.py#L16)

```python
_trim(value: Any, max_len: int, upper: bool=False) -> str | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `str`, `str(value).strip`, `text.upper`

### __init__

[Исходник: api/wms_api_server/app/services/case_pick_service.py:26](../../../api/wms_api_server/app/services/case_pick_service.py#L26)

```python
__init__(self, gateway: OracleGateway | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`

### ensure_wave_case_pick_tasks

[Исходник: api/wms_api_server/app/services/case_pick_service.py:29](../../../api/wms_api_server/app/services/case_pick_service.py#L29)

```python
ensure_wave_case_pick_tasks(self, pick_wave_id: int, actor: str='API') -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.call_number_plsql`

### list_tasks

[Исходник: api/wms_api_server/app/services/case_pick_service.py:163](../../../api/wms_api_server/app/services/case_pick_service.py#L163)

```python
list_tasks(self, resource_id: int | None=None, scope: str='mine', status: str | None=None, limit: int=100) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `legacy_case_reads`, `legacy_case_reads(self.gateway).list_tasks`

### get_task

[Исходник: api/wms_api_server/app/services/case_pick_service.py:167](../../../api/wms_api_server/app/services/case_pick_service.py#L167)

```python
get_task(self, case_pick_task_id: int) -> dict[str, Any] | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `legacy_case_reads`, `legacy_case_reads(self.gateway).get_task`

### _resource_action

[Исходник: api/wms_api_server/app/services/case_pick_service.py:171](../../../api/wms_api_server/app/services/case_pick_service.py#L171)

```python
_resource_action(self, task_id: int, action: str, request: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `execute_existing_case_action`, `type`, `type(self)`, `type(self)(gateway)._event`

### claim_task

[Исходник: api/wms_api_server/app/services/case_pick_service.py:176](../../../api/wms_api_server/app/services/case_pick_service.py#L176)

```python
claim_task(self, case_pick_task_id: int, request: CasePickTaskActionRequest) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self._resource_action`

### start_task

[Исходник: api/wms_api_server/app/services/case_pick_service.py:179](../../../api/wms_api_server/app/services/case_pick_service.py#L179)

```python
start_task(self, case_pick_task_id: int, request: CasePickTaskActionRequest) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self._resource_action`

### confirm_line

[Исходник: api/wms_api_server/app/services/case_pick_service.py:182](../../../api/wms_api_server/app/services/case_pick_service.py#L182)

```python
confirm_line(self, case_pick_task_id: int, line_id: int, request: CasePickLineConfirmRequest) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `post_existing_case_pick`, `str`

### short_line

[Исходник: api/wms_api_server/app/services/case_pick_service.py:196](../../../api/wms_api_server/app/services/case_pick_service.py#L196)

```python
short_line(self, case_pick_task_id: int, line_id: int, request: CasePickLineShortRequest) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CasePickService`, `CasePickService(bound)._short_line_locked`, `Decimal`, `HTTPException`, `TransactionGateway`, `assert_case_task_access`, `bound.fetch_all`, `case_resource_context`, `short_report_replay`, `str`, `warehouse_metadata_transaction`

### _short_line_locked

[Исходник: api/wms_api_server/app/services/case_pick_service.py:226](../../../api/wms_api_server/app/services/case_pick_service.py#L226)

```python
_short_line_locked(self, case_pick_task_id: int, line_id: int, request: CasePickLineShortRequest, approval_pending: bool=False) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `HTTPException`, `line.get`, `max`, `self._event`, `self._line_for_update`, `self._refresh_task_totals`, `self.gateway.call_number_plsql`, `self.gateway.execute`, `self.gateway.fetch_all`, `short_report_replay`, `str`

### close_task

[Исходник: api/wms_api_server/app/services/case_pick_service.py:295](../../../api/wms_api_server/app/services/case_pick_service.py#L295)

```python
close_task(self, case_pick_task_id: int, request: CasePickTaskActionRequest) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `close_existing_case_carrier`

### transfer_task

[Исходник: api/wms_api_server/app/services/case_pick_service.py:301](../../../api/wms_api_server/app/services/case_pick_service.py#L301)

```python
transfer_task(self, case_pick_task_id: int, request: CasePickTransferRequest) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self._resource_action`

### list_shorts

[Исходник: api/wms_api_server/app/services/case_pick_service.py:304](../../../api/wms_api_server/app/services/case_pick_service.py#L304)

```python
list_shorts(self, status: str | None=None, limit: int=200) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `legacy_case_reads`, `legacy_case_reads(self.gateway).list_shorts`

### approve_short

[Исходник: api/wms_api_server/app/services/case_pick_service.py:308](../../../api/wms_api_server/app/services/case_pick_service.py#L308)

```python
approve_short(self, short_id: int, request: CasePickShortDecisionRequest) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `post_existing_case_short_approval`

### reject_short

[Исходник: api/wms_api_server/app/services/case_pick_service.py:313](../../../api/wms_api_server/app/services/case_pick_service.py#L313)

```python
reject_short(self, short_id: int, request: CasePickShortDecisionRequest) -> dict[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CasePickService`, `CasePickService(bound)._reject_short_locked`, `HTTPException`, `TransactionGateway`, `assert_case_task_access`, `bound.fetch_all`, `warehouse_metadata_transaction`

### _reject_short_locked

[Исходник: api/wms_api_server/app/services/case_pick_service.py:329](../../../api/wms_api_server/app/services/case_pick_service.py#L329)

```python
_reject_short_locked(self, short_id: int, request: CasePickShortDecisionRequest) -> dict[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.execute`

### list_pallet_types

[Исходник: api/wms_api_server/app/services/case_pick_service.py:345](../../../api/wms_api_server/app/services/case_pick_service.py#L345)

```python
list_pallet_types(self, active_only: int | None=None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### upsert_pallet_type

[Исходник: api/wms_api_server/app/services/case_pick_service.py:366](../../../api/wms_api_server/app/services/case_pick_service.py#L366)

```python
upsert_pallet_type(self, request: PalletTypeUpsertRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `upsert_existing_pallet_type`

### _line_for_update

[Исходник: api/wms_api_server/app/services/case_pick_service.py:370](../../../api/wms_api_server/app/services/case_pick_service.py#L370)

```python
_line_for_update(self, case_pick_task_id: int, line_id: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `line.get`, `self.gateway.fetch_all`

### _validate_line_scan

[Исходник: api/wms_api_server/app/services/case_pick_service.py:387](../../../api/wms_api_server/app/services/case_pick_service.py#L387)

```python
_validate_line_scan(self, line: dict[str, Any], request: CasePickLineConfirmRequest) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `line.get`, `request.scan_cell.upper`, `request.scan_product.upper`, `str`, `str(line.get('articul') or '').upper`, `str(line['cell_code']).upper`

### _refresh_task_totals

[Исходник: api/wms_api_server/app/services/case_pick_service.py:400](../../../api/wms_api_server/app/services/case_pick_service.py#L400)

```python
_refresh_task_totals(self, case_pick_task_id: int, actor: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.execute`

### _create_inventory_task_for_short

[Исходник: api/wms_api_server/app/services/case_pick_service.py:438](../../../api/wms_api_server/app/services/case_pick_service.py#L438)

```python
_create_inventory_task_for_short(self, short: dict[str, Any], actor: str) -> int | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `int`, `self.gateway.call_number_plsql`, `self.gateway.fetch_all`, `settings[0].get`, `short.get`

### _offline_event_exists

[Исходник: api/wms_api_server/app/services/case_pick_service.py:480](../../../api/wms_api_server/app/services/case_pick_service.py#L480)

```python
_offline_event_exists(self, offline_event_id: str) -> bool
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `bool`, `self.gateway.fetch_all`

### _event

[Исходник: api/wms_api_server/app/services/case_pick_service.py:492](../../../api/wms_api_server/app/services/case_pick_service.py#L492)

```python
_event(self, case_pick_task_id: int | None, line_id: int | None, event_type: str, request: Any, actor: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `write_existing_case_event`

### _trim_text

[Исходник: api/wms_api_server/app/services/customer_order_service.py:9](../../../api/wms_api_server/app/services/customer_order_service.py#L9)

```python
_trim_text(value: Any, max_len: int, upper: bool=False) -> str | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `str`, `text.upper`

### __init__

[Исходник: api/wms_api_server/app/services/customer_order_service.py:17](../../../api/wms_api_server/app/services/customer_order_service.py#L17)

```python
__init__(self, gateway: OracleGateway | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`

### list_customers

[Исходник: api/wms_api_server/app/services/customer_order_service.py:20](../../../api/wms_api_server/app/services/customer_order_service.py#L20)

```python
list_customers(self, search: str | None=None, limit: int=200) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `conditions.append`, `max`, `min`, `search.upper`, `self.gateway.fetch_all`

### create_customer

[Исходник: api/wms_api_server/app/services/customer_order_service.py:63](../../../api/wms_api_server/app/services/customer_order_service.py#L63)

```python
create_customer(self, request: CustomerCreateRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_trim_text`, `request.model_dump`, `self.gateway.call_number_plsql`

### update_customer

[Исходник: api/wms_api_server/app/services/customer_order_service.py:100](../../../api/wms_api_server/app/services/customer_order_service.py#L100)

```python
update_customer(self, customer_id: int, request: CustomerUpdateRequest) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `',\n                     '.join`, `getattr`, `number_fields.items`, `self.gateway.execute_plsql`, `set_clauses.append`, `str`, `string_fields.items`, `value.upper`

### create_customer_address

[Исходник: api/wms_api_server/app/services/customer_order_service.py:160](../../../api/wms_api_server/app/services/customer_order_service.py#L160)

```python
create_customer_address(self, customer_id: int, request: CustomerAddressCreateRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_trim_text`, `request.model_dump`, `self.gateway.call_number_plsql`

### get_customer

[Исходник: api/wms_api_server/app/services/customer_order_service.py:194](../../../api/wms_api_server/app/services/customer_order_service.py#L194)

```python
get_customer(self, customer_id: int) -> dict[str, Any] | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### list_customer_orders

[Исходник: api/wms_api_server/app/services/customer_order_service.py:265](../../../api/wms_api_server/app/services/customer_order_service.py#L265)

```python
list_customer_orders(self, status: str | None=None, order_no: str | None=None, legacy_order_id: int | None=None, limit: int=200) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `build_customer_order_read_service`, `build_customer_order_read_service(self.gateway).list_rows`

### get_customer_order

[Исходник: api/wms_api_server/app/services/customer_order_service.py:273](../../../api/wms_api_server/app/services/customer_order_service.py#L273)

```python
get_customer_order(self, customer_order_id: int) -> dict[str, Any] | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `build_customer_order_read_service`, `build_customer_order_read_service(self.gateway).detail_rows`

### import_legacy_order

[Исходник: api/wms_api_server/app/services/customer_order_service.py:278](../../../api/wms_api_server/app/services/customer_order_service.py#L278)

```python
import_legacy_order(self, legacy_order_id: int, created_by: str | None=None) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.call_number_plsql`

### get_fulfillment

[Исходник: api/wms_api_server/app/services/customer_order_service.py:291](../../../api/wms_api_server/app/services/customer_order_service.py#L291)

```python
get_fulfillment(self, customer_order_id: int, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `build_fulfillment_read_service`, `build_fulfillment_read_service(self.gateway).get`

### _trim_text

[Исходник: api/wms_api_server/app/services/customer_rule_service.py:13](../../../api/wms_api_server/app/services/customer_rule_service.py#L13)

```python
_trim_text(value: Any, max_len: int, upper: bool=False) -> str | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `str`, `text.upper`

### __init__

[Исходник: api/wms_api_server/app/services/customer_rule_service.py:21](../../../api/wms_api_server/app/services/customer_rule_service.py#L21)

```python
__init__(self, gateway: OracleGateway | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`

### list_product_rules

[Исходник: api/wms_api_server/app/services/customer_rule_service.py:24](../../../api/wms_api_server/app/services/customer_rule_service.py#L24)

```python
list_product_rules(self, customer_id: int) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### create_product_rule

[Исходник: api/wms_api_server/app/services/customer_rule_service.py:56](../../../api/wms_api_server/app/services/customer_rule_service.py#L56)

```python
create_product_rule(self, customer_id: int, request: CustomerProductRuleCreateRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_trim_text`, `request.model_dump`, `self.gateway.call_number_plsql`

### list_shelf_life_rules

[Исходник: api/wms_api_server/app/services/customer_rule_service.py:96](../../../api/wms_api_server/app/services/customer_rule_service.py#L96)

```python
list_shelf_life_rules(self, customer_id: int) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### create_shelf_life_rule

[Исходник: api/wms_api_server/app/services/customer_rule_service.py:118](../../../api/wms_api_server/app/services/customer_rule_service.py#L118)

```python
create_shelf_life_rule(self, customer_id: int, request: CustomerShelfLifeRuleCreateRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_trim_text`, `request.model_dump`, `self.gateway.call_number_plsql`

### list_stack_rules

[Исходник: api/wms_api_server/app/services/customer_rule_service.py:149](../../../api/wms_api_server/app/services/customer_rule_service.py#L149)

```python
list_stack_rules(self, customer_id: int) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### create_stack_rule

[Исходник: api/wms_api_server/app/services/customer_rule_service.py:179](../../../api/wms_api_server/app/services/customer_rule_service.py#L179)

```python
create_stack_rule(self, customer_id: int, request: CustomerStackRuleCreateRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_trim_text`, `request.model_dump`, `self.gateway.call_number_plsql`

### list_vehicle_rules

[Исходник: api/wms_api_server/app/services/customer_rule_service.py:217](../../../api/wms_api_server/app/services/customer_rule_service.py#L217)

```python
list_vehicle_rules(self, customer_id: int) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### create_vehicle_rule

[Исходник: api/wms_api_server/app/services/customer_rule_service.py:244](../../../api/wms_api_server/app/services/customer_rule_service.py#L244)

```python
create_vehicle_rule(self, customer_id: int, request: CustomerVehicleRuleCreateRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `request.model_dump`, `self.gateway.call_number_plsql`

### list_vehicle_types

[Исходник: api/wms_api_server/app/services/customer_rule_service.py:269](../../../api/wms_api_server/app/services/customer_rule_service.py#L269)

```python
list_vehicle_types(self, active_only: int | None=None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `int`, `self.gateway.fetch_all`

### create_vehicle_type

[Исходник: api/wms_api_server/app/services/customer_rule_service.py:288](../../../api/wms_api_server/app/services/customer_rule_service.py#L288)

```python
create_vehicle_type(self, request: VehicleTypeCreateRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `request.model_dump`, `self.gateway.call_number_plsql`

### _upper_keys

[Исходник: api/wms_api_server/app/services/distance_matrix_service.py:22](../../../api/wms_api_server/app/services/distance_matrix_service.py#L22)

```python
_upper_keys(row: dict[str, Any]) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `row.items`, `str`, `str(key).upper`

### __init__

[Исходник: api/wms_api_server/app/services/distance_matrix_service.py:27](../../../api/wms_api_server/app/services/distance_matrix_service.py#L27)

```python
__init__(self, gateway: OracleGateway | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`

### _fetch_all

[Исходник: api/wms_api_server/app/services/distance_matrix_service.py:30](../../../api/wms_api_server/app/services/distance_matrix_service.py#L30)

```python
_fetch_all(self, sql: str, params: dict[str, Any] | None=None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_upper_keys`, `self.gateway.fetch_all`

### get_geocoded_addresses

[Исходник: api/wms_api_server/app/services/distance_matrix_service.py:33](../../../api/wms_api_server/app/services/distance_matrix_service.py#L33)

```python
get_geocoded_addresses(self) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self._fetch_all`

### _count_fresh_pairs

[Исходник: api/wms_api_server/app/services/distance_matrix_service.py:44](../../../api/wms_api_server/app/services/distance_matrix_service.py#L44)

```python
_count_fresh_pairs(self, source: str, max_age_hours: int | None) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `int`, `self._fetch_all`

### _fetch_fresh_pair_keys

[Исходник: api/wms_api_server/app/services/distance_matrix_service.py:70](../../../api/wms_api_server/app/services/distance_matrix_service.py#L70)

```python
_fetch_fresh_pair_keys(self, source: str, max_age_hours: int | None) -> set[tuple[str, str]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self._fetch_all`, `str`

### rebuild

[Исходник: api/wms_api_server/app/services/distance_matrix_service.py:96](../../../api/wms_api_server/app/services/distance_matrix_service.py#L96)

```python
rebuild(self, source: str='auto', *, force: bool=False, max_age_hours: int | None=24 * 30) -> dict[str, Any]
```

Пересчитывает матрицу и сохраняет в Oracle.

source: 'auto' | 'haversine' | 'osrm' | 'valhalla'
Возвращает total pairs and how many pairs were actually recomputed.

Вызывает: `HaversineProvider`, `OsrmProvider`, `ValhallaProvider`, `float`, `get_active_provider`, `len`, `matrix_merge_statements`, `provider.build_cost_matrix`, `self._count_fresh_pairs`, `self._fetch_fresh_pair_keys`, `self.gateway.execute_many`, `self.get_geocoded_addresses`, `set`

### get_matrix_as_dict

[Исходник: api/wms_api_server/app/services/distance_matrix_service.py:208](../../../api/wms_api_server/app/services/distance_matrix_service.py#L208)

```python
get_matrix_as_dict(self, addr_list: list[str]) -> dict[tuple[str, str], float]
```

Загружает подматрицу из Oracle для заданных адресов.

Вызывает: `','.join`, `enumerate`, `float`, `len`, `range`, `self._fetch_all`

### _model_dict

[Исходник: api/wms_api_server/app/services/finished_goods_service.py:374](../../../api/wms_api_server/app/services/finished_goods_service.py#L374)

```python
_model_dict(model) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `hasattr`, `model.dict`, `model.model_dump`

### __init__

[Исходник: api/wms_api_server/app/services/finished_goods_service.py:8](../../../api/wms_api_server/app/services/finished_goods_service.py#L8)

```python
__init__(self, gateway: OracleGateway | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`

### list_skus

[Исходник: api/wms_api_server/app/services/finished_goods_service.py:11](../../../api/wms_api_server/app/services/finished_goods_service.py#L11)

```python
list_skus(self, search: str | None=None, only_active: int | None=1, only_with_stock: int | None=None, limit: int=200) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `conditions.append`, `int`, `max`, `min`, `search.upper`, `self.gateway.fetch_all`

### update_sku_settings

[Исходник: api/wms_api_server/app/services/finished_goods_service.py:118](../../../api/wms_api_server/app/services/finished_goods_service.py#L118)

```python
update_sku_settings(self, articul: str, request: FinishedGoodsSkuSettingsUpdateRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_model_dict`, `self.gateway.execute`

### list_warehouses

[Исходник: api/wms_api_server/app/services/finished_goods_service.py:175](../../../api/wms_api_server/app/services/finished_goods_service.py#L175)

```python
list_warehouses(self, limit: int=200) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `max`, `min`, `self.gateway.fetch_all`

### list_batches

[Исходник: api/wms_api_server/app/services/finished_goods_service.py:210](../../../api/wms_api_server/app/services/finished_goods_service.py#L210)

```python
list_batches(self, prod_batch_id: int | None=None, articul: str | None=None, batch_no: str | None=None, quality_status: str | None=None, limit: int=200) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `articul.upper`, `batch_no.upper`, `conditions.append`, `int`, `max`, `min`, `quality_status.upper`, `self.gateway.fetch_all`

### list_remains

[Исходник: api/wms_api_server/app/services/finished_goods_service.py:291](../../../api/wms_api_server/app/services/finished_goods_service.py#L291)

```python
list_remains(self, prod_batch_id: int | None=None, articul: str | None=None, ware_id: int | None=None, ware_ids: str | None=None, prod_batch_no: str | None=None, cell: str | None=None, quality_status: str | None=None, only_available: int | None=1, limit: int=500) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `', '.join`, `articul.upper`, `cell.upper`, `conditions.append`, `enumerate`, `int`, `max`, `min`, `placeholders.append`, `prod_batch_no.upper`, `quality_status.upper`, `self.gateway.fetch_all`, `value.strip`, `value.strip().isdigit`, `ware_ids.split`

### haversine_m

[Исходник: api/wms_api_server/app/services/geofencing.py:17](../../../api/wms_api_server/app/services/geofencing.py#L17)

```python
haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float
```

Расстояние в метрах между двумя точками (WGS84).

Вызывает: `math.atan2`, `math.cos`, `math.radians`, `math.sin`, `math.sqrt`

### check_geofences

[Исходник: api/wms_api_server/app/services/geofencing.py:26](../../../api/wms_api_server/app/services/geofencing.py#L26)

```python
check_geofences(vehicle_id: int, lat: float, lon: float, gateway: Any) -> list[dict]
```

Sprint 118: проверить геозоны активных рейсов для машины.
Возвращает список событий: {event: 'enter'|'exit', addr_id, task_id, addr}.
GPS наблюдение не подтверждает выполнение UNLOAD без точной привязки к операции.

Вызывает: `_GEO_STATE.get`, `events.append`, `events[-1].update`, `float`, `gateway.fetch_all`, `haversine_m`, `int`, `math.isfinite`, `new_inside.add`, `r.get`, `set`, `str`

### clamp_limit

[Исходник: api/wms_api_server/app/services/mes_service.py:1102](../../../api/wms_api_server/app/services/mes_service.py#L1102)

```python
clamp_limit(value: int) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `max`, `min`

### _model_dict

[Исходник: api/wms_api_server/app/services/mes_service.py:1106](../../../api/wms_api_server/app/services/mes_service.py#L1106)

```python
_model_dict(model) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `hasattr`, `model.dict`, `model.model_dump`

### __init__

[Исходник: api/wms_api_server/app/services/mes_service.py:22](../../../api/wms_api_server/app/services/mes_service.py#L22)

```python
__init__(self, gateway: OracleGateway | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`

### create_order

[Исходник: api/wms_api_server/app/services/mes_service.py:25](../../../api/wms_api_server/app/services/mes_service.py#L25)

```python
create_order(self, request: MesProductionOrderCreateRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_model_dict`, `self.gateway.call_number_plsql`

### issue_raw

[Исходник: api/wms_api_server/app/services/mes_service.py:51](../../../api/wms_api_server/app/services/mes_service.py#L51)

```python
issue_raw(self, production_order_id: int, request: MesRawIssueRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_model_dict`, `self.gateway.call_number_plsql`

### complete_order

[Исходник: api/wms_api_server/app/services/mes_service.py:71](../../../api/wms_api_server/app/services/mes_service.py#L71)

```python
complete_order(self, production_order_id: int, request: MesCompleteOrderRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `json.dumps`, `pallet.model_dump`, `self._create_fg_storage_warehouse_tasks`, `self._ensure_completion_trace_links`, `self.gateway.call_number_plsql`

### apply_wms

[Исходник: api/wms_api_server/app/services/mes_service.py:101](../../../api/wms_api_server/app/services/mes_service.py#L101)

```python
apply_wms(self, production_order_id: int, request: MesApplyWmsRequest, actor: str | None=None) -> dict | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `apply_mes_movements`

### retry_movement

[Исходник: api/wms_api_server/app/services/mes_service.py:106](../../../api/wms_api_server/app/services/mes_service.py#L106)

```python
retry_movement(self, movement_id: int, request: MesRetryMovementRequest) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_model_dict`, `self.gateway.execute_plsql`

### get_order

[Исходник: api/wms_api_server/app/services/mes_service.py:119](../../../api/wms_api_server/app/services/mes_service.py#L119)

```python
get_order(self, production_order_id: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`, `self.list_movements`, `self.list_order_lines`

### list_orders

[Исходник: api/wms_api_server/app/services/mes_service.py:140](../../../api/wms_api_server/app/services/mes_service.py#L140)

```python
list_orders(self, status: str | None=None, target_articul: str | None=None, limit: int=100) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `clamp_limit`, `conditions.append`, `self.gateway.fetch_all`, `status.upper`, `target_articul.upper`

### list_order_lines

[Исходник: api/wms_api_server/app/services/mes_service.py:172](../../../api/wms_api_server/app/services/mes_service.py#L172)

```python
list_order_lines(self, production_order_id: int) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### list_movements

[Исходник: api/wms_api_server/app/services/mes_service.py:186](../../../api/wms_api_server/app/services/mes_service.py#L186)

```python
list_movements(self, production_order_id: int | None=None, status: str | None=None, movement_type: str | None=None, limit: int=100) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `clamp_limit`, `conditions.append`, `movement_type.upper`, `self.gateway.fetch_all`, `status.upper`

### calculate_raw_supply

[Исходник: api/wms_api_server/app/services/mes_service.py:224](../../../api/wms_api_server/app/services/mes_service.py#L224)

```python
calculate_raw_supply(self, production_order_id: int, request: MesRawSupplyCalculateRequest) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `calculate_existing_mes_supply`

### get_raw_supply

[Исходник: api/wms_api_server/app/services/mes_service.py:233](../../../api/wms_api_server/app/services/mes_service.py#L233)

```python
get_raw_supply(self, production_order_id: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `self.gateway.fetch_all`, `self.get_order`, `self.list_raw_transfer_tasks`

### release_to_production

[Исходник: api/wms_api_server/app/services/mes_service.py:279](../../../api/wms_api_server/app/services/mes_service.py#L279)

```python
release_to_production(self, production_order_id: int, request: MesReleaseToProductionRequest) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `release_supply`

### list_raw_transfer_tasks

[Исходник: api/wms_api_server/app/services/mes_service.py:288](../../../api/wms_api_server/app/services/mes_service.py#L288)

```python
list_raw_transfer_tasks(self, production_order_id: int | None=None, status: str | None=None, limit: int=100) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `clamp_limit`, `conditions.append`, `self.gateway.fetch_all`, `status.upper`

### list_raw_shortages

[Исходник: api/wms_api_server/app/services/mes_service.py:317](../../../api/wms_api_server/app/services/mes_service.py#L317)

```python
list_raw_shortages(self, production_order_id: int | None=None, status: str | None=None, raw_articul: str | None=None, limit: int=100) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `clamp_limit`, `conditions.append`, `raw_articul.upper`, `self.gateway.fetch_all`, `status.upper`

### get_raw_transfer_task_or_404

[Исходник: api/wms_api_server/app/services/mes_service.py:356](../../../api/wms_api_server/app/services/mes_service.py#L356)

```python
get_raw_transfer_task_or_404(self, task_id: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `self.gateway.fetch_all`

### confirm_raw_transfer_task

[Исходник: api/wms_api_server/app/services/mes_service.py:369](../../../api/wms_api_server/app/services/mes_service.py#L369)

```python
confirm_raw_transfer_task(self, task_id: int, request: MesRawTransferTaskConfirmRequest, sync_warehouse_task: bool=True) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `int`, `post_existing_mes_task`, `self.get_raw_transfer_task_or_404`

### cancel_raw_transfer_task

[Исходник: api/wms_api_server/app/services/mes_service.py:380](../../../api/wms_api_server/app/services/mes_service.py#L380)

```python
cancel_raw_transfer_task(self, task_id: int, request: MesRawTransferTaskCancelRequest) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `post_existing_mes_task`, `self.get_raw_transfer_task_or_404`

### _clear_raw_supply_calculation

[Исходник: api/wms_api_server/app/services/mes_service.py:390](../../../api/wms_api_server/app/services/mes_service.py#L390)

```python
_clear_raw_supply_calculation(self, production_order_id: int, updated_by: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `release_existing_document_reservations`, `self.gateway.execute`

### _issued_raw_qty

[Исходник: api/wms_api_server/app/services/mes_service.py:418](../../../api/wms_api_server/app/services/mes_service.py#L418)

```python
_issued_raw_qty(self, production_order_id: int, line: dict[str, Any]) -> float
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `float`, `line.get`, `self.gateway.fetch_all`, `str`, `str(line.get('component_articul') or '').upper`

### _assert_legacy_reservation_builder

[Исходник: api/wms_api_server/app/services/mes_service.py:439](../../../api/wms_api_server/app/services/mes_service.py#L439)

```python
_assert_legacy_reservation_builder(self) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`

### _create_soft_raw_reservation

[Исходник: api/wms_api_server/app/services/mes_service.py:442](../../../api/wms_api_server/app/services/mes_service.py#L442)

```python
_create_soft_raw_reservation(self, production_order_id: int, line: dict[str, Any], raw_articul: str, qty: float, unit_code: str | None, created_by: str) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `line.get`, `self._assert_legacy_reservation_builder`, `self._next_sequence_value`, `self.gateway.execute`

### _find_raw_candidates

[Исходник: api/wms_api_server/app/services/mes_service.py:477](../../../api/wms_api_server/app/services/mes_service.py#L477)

```python
_find_raw_candidates(self, raw_articul: str, limit: int=200) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `max`, `min`, `raw_articul.upper`, `self.gateway.fetch_all`

### _insert_raw_candidate

[Исходник: api/wms_api_server/app/services/mes_service.py:516](../../../api/wms_api_server/app/services/mes_service.py#L516)

```python
_insert_raw_candidate(self, demand_id: int, production_order_id: int, raw_articul: str, candidate: dict[str, Any], suggested_qty: float, sort_order: int) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `candidate.get`, `self._next_sequence_value`, `self.gateway.execute`

### _insert_raw_shortage

[Исходник: api/wms_api_server/app/services/mes_service.py:561](../../../api/wms_api_server/app/services/mes_service.py#L561)

```python
_insert_raw_shortage(self, production_order_id: int, demand_id: int, raw_articul: str, required_qty: float, issued_qty: float, available_qty: float, shortage_qty: float, unit_code: str | None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self._next_sequence_value`, `self.gateway.execute`

### _active_mes_task_exists

[Исходник: api/wms_api_server/app/services/mes_service.py:596](../../../api/wms_api_server/app/services/mes_service.py#L596)

```python
_active_mes_task_exists(self, production_order_id: int, candidate: dict[str, Any]) -> bool
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `bool`, `candidate.get`, `int`, `self.gateway.fetch_all`

### _create_hard_raw_reservation

[Исходник: api/wms_api_server/app/services/mes_service.py:614](../../../api/wms_api_server/app/services/mes_service.py#L614)

```python
_create_hard_raw_reservation(self, production_order_id: int, candidate: dict[str, Any], created_by: str) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `candidate.get`, `float`, `self._assert_legacy_reservation_builder`, `self._next_sequence_value`, `self.gateway.execute`

### _create_raw_transfer_task

[Исходник: api/wms_api_server/app/services/mes_service.py:657](../../../api/wms_api_server/app/services/mes_service.py#L657)

```python
_create_raw_transfer_task(self, production_order_id: int, candidate: dict[str, Any], reservation_id: int, to_ware_id: int | None, to_cell: str, created_by: str) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `candidate.get`, `self._next_sequence_value`, `self.gateway.execute`

### _create_raw_warehouse_tasks

[Исходник: api/wms_api_server/app/services/mes_service.py:707](../../../api/wms_api_server/app/services/mes_service.py#L707)

```python
_create_raw_warehouse_tasks(self, production_order_id: int) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.execute`

### _sync_warehouse_task_from_raw_task

[Исходник: api/wms_api_server/app/services/mes_service.py:736](../../../api/wms_api_server/app/services/mes_service.py#L736)

```python
_sync_warehouse_task_from_raw_task(self, source_task_id: int, status: str, updated_by: str, fact_qty: float | None=None, error_text: str | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.execute`

### _create_fg_storage_warehouse_tasks

[Исходник: api/wms_api_server/app/services/mes_service.py:780](../../../api/wms_api_server/app/services/mes_service.py#L780)

```python
_create_fg_storage_warehouse_tasks(self, production_order_id: int, request: MesCompleteOrderRequest) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `next`, `self.gateway.execute`

### _next_sequence_value

[Исходник: api/wms_api_server/app/services/mes_service.py:841](../../../api/wms_api_server/app/services/mes_service.py#L841)

```python
_next_sequence_value(self, sequence_name: str, alias: str) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `alias.lower`, `int`, `self.gateway.fetch_all`

### get_genealogy

[Исходник: api/wms_api_server/app/services/mes_service.py:845](../../../api/wms_api_server/app/services/mes_service.py#L845)

```python
get_genealogy(self, production_order_id: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `order.get`, `self.gateway.fetch_all`, `self.get_order`

### _ensure_completion_trace_links

[Исходник: api/wms_api_server/app/services/mes_service.py:895](../../../api/wms_api_server/app/services/mes_service.py#L895)

```python
_ensure_completion_trace_links(self, production_order_id: int, request: MesCompleteOrderRequest) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `order.get`, `pallet.get`, `raw.get`, `rows[0].get`, `self._add_trace_edge_once`, `self._find_completion_trace_event_id`, `self.gateway.fetch_all`, `str`

### _find_completion_trace_event_id

[Исходник: api/wms_api_server/app/services/mes_service.py:1028](../../../api/wms_api_server/app/services/mes_service.py#L1028)

```python
_find_completion_trace_event_id(self, production_order_id: int) -> int | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `int`, `self.gateway.fetch_all`, `str`

### _add_trace_edge_once

[Исходник: api/wms_api_server/app/services/mes_service.py:1046](../../../api/wms_api_server/app/services/mes_service.py#L1046)

```python
_add_trace_edge_once(self, from_entity_type: str, from_entity_id: str, to_entity_type: str, to_entity_id: str, edge_type: str, quantity: Any, unit_code: str | None, trace_event_id: int | None, created_by: str | None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.execute_plsql`

### __init__

[Исходник: api/wms_api_server/app/services/outbox_service.py:8](../../../api/wms_api_server/app/services/outbox_service.py#L8)

```python
__init__(self, gateway: OracleGateway | None=None, adapter: RegulatoryAdapter | None=None, journal: OutboxResponseJournal | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `OutboxDelivery`, `OutboxResponseJournal`, `build_regulatory_adapter`

### process_next

[Исходник: api/wms_api_server/app/services/outbox_service.py:15](../../../api/wms_api_server/app/services/outbox_service.py#L15)

```python
process_next(self, worker_id: str, target_system: str | None=None) -> dict[str, Any] | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `event.get`, `getattr`, `regulatory_delivery_decision`, `self.adapter.send`, `self.delivery.begin`, `self.delivery.claim`, `self.delivery.event`, `self.journal.finalize`, `self.journal.ready`, `self.journal.recover_one`, `self.journal.save`, `str`, `target_system.upper`, `type`

### __init__

[Исходник: api/wms_api_server/app/services/picking_service.py:23](../../../api/wms_api_server/app/services/picking_service.py#L23)

```python
__init__(self, gateway: OracleGateway | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`

### create_plan

[Исходник: api/wms_api_server/app/services/picking_service.py:26](../../../api/wms_api_server/app/services/picking_service.py#L26)

```python
create_plan(self, request: PickingPlanCreateRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `create_existing_pick_plan`

### cancel_plan

[Исходник: api/wms_api_server/app/services/picking_service.py:30](../../../api/wms_api_server/app/services/picking_service.py#L30)

```python
cancel_plan(self, pick_plan_id: int, updated_by: str | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.execute_plsql`

### create_wave

[Исходник: api/wms_api_server/app/services/picking_service.py:43](../../../api/wms_api_server/app/services/picking_service.py#L43)

```python
create_wave(self, request: PickWaveCreateRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `create_existing_wave`

### add_wave_plan

[Исходник: api/wms_api_server/app/services/picking_service.py:47](../../../api/wms_api_server/app/services/picking_service.py#L47)

```python
add_wave_plan(self, pick_wave_id: int, request: PickWaveAddPlanRequest) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `add_existing_wave_plan`

### preview_wave

[Исходник: api/wms_api_server/app/services/picking_service.py:51](../../../api/wms_api_server/app/services/picking_service.py#L51)

```python
preview_wave(self, pick_wave_id: int, request: PickWaveActionRequest) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.execute_plsql`

### _post_wave_command

[Исходник: api/wms_api_server/app/services/picking_service.py:64](../../../api/wms_api_server/app/services/picking_service.py#L64)

```python
_post_wave_command(self, command: str, wave_id: int, request: PickWaveActionRequest) -> bool
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `StockCommand`, `StockPosting`, `StockPosting().post`, `require_active_stock_release`

### launch_wave

[Исходник: api/wms_api_server/app/services/picking_service.py:81](../../../api/wms_api_server/app/services/picking_service.py#L81)

```python
launch_wave(self, pick_wave_id: int, request: PickWaveActionRequest) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CasePickService`, `CasePickService(self.gateway).ensure_wave_case_pick_tasks`, `self._enrich_replenishment_settings`, `self._hold_replenishment_rows_without_pick_face_capacity`, `self._post_wave_command`, `self._refresh_replenishment_deficit`, `self._release_cancelled_replenishment_source_reservations`, `self._release_next_replenishment_queue`, `self._reserve_replenishment_sources`, `self._sync_replenishment_warehouse_tasks`, `self.gateway.execute_plsql`

### release_minimax_replenishment

[Исходник: api/wms_api_server/app/services/picking_service.py:112](../../../api/wms_api_server/app/services/picking_service.py#L112)

```python
release_minimax_replenishment(self, pick_wave_id: int, request: PickWaveActionRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self._hold_replenishment_rows_without_pick_face_capacity`, `self._refresh_replenishment_deficit`, `self._release_cancelled_replenishment_source_reservations`, `self._release_next_replenishment_queue`, `self._reserve_replenishment_sources`, `self._sync_replenishment_warehouse_tasks`

### complete_wave_pick_task

[Исходник: api/wms_api_server/app/services/picking_service.py:123](../../../api/wms_api_server/app/services/picking_service.py#L123)

```python
complete_wave_pick_task(self, pick_wave_id: int, pick_task_id: int, request: PickTaskCompleteRequest) -> dict[str, str | int | float]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `WarehouseTaskStatusRequest`, `complete_existing_task`, `len`, `require_active_stock_release`, `self.gateway.fetch_all`, `types[0].get`

### release_wave_staging

[Исходник: api/wms_api_server/app/services/picking_service.py:164](../../../api/wms_api_server/app/services/picking_service.py#L164)

```python
release_wave_staging(self, pick_wave_id: int, request: PickWaveStagingReleaseRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `release_existing_wave_staging`

### _validate_pick_task_scans

[Исходник: api/wms_api_server/app/services/picking_service.py:168](../../../api/wms_api_server/app/services/picking_service.py#L168)

```python
_validate_pick_task_scans(self, task: dict[str, Any], request: PickTaskCompleteRequest) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `request.scanned_from_cell.upper`, `request.scanned_pallet.upper`, `request.scanned_to_cell.upper`, `str`, `str(task['source_cell_code']).upper`, `str(task['target_cell_code']).upper`, `str(value).upper`, `task.get`

### _apply_case_pick_stock_fact

[Исходник: api/wms_api_server/app/services/picking_service.py:180](../../../api/wms_api_server/app/services/picking_service.py#L180)

```python
_apply_case_pick_stock_fact(self, task: dict[str, Any], fact_qty: float) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`

### _enrich_replenishment_settings

[Исходник: api/wms_api_server/app/services/picking_service.py:183](../../../api/wms_api_server/app/services/picking_service.py#L183)

```python
_enrich_replenishment_settings(self, pick_wave_id: int, updated_by: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.execute`

### _refresh_replenishment_deficit

[Исходник: api/wms_api_server/app/services/picking_service.py:313](../../../api/wms_api_server/app/services/picking_service.py#L313)

```python
_refresh_replenishment_deficit(self, pick_wave_id: int, updated_by: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.execute`

### _reserve_replenishment_sources

[Исходник: api/wms_api_server/app/services/picking_service.py:513](../../../api/wms_api_server/app/services/picking_service.py#L513)

```python
_reserve_replenishment_sources(self, pick_wave_id: int, updated_by: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `require_active_stock_release`, `reserve_existing_wave_sources`, `route_existing_alternative_pick_faces`

### _release_cancelled_replenishment_source_reservations

[Исходник: api/wms_api_server/app/services/picking_service.py:520](../../../api/wms_api_server/app/services/picking_service.py#L520)

```python
_release_cancelled_replenishment_source_reservations(self, pick_wave_id: int, updated_by: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `release_existing_document_reservations`, `self.gateway.execute`

### _hold_replenishment_rows_without_pick_face_capacity

[Исходник: api/wms_api_server/app/services/picking_service.py:583](../../../api/wms_api_server/app/services/picking_service.py#L583)

```python
_hold_replenishment_rows_without_pick_face_capacity(self, pick_wave_id: int, updated_by: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `hold_existing_replenishment_capacity`

### _release_next_replenishment_queue

[Исходник: api/wms_api_server/app/services/picking_service.py:587](../../../api/wms_api_server/app/services/picking_service.py#L587)

```python
_release_next_replenishment_queue(self, pick_wave_id: int, updated_by: str, include_minimax: bool=True) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `isinstance`, `route_existing_alternative_pick_faces`, `self.gateway.execute`

### cancel_wave

[Исходник: api/wms_api_server/app/services/picking_service.py:731](../../../api/wms_api_server/app/services/picking_service.py#L731)

```python
cancel_wave(self, pick_wave_id: int, request: PickWaveActionRequest) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `request.model_dump`, `self._cancel_replenishment_warehouse_tasks`, `self._post_wave_command`, `self.gateway.execute_plsql`

### release_wave_reservations

[Исходник: api/wms_api_server/app/services/picking_service.py:748](../../../api/wms_api_server/app/services/picking_service.py#L748)

```python
release_wave_reservations(self, pick_wave_id: int, request: PickWaveActionRequest) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self._cancel_replenishment_warehouse_tasks`, `self._post_wave_command`, `self.gateway.execute_plsql`

### _sync_replenishment_warehouse_tasks

[Исходник: api/wms_api_server/app/services/picking_service.py:768](../../../api/wms_api_server/app/services/picking_service.py#L768)

```python
_sync_replenishment_warehouse_tasks(self, pick_wave_id: int, created_by: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `sync_existing_wave_tasks`

### _cancel_replenishment_warehouse_tasks

[Исходник: api/wms_api_server/app/services/picking_service.py:772](../../../api/wms_api_server/app/services/picking_service.py#L772)

```python
_cancel_replenishment_warehouse_tasks(self, pick_wave_id: int, cancelled_by: str, reason: str | None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `release_existing_document_reservations`, `self.gateway.execute`

### list_waves

[Исходник: api/wms_api_server/app/services/picking_service.py:835](../../../api/wms_api_server/app/services/picking_service.py#L835)

```python
list_waves(self, status: str | None=None, ware_id: int | None=None, customer_id: int | None=None, limit: int=100) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `conditions.append`, `max`, `min`, `self.gateway.fetch_all`, `status.upper`

### list_wave_candidates

[Исходник: api/wms_api_server/app/services/picking_service.py:901](../../../api/wms_api_server/app/services/picking_service.py#L901)

```python
list_wave_candidates(self, ware_id: int | None=None, route_id: int | None=None, dock_id: int | None=None, shipment_from: str | None=None, shipment_to: str | None=None, limit: int=100) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `conditions.append`, `max`, `min`, `self.gateway.fetch_all`

### get_wave_header

[Исходник: api/wms_api_server/app/services/picking_service.py:996](../../../api/wms_api_server/app/services/picking_service.py#L996)

```python
get_wave_header(self, pick_wave_id: int) -> dict[str, Any] | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `existing_wave_header`

### get_wave

[Исходник: api/wms_api_server/app/services/picking_service.py:1000](../../../api/wms_api_server/app/services/picking_service.py#L1000)

```python
get_wave(self, pick_wave_id: int) -> dict[str, Any] | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`, `self.get_wave_header`, `self.list_wave_demand`, `self.list_wave_lines`, `self.list_wave_replenishment_tasks`, `self.list_wave_reservations`, `self.list_wave_shortages`, `self.list_wave_tasks`

### get_wave_readiness

[Исходник: api/wms_api_server/app/services/picking_service.py:1030](../../../api/wms_api_server/app/services/picking_service.py#L1030)

```python
get_wave_readiness(self, pick_wave_id: int) -> dict[str, Any] | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `blockers.append`, `float`, `int`, `self.gateway.fetch_all`, `sum`

### list_wave_lines

[Исходник: api/wms_api_server/app/services/picking_service.py:1204](../../../api/wms_api_server/app/services/picking_service.py#L1204)

```python
list_wave_lines(self, pick_wave_id: int) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### list_wave_demand

[Исходник: api/wms_api_server/app/services/picking_service.py:1226](../../../api/wms_api_server/app/services/picking_service.py#L1226)

```python
list_wave_demand(self, pick_wave_id: int) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### list_wave_reservations

[Исходник: api/wms_api_server/app/services/picking_service.py:1246](../../../api/wms_api_server/app/services/picking_service.py#L1246)

```python
list_wave_reservations(self, pick_wave_id: int, limit: int=200) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `max`, `min`, `self.gateway.fetch_all`

### list_wave_replenishment_tasks

[Исходник: api/wms_api_server/app/services/picking_service.py:1285](../../../api/wms_api_server/app/services/picking_service.py#L1285)

```python
list_wave_replenishment_tasks(self, pick_wave_id: int, limit: int=200) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `max`, `min`, `self.gateway.fetch_all`

### list_wave_tasks

[Исходник: api/wms_api_server/app/services/picking_service.py:1382](../../../api/wms_api_server/app/services/picking_service.py#L1382)

```python
list_wave_tasks(self, pick_wave_id: int, limit: int=200) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `max`, `min`, `self.gateway.fetch_all`

### list_wave_shortages

[Исходник: api/wms_api_server/app/services/picking_service.py:1452](../../../api/wms_api_server/app/services/picking_service.py#L1452)

```python
list_wave_shortages(self, pick_wave_id: int, limit: int=200) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `max`, `min`, `self.gateway.fetch_all`

### list_wave_audit

[Исходник: api/wms_api_server/app/services/picking_service.py:1480](../../../api/wms_api_server/app/services/picking_service.py#L1480)

```python
list_wave_audit(self, pick_wave_id: int, limit: int=200) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `max`, `min`, `self.gateway.fetch_all`

### list_plans

[Исходник: api/wms_api_server/app/services/picking_service.py:1501](../../../api/wms_api_server/app/services/picking_service.py#L1501)

```python
list_plans(self, status: str | None=None, customer_order_id: int | None=None, customer_id: int | None=None, limit: int=100) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `conditions.append`, `max`, `min`, `self.gateway.fetch_all`, `status.upper`

### get_plan

[Исходник: api/wms_api_server/app/services/picking_service.py:1579](../../../api/wms_api_server/app/services/picking_service.py#L1579)

```python
get_plan(self, pick_plan_id: int) -> dict[str, Any] | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`, `self.list_reservations`, `self.list_shortages`

### list_reservations

[Исходник: api/wms_api_server/app/services/picking_service.py:1682](../../../api/wms_api_server/app/services/picking_service.py#L1682)

```python
list_reservations(self, pick_plan_id: int | None=None, status: str | None=None, customer_order_id: int | None=None, pallet_uid: str | None=None, articul: str | None=None, limit: int=200) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `articul.upper`, `conditions.append`, `max`, `min`, `pallet_uid.upper`, `self.gateway.fetch_all`, `status.upper`

### list_routes

[Исходник: api/wms_api_server/app/services/picking_service.py:1748](../../../api/wms_api_server/app/services/picking_service.py#L1748)

```python
list_routes(self, ware_id: int | None=None, active_only: int | None=None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `conditions.append`, `int`, `self.gateway.fetch_all`

### upsert_route

[Исходник: api/wms_api_server/app/services/picking_service.py:1792](../../../api/wms_api_server/app/services/picking_service.py#L1792)

```python
upsert_route(self, request: PickRouteUpsertRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `request.model_dump`, `self.gateway.call_number_plsql`

### list_route_cells

[Исходник: api/wms_api_server/app/services/picking_service.py:1810](../../../api/wms_api_server/app/services/picking_service.py#L1810)

```python
list_route_cells(self, pick_route_id: int | None=None, ware_id: int | None=None, active_only: int | None=None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `conditions.append`, `int`, `self.gateway.fetch_all`

### upsert_route_cell

[Исходник: api/wms_api_server/app/services/picking_service.py:1854](../../../api/wms_api_server/app/services/picking_service.py#L1854)

```python
upsert_route_cell(self, request: PickRouteCellUpsertRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `request.model_dump`, `self.gateway.call_number_plsql`

### list_pick_faces

[Исходник: api/wms_api_server/app/services/picking_service.py:1875](../../../api/wms_api_server/app/services/picking_service.py#L1875)

```python
list_pick_faces(self, ware_id: int | None=None, articul: str | None=None, active_only: int | None=None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `articul.upper`, `conditions.append`, `int`, `self.gateway.fetch_all`

### upsert_pick_face

[Исходник: api/wms_api_server/app/services/picking_service.py:1932](../../../api/wms_api_server/app/services/picking_service.py#L1932)

```python
upsert_pick_face(self, request: PickFaceUpsertRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `request.model_dump`, `self.gateway.call_number_plsql`

### list_pick_face_articuls

[Исходник: api/wms_api_server/app/services/picking_service.py:1960](../../../api/wms_api_server/app/services/picking_service.py#L1960)

```python
list_pick_face_articuls(self, pick_face_id: int) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### assign_pick_face_articul

[Исходник: api/wms_api_server/app/services/picking_service.py:1996](../../../api/wms_api_server/app/services/picking_service.py#L1996)

```python
assign_pick_face_articul(self, request: PickFaceArticulUpsertRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `configure_existing_pick_face_article`

### list_articul_replenishment_rules

[Исходник: api/wms_api_server/app/services/picking_service.py:2000](../../../api/wms_api_server/app/services/picking_service.py#L2000)

```python
list_articul_replenishment_rules(self, articul: str | None=None, active_only: int | None=None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `articul.upper`, `conditions.append`, `int`, `self.gateway.fetch_all`

### upsert_articul_replenishment_rule

[Исходник: api/wms_api_server/app/services/picking_service.py:2041](../../../api/wms_api_server/app/services/picking_service.py#L2041)

```python
upsert_articul_replenishment_rule(self, request: ArticulReplenishmentRuleUpsertRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `int`, `request.model_dump`, `self.gateway.call_number_plsql`, `self.gateway.execute`, `self.gateway.fetch_all`, `self.upsert_articul_replenishment_rule`

### list_shortages

[Исходник: api/wms_api_server/app/services/picking_service.py:2114](../../../api/wms_api_server/app/services/picking_service.py#L2114)

```python
list_shortages(self, pick_plan_id: int | None=None, limit: int=200) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `conditions.append`, `max`, `min`, `self.gateway.fetch_all`

### __init__

[Исходник: api/wms_api_server/app/services/product_service.py:8](../../../api/wms_api_server/app/services/product_service.py#L8)

```python
__init__(self, gateway: OracleGateway | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`

### list_shipment_settings

[Исходник: api/wms_api_server/app/services/product_service.py:11](../../../api/wms_api_server/app/services/product_service.py#L11)

```python
list_shipment_settings(self, articul_like: str | None=None, only_with_aging: int | None=None, limit: int=200) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `articul_like.upper`, `conditions.append`, `int`, `max`, `min`, `self.gateway.fetch_all`

### update_shipment_settings

[Исходник: api/wms_api_server/app/services/product_service.py:43](../../../api/wms_api_server/app/services/product_service.py#L43)

```python
update_shipment_settings(self, articul: str, request: ProductShipmentSettingsUpdateRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.execute`

### required_text

[Исходник: api/wms_api_server/app/services/production_exchange_service.py:241](../../../api/wms_api_server/app/services/production_exchange_service.py#L241)

```python
required_text(payload: dict[str, Any], key: str) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `payload.get`, `str`, `str(value).strip`

### __init__

[Исходник: api/wms_api_server/app/services/production_exchange_service.py:34](../../../api/wms_api_server/app/services/production_exchange_service.py#L34)

```python
__init__(self, root_dir: str | Path | None=None, gateway: OracleGateway | None=None, mes_service: MesService | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `MesService`, `OracleGateway`, `Path`, `Path(root_dir or settings.production_exchange_root_dir).resolve`, `get_settings`

### ensure_dirs

[Исходник: api/wms_api_server/app/services/production_exchange_service.py:45](../../../api/wms_api_server/app/services/production_exchange_service.py#L45)

```python
ensure_dirs(self) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(self.root_dir / name).mkdir`

### process_once

[Исходник: api/wms_api_server/app/services/production_exchange_service.py:49](../../../api/wms_api_server/app/services/production_exchange_service.py#L49)

```python
process_once(self, limit: int=10) -> list[ExchangeResult]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(self.root_dir / 'in').glob`, `max`, `results.append`, `self._move_to_processing`, `self.ensure_dirs`, `self.process_file`, `sorted`

### process_file

[Исходник: api/wms_api_server/app/services/production_exchange_service.py:57](../../../api/wms_api_server/app/services/production_exchange_service.py#L57)

```python
process_file(self, path: Path) -> ExchangeResult
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ExchangeResult`, `MesApplyWmsRequest`, `MesCompleteOrderRequest`, `MesCompletionPallet`, `MesRawIssueRequest`, `bool`, `existing.get`, `float`, `hashlib.sha256`, `hashlib.sha256(raw).hexdigest`, `json.loads`, `order.get`, `pallet.get`, `path.read_bytes`, `payload.get`, `raw.decode`, `raw_issue.get`, `required_text`, `self._create_or_get_order`, `self._move`, `self._write_out`, `self.get_log`, `self.mark_error`, `self.mark_processed`, `self.mes.apply_wms`, `self.mes.complete_order`, `self.mes.get_order`, `self.mes.issue_raw`, `self.register_message`, `str`

### _create_or_get_order

[Исходник: api/wms_api_server/app/services/production_exchange_service.py:135](../../../api/wms_api_server/app/services/production_exchange_service.py#L135)

```python
_create_or_get_order(self, payload: dict[str, Any], message_id: str) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `MesProductionOrderCreateRequest`, `float`, `int`, `payload.get`, `required_text`, `self.gateway.fetch_all`, `self.mes.create_order`

### get_log

[Исходник: api/wms_api_server/app/services/production_exchange_service.py:159](../../../api/wms_api_server/app/services/production_exchange_service.py#L159)

```python
get_log(self, message_id: str) -> dict[str, Any] | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### register_message

[Исходник: api/wms_api_server/app/services/production_exchange_service.py:170](../../../api/wms_api_server/app/services/production_exchange_service.py#L170)

```python
register_message(self, payload: dict[str, Any], path: Path, file_hash: str, source_system: str) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `payload.get`, `required_text`, `self.gateway.call_number_plsql`, `str`

### mark_processed

[Исходник: api/wms_api_server/app/services/production_exchange_service.py:195](../../../api/wms_api_server/app/services/production_exchange_service.py#L195)

```python
mark_processed(self, message_id: str, prod_batch_id: int | None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.execute_plsql`

### mark_error

[Исходник: api/wms_api_server/app/services/production_exchange_service.py:209](../../../api/wms_api_server/app/services/production_exchange_service.py#L209)

```python
mark_error(self, message_id: str, code: str, error: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.execute_plsql`

### _move_to_processing

[Исходник: api/wms_api_server/app/services/production_exchange_service.py:224](../../../api/wms_api_server/app/services/production_exchange_service.py#L224)

```python
_move_to_processing(self, path: Path) -> Path
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self._move`

### _move

[Исходник: api/wms_api_server/app/services/production_exchange_service.py:228](../../../api/wms_api_server/app/services/production_exchange_service.py#L228)

```python
_move(self, source: Path, target: Path) -> Path
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `int`, `shutil.move`, `str`, `target.exists`, `target.parent.mkdir`, `target.with_name`, `time.time`

### _write_out

[Исходник: api/wms_api_server/app/services/production_exchange_service.py:235](../../../api/wms_api_server/app/services/production_exchange_service.py#L235)

```python
_write_out(self, message_id: str, payload: dict[str, Any], suffix: str='') -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `json.dumps`, `out_path.parent.mkdir`, `out_path.write_text`

### _model_dict

[Исходник: api/wms_api_server/app/services/production_service.py:515](../../../api/wms_api_server/app/services/production_service.py#L515)

```python
_model_dict(model) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `hasattr`, `model.dict`, `model.model_dump`

### __init__

[Исходник: api/wms_api_server/app/services/production_service.py:21](../../../api/wms_api_server/app/services/production_service.py#L21)

```python
__init__(self, gateway: OracleGateway | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`

### create_batch

[Исходник: api/wms_api_server/app/services/production_service.py:24](../../../api/wms_api_server/app/services/production_service.py#L24)

```python
create_batch(self, request: ProductionBatchCreate) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_model_dict`, `self.gateway.call_number_plsql`

### attach_pallet

[Исходник: api/wms_api_server/app/services/production_service.py:58](../../../api/wms_api_server/app/services/production_service.py#L58)

```python
attach_pallet(self, prod_batch_id: int, request: PalletAttachRequest) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_model_dict`, `self.gateway.execute_plsql`

### create_raw_batch

[Исходник: api/wms_api_server/app/services/production_service.py:79](../../../api/wms_api_server/app/services/production_service.py#L79)

```python
create_raw_batch(self, request: RawBatchCreate) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_model_dict`, `self.gateway.call_number_plsql`, `self.gateway.execute`

### add_raw_usage

[Исходник: api/wms_api_server/app/services/production_service.py:134](../../../api/wms_api_server/app/services/production_service.py#L134)

```python
add_raw_usage(self, prod_batch_id: int, request: RawUsageRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_model_dict`, `self.gateway.call_number_plsql`

### add_crpt_code

[Исходник: api/wms_api_server/app/services/production_service.py:152](../../../api/wms_api_server/app/services/production_service.py#L152)

```python
add_crpt_code(self, prod_batch_id: int, request: CrptCodeRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_model_dict`, `self.gateway.call_number_plsql`

### create_aggregation

[Исходник: api/wms_api_server/app/services/production_service.py:170](../../../api/wms_api_server/app/services/production_service.py#L170)

```python
create_aggregation(self, prod_batch_id: int, request: AggregationCreateRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_model_dict`, `self.gateway.call_number_plsql`

### add_aggregation_item

[Исходник: api/wms_api_server/app/services/production_service.py:186](../../../api/wms_api_server/app/services/production_service.py#L186)

```python
add_aggregation_item(self, aggregation_id: int, request: AggregationItemRequest) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_model_dict`, `self.gateway.execute_plsql`

### set_mercury_batch

[Исходник: api/wms_api_server/app/services/production_service.py:203](../../../api/wms_api_server/app/services/production_service.py#L203)

```python
set_mercury_batch(self, prod_batch_id: int, request: MercuryBatchRequest) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_model_dict`, `self.gateway.execute_plsql`

### upsert_mercury_site

[Исходник: api/wms_api_server/app/services/production_service.py:225](../../../api/wms_api_server/app/services/production_service.py#L225)

```python
upsert_mercury_site(self, request: MercurySiteRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_model_dict`, `self.gateway.call_number_plsql`

### create_mercury_operation

[Исходник: api/wms_api_server/app/services/production_service.py:246](../../../api/wms_api_server/app/services/production_service.py#L246)

```python
create_mercury_operation(self, prod_batch_id: int | None, request: MercuryOperationCreateRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_model_dict`, `self.gateway.call_number_plsql`

### update_mercury_operation

[Исходник: api/wms_api_server/app/services/production_service.py:268](../../../api/wms_api_server/app/services/production_service.py#L268)

```python
update_mercury_operation(self, operation_row_id: int, request: MercuryOperationUpdateRequest) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_model_dict`, `self.gateway.execute_plsql`

### set_crpt_code_status

[Исходник: api/wms_api_server/app/services/production_service.py:288](../../../api/wms_api_server/app/services/production_service.py#L288)

```python
set_crpt_code_status(self, request: CrptCodeStatusRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_model_dict`, `self.gateway.call_number_plsql`

### get_batch_status

[Исходник: api/wms_api_server/app/services/production_service.py:307](../../../api/wms_api_server/app/services/production_service.py#L307)

```python
get_batch_status(self, prod_batch_id: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### get_regulatory_status

[Исходник: api/wms_api_server/app/services/production_service.py:332](../../../api/wms_api_server/app/services/production_service.py#L332)

```python
get_regulatory_status(self, prod_batch_id: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### list_mercury_sites

[Исходник: api/wms_api_server/app/services/production_service.py:412](../../../api/wms_api_server/app/services/production_service.py#L412)

```python
list_mercury_sites(self, active: int | None=None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### get_raw_batch

[Исходник: api/wms_api_server/app/services/production_service.py:435](../../../api/wms_api_server/app/services/production_service.py#L435)

```python
get_raw_batch(self, raw_batch_id: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### list_journal

[Исходник: api/wms_api_server/app/services/production_service.py:451](../../../api/wms_api_server/app/services/production_service.py#L451)

```python
list_journal(self, prod_batch_id: int | None=None, system_code: str | None=None, limit: int=100) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `conditions.append`, `max`, `min`, `self.gateway.fetch_all`

### list_outbox

[Исходник: api/wms_api_server/app/services/production_service.py:483](../../../api/wms_api_server/app/services/production_service.py#L483)

```python
list_outbox(self, status: str | None=None, system_code: str | None=None, limit: int=100) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `conditions.append`, `max`, `min`, `self.gateway.fetch_all`

### _model_dict

[Исходник: api/wms_api_server/app/services/raw_material_service.py:255](../../../api/wms_api_server/app/services/raw_material_service.py#L255)

```python
_model_dict(model) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `hasattr`, `model.dict`, `model.model_dump`

### __init__

[Исходник: api/wms_api_server/app/services/raw_material_service.py:8](../../../api/wms_api_server/app/services/raw_material_service.py#L8)

```python
__init__(self, gateway: OracleGateway | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`

### list_skus

[Исходник: api/wms_api_server/app/services/raw_material_service.py:11](../../../api/wms_api_server/app/services/raw_material_service.py#L11)

```python
list_skus(self, search: str | None=None, only_active: int | None=1, only_with_stock: int | None=None, limit: int=200) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `conditions.append`, `int`, `max`, `min`, `search.upper`, `self.gateway.fetch_all`

### update_sku_settings

[Исходник: api/wms_api_server/app/services/raw_material_service.py:94](../../../api/wms_api_server/app/services/raw_material_service.py#L94)

```python
update_sku_settings(self, articul: str, request: RawMaterialSkuSettingsUpdateRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_model_dict`, `self.gateway.execute`

### list_warehouses

[Исходник: api/wms_api_server/app/services/raw_material_service.py:145](../../../api/wms_api_server/app/services/raw_material_service.py#L145)

```python
list_warehouses(self, limit: int=200) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `max`, `min`, `self.gateway.fetch_all`

### list_remains

[Исходник: api/wms_api_server/app/services/raw_material_service.py:175](../../../api/wms_api_server/app/services/raw_material_service.py#L175)

```python
list_remains(self, articul: str | None=None, ware_id: int | None=None, ware_ids: str | None=None, cell: str | None=None, batch_no: str | None=None, quality_status: str | None=None, only_available: int | None=1, limit: int=500) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `', '.join`, `articul.upper`, `batch_no.upper`, `cell.upper`, `conditions.append`, `enumerate`, `int`, `max`, `min`, `placeholders.append`, `quality_status.upper`, `self.gateway.fetch_all`, `value.strip`, `value.strip().isdigit`, `ware_ids.split`

### __init__

[Исходник: api/wms_api_server/app/services/resource_management_service.py:18](../../../api/wms_api_server/app/services/resource_management_service.py#L18)

```python
__init__(self, gateway: OracleGateway | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`

### list_resource_types

[Исходник: api/wms_api_server/app/services/resource_management_service.py:21](../../../api/wms_api_server/app/services/resource_management_service.py#L21)

```python
list_resource_types(self, active: int | None=1) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `conditions.append`, `int`, `self.gateway.fetch_all`

### list_equipment

[Исходник: api/wms_api_server/app/services/resource_management_service.py:39](../../../api/wms_api_server/app/services/resource_management_service.py#L39)

```python
list_equipment(self, equipment_type: str | None=None, service_status: str | None=None, active: int | None=1, limit: int=200) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `clamp_limit`, `conditions.append`, `equipment_type.upper`, `int`, `self.gateway.fetch_all`, `service_status.upper`

### create_equipment

[Исходник: api/wms_api_server/app/services/resource_management_service.py:75](../../../api/wms_api_server/app/services/resource_management_service.py#L75)

```python
create_equipment(self, request: ResourceEquipmentCreateRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(request.service_status or 'ACTIVE').upper`, `int`, `request.equipment_type.upper`, `self.gateway.call_number_plsql`

### list_resources

[Исходник: api/wms_api_server/app/services/resource_management_service.py:104](../../../api/wms_api_server/app/services/resource_management_service.py#L104)

```python
list_resources(self, resource_type: str | None=None, resource_class: str | None=None, status: str | None=None, ware_id: int | None=None, zone_code: str | None=None, active: int | None=1, limit: int=200) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `clamp_limit`, `conditions.append`, `int`, `resource_class.upper`, `resource_type.upper`, `self.gateway.fetch_all`, `status.upper`, `zone_code.upper`

### create_resource

[Исходник: api/wms_api_server/app/services/resource_management_service.py:166](../../../api/wms_api_server/app/services/resource_management_service.py#L166)

```python
create_resource(self, request: ResourceCreateRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(request.status or 'AVAILABLE').upper`, `int`, `request.resource_class.upper`, `request.resource_type.upper`, `self._get_resource_class`, `self.gateway.call_number_plsql`

### list_shifts

[Исходник: api/wms_api_server/app/services/resource_management_service.py:201](../../../api/wms_api_server/app/services/resource_management_service.py#L201)

```python
list_shifts(self, shift_date: str | None=None, ware_id: int | None=None, status: str | None=None, limit: int=100) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `clamp_limit`, `conditions.append`, `self.gateway.fetch_all`, `status.upper`

### create_shift

[Исходник: api/wms_api_server/app/services/resource_management_service.py:236](../../../api/wms_api_server/app/services/resource_management_service.py#L236)

```python
create_shift(self, request: ResourceShiftCreateRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(request.status or 'PLANNED').upper`, `self.gateway.call_number_plsql`

### list_sessions

[Исходник: api/wms_api_server/app/services/resource_management_service.py:263](../../../api/wms_api_server/app/services/resource_management_service.py#L263)

```python
list_sessions(self, session_id: int | None=None, shift_id: int | None=None, resource_id: int | None=None, status: str | None=None, limit: int=100) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `clamp_limit`, `conditions.append`, `self.gateway.fetch_all`, `status.upper`

### login_session

[Исходник: api/wms_api_server/app/services/resource_management_service.py:307](../../../api/wms_api_server/app/services/resource_management_service.py#L307)

```python
login_session(self, request: ResourceSessionLoginRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ResourceManagementService`, `ResourceManagementService(gateway).login_session`, `getattr`, `open_existing_resource_session`, `resource.get`, `self._get_resource`, `self.gateway.call_number_plsql`

### login_tsd

[Исходник: api/wms_api_server/app/services/resource_management_service.py:340](../../../api/wms_api_server/app/services/resource_management_service.py#L340)

```python
login_tsd(self, request: ResourceTsdLoginRequest) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(request.barcode or '').strip`, `(request.driver_code or request.barcode or '').strip`, `HTTPException`, `ResourceSessionLoginRequest`, `equipment.get`, `existing.get`, `int`, `operator_user_id.upper`, `resource.get`, `self._find_active_session`, `self._resolve_active_shift`, `self._resolve_equipment`, `self._resolve_tsd_resource`, `self._validate_legacy_user_password`, `self.list_sessions`, `self.login_session`, `session.get`, `str`, `str(existing.get('operator_user_id') or '').upper`

### heartbeat

[Исходник: api/wms_api_server/app/services/resource_management_service.py:404](../../../api/wms_api_server/app/services/resource_management_service.py#L404)

```python
heartbeat(self, session_id: int) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `self.gateway.execute`

### pause_session

[Исходник: api/wms_api_server/app/services/resource_management_service.py:417](../../../api/wms_api_server/app/services/resource_management_service.py#L417)

```python
pause_session(self, session_id: int, request: ResourceSessionStatusRequest) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self._set_session_status`

### resume_session

[Исходник: api/wms_api_server/app/services/resource_management_service.py:420](../../../api/wms_api_server/app/services/resource_management_service.py#L420)

```python
resume_session(self, session_id: int, request: ResourceSessionStatusRequest) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self._set_session_status`

### logout_session

[Исходник: api/wms_api_server/app/services/resource_management_service.py:423](../../../api/wms_api_server/app/services/resource_management_service.py#L423)

```python
logout_session(self, session_id: int, request: ResourceSessionStatusRequest) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `close_existing_resource_session`

### _set_session_status

[Исходник: api/wms_api_server/app/services/resource_management_service.py:427](../../../api/wms_api_server/app/services/resource_management_service.py#L427)

```python
_set_session_status(self, session_id: int, status: str, updated_by: str | None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `self.gateway.execute`

### _get_resource_class

[Исходник: api/wms_api_server/app/services/resource_management_service.py:442](../../../api/wms_api_server/app/services/resource_management_service.py#L442)

```python
_get_resource_class(self, resource_type: str) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `rows[0].get`, `self.gateway.fetch_all`, `str`

### _get_resource

[Исходник: api/wms_api_server/app/services/resource_management_service.py:455](../../../api/wms_api_server/app/services/resource_management_service.py#L455)

```python
_get_resource(self, resource_id: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `int`, `row.get`, `self.gateway.fetch_all`

### _resolve_tsd_resource

[Исходник: api/wms_api_server/app/services/resource_management_service.py:472](../../../api/wms_api_server/app/services/resource_management_service.py#L472)

```python
_resolve_tsd_resource(self, driver_code: str, barcode: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(driver_code or barcode).upper`, `HTTPException`, `self.gateway.fetch_all`

### _resolve_equipment

[Исходник: api/wms_api_server/app/services/resource_management_service.py:499](../../../api/wms_api_server/app/services/resource_management_service.py#L499)

```python
_resolve_equipment(self, equipment_code: str | None, default_equipment_id: Any) -> dict[str, Any] | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `equipment_code.upper`, `int`, `row.get`, `self.gateway.fetch_all`

### _resolve_active_shift

[Исходник: api/wms_api_server/app/services/resource_management_service.py:527](../../../api/wms_api_server/app/services/resource_management_service.py#L527)

```python
_resolve_active_shift(self, ware_id: Any | None, shift_id: int | None=None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `any`, `len`, `self.gateway.fetch_all`

### _find_active_session

[Исходник: api/wms_api_server/app/services/resource_management_service.py:552](../../../api/wms_api_server/app/services/resource_management_service.py#L552)

```python
_find_active_session(self, resource_id: int, equipment_id: int | None, operator_user_id: str) -> dict[str, Any] | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `operator_user_id.upper`, `self.gateway.fetch_all`

### _validate_legacy_user_password

[Исходник: api/wms_api_server/app/services/resource_management_service.py:584](../../../api/wms_api_server/app/services/resource_management_service.py#L584)

```python
_validate_legacy_user_password(self, user_id: str, password: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `self.gateway.fetch_all`

### _haversine_km

[Исходник: api/wms_api_server/app/services/routing.py:55](../../../api/wms_api_server/app/services/routing.py#L55)

```python
_haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `math.asin`, `math.cos`, `math.radians`, `math.sin`, `math.sqrt`

### _cached_availability

[Исходник: api/wms_api_server/app/services/routing.py:99](../../../api/wms_api_server/app/services/routing.py#L99)

```python
_cached_availability(name: str, loader: Any) -> bool
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_AVAILABILITY_CACHE.get`, `bool`, `loader`, `time.monotonic`

### _tcp_url_available

[Исходник: api/wms_api_server/app/services/routing.py:109](../../../api/wms_api_server/app/services/routing.py#L109)

```python
_tcp_url_available(url: str) -> bool
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `socket.create_connection`, `urlparse`

### get_active_provider

[Исходник: api/wms_api_server/app/services/routing.py:175](../../../api/wms_api_server/app/services/routing.py#L175)

```python
get_active_provider() -> RoutingProvider
```

Возвращает первый доступный провайдер (OSRM → Valhalla → Haversine).

Вызывает: `HaversineProvider`, `p.is_available`

### is_available

[Исходник: api/wms_api_server/app/services/routing.py:33](../../../api/wms_api_server/app/services/routing.py#L33)

```python
is_available(self) -> bool
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### build_cost_matrix

[Исходник: api/wms_api_server/app/services/routing.py:36](../../../api/wms_api_server/app/services/routing.py#L36)

```python
build_cost_matrix(self, points: list[tuple[float, float]]) -> tuple[list[list[float]], list[list[float]] | None]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.build_matrix`

### build_matrix

[Исходник: api/wms_api_server/app/services/routing.py:40](../../../api/wms_api_server/app/services/routing.py#L40)

```python
build_matrix(self, points: list[tuple[float, float]]) -> list[list[float]]
```

Возвращает матрицу расстояний (км) N×N.

Вызывает: 

### is_available

[Исходник: api/wms_api_server/app/services/routing.py:67](../../../api/wms_api_server/app/services/routing.py#L67)

```python
is_available(self) -> bool
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### build_matrix

[Исходник: api/wms_api_server/app/services/routing.py:70](../../../api/wms_api_server/app/services/routing.py#L70)

```python
build_matrix(self, points: list[tuple[float, float]]) -> list[list[float]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_haversine_km`, `len`, `matrix.append`, `range`, `round`, `row.append`

### is_available

[Исходник: api/wms_api_server/app/services/routing.py:123](../../../api/wms_api_server/app/services/routing.py#L123)

```python
is_available(self) -> bool
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_cached_availability`, `_tcp_url_available`

### build_matrix

[Исходник: api/wms_api_server/app/services/routing.py:126](../../../api/wms_api_server/app/services/routing.py#L126)

```python
build_matrix(self, points: list[tuple[float, float]]) -> list[list[float]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.build_cost_matrix`

### build_cost_matrix

[Исходник: api/wms_api_server/app/services/routing.py:129](../../../api/wms_api_server/app/services/routing.py#L129)

```python
build_cost_matrix(self, points: list[tuple[float, float]]) -> tuple[list[list[float]], list[list[float]]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `';'.join`, `httpx.get`, `len`, `osrm_costs`, `response.json`, `response.raise_for_status`, `validate_points`

### is_available

[Исходник: api/wms_api_server/app/services/routing.py:150](../../../api/wms_api_server/app/services/routing.py#L150)

```python
is_available(self) -> bool
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_cached_availability`, `_tcp_url_available`

### build_matrix

[Исходник: api/wms_api_server/app/services/routing.py:153](../../../api/wms_api_server/app/services/routing.py#L153)

```python
build_matrix(self, points: list[tuple[float, float]]) -> list[list[float]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.build_cost_matrix`

### build_cost_matrix

[Исходник: api/wms_api_server/app/services/routing.py:156](../../../api/wms_api_server/app/services/routing.py#L156)

```python
build_cost_matrix(self, points: list[tuple[float, float]]) -> tuple[list[list[float]], list[list[float]]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `httpx.post`, `len`, `response.json`, `response.raise_for_status`, `valhalla_costs`, `validate_points`

### __init__

[Исходник: api/wms_api_server/app/services/slow_sql_service.py:7](../../../api/wms_api_server/app/services/slow_sql_service.py#L7)

```python
__init__(self, gateway: OracleGateway | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`

### list_entries

[Исходник: api/wms_api_server/app/services/slow_sql_service.py:10](../../../api/wms_api_server/app/services/slow_sql_service.py#L10)

```python
list_entries(self, from_log_id: int | None=None, to_log_id: int | None=None, api_call_id: int | None=None, path_like: str | None=None, sql_hash: str | None=None, min_elapsed_ms: int | None=None, error_only: int | None=None, limit: int=100, offset: int=0) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `max`, `min`, `self._filters`, `self.gateway.fetch_all`

### get_entry

[Исходник: api/wms_api_server/app/services/slow_sql_service.py:54](../../../api/wms_api_server/app/services/slow_sql_service.py#L54)

```python
get_entry(self, log_id: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### top_entries

[Исходник: api/wms_api_server/app/services/slow_sql_service.py:68](../../../api/wms_api_server/app/services/slow_sql_service.py#L68)

```python
top_entries(self, limit: int=50) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `max`, `min`, `self.gateway.fetch_all`

### oracle_top_sql

[Исходник: api/wms_api_server/app/services/slow_sql_service.py:91](../../../api/wms_api_server/app/services/slow_sql_service.py#L91)

```python
oracle_top_sql(self, limit: int=50) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `max`, `min`, `self.gateway.fetch_all`, `str`

### _filters

[Исходник: api/wms_api_server/app/services/slow_sql_service.py:126](../../../api/wms_api_server/app/services/slow_sql_service.py#L126)

```python
_filters(self, from_log_id: int | None, to_log_id: int | None, api_call_id: int | None, path_like: str | None, sql_hash: str | None, min_elapsed_ms: int | None, error_only: int | None) -> tuple[str, dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `conditions.append`, `int`

### _upper_or_none

[Исходник: api/wms_api_server/app/services/stock_reservation_service.py:219](../../../api/wms_api_server/app/services/stock_reservation_service.py#L219)

```python
_upper_or_none(value: Any) -> str | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `str`, `str(value).strip`, `text.upper`

### _model_dict

[Исходник: api/wms_api_server/app/services/stock_reservation_service.py:226](../../../api/wms_api_server/app/services/stock_reservation_service.py#L226)

```python
_model_dict(model) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `hasattr`, `model.dict`, `model.model_dump`

### __init__

[Исходник: api/wms_api_server/app/services/stock_reservation_service.py:19](../../../api/wms_api_server/app/services/stock_reservation_service.py#L19)

```python
__init__(self, gateway: OracleGateway | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`

### list_reservations

[Исходник: api/wms_api_server/app/services/stock_reservation_service.py:22](../../../api/wms_api_server/app/services/stock_reservation_service.py#L22)

```python
list_reservations(self, reservation_kind: str | None=None, reservation_domain: str | None=None, status: str | None=None, source_doc_type: str | None=None, source_doc_id: int | None=None, articul: str | None=None, ware_id: int | None=None, cell: str | None=None, uid_pallet: str | None=None, batch_id: str | None=None, production_order_id: int | None=None, pick_plan_id: int | None=None, pick_wave_id: int | None=None, only_active: int | None=None, limit: int=200) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `articul.upper`, `batch_id.upper`, `cell.upper`, `conditions.append`, `int`, `max`, `min`, `reservation_domain.upper`, `reservation_kind.upper`, `self.gateway.fetch_all`, `source_doc_type.upper`, `status.upper`, `uid_pallet.upper`

### get_reservation

[Исходник: api/wms_api_server/app/services/stock_reservation_service.py:98](../../../api/wms_api_server/app/services/stock_reservation_service.py#L98)

```python
get_reservation(self, reservation_id: int) -> dict[str, Any] | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### create_reservation

[Исходник: api/wms_api_server/app/services/stock_reservation_service.py:109](../../../api/wms_api_server/app/services/stock_reservation_service.py#L109)

```python
create_reservation(self, request: StockReservationCreateRequest, actor: str | None=None) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `int`, `post_reservation`

### promote_to_hard

[Исходник: api/wms_api_server/app/services/stock_reservation_service.py:114](../../../api/wms_api_server/app/services/stock_reservation_service.py#L114)

```python
promote_to_hard(self, reservation_id: int, request: StockReservationPromoteRequest, actor: str | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `post_reservation`

### release_reservation

[Исходник: api/wms_api_server/app/services/stock_reservation_service.py:119](../../../api/wms_api_server/app/services/stock_reservation_service.py#L119)

```python
release_reservation(self, reservation_id: int, request: StockReservationStatusRequest, actor: str | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `post_reservation`

### consume_reservation

[Исходник: api/wms_api_server/app/services/stock_reservation_service.py:124](../../../api/wms_api_server/app/services/stock_reservation_service.py#L124)

```python
consume_reservation(self, reservation_id: int, request: StockReservationStatusRequest, actor: str | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `post_reservation`

### cancel_reservation

[Исходник: api/wms_api_server/app/services/stock_reservation_service.py:129](../../../api/wms_api_server/app/services/stock_reservation_service.py#L129)

```python
cancel_reservation(self, reservation_id: int, request: StockReservationStatusRequest, actor: str | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `post_reservation`

### _set_status

[Исходник: api/wms_api_server/app/services/stock_reservation_service.py:134](../../../api/wms_api_server/app/services/stock_reservation_service.py#L134)

```python
_set_status(self, reservation_id: int, status: str, actor: str | None, reason: str | None, timestamp_column: str, actor_column: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LookupError`, `self.gateway.execute`, `self.get_reservation`

### _next_id

[Исходник: api/wms_api_server/app/services/stock_reservation_service.py:163](../../../api/wms_api_server/app/services/stock_reservation_service.py#L163)

```python
_next_id(self) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `int`, `self.gateway.fetch_all`

### _validate_kind_scope_status

[Исходник: api/wms_api_server/app/services/stock_reservation_service.py:169](../../../api/wms_api_server/app/services/stock_reservation_service.py#L169)

```python
_validate_kind_scope_status(self, data: dict[str, Any]) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `data.get`, `str`, `str(data.get('reservation_kind') or '').upper`, `str(data.get('reservation_scope') or 'QTY').upper`, `str(data.get('status') or 'ACTIVE').upper`, `str(domain).upper`

### _validate_physical_fields

[Исходник: api/wms_api_server/app/services/stock_reservation_service.py:183](../../../api/wms_api_server/app/services/stock_reservation_service.py#L183)

```python
_validate_physical_fields(self, data: dict[str, Any]) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `any`, `data.get`, `str`, `str(data.get('reservation_kind') or '').upper`

### _normalized_params

[Исходник: api/wms_api_server/app/services/stock_reservation_service.py:202](../../../api/wms_api_server/app/services/stock_reservation_service.py#L202)

```python
_normalized_params(self, data: dict[str, Any]) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_upper_or_none`, `data.get`, `str`, `str(data.get('articul') or '').upper`, `str(data.get('reservation_domain') or '').upper`, `str(data.get('reservation_kind') or 'SOFT').upper`, `str(data.get('reservation_scope') or 'QTY').upper`, `str(data.get('source_doc_type') or '').upper`, `str(data.get('status') or 'ACTIVE').upper`

### normalize_entity_type

[Исходник: api/wms_api_server/app/services/traceability_service.py:275](../../../api/wms_api_server/app/services/traceability_service.py#L275)

```python
normalize_entity_type(value: str) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `len`, `value.strip`, `value.strip().upper`

### clamp_limit

[Исходник: api/wms_api_server/app/services/traceability_service.py:284](../../../api/wms_api_server/app/services/traceability_service.py#L284)

```python
clamp_limit(value: int) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `max`, `min`

### __init__

[Исходник: api/wms_api_server/app/services/traceability_service.py:10](../../../api/wms_api_server/app/services/traceability_service.py#L10)

```python
__init__(self, gateway: OracleGateway | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`

### list_edges

[Исходник: api/wms_api_server/app/services/traceability_service.py:13](../../../api/wms_api_server/app/services/traceability_service.py#L13)

```python
list_edges(self, entity_type: str, entity_id: str, direction: str, limit: int=100) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `clamp_limit`, `direction.lower`, `normalize_entity_type`, `self.gateway.fetch_all`

### list_outbox

[Исходник: api/wms_api_server/app/services/traceability_service.py:61](../../../api/wms_api_server/app/services/traceability_service.py#L61)

```python
list_outbox(self, status: str | None=None, target_system: str | None=None, event_type: str | None=None, aggregate_type: str | None=None, aggregate_id: str | None=None, limit: int=100) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `aggregate_type.upper`, `clamp_limit`, `conditions.append`, `event_type.upper`, `self.gateway.fetch_all`, `status.upper`, `target_system.upper`

### get_outbox_event

[Исходник: api/wms_api_server/app/services/traceability_service.py:121](../../../api/wms_api_server/app/services/traceability_service.py#L121)

```python
get_outbox_event(self, event_outbox_id: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`, `self.list_adapter_requests`

### retry_outbox_event

[Исходник: api/wms_api_server/app/services/traceability_service.py:156](../../../api/wms_api_server/app/services/traceability_service.py#L156)

```python
retry_outbox_event(self, event_outbox_id: int, dry_run: bool=True, reason: str | None=None, actor: str | None=None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `OutboxDelivery`, `OutboxDelivery(self.gateway).retry`, `event.get`, `getattr`, `self.get_outbox_event`, `str`, `str(exc).split`

### list_adapter_requests

[Исходник: api/wms_api_server/app/services/traceability_service.py:188](../../../api/wms_api_server/app/services/traceability_service.py#L188)

```python
list_adapter_requests(self, event_outbox_id: int | None=None, system_code: str | None=None, status: str | None=None, business_key: str | None=None, limit: int=100) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `adapter_request_evidence`, `clamp_limit`, `conditions.append`, `self.gateway.fetch_all`, `status.upper`, `system_code.upper`

### get_adapter_request

[Исходник: api/wms_api_server/app/services/traceability_service.py:243](../../../api/wms_api_server/app/services/traceability_service.py#L243)

```python
get_adapter_request(self, adapter_request_id: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `adapter_request_evidence`, `self.gateway.fetch_all`

### _upper_keys

[Исходник: api/wms_api_server/app/services/transport_service.py:50](../../../api/wms_api_server/app/services/transport_service.py#L50)

```python
_upper_keys(row: dict[str, Any]) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `row.items`, `str`, `str(key).upper`

### _clear_available_sts_cache

[Исходник: api/wms_api_server/app/services/transport_service.py:68](../../../api/wms_api_server/app/services/transport_service.py#L68)

```python
_clear_available_sts_cache() -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_AVAILABLE_STS_CACHE.clear`, `_invalidate_ref_cache`

### _clear_task_sts_cache

[Исходник: api/wms_api_server/app/services/transport_service.py:74](../../../api/wms_api_server/app/services/transport_service.py#L74)

```python
_clear_task_sts_cache(task_id: int | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_TASK_STS_CACHE.clear`, `_TASK_STS_CACHE.pop`

### _clear_vehicle_availability_cache

[Исходник: api/wms_api_server/app/services/transport_service.py:82](../../../api/wms_api_server/app/services/transport_service.py#L82)

```python
_clear_vehicle_availability_cache() -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_VEHICLE_AVAILABILITY_CACHE.clear`

### _invalidate_ref_cache

[Исходник: api/wms_api_server/app/services/transport_service.py:87](../../../api/wms_api_server/app/services/transport_service.py#L87)

```python
_invalidate_ref_cache(prefix: str) -> None
```

Инвалидировать записи _REF_CACHE с ключами, начинающимися на prefix.

Вызывает: `_REF_CACHE.keys`, `_REF_CACHE.pop`, `list`

### _minutes_from_shift_start

[Исходник: api/wms_api_server/app/services/transport_service.py:95](../../../api/wms_api_server/app/services/transport_service.py#L95)

```python
_minutes_from_shift_start(value: Any, shift_start_hour: int=6, default: int | None=None) -> int | None
```

Convert Oracle date/time/string values to minutes from the dispatch shift start.

Вызывает: `datetime.fromisoformat`, `datetime.strptime`, `int`, `isinstance`, `max`, `str`, `str(value).strip`, `text.replace`, `text[:5].split`

### _fallback_time_window_from_ord

[Исходник: api/wms_api_server/app/services/transport_service.py:124](../../../api/wms_api_server/app/services/transport_service.py#L124)

```python
_fallback_time_window_from_ord(ord_value: Any) -> tuple[int, int]
```

Fallback store acceptance window when legacy ST rows do not carry one.

Вызывает: `int`, `max`

### _clock_from_shift_minutes

[Исходник: api/wms_api_server/app/services/transport_service.py:135](../../../api/wms_api_server/app/services/transport_service.py#L135)

```python
_clock_from_shift_minutes(minutes_from_shift: int, shift_start_hour: int=6) -> str
```

Return HH:MM clock string from minutes after the dispatch shift start.

Вызывает: `int`

### _fill_visible_time_window

[Исходник: api/wms_api_server/app/services/transport_service.py:141](../../../api/wms_api_server/app/services/transport_service.py#L141)

```python
_fill_visible_time_window(row: dict[str, Any]) -> dict[str, Any]
```

Expose the same fallback TW used by VRP on read endpoints for traceability.

Вызывает: `_clock_from_shift_minutes`, `_fallback_time_window_from_ord`, `row.get`

### _normalize_task_condition

[Исходник: api/wms_api_server/app/services/transport_service.py:154](../../../api/wms_api_server/app/services/transport_service.py#L154)

```python
_normalize_task_condition(value: Any) -> Any
```

Legacy package-created open tasks can store Cyrillic as question marks.

Вызывает: `isinstance`, `set`, `value.strip`

### _normalize_task_row

[Исходник: api/wms_api_server/app/services/transport_service.py:161](../../../api/wms_api_server/app/services/transport_service.py#L161)

```python
_normalize_task_row(row: dict[str, Any]) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_normalize_task_condition`, `row.get`

### _cached_ref

[Исходник: api/wms_api_server/app/services/transport_service.py:169](../../../api/wms_api_server/app/services/transport_service.py#L169)

```python
_cached_ref(key: tuple[str, Any], loader: Callable[[], list[dict[str, Any]]]) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_REF_CACHE.get`, `dict`, `loader`, `time.monotonic`

### __init__

[Исходник: api/wms_api_server/app/services/transport_service.py:184](../../../api/wms_api_server/app/services/transport_service.py#L184)

```python
__init__(self, gateway: OracleGateway) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### fetch_all

[Исходник: api/wms_api_server/app/services/transport_service.py:187](../../../api/wms_api_server/app/services/transport_service.py#L187)

```python
fetch_all(self, sql: str, params: dict[str, Any] | None=None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_upper_keys`, `self._gateway.fetch_all`

### __getattr__

[Исходник: api/wms_api_server/app/services/transport_service.py:190](../../../api/wms_api_server/app/services/transport_service.py#L190)

```python
__getattr__(self, name: str) -> Any
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `getattr`

### __init__

[Исходник: api/wms_api_server/app/services/transport_service.py:195](../../../api/wms_api_server/app/services/transport_service.py#L195)

```python
__init__(self, gateway: OracleGateway | None=None, departure: Callable[[int, str], dict[str, Any]] | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `_TransportGateway`

### list_clusters

[Исходник: api/wms_api_server/app/services/transport_service.py:207](../../../api/wms_api_server/app/services/transport_service.py#L207)

```python
list_clusters(self, stdate: date | None=None, ware_ids: list[int] | None=None) -> list[dict[str, Any]]
```

Группирует свободные СТ по RAION. Вычисляется в Python поверх list_available_sts.

Вызывает: `c['STS'].append`, `clusters.values`, `round`, `self.list_available_sts`, `sorted`, `st.get`

### create_task_from_cluster

[Исходник: api/wms_api_server/app/services/transport_service.py:238](../../../api/wms_api_server/app/services/transport_service.py#L238)

```python
create_task_from_cluster(self, raion: str, req: 'ClusterCreateTaskRequest', user_id: str) -> dict[str, Any]
```

Создаёт рейс из всех свободных СТ района одним запросом (Sprint 29, Phase 2).

Существующий поиск СТ района; создание, реквизиты и назначение
исполняются в одной транзакции с общим native capacity validator.

Вызывает: `HTTPException`, `_normalize_transtype`, `create_existing_cluster`, `self.list_available_sts`, `str`, `{'transport': req.vehicle, 'voditel_id': req.driver_id, 'dock': req.dock}.items`

### list_vehicles

[Исходник: api/wms_api_server/app/services/transport_service.py:267](../../../api/wms_api_server/app/services/transport_service.py#L267)

```python
list_vehicles(self, active_only: bool=True) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_cached_ref`, `self.gateway.fetch_all`

### list_vehicles_full

[Исходник: api/wms_api_server/app/services/transport_service.py:286](../../../api/wms_api_server/app/services/transport_service.py#L286)

```python
list_vehicles_full(self) -> list[dict[str, Any]]
```

Все ТС для страницы управления флотом (Sprint 97).

Вызывает: `_upper_keys`, `self.gateway.fetch_all`

### create_vehicle

[Исходник: api/wms_api_server/app/services/transport_service.py:306](../../../api/wms_api_server/app/services/transport_service.py#L306)

```python
create_vehicle(self, num_plat: str, transtype_id: str | None, max_weight_kg: int, max_pallets: int, sobstvennyy: bool, doverennost_ot: str | None) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_invalidate_ref_cache`, `self.gateway.call_number_plsql`

### update_vehicle

[Исходник: api/wms_api_server/app/services/transport_service.py:337](../../../api/wms_api_server/app/services/transport_service.py#L337)

```python
update_vehicle(self, vehicle_id: int, num_plat: str, transtype_id: str | None, max_weight_kg: int, max_pallets: int, sobstvennyy: bool, doverennost_ot: str | None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_invalidate_ref_cache`, `self.gateway.execute`

### delete_vehicle

[Исходник: api/wms_api_server/app/services/transport_service.py:368](../../../api/wms_api_server/app/services/transport_service.py#L368)

```python
delete_vehicle(self, vehicle_id: int) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_invalidate_ref_cache`, `self.gateway.execute`

### list_drivers

[Исходник: api/wms_api_server/app/services/transport_service.py:375](../../../api/wms_api_server/app/services/transport_service.py#L375)

```python
list_drivers(self, active_only: bool=True) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_cached_ref`, `self.gateway.fetch_all`

### list_drivers_full

[Исходник: api/wms_api_server/app/services/transport_service.py:396](../../../api/wms_api_server/app/services/transport_service.py#L396)

```python
list_drivers_full(self) -> list[dict[str, Any]]
```

Все водители для страницы управления флотом.

Вызывает: `_upper_keys`, `self.gateway.fetch_all`

### create_driver

[Исходник: api/wms_api_server/app/services/transport_service.py:414](../../../api/wms_api_server/app/services/transport_service.py#L414)

```python
create_driver(self, name: str, phone: str | None, license_number: str | None, company: str | None) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_invalidate_ref_cache`, `self.gateway.call_number_plsql`

### update_driver

[Исходник: api/wms_api_server/app/services/transport_service.py:432](../../../api/wms_api_server/app/services/transport_service.py#L432)

```python
update_driver(self, driver_id: int, name: str, phone: str | None, license_number: str | None, company: str | None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_invalidate_ref_cache`, `self.gateway.execute`

### delete_driver

[Исходник: api/wms_api_server/app/services/transport_service.py:451](../../../api/wms_api_server/app/services/transport_service.py#L451)

```python
delete_driver(self, driver_id: int) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_invalidate_ref_cache`, `self.gateway.execute`

### list_transport_types

[Исходник: api/wms_api_server/app/services/transport_service.py:458](../../../api/wms_api_server/app/services/transport_service.py#L458)

```python
list_transport_types(self) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_cached_ref`, `self.gateway.fetch_all`

### list_tasks

[Исходник: api/wms_api_server/app/services/transport_service.py:480](../../../api/wms_api_server/app/services/transport_service.py#L480)

```python
list_tasks(self, shipment_date: date | None=None, condition: str | None=None, include_deleted: bool=False, include_readiness: bool=False, task_id: int | None=None, transport_mask: str | None=None, company_mask: str | None=None, date_from: date | None=None, date_to: date | None=None, no_payments_only: bool=False) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' AND '.join`, `_normalize_task_row`, `conditions.append`, `date.today`, `dict`, `self.gateway.fetch_all`, `timedelta`

### get_task

[Исходник: api/wms_api_server/app/services/transport_service.py:592](../../../api/wms_api_server/app/services/transport_service.py#L592)

```python
get_task(self, task_id: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `_normalize_task_row`, `dict`, `self.gateway.fetch_all`

### create_task

[Исходник: api/wms_api_server/app/services/transport_service.py:625](../../../api/wms_api_server/app/services/transport_service.py#L625)

```python
create_task(self, req: TransportTaskCreateRequest, user_id: str) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `_normalize_transtype`, `create_existing_trip`, `str`

### update_task

[Исходник: api/wms_api_server/app/services/transport_service.py:630](../../../api/wms_api_server/app/services/transport_service.py#L630)

```python
update_task(self, task_id: int, req: TransportTaskUpdateRequest, user_id: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `_normalize_transtype`, `req.model_dump`, `str`, `update_existing_trip`

### close_task

[Исходник: api/wms_api_server/app/services/transport_service.py:638](../../../api/wms_api_server/app/services/transport_service.py#L638)

```python
close_task(self, task_id: int, user_id: str) -> None
```

Existing close action delegates the physical departure gate.

Вызывает: `HTTPException`, `_clear_task_sts_cache`, `_clear_vehicle_availability_cache`, `self._departure`, `str`

### cancel_task

[Исходник: api/wms_api_server/app/services/transport_service.py:651](../../../api/wms_api_server/app/services/transport_service.py#L651)

```python
cancel_task(self, task_id: int, user_id: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `_clear_available_sts_cache`, `_clear_task_sts_cache`, `cancel_trip`, `str`

### get_task_sts

[Исходник: api/wms_api_server/app/services/transport_service.py:664](../../../api/wms_api_server/app/services/transport_service.py#L664)

```python
get_task_sts(self, task_id: int) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_TASK_STS_CACHE.get`, `dict`, `self.gateway.fetch_all`, `time.monotonic`

### assign_sts

[Исходник: api/wms_api_server/app/services/transport_service.py:709](../../../api/wms_api_server/app/services/transport_service.py#L709)

```python
assign_sts(self, task_id: int, st_numbers: list[str], user_id: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `_clear_available_sts_cache`, `_clear_task_sts_cache`, `assign_sts`, `str`

### unassign_st

[Исходник: api/wms_api_server/app/services/transport_service.py:721](../../../api/wms_api_server/app/services/transport_service.py#L721)

```python
unassign_st(self, task_id: int, st_number: str, user_id: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `_clear_available_sts_cache`, `_clear_task_sts_cache`, `str`, `unassign_st`

### set_st_load_type

[Исходник: api/wms_api_server/app/services/transport_service.py:730](../../../api/wms_api_server/app/services/transport_service.py#L730)

```python
set_st_load_type(self, task_id: int, st_number: str, load_type: str, user_id: str) -> None
```

Установить способ погрузки СТ: '' | 'Г' | 'П'.

Вызывает: `_clear_task_sts_cache`, `self.gateway.execute`

### set_st_order

[Исходник: api/wms_api_server/app/services/transport_service.py:746](../../../api/wms_api_server/app/services/transport_service.py#L746)

```python
set_st_order(self, task_id: int, st_number: str, ord_value: int, user_id: str) -> None
```

Вручную задать порядок (ORD) адреса доставки в рейсе.

Вызывает: `_clear_task_sts_cache`, `self.gateway.execute`

### list_available_sts

[Исходник: api/wms_api_server/app/services/transport_service.py:766](../../../api/wms_api_server/app/services/transport_service.py#L766)

```python
list_available_sts(self, stdate: date | None=None, date_to: date | None=None, unassigned_only: bool=True, ware_id: int | None=None, ware_ids: list[int] | None=None, addr_mask: str | None=None, st_mask: str | None=None, st_mask_exclude: bool=False, transport_type: str | None=None, assembled_only: bool=False, not_assembled_only: bool=False, max_weight_kg: float | None=None, max_volume_m3: float | None=None, articul: str | None=None, raion: str | None=None, page: int | None=None, page_size: int | None=None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_AVAILABLE_STS_CACHE.get`, `_fill_visible_time_window`, `available_sts_query`, `dict`, `filters.values`, `isinstance`, `row.pop`, `self.gateway.fetch_all`, `time.monotonic`, `tuple`

### _has_sborka_rows_for_period

[Исходник: api/wms_api_server/app/services/transport_service.py:816](../../../api/wms_api_server/app/services/transport_service.py#L816)

```python
_has_sborka_rows_for_period(self, stdate: date | None, date_to: date | None, unassigned_only: bool) -> bool
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' AND '.join`, `bool`, `conditions.append`, `self.gateway.fetch_all`, `timedelta`

### get_planner_orders

[Исходник: api/wms_api_server/app/services/transport_service.py:853](../../../api/wms_api_server/app/services/transport_service.py#L853)

```python
get_planner_orders(self, plan_date: date | None=None, ware_ids: list[int] | None=None, transport_type: str | None=None) -> list[dict[str, Any]]
```

Возвращает свободные СТ с координатами для отображения на карте.

Вызывает: `' AND '.join`, `', '.join`, `_REF_CACHE.get`, `_fill_visible_time_window`, `conditions.append`, `dict`, `enumerate`, `len`, `range`, `self._has_sborka_rows_for_period`, `self.gateway.fetch_all`, `time.monotonic`, `timedelta`, `tuple`

### get_routing_status

[Исходник: api/wms_api_server/app/services/transport_service.py:942](../../../api/wms_api_server/app/services/transport_service.py#L942)

```python
get_routing_status(self) -> dict[str, Any]
```

Возвращает статус геокодирования адресов.

Вызывает: `HaversineProvider`, `HaversineProvider().is_available`, `OsrmProvider`, `OsrmProvider().is_available`, `ValhallaProvider`, `ValhallaProvider().is_available`, `_REF_CACHE.get`, `dict`, `get_active_provider`, `int`, `self.gateway.fetch_all`, `time.monotonic`

### list_st_pallets

[Исходник: api/wms_api_server/app/services/transport_service.py:986](../../../api/wms_api_server/app/services/transport_service.py#L986)

```python
list_st_pallets(self, st_number: str) -> list[dict[str, Any]]
```

Возвращает плоский список строк паллет для СТ — группировка по PALLET_UID на фронте.

Вызывает: `self.gateway.fetch_all`

### solve_vrp

[Исходник: api/wms_api_server/app/services/transport_service.py:1008](../../../api/wms_api_server/app/services/transport_service.py#L1008)

```python
solve_vrp(self, plan_date: date, ware_ids: list[int] | None=None, transport_type: str | None=None, time_limit_s: int=30, source: str='auto', solver: str='auto', cancel_event: 'threading.Event | None'=None) -> VrpPlanResponse
```

Запускает VRP-решатель, сохраняет план и возвращает ответ.

Вызывает: `HTTPException`, `VrpOrder`, `VrpPlanResponse`, `VrpRouteItem`, `VrpVehicle`, `_VrpPlanInner`, `_VrpRouteInner`, `_fallback_time_window_from_ord`, `_minutes_from_shift_start`, `am_available`, `bool`, `explain_steps.append`, `explain_warnings.append`, `float`, `get_active_provider`, `int`, `json.dumps`, `len`, `max`, `min`, `o.get`, `orders.append`, `planner_constraint_evidence`, `planner_inputs`, `round`, `route_payload`, `route_response`, `self.gateway.execute`, `self.gateway.fetch_all`, `self.get_planner_orders`, `self.list_vehicles`, `solve_am`, `str`, `sum`, `time.perf_counter` (остальные вызовы — в исходнике)

### apply_vrp_plan

[Исходник: api/wms_api_server/app/services/transport_service.py:1302](../../../api/wms_api_server/app/services/transport_service.py#L1302)

```python
apply_vrp_plan(self, plan_id: int, shipment_date: date, dock: str | None, user_id: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `_clear_available_sts_cache`, `_clear_task_sts_cache`, `apply_existing_plan`, `str`

### get_plan_metrics

[Исходник: api/wms_api_server/app/services/transport_service.py:1312](../../../api/wms_api_server/app/services/transport_service.py#L1312)

```python
get_plan_metrics(self, plan_id: int | None=None) -> dict[str, Any]
```

Возвращает метрики плана. plan_id=None → последний план.

Вызывает: `float`, `int`, `json.loads`, `len`, `plan_data.get`, `row.get`, `self.gateway.fetch_all`, `str`

### get_plan_templates

[Исходник: api/wms_api_server/app/services/transport_service.py:1366](../../../api/wms_api_server/app/services/transport_service.py#L1366)

```python
get_plan_templates(self, plan_date: date, lookback_days: int=90, min_jaccard: float=0.7, limit: int=5) -> list[dict[str, Any]]
```

Находит исторические планы, похожие на сегодняшний набор адресов,
используя Jaccard similarity по ST_NUMBER.

Возвращает список шаблонов: plan_id, plan_date, score, jaccard, routes_count.

Вызывает: `date.fromordinal`, `float`, `hist_sts.update`, `int`, `json.loads`, `len`, `plan_data.get`, `plan_date.toordinal`, `r.get`, `results.append`, `results.sort`, `round`, `route.get`, `row.get`, `self.gateway.fetch_all`, `self.get_planner_orders`, `set`, `str`

### get_plan_history

[Исходник: api/wms_api_server/app/services/transport_service.py:1434](../../../api/wms_api_server/app/services/transport_service.py#L1434)

```python
get_plan_history(self, date_from: date, date_to: date, limit: int=25) -> list[dict[str, Any]]
```

История применённых планов за период с метриками Score, утилизация, пробег.

Вызывает: `_REF_CACHE.get`, `dict`, `float`, `int`, `json.loads`, `len`, `max`, `min`, `plan_data.get`, `result.append`, `row.get`, `self.gateway.fetch_all`, `str`, `time.monotonic`

### get_demand_forecast

[Исходник: api/wms_api_server/app/services/transport_service.py:1479](../../../api/wms_api_server/app/services/transport_service.py#L1479)

```python
get_demand_forecast(self, target_date: date, lookback_weeks: int=8) -> dict[str, Any]
```

Прогноз числа СТ на целевую дату по историческим данным аналогичного дня недели.
Использует COUNT(*) из RRL_V_AVAILABLE_STS за предыдущие N недель того же дня.

Вызывает: `_REF_CACHE.get`, `counts.append`, `date.fromordinal`, `dict`, `int`, `len`, `range`, `round`, `self.gateway.fetch_all`, `str`, `sum`, `target_date.toordinal`, `target_date.weekday`, `time.monotonic`, `timedelta`

### _load_norms

[Исходник: api/wms_api_server/app/services/transport_service.py:1552](../../../api/wms_api_server/app/services/transport_service.py#L1552)

```python
_load_norms(self) -> dict[str, dict]
```

Загружает нормативы из RRL_TRANSPORT_NORMS → {code: {dur, per_unit}}.

Вызывает: `_cached_ref`, `float`, `int`, `self.gateway.fetch_all`

### plan_operations

[Исходник: api/wms_api_server/app/services/transport_service.py:1568](../../../api/wms_api_server/app/services/transport_service.py#L1568)

```python
plan_operations(self, task_id: int, user_id: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `_clear_vehicle_availability_cache`, `generate_existing_operations`, `str`

### get_operations

[Исходник: api/wms_api_server/app/services/transport_service.py:1577](../../../api/wms_api_server/app/services/transport_service.py#L1577)

```python
get_operations(self, task_id: int) -> list[dict]
```

Список операций рейса с расчётом отклонения.

Вызывает: `self._operation_row_to_dict`, `self.gateway.fetch_all`

### _operation_row_to_dict

[Исходник: api/wms_api_server/app/services/transport_service.py:1596](../../../api/wms_api_server/app/services/transport_service.py#L1596)

```python
_operation_row_to_dict(self, r: dict[str, Any]) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(_parse(r['FACT_END']) - _parse(r['PLAN_END'])).total_seconds`, `_parse`, `dt.strptime`, `float`, `int`, `r.get`, `round`, `str`

### update_operation_fact

[Исходник: api/wms_api_server/app/services/transport_service.py:1619](../../../api/wms_api_server/app/services/transport_service.py#L1619)

```python
update_operation_fact(self, op_id: int, data: OperationFactUpdate, user_id: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `_clear_vehicle_availability_cache`, `data.model_dump`, `str`, `update_existing_operation_fact`

### get_vehicles_gantt

[Исходник: api/wms_api_server/app/services/transport_service.py:1630](../../../api/wms_api_server/app/services/transport_service.py#L1630)

```python
get_vehicles_gantt(self, gantt_date: date) -> list[dict]
```

Данные Ганта для всех машин на день.

Вызывает: `HTTPException`, `by_vehicle.get`, `entry.pop`, `entry['operations'].append`, `gantt_rows`, `int`, `len`, `result.append`, `row.get`, `self._operation_row_to_dict`

### get_vehicles_available

[Исходник: api/wms_api_server/app/services/transport_service.py:1679](../../../api/wms_api_server/app/services/transport_service.py#L1679)

```python
get_vehicles_available(self, shipment_time: str, pallets: int) -> list[dict]
```

Возвращает список машин с индикатором доступности к времени отгрузки.

Проверки:
  1. Машина не занята в запрашиваемый интервал (текущая занятость).
  2. CLEAN_RETURNS.PLAN_END завершена до shipment_time (освобождение).
  3. Вместимость машины достаточна для переданного числа паллет.
  4. Машина не заблокирована (BLOCKED = 0).

Статус:
  green  — машина свободна к shipment_time
  yellow — освобождается < 60 мин позже
  red    — освободится > 60 мин позже или не хватает паллет

Вызывает: `(last_end_dt - requested_dt).total_seconds`, `HTTPException`, `_VEHICLE_AVAILABILITY_CACHE.get`, `bool`, `dict`, `dt.strptime`, `int`, `last_end_dt.strftime`, `order.get`, `r.get`, `requested_dt.date`, `requested_dt.strftime`, `result.append`, `result.sort`, `round`, `self.gateway.fetch_all`, `str`, `time.monotonic`

### list_billing_orders

[Исходник: api/wms_api_server/app/services/transport_service.py:1792](../../../api/wms_api_server/app/services/transport_service.py#L1792)

```python
list_billing_orders(self, company: str | None=None, date_from: date | None=None, date_to: date | None=None, closed: int | None=None, payed: int | None=None) -> list[dict]
```

Список биллинг-заказов с суммой и числом рейсов.

Вызывает: `' AND '.join`, `conditions.append`, `float`, `int`, `r.get`, `self.gateway.fetch_all`, `str`

### create_billing_order

[Исходник: api/wms_api_server/app/services/transport_service.py:1854](../../../api/wms_api_server/app/services/transport_service.py#L1854)

```python
create_billing_order(self, company: str, date_from: str, date_to: str) -> int
```

Создаёт новый биллинг-заказ и возвращает его ID.

Вызывает: `int`, `self.gateway.execute`, `self.gateway.fetch_all`

### add_tasks_to_order

[Исходник: api/wms_api_server/app/services/transport_service.py:1871](../../../api/wms_api_server/app/services/transport_service.py#L1871)

```python
add_tasks_to_order(self, order_id: int, tt_ids: list[int]) -> None
```

Привязывает рейсы к биллинг-заказу через legacy Oracle-функцию.

Вызывает: `HTTPException`, `result.lower`, `self.gateway.call_varchar_plsql`, `self.get_billing_order`

### get_task_billing

[Исходник: api/wms_api_server/app/services/transport_service.py:1883](../../../api/wms_api_server/app/services/transport_service.py#L1883)

```python
get_task_billing(self, tt_id: int) -> dict | None
```

Возвращает данные биллинг-заказа для рейса или None.

Вызывает: `int`, `r.get`, `self.gateway.fetch_all`

### get_billing_order

[Исходник: api/wms_api_server/app/services/transport_service.py:1912](../../../api/wms_api_server/app/services/transport_service.py#L1912)

```python
get_billing_order(self, order_id: int) -> dict | None
```

Один биллинг-заказ по ID.

Вызывает: `float`, `int`, `r.get`, `self.gateway.fetch_all`

### close_billing_order

[Исходник: api/wms_api_server/app/services/transport_service.py:1947](../../../api/wms_api_server/app/services/transport_service.py#L1947)

```python
close_billing_order(self, order_id: int) -> dict
```

Закрывает биллинг-заказ через Oracle-процедуру.

Вызывает: `HTTPException`, `result.lower`, `self.gateway.call_varchar_plsql`, `self.get_billing_order`

### pay_billing_order

[Исходник: api/wms_api_server/app/services/transport_service.py:1962](../../../api/wms_api_server/app/services/transport_service.py#L1962)

```python
pay_billing_order(self, order_id: int) -> dict
```

Отмечает биллинг-заказ как оплаченный через Oracle-процедуру.

Вызывает: `HTTPException`, `result.lower`, `self.gateway.call_varchar_plsql`, `self.get_billing_order`

### open_billing_for_task

[Исходник: api/wms_api_server/app/services/transport_service.py:1977](../../../api/wms_api_server/app/services/transport_service.py#L1977)

```python
open_billing_for_task(self, tt_id: int) -> dict
```

Создаёт биллинг-заказ для рейса и привязывает его.

Компания берётся из поля DOVERENNOST_OT водителя рейса.
Дата периода = дата отгрузки рейса.

Вызывает: `HTTPException`, `_date.today`, `float`, `self.add_tasks_to_order`, `self.create_billing_order`, `self.get_task`, `self.get_task_billing`, `str`, `task.get`

### get_billing_order_tasks

[Исходник: api/wms_api_server/app/services/transport_service.py:2005](../../../api/wms_api_server/app/services/transport_service.py#L2005)

```python
get_billing_order_tasks(self, order_id: int) -> list[dict]
```

Список рейсов в биллинг-заказе.

Вызывает: `HTTPException`, `_normalize_task_condition`, `float`, `int`, `r.get`, `self.gateway.fetch_all`, `self.get_billing_order`

### recalculate_price

[Исходник: api/wms_api_server/app/services/transport_service.py:2030](../../../api/wms_api_server/app/services/transport_service.py#L2030)

```python
recalculate_price(self, task_id: int) -> dict
```

Пересчитывает и сохраняет стоимость рейса через Oracle-функцию RRL_UPDATE_PRICE.

Вызывает: `HTTPException`, `float`, `self.gateway.call_optional_number_plsql`, `self.get_task`

### list_billing_companies

[Исходник: api/wms_api_server/app/services/transport_service.py:2042](../../../api/wms_api_server/app/services/transport_service.py#L2042)

```python
list_billing_companies(self) -> list[str]
```

Справочник транспортных компаний из RRL_BILL_COMPANY.

Вызывает: `_cached_ref`, `r.get`, `self.gateway.fetch_all`, `str`

### set_task_price

[Исходник: api/wms_api_server/app/services/transport_service.py:2057](../../../api/wms_api_server/app/services/transport_service.py#L2057)

```python
set_task_price(self, task_id: int, price: float) -> dict
```

Ручная установка стоимости рейса (право CREATE_TT_PRICE).

Вызывает: `HTTPException`, `self.gateway.execute`, `self.get_task`

### export_billing_order_xlsx

[Исходник: api/wms_api_server/app/services/transport_service.py:2068](../../../api/wms_api_server/app/services/transport_service.py#L2068)

```python
export_billing_order_xlsx(self, order_id: int) -> bytes
```

Генерирует XLSX-файл с составом биллинг-заказа (Sprint 26, DoD §12 #7).

Вызывает: `Alignment`, `Border`, `Font`, `HTTPException`, `PatternFill`, `Side`, `Workbook`, `buf.getvalue`, `enumerate`, `float`, `io.BytesIO`, `len`, `order.get`, `self._export_billing_order_xlsx_zip`, `self.get_billing_order`, `self.get_billing_order_tasks`, `t.get`, `wb.save`, `ws.cell`, `zip`

### _export_billing_order_xlsx_zip

[Исходник: api/wms_api_server/app/services/transport_service.py:2143](../../../api/wms_api_server/app/services/transport_service.py#L2143)

```python
_export_billing_order_xlsx_zip(self, order_id: int, order: dict, tasks: list[dict]) -> bytes
```

Минимальный XLSX без внешних зависимостей для окружений без openpyxl.

Вызывает: `''.join`, `archive.writestr`, `buf.getvalue`, `cell_ref`, `chr`, `divmod`, `enumerate`, `float`, `html.escape`, `io.BytesIO`, `isinstance`, `list`, `order.get`, `rows.append`, `sheet_rows.append`, `str`, `task.get`, `value_cell`, `zipfile.ZipFile`

### export_billing_registry_xlsx

[Исходник: api/wms_api_server/app/services/transport_service.py:2235](../../../api/wms_api_server/app/services/transport_service.py#L2235)

```python
export_billing_registry_xlsx(self, company: str | None=None, date_from: date | None=None, date_to: date | None=None, closed: int | None=None, payed: int | None=None) -> bytes
```

Генерирует XLSX-реестр всех счетов по фильтру (Sprint 27).

Вызывает: `' | '.join`, `Alignment`, `Border`, `Font`, `PatternFill`, `Side`, `Workbook`, `buf.getvalue`, `enumerate`, `filter`, `float`, `int`, `io.BytesIO`, `len`, `o.get`, `self._export_billing_registry_xlsx_zip`, `self.list_billing_orders`, `status_map.get`, `wb.save`, `ws.cell`, `zip`

### _export_billing_registry_xlsx_zip

[Исходник: api/wms_api_server/app/services/transport_service.py:2316](../../../api/wms_api_server/app/services/transport_service.py#L2316)

```python
_export_billing_registry_xlsx_zip(self, orders: list[dict], company: str | None, date_from: date | None, date_to: date | None) -> bytes
```

Минимальный XLSX-реестр без openpyxl.

Вызывает: `' | '.join`, `''.join`, `archive.writestr`, `buf.getvalue`, `cell_ref`, `chr`, `divmod`, `enumerate`, `filter`, `float`, `html.escape`, `int`, `io.BytesIO`, `isinstance`, `order.get`, `rows.append`, `sheet_rows.append`, `status_map.get`, `str`, `value_cell`, `zipfile.ZipFile`

### remove_task_from_billing_order

[Исходник: api/wms_api_server/app/services/transport_service.py:2419](../../../api/wms_api_server/app/services/transport_service.py#L2419)

```python
remove_task_from_billing_order(self, order_id: int, tt_id: int) -> dict
```

Отвязывает рейс от биллинг-заказа (обнуляет PAY_ORDER_ID).

Вызывает: `HTTPException`, `order.get`, `self.gateway.execute`, `self.get_billing_order`

### export_tasks_xlsx

[Исходник: api/wms_api_server/app/services/transport_service.py:2441](../../../api/wms_api_server/app/services/transport_service.py#L2441)

```python
export_tasks_xlsx(self, shipment_date: date | None=None, condition: str | None=None, task_id: int | None=None, transport_mask: str | None=None, company_mask: str | None=None, date_from: date | None=None, date_to: date | None=None, no_payments_only: bool=False) -> bytes
```

Генерирует XLSX-список рейсов (Sprint 28, ТЗ §3 «В Excel»).

Вызывает: `Alignment`, `Border`, `Font`, `PatternFill`, `Side`, `Workbook`, `buf.getvalue`, `chr`, `enumerate`, `float`, `io.BytesIO`, `self._export_tasks_xlsx_zip`, `self.list_tasks`, `str`, `t.get`, `wb.save`, `ws.cell`

### _export_tasks_xlsx_zip

[Исходник: api/wms_api_server/app/services/transport_service.py:2536](../../../api/wms_api_server/app/services/transport_service.py#L2536)

```python
_export_tasks_xlsx_zip(self, tasks: list[dict], shipment_date: date | None) -> bytes
```

Минимальный XLSX-список рейсов без openpyxl.

Вызывает: `''.join`, `archive.writestr`, `buf.getvalue`, `cell_ref`, `chr`, `divmod`, `enumerate`, `float`, `html.escape`, `io.BytesIO`, `isinstance`, `rows.append`, `sheet_rows.append`, `str`, `task.get`, `value_cell`, `zipfile.ZipFile`

### get_plan_fact

[Исходник: api/wms_api_server/app/services/transport_service.py:2626](../../../api/wms_api_server/app/services/transport_service.py#L2626)

```python
get_plan_fact(self, date_from: date, date_to: date, vehicle: str | None=None) -> list[dict]
```

Сводный план-фактный отчёт по всем рейсам периода.

Вызывает: `abs`, `int`, `result.append`, `round`, `self.gateway.fetch_all`, `self.get_operations`, `str`, `sum`, `t.get`

### load

[Исходник: api/wms_api_server/app/services/transport_service.py:268](../../../api/wms_api_server/app/services/transport_service.py#L268)

```python
load() -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### load

[Исходник: api/wms_api_server/app/services/transport_service.py:376](../../../api/wms_api_server/app/services/transport_service.py#L376)

```python
load() -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### load

[Исходник: api/wms_api_server/app/services/transport_service.py:459](../../../api/wms_api_server/app/services/transport_service.py#L459)

```python
load() -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### _parse

[Исходник: api/wms_api_server/app/services/transport_service.py:1599](../../../api/wms_api_server/app/services/transport_service.py#L1599)

```python
_parse(value: Any)
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `dt.strptime`, `str`

### cell_ref

[Исходник: api/wms_api_server/app/services/transport_service.py:2149](../../../api/wms_api_server/app/services/transport_service.py#L2149)

```python
cell_ref(row: int, col: int) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `chr`, `divmod`

### value_cell

[Исходник: api/wms_api_server/app/services/transport_service.py:2156](../../../api/wms_api_server/app/services/transport_service.py#L2156)

```python
value_cell(row: int, col: int, value: object) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cell_ref`, `html.escape`, `isinstance`, `str`

### cell_ref

[Исходник: api/wms_api_server/app/services/transport_service.py:2328](../../../api/wms_api_server/app/services/transport_service.py#L2328)

```python
cell_ref(row: int, col: int) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `chr`, `divmod`

### value_cell

[Исходник: api/wms_api_server/app/services/transport_service.py:2335](../../../api/wms_api_server/app/services/transport_service.py#L2335)

```python
value_cell(row: int, col: int, value: object) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cell_ref`, `html.escape`, `isinstance`, `str`

### cell_ref

[Исходник: api/wms_api_server/app/services/transport_service.py:2542](../../../api/wms_api_server/app/services/transport_service.py#L2542)

```python
cell_ref(row: int, col: int) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `chr`, `divmod`

### value_cell

[Исходник: api/wms_api_server/app/services/transport_service.py:2549](../../../api/wms_api_server/app/services/transport_service.py#L2549)

```python
value_cell(row: int, col: int, value: object) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cell_ref`, `html.escape`, `isinstance`, `str`

### normalize_pallet_identifier

[Исходник: api/wms_api_server/app/services/tserver_service.py:28](../../../api/wms_api_server/app/services/tserver_service.py#L28)

```python
normalize_pallet_identifier(value: str) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(value or '').strip`, `candidate.startswith`, `match.group`, `re.fullmatch`, `re.sub`

### __init__

[Исходник: api/wms_api_server/app/services/tserver_service.py:66](../../../api/wms_api_server/app/services/tserver_service.py#L66)

```python
__init__(self, gateway: OracleGateway | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`

### execute_legacy_payload

[Исходник: api/wms_api_server/app/services/tserver_service.py:69](../../../api/wms_api_server/app/services/tserver_service.py#L69)

```python
execute_legacy_payload(self, payload: str, actor: str | None=None) -> tuple[str, list[LegacyBlock]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `encode_legacy_blocks`, `fault`, `parse_legacy_payload`, `self._dispatch`, `str`

### _dispatch

[Исходник: api/wms_api_server/app/services/tserver_service.py:82](../../../api/wms_api_server/app/services/tserver_service.py#L82)

```python
_dispatch(self, blocks: list[LegacyBlock], actor: str | None=None) -> list[LegacyBlock]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CallSpfRequest`, `LegacyBlock`, `dict`, `head.get`, `key.lower`, `self._lot_check_from_legacy`, `self._order_check_from_legacy`, `self._place_check_from_legacy`, `self.call_spf`, `self.confirm_lot_check`, `self.confirm_order_check`, `self.confirm_place_check`, `self.get_lot_items`, `self.get_place_items`, `self.get_product_info`, `self.get_ruser`, `zero`

### get_ruser

[Исходник: api/wms_api_server/app/services/tserver_service.py:118](../../../api/wms_api_server/app/services/tserver_service.py#L118)

```python
get_ruser(self, user_id: str) -> list[LegacyBlock]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LegacyBlock`, `row.get`, `scalar_to_text`, `self.gateway.fetch_all`

### get_product_info

[Исходник: api/wms_api_server/app/services/tserver_service.py:156](../../../api/wms_api_server/app/services/tserver_service.py#L156)

```python
get_product_info(self, barcode: str) -> list[LegacyBlock]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LegacyBlock`, `barcode.strip`, `row.get`, `scalar_to_text`, `self.gateway.fetch_all`, `str`

### get_lot_items

[Исходник: api/wms_api_server/app/services/tserver_service.py:262](../../../api/wms_api_server/app/services/tserver_service.py#L262)

```python
get_lot_items(self, usscc: str) -> list[LegacyBlock]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LegacyBlock`, `blocks.append`, `enumerate`, `len`, `normalize_pallet_identifier`, `row.get`, `rows[0].get`, `scalar_to_text`, `self.gateway.fetch_all`, `str`

### get_place_items

[Исходник: api/wms_api_server/app/services/tserver_service.py:317](../../../api/wms_api_server/app/services/tserver_service.py#L317)

```python
get_place_items(self, place_id: str) -> list[LegacyBlock]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LegacyBlock`, `blocks.append`, `enumerate`, `len`, `row.get`, `scalar_to_text`, `self.gateway.fetch_all`, `str`

### confirm_lot_check

[Исходник: api/wms_api_server/app/services/tserver_service.py:392](../../../api/wms_api_server/app/services/tserver_service.py#L392)

```python
confirm_lot_check(self, usscc: str, request: LotCheckRequest) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `normalize_pallet_identifier`, `post_existing_terminal_quality`

### confirm_place_check

[Исходник: api/wms_api_server/app/services/tserver_service.py:397](../../../api/wms_api_server/app/services/tserver_service.py#L397)

```python
confirm_place_check(self, request: PlaceCheckRequest) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.execute_many`, `statements.append`

### confirm_order_check

[Исходник: api/wms_api_server/app/services/tserver_service.py:450](../../../api/wms_api_server/app/services/tserver_service.py#L450)

```python
confirm_order_check(self, request: OrderCheckRequest) -> dict[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.execute_many`, `statements.append`

### call_spf

[Исходник: api/wms_api_server/app/services/tserver_service.py:488](../../../api/wms_api_server/app/services/tserver_service.py#L488)

```python
call_spf(self, request: CallSpfRequest, actor: str | None=None) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `key.lower`, `name.upper`, `params.pop`, `request.params.items`, `request.spf_name.strip`, `self.gateway.call_varchar_function`

### _lot_check_from_legacy

[Исходник: api/wms_api_server/app/services/tserver_service.py:505](../../../api/wms_api_server/app/services/tserver_service.py#L505)

```python
_lot_check_from_legacy(self, blocks: list[LegacyBlock]) -> LotCheckRequest
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LotCheckRequest`, `block.get`, `errors.append`, `float`, `head.get`, `int`, `vp_lines.append`

### _place_check_from_legacy

[Исходник: api/wms_api_server/app/services/tserver_service.py:537](../../../api/wms_api_server/app/services/tserver_service.py#L537)

```python
_place_check_from_legacy(self, blocks: list[LegacyBlock]) -> PlaceCheckRequest
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `PlaceCheckRequest`, `block.get`, `errors.append`, `float`, `head.get`, `inventory_lines.append`

### _order_check_from_legacy

[Исходник: api/wms_api_server/app/services/tserver_service.py:562](../../../api/wms_api_server/app/services/tserver_service.py#L562)

```python
_order_check_from_legacy(self, blocks: list[LegacyBlock]) -> OrderCheckRequest
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OrderCheckRequest`, `block.get`, `errors.append`, `float`, `head.get`

### put_event

[Исходник: api/wms_api_server/app/services/vrp_job_store.py:26](../../../api/wms_api_server/app/services/vrp_job_store.py#L26)

```python
put_event(self, event: dict) -> None
```

Вызывается из sync-потока VRP-решателя.

Вызывает: `asyncio.run_coroutine_threadsafe`, `self._loop.is_running`, `self._queue.put`, `self.events.append`

### stream

[Исходник: api/wms_api_server/app/services/vrp_job_store.py:32](../../../api/wms_api_server/app/services/vrp_job_store.py#L32)

```python
stream(self) -> AsyncGenerator[str, None]
```

Генератор SSE-событий для GET /planner/solve/{job_id}/stream.

Вызывает: `asyncio.Queue`, `asyncio.get_running_loop`, `asyncio.wait_for`, `json.dumps`, `self._queue.get`

### __init__

[Исходник: api/wms_api_server/app/services/vrp_job_store.py:53](../../../api/wms_api_server/app/services/vrp_job_store.py#L53)

```python
__init__(self) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `threading.Lock`

### create

[Исходник: api/wms_api_server/app/services/vrp_job_store.py:57](../../../api/wms_api_server/app/services/vrp_job_store.py#L57)

```python
create(self) -> VrpJob
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `VrpJob`, `str`, `uuid.uuid4`

### get

[Исходник: api/wms_api_server/app/services/vrp_job_store.py:63](../../../api/wms_api_server/app/services/vrp_job_store.py#L63)

```python
get(self, job_id: str) -> VrpJob | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self._jobs.get`

### cancel

[Исходник: api/wms_api_server/app/services/vrp_job_store.py:66](../../../api/wms_api_server/app/services/vrp_job_store.py#L66)

```python
cancel(self, job_id: str) -> bool
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `job.cancel_event.set`, `job.put_event`, `self.get`

### cleanup_done

[Исходник: api/wms_api_server/app/services/vrp_job_store.py:75](../../../api/wms_api_server/app/services/vrp_job_store.py#L75)

```python
cleanup_done(self) -> None
```

Удалить завершённые задачи (вызывать периодически).

Вызывает: `self._jobs.items`

### _hav_km

[Исходник: api/wms_api_server/app/services/vrp_solver.py:35](../../../api/wms_api_server/app/services/vrp_solver.py#L35)

```python
_hav_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `math.asin`, `math.cos`, `math.radians`, `math.sin`, `math.sqrt`

### _dist

[Исходник: api/wms_api_server/app/services/vrp_solver.py:44](../../../api/wms_api_server/app/services/vrp_solver.py#L44)

```python
_dist(a: VrpOrder, b: VrpOrder) -> float
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_hav_km`

### _solve_ortools

[Исходник: api/wms_api_server/app/services/vrp_solver.py:52](../../../api/wms_api_server/app/services/vrp_solver.py#L52)

```python
_solve_ortools(orders: list[VrpOrder], vehicles: list[VrpVehicle], dist_matrix: list[list[int]], depot_idx: int, time_limit_s: int, time_matrix: list[list[int]] | None=None) -> 'Any'
```

Returns (manager, routing, solution) or raises ImportError.

Вызывает: `enumerate`, `len`, `manager.IndexToNode`, `manager.NodeToIndex`, `math.ceil`, `pywrapcp.DefaultRoutingSearchParameters`, `pywrapcp.RoutingIndexManager`, `pywrapcp.RoutingModel`, `range`, `routing.AddDimension`, `routing.AddDimensionWithVehicleCapacity`, `routing.AddDisjunction`, `routing.GetDimensionOrDie`, `routing.RegisterTransitCallback`, `routing.RegisterUnaryTransitCallback`, `routing.SetArcCostEvaluatorOfAllVehicles`, `routing.SolveWithParameters`, `time_dim.CumulVar`, `time_dim.CumulVar(node_idx).SetRange`, `time_dim.SetCumulVarSoftLowerBound`, `time_dim.SetCumulVarSoftUpperBound`

### _solve_clarke_wright

[Исходник: api/wms_api_server/app/services/vrp_solver.py:148](../../../api/wms_api_server/app/services/vrp_solver.py#L148)

```python
_solve_clarke_wright(orders: list[VrpOrder], vehicles: list[VrpVehicle]) -> VrpPlan
```

Greedy Clarke-Wright savings heuristic — O(n² log n).

Вызывает: `VrpPlan`, `VrpRoute`, `_Depot`, `_can_add`, `_d`, `_hav_km`, `assigned.add`, `enumerate`, `int`, `len`, `range`, `round`, `route.stops.append`, `set`, `sorted`, `sum`, `time.time`

### _solve_dbscan_cluster

[Исходник: api/wms_api_server/app/services/vrp_solver.py:258](../../../api/wms_api_server/app/services/vrp_solver.py#L258)

```python
_solve_dbscan_cluster(orders: list[VrpOrder], vehicles: list[VrpVehicle], dist_cache: dict[tuple[str, str], float] | None, time_limit_s: int) -> VrpPlan
```

Кластеризует заказы DBSCAN → запускает локальный VRP в каждом кластере.
Если sklearn недоступен — откатывается до Clarke-Wright.

Вызывает: `DBSCAN`, `DBSCAN(eps=0.5, min_samples=2, metric='haversine').fit`, `VrpPlan`, `_solve_clarke_wright`, `all_routes.extend`, `clusters.keys`, `clusters.setdefault`, `clusters.setdefault(label, []).append`, `enumerate`, `int`, `len`, `list`, `max`, `np.array`, `np.radians`, `round`, `sorted`, `sum`, `time.time`, `unassigned_orders.extend`

### solve

[Исходник: api/wms_api_server/app/services/vrp_solver.py:329](../../../api/wms_api_server/app/services/vrp_solver.py#L329)

```python
solve(orders: list[VrpOrder], vehicles: list[VrpVehicle], dist_cache: dict[tuple[str, str], float] | None=None, time_limit_s: int=30, solver: str='auto', duration_cache: dict[tuple[str, str], float] | None=None, origin: dict | None=None) -> VrpPlan
```

Запускает решатель.

solver: 'auto' | 'ortools' | 'cluster' | 'savings'
Приоритет при 'auto':
  1. OR-Tools CVRPTW (если установлен)
  2. Clarke-Wright savings (всегда доступен)

Вызывает: `VrpPlan`, `_solve_clarke_wright`, `_solve_dbscan_cluster`, `_solve_with_ortools`, `_t.time`, `time.time`

### _solve_with_ortools

[Исходник: api/wms_api_server/app/services/vrp_solver.py:372](../../../api/wms_api_server/app/services/vrp_solver.py#L372)

```python
_solve_with_ortools(orders: list[VrpOrder], vehicles: list[VrpVehicle], dist_cache: dict[tuple[str, str], float] | None, time_limit_s: int, t0: float, duration_cache: dict[tuple[str, str], float] | None=None, origin: dict | None=None) -> VrpPlan
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `VrpPlan`, `_solve_clarke_wright`, `_solve_ortools`, `distance_costs`, `extract_solver_routes`, `int`, `len`, `round`, `sum`, `time.time`, `travel_times`

### dist_cb

[Исходник: api/wms_api_server/app/services/vrp_solver.py:71](../../../api/wms_api_server/app/services/vrp_solver.py#L71)

```python
dist_cb(from_idx: int, to_idx: int) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `manager.IndexToNode`

### pallet_demand

[Исходник: api/wms_api_server/app/services/vrp_solver.py:80](../../../api/wms_api_server/app/services/vrp_solver.py#L80)

```python
pallet_demand(idx: int) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `manager.IndexToNode`

### time_cb

[Исходник: api/wms_api_server/app/services/vrp_solver.py:98](../../../api/wms_api_server/app/services/vrp_solver.py#L98)

```python
time_cb(from_idx: int, to_idx: int) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `manager.IndexToNode`, `math.ceil`

### _d

[Исходник: api/wms_api_server/app/services/vrp_solver.py:170](../../../api/wms_api_server/app/services/vrp_solver.py#L170)

```python
_d(a: Any, b: Any) -> float
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_hav_km`

### _can_add

[Исходник: api/wms_api_server/app/services/vrp_solver.py:186](../../../api/wms_api_server/app/services/vrp_solver.py#L186)

```python
_can_add(route: VrpRoute, order: VrpOrder) -> bool
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### __init__

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:45](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L45)

```python
__init__(self, root_dir: str | None=None, gateway: OracleGateway | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `Path`, `os.getenv`, `self.root.mkdir`

### list_drafts

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:50](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L50)

```python
list_drafts(self) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `drafts.sort`, `item.get`, `self._read`, `self._summary`, `self.root.glob`, `sorted`, `str`

### create_draft

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:55](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L55)

```python
create_draft(self, request: WarehouseMapDraftCreateRequest, username: str | None) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `bytearray`, `grid.model_dump`, `self._cell_count`, `self._count_roles`, `self._decode_roles`, `self._encode_roles`, `self._now`, `self._write`, `uuid4`

### get_draft

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:95](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L95)

```python
get_draft(self, draft_id: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self._path`, `self._read`

### load_from_db

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:98](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L98)

```python
load_from_db(self, request: WarehouseMapDraftLoadFromDbRequest, username: str | None) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `WarehouseMapGrid`, `canvas.get`, `dict`, `draft.get`, `int`, `isinstance`, `payload.get`, `self._count_roles`, `self._decode_roles`, `self._encode_roles`, `self._now`, `self._oracle_draft_payload`, `self._require_canvas`, `self._reset_base_snapshots`, `self._write`, `str`, `uuid4`

### save_to_db

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:128](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L128)

```python
save_to_db(self, draft_id: str, request: WarehouseMapDraftSaveToDbRequest, username: str | None) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `WarehouseMapGrid`, `canvas.get`, `draft.get`, `existing_canvas.get`, `int`, `item.get`, `len`, `self._canvas_code`, `self._create_canvas_payload`, `self._ensure_default_camera`, `self._ensure_revision`, `self._find_canvas_by_code`, `self._find_canvas_by_idempotency_key`, `self._first_camera_id`, `self._idempotency_key`, `self._now`, `self._require_canvas`, `self._require_warehouse`, `self._reset_base_snapshots`, `self._set_canvas_idempotency_key`, `self._update_canvas_payload`, `self._write`, `self.get_draft`, `self.validate_draft`

### patch_cells

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:211](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L211)

```python
patch_cells(self, draft_id: str, request: WarehouseMapDraftCellsPatchRequest, username: str | None) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `WarehouseMapGrid`, `draft.get`, `int`, `self._count_roles`, `self._decode_roles`, `self._encode_roles`, `self._ensure_revision`, `self._now`, `self._write`, `self.get_draft`

### patch_metadata

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:224](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L224)

```python
patch_metadata(self, draft_id: str, request: WarehouseMapDraftMetadataPatchRequest, username: str | None) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `draft.get`, `int`, `self._ensure_revision`, `self._now`, `self._write`, `self.get_draft`

### diff_draft

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:241](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L241)

```python
diff_draft(self, draft_id: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `WarehouseMapGrid`, `changed_by_role.get`, `draft.get`, `enumerate`, `int`, `item.get`, `len`, `preview.append`, `self._cell_from_index`, `self._decode_roles`, `self._json_changed`, `self._list_diff_count`, `self._physical_cell_code`, `self.get_draft`, `zip`

### build_route

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:281](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L281)

```python
build_route(self, draft_id: str, request: WarehouseMapDraftRouteBuildRequest, username: str | None) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `WarehouseMapGrid`, `draft.get`, `float`, `int`, `item.get`, `len`, `route_rows.append`, `route_rows.sort`, `self._cell_index`, `self._decode_roles`, `self._ensure_revision`, `self._normalize_selection`, `self._now`, `self._physical_cell_code`, `self._route_ordered_cells`, `self._write`, `self.get_draft`, `uuid4`

### patch_route

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:340](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L340)

```python
patch_route(self, draft_id: str, request: WarehouseMapDraftRoutePatchRequest, username: str | None) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `draft.get`, `float`, `int`, `item.get`, `len`, `route_rows.sort`, `route_rows[0].get`, `self._ensure_revision`, `self._normalize_route_rows`, `self._now`, `self._write`, `self.get_draft`

### bulk_role

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:364](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L364)

```python
bulk_role(self, draft_id: str, request: WarehouseMapBulkRoleRequest, username: str | None) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `WarehouseMapGrid`, `range`, `self._cell_index`, `self._count_roles`, `self._decode_roles`, `self._encode_roles`, `self._normalize_selection`, `self._now`, `self._request_selections`, `self._selection_size`, `self._write`, `self.get_draft`, `sum`

### validate_draft

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:398](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L398)

```python
validate_draft(self, draft_id: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `WarehouseMapGrid`, `codes.count`, `draft.get`, `errors.append`, `errors.extend`, `int`, `item.get`, `len`, `self._cell_count`, `self._cell_index`, `self._count_roles`, `self._decode_roles`, `self._validate_route_rows`, `self._validate_small_pick_faces`, `self._validate_storage_slots`, `self.get_draft`, `sorted`, `str`

### preview_projection

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:440](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L440)

```python
preview_projection(self, draft_id: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `WarehouseMapGrid`, `cells.append`, `draft.get`, `item.get`, `len`, `range`, `role_counts.values`, `round`, `self._cell_index`, `self._decode_roles`, `self._physical_cell_code`, `self.get_draft`, `self.validate_draft`, `sum`

### save_projection_to_topology

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:517](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L517)

```python
save_projection_to_topology(self, draft_id: str, request: WarehouseMapDraftProjectionSaveRequest, username: str | None) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `WarehouseMapGrid`, `cell_rows.append`, `cursor.execute`, `cursor.executemany`, `cursor.fetchall`, `cursor.fetchone`, `draft.get`, `existing_topology.get`, `grouped_slots.items`, `grouped_slots.setdefault`, `grouped_slots.setdefault(slot['sql'], []).append`, `int`, `len`, `role_counts.get`, `self._camera_id_for_projected_cell`, `self._decode_roles`, `self._ensure_revision`, `self._find_topology_by_code`, `self._find_topology_by_idempotency_key`, `self._idempotency_key`, `self._now`, `self._projection_camera_regions`, `self._projection_cells`, `self._projection_slot_rows`, `self._require_warehouse`, `self._topology_code`, `self._topology_projection_counts`, `self._write`, `self.gateway.transaction`, `self.get_draft`, `self.validate_draft`, `str`, `zip`

### save_route_to_db

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:702](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L702)

```python
save_route_to_db(self, draft_id: str, request: WarehouseMapDraftRouteSaveToDbRequest, username: str | None) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `draft.get`, `enumerate`, `existing_route.get`, `float`, `int`, `item.get`, `len`, `oracle_validation.get`, `route_rows[0].get`, `row.get`, `self._active_pick_route_for_topology`, `self._ensure_revision`, `self._find_route_by_idempotency_key`, `self._idempotency_key`, `self._nextval`, `self._now`, `self._require_topology`, `self._route_code`, `self._route_row_count`, `self._route_row_to_oracle`, `self._topology_route_lookup`, `self._validate_oracle_draft`, `self._write`, `self.gateway.execute`, `self.gateway.execute_many`, `self.get_draft`, `self.validate_draft`, `sorted`, `statements.append`, `str`, `topology.get`

### publish_oracle

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:830](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L830)

```python
publish_oracle(self, draft_id: str, request: WarehouseMapDraftOraclePublishRequest, username: str | None) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `draft.get`, `int`, `oracle_validation.get`, `self._canvas_publish_idempotency_key`, `self._ensure_revision`, `self._idempotency_key`, `self._now`, `self._oracle_publish_status`, `self._set_canvas_publish_idempotency_key`, `self._validate_oracle_draft`, `self._write`, `self.gateway.execute`, `self.gateway.execute_plsql`, `self.get_draft`, `statuses.get`, `str`

### generate_pick_face_addresses

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:932](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L932)

```python
generate_pick_face_addresses(self, draft_id: str, request: WarehouseMapPickFaceAddressRequest, username: str | None) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `WarehouseMapGrid`, `addresses.append`, `cells.reverse`, `draft.get`, `len`, `preview.append`, `request.anchor_cell.model_dump`, `request.focus_cell.model_dump`, `self._address_inside`, `self._cell_index`, `self._decode_roles`, `self._format_pick_face_code`, `self._normalize_selection`, `self._now`, `self._ordered_cells`, `self._write`, `self.get_draft`

### publish_draft

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:985](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L985)

```python
publish_draft(self, draft_id: str, username: str | None) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `draft.get`, `item.get`, `json.dumps`, `len`, `self._now`, `self._published_path`, `self._published_path(published['published_topology_id']).write_text`, `self._write`, `self.get_draft`, `self.validate_draft`, `uuid4`

### generate_small_pick_faces

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1013](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1013)

```python
generate_small_pick_faces(self, draft_id: str, request: WarehouseMapSmallPickFaceGenerateRequest, username: str | None) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `WarehouseMapGrid`, `cell.model_dump`, `created.append`, `draft.get`, `len`, `self._cell_index`, `self._count_roles`, `self._decode_roles`, `self._encode_roles`, `self._ensure_cell_inside`, `self._format_small_pick_code`, `self._is_same_physical_cell_ref`, `self._now`, `self._physical_cell_code`, `self._small_pick_positions`, `self._small_pick_request_cells`, `self._write`, `self.get_draft`, `uuid4`

### patch_small_pick_face

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1064](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1064)

```python
patch_small_pick_face(self, draft_id: str, small_pick_face_id: str, request: WarehouseMapSmallPickFacePatchRequest, username: str | None) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `draft.get`, `getattr`, `item.get`, `next`, `self._now`, `self._write`, `self.get_draft`

### renumber_small_pick_faces

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1082](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1082)

```python
renumber_small_pick_faces(self, draft_id: str, request: WarehouseMapSmallPickFaceRenumberRequest, username: str | None) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `WarehouseMapGrid`, `draft.get`, `item.get`, `len`, `self._ensure_cell_inside`, `self._is_same_physical_cell`, `self._now`, `self._small_pick_sort_key`, `self._write`, `self.get_draft`, `target.sort`

### generate_storage_slots

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1108](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1108)

```python
generate_storage_slots(self, draft_id: str, request: WarehouseMapStorageSlotGenerateRequest, username: str | None) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `WarehouseMapGrid`, `cell.model_dump`, `created.append`, `draft.get`, `len`, `range`, `self._cell_index`, `self._count_roles`, `self._decode_roles`, `self._encode_roles`, `self._ensure_cell_inside`, `self._format_storage_slot_code`, `self._is_same_physical_cell_ref`, `self._now`, `self._physical_cell_code`, `self._small_pick_request_cells`, `self._write`, `self.get_draft`, `uuid4`

### patch_storage_slot

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1167](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1167)

```python
patch_storage_slot(self, draft_id: str, storage_slot_id: str, request: WarehouseMapStorageSlotPatchRequest, username: str | None) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `draft.get`, `getattr`, `item.get`, `next`, `self._now`, `self._write`, `self.get_draft`

### _request_selections

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1185](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1185)

```python
_request_selections(self, request: WarehouseMapBulkRoleRequest) -> list[WarehouseMapSelectionRequest]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `list`, `selections.append`

### _normalize_selection

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1193](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1193)

```python
_normalize_selection(self, selection: WarehouseMapSelectionRequest, grid: WarehouseMapGrid) -> WarehouseMapSelectionRequest
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `WarehouseMapSelectionRequest`, `max`, `min`

### _summary

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1211](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1211)

```python
_summary(self, draft: dict) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `draft.get`

### _path

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1214](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1214)

```python
_path(self, draft_id: str) -> Path
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `draft_id.replace`, `draft_id.replace('-', '').replace`, `draft_id.replace('-', '').replace('_', '').isalnum`

### _published_path

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1219](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1219)

```python
_published_path(self, published_topology_id: str) -> Path
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `published_root.mkdir`

### _require_warehouse

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1224](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1224)

```python
_require_warehouse(self, ware_id: int) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `self.gateway.fetch_all`

### _require_canvas

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1233](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1233)

```python
_require_canvas(self, canvas_id: int) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `self.gateway.fetch_all`

### _find_canvas_by_code

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1247](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1247)

```python
_find_canvas_by_code(self, ware_id: int, canvas_code: str) -> dict | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### _find_canvas_by_idempotency_key

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1260](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1260)

```python
_find_canvas_by_idempotency_key(self, ware_id: int, idempotency_key: str) -> dict | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### _set_canvas_idempotency_key

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1273](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1273)

```python
_set_canvas_idempotency_key(self, canvas_id: int, idempotency_key: str, updated_by: str | None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.execute`

### _first_camera_id

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1286](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1286)

```python
_first_camera_id(self, canvas_id: int) -> int | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `int`, `self.gateway.fetch_all`

### _require_topology

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1299](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1299)

```python
_require_topology(self, topology_id: int, ware_id: int) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `self.gateway.fetch_all`

### _find_topology_by_code

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1314](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1314)

```python
_find_topology_by_code(self, ware_id: int, topology_code: str) -> dict | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### _find_topology_by_idempotency_key

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1327](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1327)

```python
_find_topology_by_idempotency_key(self, ware_id: int, idempotency_key: str) -> dict | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### _topology_projection_counts

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1340](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1340)

```python
_topology_projection_counts(self, topology_id: int) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `int`, `role_counts.values`, `self.gateway.fetch_all`, `slot_counts.get`, `str`, `sum`

### _active_pick_route_for_topology

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1373](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1373)

```python
_active_pick_route_for_topology(self, topology_id: int, route_code: str | None=None) -> dict | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### _find_route_by_idempotency_key

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1395](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1395)

```python
_find_route_by_idempotency_key(self, topology_id: int, idempotency_key: str) -> dict | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### _route_row_count

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1411](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1411)

```python
_route_row_count(self, pick_route_id: int) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `int`, `self.gateway.fetch_all`

### _oracle_draft_payload

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1423](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1423)

```python
_oracle_draft_payload(self, canvas: dict) -> dict | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `canvas.get`, `json.loads`, `payload.get`, `str`

### _create_canvas_payload

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1435](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1435)

```python
_create_canvas_payload(self, request: WarehouseMapDraftSaveToDbRequest, draft: dict, grid: WarehouseMapGrid, updated_by: str | None) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `draft.get`, `self._canvas_code`, `self._db_payload`, `self._json_text`, `self._nextval`, `self.gateway.execute`

### _update_canvas_payload

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1472](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1472)

```python
_update_canvas_payload(self, canvas_id: int, request: WarehouseMapDraftSaveToDbRequest, draft: dict, grid: WarehouseMapGrid, updated_by: str | None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self._db_payload`, `self._json_text`, `self._now`, `self.gateway.execute`

### _ensure_default_camera

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1507](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1507)

```python
_ensure_default_camera(self, canvas_id: int, ware_id: int, request: WarehouseMapDraftSaveToDbRequest, grid: WarehouseMapGrid, updated_by: str | None) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `grid.model_dump`, `int`, `round`, `self._json_text`, `self._nextval`, `self.gateway.execute`, `self.gateway.fetch_all`

### _db_payload

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1587](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1587)

```python
_db_payload(self, draft: dict) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self._now`

### _canvas_code

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1594](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1594)

```python
_canvas_code(self, request: WarehouseMapDraftSaveToDbRequest, draft: dict, canvas_id: int) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `''.join`, `''.join((ch if ch.isalnum() or ch in {'-', '_'} else '-' for ch in str(raw).upper())).strip`, `ch.isalnum`, `draft.get`, `str`, `str(raw).upper`

### _topology_code

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1599](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1599)

```python
_topology_code(self, request: WarehouseMapDraftProjectionSaveRequest, draft: dict, topology_id: int) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `''.join`, `''.join((ch if ch.isalnum() or ch in {'-', '_'} else '-' for ch in str(raw).upper())).strip`, `ch.isalnum`, `draft.get`, `str`, `str(raw).upper`

### _route_code

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1604](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1604)

```python
_route_code(self, request: WarehouseMapDraftRouteSaveToDbRequest, route_rows: list[dict], topology_id: int) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `''.join`, `''.join((ch if ch.isalnum() or ch in {'-', '_'} else '-' for ch in str(raw).upper())).strip`, `ch.isalnum`, `route_rows[0].get`, `str`, `str(raw).upper`

### _idempotency_key

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1609](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1609)

```python
_idempotency_key(self, value: str | None) -> str | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `''.join`, `ch.isalnum`, `normalized.strip`, `str`, `str(value).strip`

### _projection_cells

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1620](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1620)

```python
_projection_cells(self, grid: WarehouseMapGrid, roles: bytearray) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cells.append`, `range`, `round`, `self._cell_index`, `self._physical_cell_code`

### _projection_camera_regions

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1653](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1653)

```python
_projection_camera_regions(self, draft: dict, default_camera_id: int | None) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `draft.get`, `int`, `item.get`, `metadata.get`, `regions.append`, `self._active_camera_ids`

### _active_camera_ids

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1687](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1687)

```python
_active_camera_ids(self, canvas_id: int) -> set[int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `int`, `self.gateway.fetch_all`, `set`

### _camera_id_for_projected_cell

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1701](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1701)

```python
_camera_id_for_projected_cell(self, regions: list[dict], cell: dict) -> int | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `int`

### _projection_slot_rows

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1711](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1711)

```python
_projection_slot_rows(self, draft: dict, projected_cells: dict[str, int], topology_id: int, updated_by: str | None) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `draft.get`, `enumerate`, `int`, `item.get`, `pick_indexes.get`, `projected_cells.get`, `rows.append`, `self._slot_statement`, `slot.get`, `storage_indexes.get`, `str`

### _slot_statement

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1769](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1769)

```python
_slot_statement(self, topology_id: int, topology_cell_id: int, parent_slot_layer_kind: str, slot_kind: str, slot_code: str, fraction_count: int, fraction_index: int, sub_level, sub_column, pick_order, storage_order, capacity_qty, capacity_volume_m3, capacity_weight_kg, updated_by: str | None) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### _topology_route_lookup

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1822](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1822)

```python
_topology_route_lookup(self, topology_id: int) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self._group_pick_slots_by_parent`, `self.gateway.fetch_all`, `str`

### _group_pick_slots_by_parent

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1857](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1857)

```python
_group_pick_slots_by_parent(self, slots: list[dict]) -> dict[str, list[dict]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `grouped.setdefault`, `grouped.setdefault(parent, []).append`, `grouped.values`, `item.get`, `items.sort`, `str`

### _route_row_to_oracle

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1868](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1868)

```python
_route_row_to_oracle(self, row: dict, lookup: dict) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `cell.get`, `lookup['cells_by_code'].get`, `row.get`, `slot.get`, `str`

### _validate_oracle_draft

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1912](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1912)

```python
_validate_oracle_draft(self, canvas_id: int, pick_route_id: int) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `json.loads`, `rows[0].get`, `self.gateway.fetch_all`, `str`

### _oracle_publish_status

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1926](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1926)

```python
_oracle_publish_status(self, canvas_id: int, topology_id: int, pick_route_id: int) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### _canvas_publish_idempotency_key

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1952](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1952)

```python
_canvas_publish_idempotency_key(self, canvas_id: int) -> str | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `rows[0].get`, `self.gateway.fetch_all`, `str`

### _set_canvas_publish_idempotency_key

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1966](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1966)

```python
_set_canvas_publish_idempotency_key(self, canvas_id: int, idempotency_key: str, published_by: str | None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.execute`

### _json_text

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1978](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1978)

```python
_json_text(self, value) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `json.dumps`

### _nextval

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1981](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1981)

```python
_nextval(self, sequence_name: str) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.call_number_plsql`

### _nextvals

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1984](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1984)

```python
_nextvals(self, sequence_name: str, count: int) -> list[int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `int`, `self.gateway.fetch_all`, `sequence_name.replace`, `sequence_name.replace('_', '').isalnum`

### _reset_base_snapshots

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:1995](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L1995)

```python
_reset_base_snapshots(self, draft: dict) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `draft.get`, `list`

### _read

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:2003](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L2003)

```python
_read(self, path: Path) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `json.loads`, `path.exists`, `path.read_text`

### _write

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:2008](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L2008)

```python
_write(self, draft: dict) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `json.dumps`, `self._path`, `self._path(draft['draft_id']).write_text`

### _decode_roles

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:2011](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L2011)

```python
_decode_roles(self, encoded: str, grid: WarehouseMapGrid) -> bytearray
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `any`, `base64.b64decode`, `bytearray`, `encoded.encode`, `len`, `self._cell_count`

### _encode_roles

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:2022](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L2022)

```python
_encode_roles(self, roles: bytearray) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `base64.b64encode`, `base64.b64encode(bytes(roles)).decode`, `bytes`

### _count_roles

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:2025](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L2025)

```python
_count_roles(self, roles: bytearray) -> dict[str, int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### _selection_size

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:2031](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L2031)

```python
_selection_size(self, selection: WarehouseMapSelectionRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### _cell_count

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:2034](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L2034)

```python
_cell_count(self, grid: WarehouseMapGrid) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### _cell_index

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:2037](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L2037)

```python
_cell_index(self, grid: WarehouseMapGrid, aisle: int, slot: int, level: int) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### _cell_from_index

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:2040](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L2040)

```python
_cell_from_index(self, grid: WarehouseMapGrid, index: int) -> tuple[int, int, int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### _ensure_revision

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:2048](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L2048)

```python
_ensure_revision(self, draft: dict, expected_revision: int | None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `draft.get`, `int`

### _stable_json

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:2062](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L2062)

```python
_stable_json(self, value) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `json.dumps`

### _json_changed

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:2065](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L2065)

```python
_json_changed(self, before, after) -> bool
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self._stable_json`

### _list_diff_count

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:2068](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L2068)

```python
_list_diff_count(self, before: list, after: list) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `before_items.symmetric_difference`, `len`, `self._stable_json`

### _ensure_cell_inside

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:2073](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L2073)

```python
_ensure_cell_inside(self, grid: WarehouseMapGrid, aisle: int, slot: int, level: int) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`

### _ordered_cells

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:2077](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L2077)

```python
_ordered_cells(self, selection: WarehouseMapSelectionRequest, anchor: dict, focus: dict) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `int`, `range`

### _route_ordered_cells

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:2086](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L2086)

```python
_route_ordered_cells(self, selection: WarehouseMapSelectionRequest, route_pattern: str) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `enumerate`, `list`, `range`, `reversed`, `rows.append`

### _normalize_route_rows

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:2105](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L2105)

```python
_normalize_route_rows(self, rows: list[dict]) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `all`, `float`, `int`, `normalized.append`, `row.get`, `self._physical_cell_code`, `str`, `uuid4`

### _validate_route_rows

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:2133](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L2133)

```python
_validate_route_rows(self, draft: dict, grid: WarehouseMapGrid, roles: bytearray) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cell.get`, `cells.count`, `draft.get`, `errors.append`, `float`, `int`, `item.get`, `len`, `row.get`, `self._cell_index`, `sequences.count`, `set`, `sorted`, `str`

### _address_inside

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:2172](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L2172)

```python
_address_inside(self, item: dict, selection: WarehouseMapSelectionRequest) -> bool
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `int`, `item.get`

### _format_pick_face_code

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:2179](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L2179)

```python
_format_pick_face_code(self, mask: str, aisle_no: int, pick_no: int, level: int, side: str | None) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `mask.format`, `str`, `str(aisle_no).zfill`, `str(pick_no).zfill`

### _small_pick_request_cells

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:2187](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L2187)

```python
_small_pick_request_cells(self, request: WarehouseMapSmallPickFaceGenerateRequest)
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `cells.append`, `list`, `unique.values`

### _small_pick_positions

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:2198](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L2198)

```python
_small_pick_positions(self, request: WarehouseMapSmallPickFaceGenerateRequest | WarehouseMapSmallPickFaceRenumberRequest) -> list[tuple[int, int]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `getattr`, `range`

### _physical_cell_code

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:2205](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L2205)

```python
_physical_cell_code(self, aisle: int, slot: int, level: int) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### _format_small_pick_code

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:2208](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L2208)

```python
_format_small_pick_code(self, mask: str, physical_code: str, cell, sub_level: int, sub_column: int, pick_order: int, side: str | None) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `mask.format`, `str`, `str(cell.aisle).zfill`, `str(cell.slot).zfill`

### _format_storage_slot_code

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:2229](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L2229)

```python
_format_storage_slot_code(self, mask: str, physical_code: str, cell, sub_column: int, storage_order: int) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `mask.format`, `str`, `str(cell.aisle).zfill`, `str(cell.slot).zfill`

### _is_same_physical_cell_ref

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:2239](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L2239)

```python
_is_same_physical_cell_ref(self, item: dict, cells) -> bool
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `any`, `self._is_same_physical_cell`

### _is_same_physical_cell

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:2242](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L2242)

```python
_is_same_physical_cell(self, item: dict, aisle: int, slot: int, level: int) -> bool
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cell.get`, `int`, `item.get`

### _small_pick_sort_key

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:2246](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L2246)

```python
_small_pick_sort_key(self, item: dict, order_mode: str) -> tuple[int, int, int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `int`, `item.get`

### _validate_small_pick_faces

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:2254](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L2254)

```python
_validate_small_pick_faces(self, draft: dict, grid: WarehouseMapGrid, roles: bytearray) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `codes.count`, `draft.get`, `errors.append`, `groups.setdefault`, `groups.setdefault(key, []).append`, `groups.values`, `int`, `item.get`, `iter`, `len`, `next`, `self._cell_index`, `self._ensure_cell_inside`, `set`, `sorted`, `str`

### _validate_storage_slots

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:2292](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L2292)

```python
_validate_storage_slots(self, draft: dict, grid: WarehouseMapGrid, roles: bytearray) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `codes.count`, `draft.get`, `errors.append`, `float`, `groups.setdefault`, `groups.setdefault(key, []).append`, `groups.values`, `int`, `item.get`, `iter`, `len`, `next`, `self._cell_index`, `self._ensure_cell_inside`, `set`, `sorted`, `str`

### _now

[Исходник: api/wms_api_server/app/services/warehouse_map_draft_service.py:2334](../../../api/wms_api_server/app/services/warehouse_map_draft_service.py#L2334)

```python
_now(self) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `datetime.now`, `datetime.now(timezone.utc).isoformat`

### _decode_json_rows

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:1130](../../../api/wms_api_server/app/services/warehouse_map_service.py#L1130)

```python
_decode_json_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_decode_json_row`

### _decode_json_row

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:1134](../../../api/wms_api_server/app/services/warehouse_map_service.py#L1134)

```python
_decode_json_row(row: dict[str, Any] | None) -> dict[str, Any] | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_json_value`, `dict`

### _json_value

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:1144](../../../api/wms_api_server/app/services/warehouse_map_service.py#L1144)

```python
_json_value(value: Any) -> Any
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `isinstance`, `json.loads`

### _group_by

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:1155](../../../api/wms_api_server/app/services/warehouse_map_service.py#L1155)

```python
_group_by(rows: list[dict[str, Any]], key: str) -> dict[Any, list[dict[str, Any]]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `grouped.setdefault`, `grouped.setdefault(row.get(key), []).append`, `row.get`

### _count_by

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:1162](../../../api/wms_api_server/app/services/warehouse_map_service.py#L1162)

```python
_count_by(rows: list[dict[str, Any]], key: str) -> dict[Any, int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `counts.get`, `row.get`

### _json_text

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:1169](../../../api/wms_api_server/app/services/warehouse_map_service.py#L1169)

```python
_json_text(value: Any) -> str | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `isinstance`, `json.dumps`

### _clean_code

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:1177](../../../api/wms_api_server/app/services/warehouse_map_service.py#L1177)

```python
_clean_code(value: str | None) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(value or '').strip`, `(value or '').strip().upper`

### __init__

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:30](../../../api/wms_api_server/app/services/warehouse_map_service.py#L30)

```python
__init__(self, gateway: OracleGateway | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`

### list_canvases

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:33](../../../api/wms_api_server/app/services/warehouse_map_service.py#L33)

```python
list_canvases(self, ware_id: int) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self._require_warehouse`, `self.gateway.fetch_all`

### get_warehouse_state

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:91](../../../api/wms_api_server/app/services/warehouse_map_service.py#L91)

```python
get_warehouse_state(self, ware_id: int, canvas_id: int | None=None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `self._require_warehouse`, `self._select_canvas`, `self._select_topology`, `self._state`

### get_canvas_state

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:99](../../../api/wms_api_server/app/services/warehouse_map_service.py#L99)

```python
get_canvas_state(self, canvas_id: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `int`, `self._canvas`, `self._require_warehouse`, `self._select_topology`, `self._state`

### create_canvas

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:107](../../../api/wms_api_server/app/services/warehouse_map_service.py#L107)

```python
create_canvas(self, ware_id: int, request: WarehouseMapCanvasCreateRequest, username: str | None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `_clean_code`, `_json_text`, `self._canvas_code_exists`, `self._nextval`, `self._require_topology_for_warehouse`, `self._require_warehouse`, `self.gateway.execute`, `self.get_canvas_state`

### archive_canvas

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:147](../../../api/wms_api_server/app/services/warehouse_map_service.py#L147)

```python
archive_canvas(self, canvas_id: int, request: WarehouseMapArchiveRequest, username: str | None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `canvas.get`, `cursor.execute`, `int`, `self._require_canvas`, `self.gateway.transaction`

### create_camera

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:247](../../../api/wms_api_server/app/services/warehouse_map_service.py#L247)

```python
create_camera(self, canvas_id: int, request: WarehouseMapCameraCreateRequest, username: str | None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `_clean_code`, `_decode_json_row`, `_json_text`, `request.camera_name.strip`, `self._camera_code_exists`, `self._nextval`, `self._require_camera`, `self._require_canvas`, `self.gateway.execute`, `self.get_canvas_state`

### clone_camera

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:296](../../../api/wms_api_server/app/services/warehouse_map_service.py#L296)

```python
clone_camera(self, camera_id: int, request: WarehouseMapCameraCloneRequest, username: str | None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `_clean_code`, `_decode_json_row`, `int`, `self._camera_code_exists`, `self._next_camera_copy_code`, `self._nextval`, `self._require_camera`, `self.gateway.execute`, `self.get_canvas_state`, `source.get`, `str`

### archive_camera

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:344](../../../api/wms_api_server/app/services/warehouse_map_service.py#L344)

```python
archive_camera(self, camera_id: int, request: WarehouseMapArchiveRequest, username: str | None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `dependencies.items`, `f"Archived from map UI. {request.reason or ''}".strip`, `int`, `self._camera_dependency_counts`, `self._require_camera`, `self.gateway.execute`, `self.get_canvas_state`

### replace_camera_objects

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:379](../../../api/wms_api_server/app/services/warehouse_map_service.py#L379)

```python
replace_camera_objects(self, camera_id: int, request: WarehouseMapObjectsPatchRequest, username: str | None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_clean_code`, `_json_text`, `enumerate`, `int`, `len`, `self._nextval`, `self._require_camera`, `self.gateway.execute_many`, `self.get_canvas_state`, `statements.append`

### replace_camera_passages

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:436](../../../api/wms_api_server/app/services/warehouse_map_service.py#L436)

```python
replace_camera_passages(self, camera_id: int, request: WarehouseMapPassagesPatchRequest, username: str | None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_clean_code`, `_json_text`, `enumerate`, `int`, `len`, `self._nextval`, `self._require_camera`, `self.gateway.execute_many`, `self.get_canvas_state`, `statements.append`

### replace_camera_links

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:492](../../../api/wms_api_server/app/services/warehouse_map_service.py#L492)

```python
replace_camera_links(self, canvas_id: int, request: WarehouseMapCameraLinksPatchRequest, username: str | None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `_clean_code`, `enumerate`, `int`, `len`, `self._nextval`, `self._require_camera`, `self._require_canvas`, `self.gateway.execute_many`, `self.get_canvas_state`, `statements.append`

### _state

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:552](../../../api/wms_api_server/app/services/warehouse_map_service.py#L552)

```python
_state(self, warehouse: dict[str, Any], canvas: dict[str, Any] | None, topology: dict[str, Any] | None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_count_by`, `_decode_json_row`, `_decode_json_rows`, `_group_by`, `canvas.get`, `excluded_by_route.get`, `int`, `len`, `route.get`, `route_rows_by_route.get`, `self._aisles`, `self._camera_links`, `self._cameras`, `self._canvas_objects`, `self._cell_slots`, `self._excluded_storage_route_rows`, `self._gates`, `self._passages`, `self._route_rows`, `self._routes`, `self._topology_cells`, `self._zones`, `slot.get`, `sum`, `warnings.append`

### _require_warehouse

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:624](../../../api/wms_api_server/app/services/warehouse_map_service.py#L624)

```python
_require_warehouse(self, ware_id: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `self.gateway.fetch_all`

### _require_topology_for_warehouse

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:650](../../../api/wms_api_server/app/services/warehouse_map_service.py#L650)

```python
_require_topology_for_warehouse(self, ware_id: int, topology_id: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `self.gateway.fetch_all`

### _require_canvas

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:665](../../../api/wms_api_server/app/services/warehouse_map_service.py#L665)

```python
_require_canvas(self, canvas_id: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `self._canvas`

### _require_camera

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:671](../../../api/wms_api_server/app/services/warehouse_map_service.py#L671)

```python
_require_camera(self, camera_id: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `self._camera`

### _select_canvas

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:677](../../../api/wms_api_server/app/services/warehouse_map_service.py#L677)

```python
_select_canvas(self, ware_id: int, canvas_id: int | None=None) -> dict[str, Any] | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `int`, `self._canvas`, `self.gateway.fetch_all`

### _camera

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:706](../../../api/wms_api_server/app/services/warehouse_map_service.py#L706)

```python
_camera(self, camera_id: int) -> dict[str, Any] | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### _canvas_code_exists

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:718](../../../api/wms_api_server/app/services/warehouse_map_service.py#L718)

```python
_canvas_code_exists(self, ware_id: int, canvas_code: str) -> bool
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `int`, `self.gateway.fetch_all`

### _camera_code_exists

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:731](../../../api/wms_api_server/app/services/warehouse_map_service.py#L731)

```python
_camera_code_exists(self, canvas_id: int, camera_code: str) -> bool
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `int`, `self.gateway.fetch_all`

### _next_camera_copy_code

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:744](../../../api/wms_api_server/app/services/warehouse_map_service.py#L744)

```python
_next_camera_copy_code(self, canvas_id: int, source_code: str) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `len`, `self._camera_code_exists`

### _camera_dependency_counts

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:755](../../../api/wms_api_server/app/services/warehouse_map_service.py#L755)

```python
_camera_dependency_counts(self, camera_id: int) -> dict[str, int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `int`, `self.gateway.fetch_all`, `str`

### _nextval

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:782](../../../api/wms_api_server/app/services/warehouse_map_service.py#L782)

```python
_nextval(self, sequence_name: str) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.call_number_plsql`

### _canvas

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:785](../../../api/wms_api_server/app/services/warehouse_map_service.py#L785)

```python
_canvas(self, canvas_id: int) -> dict[str, Any] | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### _select_topology

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:804](../../../api/wms_api_server/app/services/warehouse_map_service.py#L804)

```python
_select_topology(self, ware_id: int, canvas: dict[str, Any] | None) -> dict[str, Any] | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `canvas.get`, `self.gateway.fetch_all`

### _cameras

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:844](../../../api/wms_api_server/app/services/warehouse_map_service.py#L844)

```python
_cameras(self, canvas_id: int | None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### _camera_links

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:858](../../../api/wms_api_server/app/services/warehouse_map_service.py#L858)

```python
_camera_links(self, canvas_id: int | None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### _canvas_objects

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:872](../../../api/wms_api_server/app/services/warehouse_map_service.py#L872)

```python
_canvas_objects(self, canvas_id: int | None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### _passages

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:886](../../../api/wms_api_server/app/services/warehouse_map_service.py#L886)

```python
_passages(self, canvas_id: int | None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### _zones

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:900](../../../api/wms_api_server/app/services/warehouse_map_service.py#L900)

```python
_zones(self, topology_id: int | None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### _aisles

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:914](../../../api/wms_api_server/app/services/warehouse_map_service.py#L914)

```python
_aisles(self, topology_id: int | None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### _gates

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:928](../../../api/wms_api_server/app/services/warehouse_map_service.py#L928)

```python
_gates(self, topology_id: int | None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### _topology_cells

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:942](../../../api/wms_api_server/app/services/warehouse_map_service.py#L942)

```python
_topology_cells(self, topology_id: int | None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### _cell_slots

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:984](../../../api/wms_api_server/app/services/warehouse_map_service.py#L984)

```python
_cell_slots(self, topology_id: int | None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### _routes

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:1025](../../../api/wms_api_server/app/services/warehouse_map_service.py#L1025)

```python
_routes(self, topology_id: int | None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### _route_rows

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:1060](../../../api/wms_api_server/app/services/warehouse_map_service.py#L1060)

```python
_route_rows(self, topology_id: int | None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### _excluded_storage_route_rows

[Исходник: api/wms_api_server/app/services/warehouse_map_service.py:1104](../../../api/wms_api_server/app/services/warehouse_map_service.py#L1104)

```python
_excluded_storage_route_rows(self, topology_id: int | None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### _model_dict

[Исходник: api/wms_api_server/app/services/warehouse_service.py:81](../../../api/wms_api_server/app/services/warehouse_service.py#L81)

```python
_model_dict(model) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `hasattr`, `model.dict`, `model.model_dump`

### role_to_column

[Исходник: api/wms_api_server/app/services/warehouse_service.py:87](../../../api/wms_api_server/app/services/warehouse_service.py#L87)

```python
role_to_column(role: str) -> str | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `role.upper`, `{'RAW_MATERIAL': 'FLAG_RAW_MATERIAL', 'PRODUCTION': 'FLAG_PRODUCTION', 'PRODUCTION_BUFFER': 'FLAG_PRODUCTION_BUFFER', 'FINISHED_GOODS': 'FLAG_FINISHED_GOODS'}.get`

### __init__

[Исходник: api/wms_api_server/app/services/warehouse_service.py:8](../../../api/wms_api_server/app/services/warehouse_service.py#L8)

```python
__init__(self, gateway: OracleGateway | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`

### list_warehouses

[Исходник: api/wms_api_server/app/services/warehouse_service.py:11](../../../api/wms_api_server/app/services/warehouse_service.py#L11)

```python
list_warehouses(self, role: str | None=None, mes_enabled: int | None=None, limit: int=200) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `conditions.append`, `int`, `max`, `min`, `role_to_column`, `self.gateway.fetch_all`

### update_warehouse

[Исходник: api/wms_api_server/app/services/warehouse_service.py:63](../../../api/wms_api_server/app/services/warehouse_service.py#L63)

```python
update_warehouse(self, ware_id: int, request: WarehouseSettingsUpdateRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_model_dict`, `self.gateway.execute`

### __init__

[Исходник: api/wms_api_server/app/services/warehouse_task_domain_sync_service.py:17](../../../api/wms_api_server/app/services/warehouse_task_domain_sync_service.py#L17)

```python
__init__(self, gateway: OracleGateway | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`

### _explicit_sync

[Исходник: api/wms_api_server/app/services/warehouse_task_domain_sync_service.py:20](../../../api/wms_api_server/app/services/warehouse_task_domain_sync_service.py#L20)

```python
_explicit_sync(self, task_id: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `self.gateway.fetch_all`

### is_supported

[Исходник: api/wms_api_server/app/services/warehouse_task_domain_sync_service.py:68](../../../api/wms_api_server/app/services/warehouse_task_domain_sync_service.py#L68)

```python
is_supported(self, task: dict[str, Any]) -> bool
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self._target_key`

### dispatch_after_complete

[Исходник: api/wms_api_server/app/services/warehouse_task_domain_sync_service.py:71](../../../api/wms_api_server/app/services/warehouse_task_domain_sync_service.py#L71)

```python
dispatch_after_complete(self, task_id: int, updated_by: str | None=None) -> dict[str, Any] | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self._explicit_sync`, `self._get_task`, `self.is_supported`

### retry_task_sync

[Исходник: api/wms_api_server/app/services/warehouse_task_domain_sync_service.py:77](../../../api/wms_api_server/app/services/warehouse_task_domain_sync_service.py#L77)

```python
retry_task_sync(self, task_id: int, updated_by: str | None=None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self._explicit_sync`

### get_task_sync

[Исходник: api/wms_api_server/app/services/warehouse_task_domain_sync_service.py:80](../../../api/wms_api_server/app/services/warehouse_task_domain_sync_service.py#L80)

```python
get_task_sync(self, task_id: int) -> dict[str, Any] | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### list_sync

[Исходник: api/wms_api_server/app/services/warehouse_task_domain_sync_service.py:92](../../../api/wms_api_server/app/services/warehouse_task_domain_sync_service.py#L92)

```python
list_sync(self, status: str | None=None, task_source: str | None=None, source_doc_type: str | None=None, source_doc_id: int | None=None, limit: int=100, scope_warehouse_id: int | None=None, scope_global: bool=True) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `clamp_limit`, `conditions.append`, `self.gateway.fetch_all`, `source_doc_type.upper`, `status.upper`, `task_source.upper`

### _get_task

[Исходник: api/wms_api_server/app/services/warehouse_task_domain_sync_service.py:145](../../../api/wms_api_server/app/services/warehouse_task_domain_sync_service.py#L145)

```python
_get_task(self, task_id: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `self.gateway.fetch_all`

### _target_key

[Исходник: api/wms_api_server/app/services/warehouse_task_domain_sync_service.py:158](../../../api/wms_api_server/app/services/warehouse_task_domain_sync_service.py#L158)

```python
_target_key(self, task: dict[str, Any]) -> tuple[str | None, str | None, str | None]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `str`, `str(task.get('source_doc_type') or '').upper`, `str(task.get('task_source') or '').upper`, `str(task.get('task_type') or '').upper`, `task.get`

### _normalize

[Исходник: api/wms_api_server/app/services/warehouse_task_domain_sync_service.py:165](../../../api/wms_api_server/app/services/warehouse_task_domain_sync_service.py#L165)

```python
_normalize(self, value: Any) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `str`, `str(value or '').strip`, `str(value or '').strip().upper`

### __init__

[Исходник: api/wms_api_server/app/services/warehouse_task_service.py:12](../../../api/wms_api_server/app/services/warehouse_task_service.py#L12)

```python
__init__(self, gateway: OracleGateway | TransactionGateway | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`

### list_tasks

[Исходник: api/wms_api_server/app/services/warehouse_task_service.py:15](../../../api/wms_api_server/app/services/warehouse_task_service.py#L15)

```python
list_tasks(self, status: str | None=None, task_type: str | None=None, task_source: str | None=None, assigned_to: str | None=None, production_order_id: int | None=None, source_doc_type: str | None=None, source_doc_id: int | None=None, limit: int=100, scope_warehouse_id: int | None=None, scope_global: bool=True, queue_group: str | None=None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `build_task_queue_read`, `build_task_queue_read(self.gateway).list`

### get_task_or_404

[Исходник: api/wms_api_server/app/services/warehouse_task_service.py:36](../../../api/wms_api_server/app/services/warehouse_task_service.py#L36)

```python
get_task_or_404(self, task_id: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `build_task_queue_read`, `build_task_queue_read(self.gateway).get`

### assign_task

[Исходник: api/wms_api_server/app/services/warehouse_task_service.py:43](../../../api/wms_api_server/app/services/warehouse_task_service.py#L43)

```python
assign_task(self, task_id: int, request: WarehouseTaskStatusRequest) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `all`, `getattr`, `resource_ctx.items`, `run_existing_warehouse_task_action`, `self._resource_context`, `self._resource_event_statement`, `self._sync_wave_picking_move_status`, `self._sync_wave_replenishment_status`, `self.gateway.execute_many`, `self.get_task_or_404`, `task.get`, `type`

### start_task

[Исходник: api/wms_api_server/app/services/warehouse_task_service.py:84](../../../api/wms_api_server/app/services/warehouse_task_service.py#L84)

```python
start_task(self, task_id: int, request: WarehouseTaskStatusRequest) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `getattr`, `run_existing_warehouse_task_action`, `self._resource_context`, `self._resource_event_statement`, `self._sync_wave_picking_move_status`, `self._sync_wave_replenishment_status`, `self.gateway.execute`, `self.gateway.execute_many`, `self.get_task_or_404`, `task.get`, `type`

### complete_task

[Исходник: api/wms_api_server/app/services/warehouse_task_service.py:129](../../../api/wms_api_server/app/services/warehouse_task_service.py#L129)

```python
complete_task(self, task_id: int, request: WarehouseTaskStatusRequest, actor: str | None=None) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `complete_existing_warehouse_task`

### cancel_task

[Исходник: api/wms_api_server/app/services/warehouse_task_service.py:133](../../../api/wms_api_server/app/services/warehouse_task_service.py#L133)

```python
cancel_task(self, task_id: int, request: WarehouseTaskStatusRequest) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `build_receiving_service`, `build_receiving_service().cancel`, `getattr`, `release_cancelled_warehouse_task_resource`, `run_existing_warehouse_task_action`, `self._sync_wave_picking_move_status`, `self._sync_wave_replenishment_status`, `self.gateway.execute`, `self.get_task_or_404`, `str`, `task.get`, `type`

### _resource_context

[Исходник: api/wms_api_server/app/services/warehouse_task_service.py:180](../../../api/wms_api_server/app/services/warehouse_task_service.py#L180)

```python
_resource_context(self, request: WarehouseTaskStatusRequest, task: dict[str, Any], action: str, assignee: str | None=None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `existing_task_resource_context`

### _resource_event_statement

[Исходник: api/wms_api_server/app/services/warehouse_task_service.py:186](../../../api/wms_api_server/app/services/warehouse_task_service.py#L186)

```python
_resource_event_statement(self, task_id: int, event_type: str, event_by: str | None, resource_ctx: dict[str, Any], payload_json: str | None=None) -> tuple[str, dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### _sync_wave_replenishment_status

[Исходник: api/wms_api_server/app/services/warehouse_task_service.py:217](../../../api/wms_api_server/app/services/warehouse_task_service.py#L217)

```python
_sync_wave_replenishment_status(self, task: dict[str, Any], status: str, updated_by: str | None, fact_qty: float | None=None, error_text: str | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.execute`, `task.get`

### _sync_wave_picking_move_status

[Исходник: api/wms_api_server/app/services/warehouse_task_service.py:246](../../../api/wms_api_server/app/services/warehouse_task_service.py#L246)

```python
_sync_wave_picking_move_status(self, task: dict[str, Any], status: str, updated_by: str | None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.execute`, `task.get`

### _json_text

[Исходник: api/wms_api_server/app/services/warehouse_topology_service.py:1267](../../../api/wms_api_server/app/services/warehouse_topology_service.py#L1267)

```python
_json_text(value: Any) -> str | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `json.dumps`

### __init__

[Исходник: api/wms_api_server/app/services/warehouse_topology_service.py:17](../../../api/wms_api_server/app/services/warehouse_topology_service.py#L17)

```python
__init__(self, gateway: OracleGateway | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`

### list_topologies

[Исходник: api/wms_api_server/app/services/warehouse_topology_service.py:20](../../../api/wms_api_server/app/services/warehouse_topology_service.py#L20)

```python
list_topologies(self, ware_id: int | None=None, status: str | None=None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `conditions.append`, `self.gateway.fetch_all`, `status.upper`

### create_topology

[Исходник: api/wms_api_server/app/services/warehouse_topology_service.py:54](../../../api/wms_api_server/app/services/warehouse_topology_service.py#L54)

```python
create_topology(self, request: WarehouseTopologyCreateRequest) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `request.model_dump`, `self._log_change`, `self._nextval`, `self.gateway.execute`

### get_topology_map

[Исходник: api/wms_api_server/app/services/warehouse_topology_service.py:71](../../../api/wms_api_server/app/services/warehouse_topology_service.py#L71)

```python
get_topology_map(self, topology_id: int) -> dict[str, Any] | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `active_route.get`, `next`, `route.get`, `self.gateway.fetch_all`, `self.list_pick_routes`

### generate_cells

[Исходник: api/wms_api_server/app/services/warehouse_topology_service.py:181](../../../api/wms_api_server/app/services/warehouse_topology_service.py#L181)

```python
generate_cells(self, topology_id: int, request: WarehouseTopologyGenerateRequest) -> dict[str, int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `int`, `range`, `request.model_dump`, `self._aisle_exists`, `self._cell_exists`, `self._ensure_zone`, `self._log_change`, `self._topology`, `self.gateway.execute`, `self.gateway.execute_many`, `side.upper`, `statements.append`, `topology.get`

### generate_gates

[Исходник: api/wms_api_server/app/services/warehouse_topology_service.py:287](../../../api/wms_api_server/app/services/warehouse_topology_service.py#L287)

```python
generate_gates(self, topology_id: int, request: TopologyGateGenerateRequest) -> dict[str, int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `range`, `request.model_dump`, `self._log_change`, `self._topology`, `self.gateway.execute`, `self.gateway.execute_many`, `self.gateway.fetch_all`, `statements.append`, `topology.get`

### recalculate_gate_distances

[Исходник: api/wms_api_server/app/services/warehouse_topology_service.py:348](../../../api/wms_api_server/app/services/warehouse_topology_service.py#L348)

```python
recalculate_gate_distances(self, topology_id: int, request: TopologyDistanceRecalculateRequest) -> dict[str, int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `cell.get`, `len`, `request.flow_kind.upper`, `request.model_dump`, `round`, `self._gate_distance`, `self._log_change`, `self._topology`, `self.gateway.execute`, `self.gateway.execute_many`, `self.gateway.fetch_all`, `statements.append`

### patch_cell

[Исходник: api/wms_api_server/app/services/warehouse_topology_service.py:444](../../../api/wms_api_server/app/services/warehouse_topology_service.py#L444)

```python
patch_cell(self, topology_cell_id: int, request: TopologyCellPatchRequest) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `', '.join`, `HTTPException`, `field.endswith`, `getattr`, `isinstance`, `request.model_dump`, `self._log_change`, `self.gateway.execute`, `self.gateway.fetch_all`, `updates.append`, `value.upper`

### validate_topology

[Исходник: api/wms_api_server/app/services/warehouse_topology_service.py:478](../../../api/wms_api_server/app/services/warehouse_topology_service.py#L478)

```python
validate_topology(self, topology_id: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `checks.values`, `len`, `self.gateway.execute`, `self.gateway.fetch_all`, `sum`

### normalize_pick_face_cell_codes

[Исходник: api/wms_api_server/app/services/warehouse_topology_service.py:653](../../../api/wms_api_server/app/services/warehouse_topology_service.py#L653)

```python
normalize_pick_face_cell_codes(self, topology_id: int, user: str | None) -> dict[str, int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `candidates[0].get`, `int`, `remaining[0].get`, `self._log_change`, `self._topology`, `self.gateway.execute`, `self.gateway.fetch_all`

### publish_topology

[Исходник: api/wms_api_server/app/services/warehouse_topology_service.py:793](../../../api/wms_api_server/app/services/warehouse_topology_service.py#L793)

```python
publish_topology(self, topology_id: int, user: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `self._log_change`, `self._topology`, `self.gateway.execute`, `self.validate_topology`

### list_pick_routes

[Исходник: api/wms_api_server/app/services/warehouse_topology_service.py:826](../../../api/wms_api_server/app/services/warehouse_topology_service.py#L826)

```python
list_pick_routes(self, topology_id: int | None=None, ware_id: int | None=None, status: str | None=None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `conditions.append`, `self.gateway.fetch_all`, `status.upper`

### build_pick_route

[Исходник: api/wms_api_server/app/services/warehouse_topology_service.py:866](../../../api/wms_api_server/app/services/warehouse_topology_service.py#L866)

```python
build_pick_route(self, request: PickRouteBuildRequest) -> dict[str, int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `cell.get`, `enumerate`, `len`, `prev.get`, `request.model_dump`, `self._archive_other_pick_routes`, `self._assert_linear_route_invariants`, `self._distance`, `self._log_change`, `self._nextval`, `self._order_route_cells`, `self._route_source_cells`, `self._topology`, `self.gateway.execute`, `self.gateway.execute_many`, `self.gateway.fetch_all`, `self.normalize_pick_face_cell_codes`, `statements.append`

### publish_pick_route

[Исходник: api/wms_api_server/app/services/warehouse_topology_service.py:1002](../../../api/wms_api_server/app/services/warehouse_topology_service.py#L1002)

```python
publish_pick_route(self, pick_route_id: int, user: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `int`, `route.get`, `self._log_change`, `self.gateway.execute`, `self.gateway.fetch_all`

### _route_source_cells

[Исходник: api/wms_api_server/app/services/warehouse_topology_service.py:1050](../../../api/wms_api_server/app/services/warehouse_topology_service.py#L1050)

```python
_route_source_cells(self, request: PickRouteBuildRequest) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `', '.join`, `conditions.append`, `enumerate`, `placeholders.append`, `self.gateway.fetch_all`

### _order_route_cells

[Исходник: api/wms_api_server/app/services/warehouse_topology_service.py:1084](../../../api/wms_api_server/app/services/warehouse_topology_service.py#L1084)

```python
_order_route_cells(self, cells: list[dict[str, Any]], request: PickRouteBuildRequest) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(request.route_pattern or 'Z').upper`, `aisle_cells.sort`, `aisle_order.get`, `cell.get`, `enumerate`, `float`, `groups.items`, `groups.setdefault`, `groups.setdefault(str(cell.get('aisle_code') or ''), []).append`, `ordered.extend`, `row.get`, `side.upper`, `side_rank.get`, `sorted`, `str`, `str(row.get('side_code') or '').upper`

### _ensure_zone

[Исходник: api/wms_api_server/app/services/warehouse_topology_service.py:1121](../../../api/wms_api_server/app/services/warehouse_topology_service.py#L1121)

```python
_ensure_zone(self, topology_id: int, request: WarehouseTopologyGenerateRequest) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.execute`, `self.gateway.fetch_all`

### _topology

[Исходник: api/wms_api_server/app/services/warehouse_topology_service.py:1150](../../../api/wms_api_server/app/services/warehouse_topology_service.py#L1150)

```python
_topology(self, topology_id: int) -> dict[str, Any] | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### _archive_other_pick_routes

[Исходник: api/wms_api_server/app/services/warehouse_topology_service.py:1157](../../../api/wms_api_server/app/services/warehouse_topology_service.py#L1157)

```python
_archive_other_pick_routes(self, topology_id: int, keep_route_id: int, user: str | None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.execute`

### _assert_linear_route_invariants

[Исходник: api/wms_api_server/app/services/warehouse_topology_service.py:1173](../../../api/wms_api_server/app/services/warehouse_topology_service.py#L1173)

```python
_assert_linear_route_invariants(self, pick_route_id: int) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `int`, `row.get`, `self.gateway.fetch_all`

### _aisle_exists

[Исходник: api/wms_api_server/app/services/warehouse_topology_service.py:1203](../../../api/wms_api_server/app/services/warehouse_topology_service.py#L1203)

```python
_aisle_exists(self, topology_id: int, aisle_code: str) -> bool
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `bool`, `self.gateway.fetch_all`

### _cell_exists

[Исходник: api/wms_api_server/app/services/warehouse_topology_service.py:1209](../../../api/wms_api_server/app/services/warehouse_topology_service.py#L1209)

```python
_cell_exists(self, topology_id: int, cell_code: str) -> bool
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `bool`, `self.gateway.fetch_all`

### _nextval

[Исходник: api/wms_api_server/app/services/warehouse_topology_service.py:1215](../../../api/wms_api_server/app/services/warehouse_topology_service.py#L1215)

```python
_nextval(self, sequence_name: str) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.call_number_plsql`

### _log_change

[Исходник: api/wms_api_server/app/services/warehouse_topology_service.py:1218](../../../api/wms_api_server/app/services/warehouse_topology_service.py#L1218)

```python
_log_change(self, topology_id: int | None, entity_kind: str, entity_id: int | None, change_kind: str, old_value: Any, new_value: Any, user: str | None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_json_text`, `self.gateway.execute`

### _distance

[Исходник: api/wms_api_server/app/services/warehouse_topology_service.py:1252](../../../api/wms_api_server/app/services/warehouse_topology_service.py#L1252)

```python
_distance(prev: dict[str, Any] | None, cell: dict[str, Any]) -> float
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cell.get`, `float`, `prev.get`, `round`

### _gate_distance

[Исходник: api/wms_api_server/app/services/warehouse_topology_service.py:1260](../../../api/wms_api_server/app/services/warehouse_topology_service.py#L1260)

```python
_gate_distance(cell: dict[str, Any], gate: dict[str, Any]) -> float
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `abs`, `cell.get`, `float`, `gate.get`, `round`

### route_sort_key

[Исходник: api/wms_api_server/app/services/warehouse_topology_service.py:1102](../../../api/wms_api_server/app/services/warehouse_topology_service.py#L1102)

```python
route_sort_key(row: dict[str, Any]) -> tuple[float, float, float, float]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `float`, `row.get`, `side_rank.get`, `str`, `str(row.get('side_code') or '').upper`

### __init__

[Исходник: api/wms_api_server/app/services/ws_manager.py:24](../../../api/wms_api_server/app/services/ws_manager.py#L24)

```python
__init__(self) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### connect

[Исходник: api/wms_api_server/app/services/ws_manager.py:28](../../../api/wms_api_server/app/services/ws_manager.py#L28)

```python
connect(self, websocket: WebSocket) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `asyncio.get_running_loop`, `len`, `log.debug`, `self._connections.append`, `websocket.accept`

### disconnect

[Исходник: api/wms_api_server/app/services/ws_manager.py:38](../../../api/wms_api_server/app/services/ws_manager.py#L38)

```python
disconnect(self, websocket: WebSocket) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `len`, `log.debug`, `self._connections.remove`

### broadcast

[Исходник: api/wms_api_server/app/services/ws_manager.py:45](../../../api/wms_api_server/app/services/ws_manager.py#L45)

```python
broadcast(self, message: dict[str, Any]) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `dead.append`, `json.dumps`, `list`, `self.disconnect`, `ws.send_text`

### broadcast_sync

[Исходник: api/wms_api_server/app/services/ws_manager.py:58](../../../api/wms_api_server/app/services/ws_manager.py#L58)

```python
broadcast_sync(self, message: dict[str, Any]) -> None
```

Вызвать из синхронного endpoint после успешной мутации.

Вызывает: `asyncio.run_coroutine_threadsafe`, `loop.is_running`, `self.broadcast`

### connection_count

[Исходник: api/wms_api_server/app/services/ws_manager.py:68](../../../api/wms_api_server/app/services/ws_manager.py#L68)

```python
connection_count(self) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `len`
