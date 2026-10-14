# Методы: resources

### resource_view

[Исходник: api/wms_api_server/app/modules/resources/api/qualification_routes.py:16](../../../api/wms_api_server/app/modules/resources/api/qualification_routes.py#L16)

```python
resource_view() -> ResourceUser
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### qualification_edit

[Исходник: api/wms_api_server/app/modules/resources/api/qualification_routes.py:19](../../../api/wms_api_server/app/modules/resources/api/qualification_routes.py#L19)

```python
qualification_edit() -> ResourceUser
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### resource_position_user

[Исходник: api/wms_api_server/app/modules/resources/api/qualification_routes.py:22](../../../api/wms_api_server/app/modules/resources/api/qualification_routes.py#L22)

```python
resource_position_user() -> ResourceUser
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### resource_dispatch_user

[Исходник: api/wms_api_server/app/modules/resources/api/qualification_routes.py:25](../../../api/wms_api_server/app/modules/resources/api/qualification_routes.py#L25)

```python
resource_dispatch_user() -> ResourceUser
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### qualification_service

[Исходник: api/wms_api_server/app/modules/resources/api/qualification_routes.py:28](../../../api/wms_api_server/app/modules/resources/api/qualification_routes.py#L28)

```python
qualification_service() -> QualificationPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### list_qualifications

[Исходник: api/wms_api_server/app/modules/resources/api/qualification_routes.py:41](../../../api/wms_api_server/app/modules/resources/api/qualification_routes.py#L41)

```python
list_qualifications(resource_id: int, user: ResourceUser=Depends(resource_view), service: QualificationPort=Depends(qualification_service)) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `router.get`, `service.qualifications`

### save_qualification

[Исходник: api/wms_api_server/app/modules/resources/api/qualification_routes.py:46](../../../api/wms_api_server/app/modules/resources/api/qualification_routes.py#L46)

```python
save_qualification(resource_id: int, request: QualificationInput, user: ResourceUser=Depends(qualification_edit), service: QualificationPort=Depends(qualification_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `router.put`, `service.set_qualification`

### confirm_position

[Исходник: api/wms_api_server/app/modules/resources/api/qualification_routes.py:52](../../../api/wms_api_server/app/modules/resources/api/qualification_routes.py#L52)

```python
confirm_position(session_id: int, request: PositionInput, user: ResourceUser=Depends(resource_position_user), service: QualificationPort=Depends(qualification_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `router.post`, `service.position`

### nearest_candidates

[Исходник: api/wms_api_server/app/modules/resources/api/qualification_routes.py:58](../../../api/wms_api_server/app/modules/resources/api/qualification_routes.py#L58)

```python
nearest_candidates(task_id: int, limit: int=Query(default=10, ge=1, le=20), user: ResourceUser=Depends(resource_view), service: QualificationPort=Depends(qualification_service)) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Query`, `router.get`, `service.warehouse`

### dispatch_nearest

[Исходник: api/wms_api_server/app/modules/resources/api/qualification_routes.py:64](../../../api/wms_api_server/app/modules/resources/api/qualification_routes.py#L64)

```python
dispatch_nearest(task_id: int, user: ResourceUser=Depends(resource_dispatch_user), service: QualificationPort=Depends(qualification_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `router.post`, `service.dispatch`

### qualifications

[Исходник: api/wms_api_server/app/modules/resources/api/qualification_routes.py:10](../../../api/wms_api_server/app/modules/resources/api/qualification_routes.py#L10)

```python
qualifications(self, resource_id: int) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### set_qualification

[Исходник: api/wms_api_server/app/modules/resources/api/qualification_routes.py:11](../../../api/wms_api_server/app/modules/resources/api/qualification_routes.py#L11)

```python
set_qualification(self, resource_id: int, task_type: str, active: bool, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### position

[Исходник: api/wms_api_server/app/modules/resources/api/qualification_routes.py:12](../../../api/wms_api_server/app/modules/resources/api/qualification_routes.py#L12)

```python
position(self, session_id: int, cell: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### warehouse

[Исходник: api/wms_api_server/app/modules/resources/api/qualification_routes.py:13](../../../api/wms_api_server/app/modules/resources/api/qualification_routes.py#L13)

```python
warehouse(self, task_id: int, limit: int) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### dispatch

[Исходник: api/wms_api_server/app/modules/resources/api/qualification_routes.py:14](../../../api/wms_api_server/app/modules/resources/api/qualification_routes.py#L14)

```python
dispatch(self, task_id: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### reach_shift_view

[Исходник: api/wms_api_server/app/modules/resources/api/reach_shift_routes.py:18](../../../api/wms_api_server/app/modules/resources/api/reach_shift_routes.py#L18)

```python
reach_shift_view() -> ShiftUser
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### reach_shift_edit

[Исходник: api/wms_api_server/app/modules/resources/api/reach_shift_routes.py:21](../../../api/wms_api_server/app/modules/resources/api/reach_shift_routes.py#L21)

```python
reach_shift_edit() -> ShiftUser
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### reach_shift_service

[Исходник: api/wms_api_server/app/modules/resources/api/reach_shift_routes.py:24](../../../api/wms_api_server/app/modules/resources/api/reach_shift_routes.py#L24)

```python
reach_shift_service() -> ReachShiftPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### read

[Исходник: api/wms_api_server/app/modules/resources/api/reach_shift_routes.py:30](../../../api/wms_api_server/app/modules/resources/api/reach_shift_routes.py#L30)

```python
read(base_shift_id: int=Path(gt=0), user: ShiftUser=Depends(reach_shift_view), service: ReachShiftPort=Depends(reach_shift_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Path`, `router.get`, `service.read`

### create

[Исходник: api/wms_api_server/app/modules/resources/api/reach_shift_routes.py:35](../../../api/wms_api_server/app/modules/resources/api/reach_shift_routes.py#L35)

```python
create(request: ReachShiftInput, base_shift_id: int=Path(gt=0), user: ShiftUser=Depends(reach_shift_edit), service: ReachShiftPort=Depends(reach_shift_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Path`, `router.post`, `service.create`

### read

[Исходник: api/wms_api_server/app/modules/resources/api/reach_shift_routes.py:15](../../../api/wms_api_server/app/modules/resources/api/reach_shift_routes.py#L15)

```python
read(self, base_shift_id: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### create

[Исходник: api/wms_api_server/app/modules/resources/api/reach_shift_routes.py:16](../../../api/wms_api_server/app/modules/resources/api/reach_shift_routes.py#L16)

```python
create(self, base_shift_id: int, main_drivers: int, duty_drivers: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### context

[Исходник: api/wms_api_server/app/modules/resources/api/wave_time_routes.py:28](../../../api/wms_api_server/app/modules/resources/api/wave_time_routes.py#L28)

```python
context(wave_id: int=Path(gt=0), user: AdminUser=Depends(require_permission('pick_wave_view')), service: WaveTimePort=Depends(wave_time_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Path`, `require_permission`, `router.get`, `service.context`, `str`

### approve

[Исходник: api/wms_api_server/app/modules/resources/api/wave_time_routes.py:33](../../../api/wms_api_server/app/modules/resources/api/wave_time_routes.py#L33)

```python
approve(request: WaveTimeApproval, user: AdminUser=Depends(require_permission('pick_wave_launch')), service: WaveTimePort=Depends(wave_time_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `getattr`, `getattr(request, key).astimezone`, `getattr(request, key).astimezone(timezone.utc).isoformat`, `request.model_dump`, `require_permission`, `router.post`, `service.approve`, `str`

### bounded_period

[Исходник: api/wms_api_server/app/modules/resources/api/wave_time_routes.py:20](../../../api/wms_api_server/app/modules/resources/api/wave_time_routes.py#L20)

```python
bounded_period(self) -> 'WaveTimeApproval'
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(self.finish_at - self.start_at).total_seconds`, `ValueError`, `model_validator`

### invoke

[Исходник: api/wms_api_server/app/modules/resources/api/workload_config_routes.py:42](../../../api/wms_api_server/app/modules/resources/api/workload_config_routes.py#L42)

```python
invoke(request: CommandInput, action: str, user: AdminUser, service: WorkloadConfigPort) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `body.items`, `isinstance`, `list`, `request.model_dump`, `service.command`, `str`, `value.astimezone`, `value.astimezone(timezone.utc).isoformat`

### save_norm

[Исходник: api/wms_api_server/app/modules/resources/api/workload_config_routes.py:51](../../../api/wms_api_server/app/modules/resources/api/workload_config_routes.py#L51)

```python
save_norm(request: NormInput, user: AdminUser=Depends(require_permission('resource_shift_edit')), service: WorkloadConfigPort=Depends(workload_config_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `invoke`, `require_permission`, `router.post`

### plan_attendance

[Исходник: api/wms_api_server/app/modules/resources/api/workload_config_routes.py:55](../../../api/wms_api_server/app/modules/resources/api/workload_config_routes.py#L55)

```python
plan_attendance(request: AttendanceInput, user: AdminUser=Depends(require_permission('resource_shift_edit')), service: WorkloadConfigPort=Depends(workload_config_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `invoke`, `require_permission`, `router.post`

### replace_attendance

[Исходник: api/wms_api_server/app/modules/resources/api/workload_config_routes.py:59](../../../api/wms_api_server/app/modules/resources/api/workload_config_routes.py#L59)

```python
replace_attendance(request: ReplaceAttendanceInput, user: AdminUser=Depends(require_permission('resource_shift_edit')), service: WorkloadConfigPort=Depends(workload_config_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `invoke`, `require_permission`, `router.post`

### cancel_attendance

[Исходник: api/wms_api_server/app/modules/resources/api/workload_config_routes.py:63](../../../api/wms_api_server/app/modules/resources/api/workload_config_routes.py#L63)

```python
cancel_attendance(request: CancelInput, user: AdminUser=Depends(require_permission('resource_shift_edit')), service: WorkloadConfigPort=Depends(workload_config_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `invoke`, `require_permission`, `router.post`

### read_configuration

[Исходник: api/wms_api_server/app/modules/resources/api/workload_config_routes.py:67](../../../api/wms_api_server/app/modules/resources/api/workload_config_routes.py#L67)

```python
read_configuration(ware_id: int=Path(gt=0), site_code: str | None=Query(None, min_length=1, max_length=50), start_at: AwareDatetime | None=None, finish_at: AwareDatetime | None=None, user: AdminUser=Depends(require_permission('resource_shift_view')), service: WorkloadConfigPort=Depends(workload_config_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(finish_at - start_at).total_seconds`, `Depends`, `HTTPException`, `Path`, `Query`, `require_permission`, `router.get`, `service.configuration`, `str`

### save_forecast_scope

[Исходник: api/wms_api_server/app/modules/resources/api/workload_config_routes.py:86](../../../api/wms_api_server/app/modules/resources/api/workload_config_routes.py#L86)

```python
save_forecast_scope(request: ForecastScopeInput, user: AdminUser=Depends(require_permission('resource_shift_edit')), service: WorkloadConfigPort=Depends(workload_config_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `invoke`, `require_permission`, `router.post`

### valid_interval

[Исходник: api/wms_api_server/app/modules/resources/api/workload_config_routes.py:30](../../../api/wms_api_server/app/modules/resources/api/workload_config_routes.py#L30)

```python
valid_interval(self) -> 'AttendanceInput'
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(self.finish_at - self.start_at).total_seconds`, `ValueError`, `model_validator`

### history

[Исходник: api/wms_api_server/app/modules/resources/api/workload_history_routes.py:9](../../../api/wms_api_server/app/modules/resources/api/workload_history_routes.py#L9)

```python
history(ware_id: int=Path(gt=0), plan_id: str=Path(min_length=1, max_length=100), limit: int=Query(25, ge=1, le=50), user: AdminUser=Depends(require_permission('resource_shift_view')), service: WorkloadHistoryPort=Depends(workload_history_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Path`, `Query`, `require_permission`, `router.get`, `service.read`, `str`

### workload_monitor_service

[Исходник: api/wms_api_server/app/modules/resources/api/workload_monitor_routes.py:11](../../../api/wms_api_server/app/modules/resources/api/workload_monitor_routes.py#L11)

```python
workload_monitor_service() -> WorkloadMonitorPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### preview

[Исходник: api/wms_api_server/app/modules/resources/api/workload_monitor_routes.py:35](../../../api/wms_api_server/app/modules/resources/api/workload_monitor_routes.py#L35)

```python
preview(request: MonitorInput, ware_id: int=Path(gt=0), user: AdminUser=Depends(require_permission('resource_shift_view')), service: WorkloadMonitorPort=Depends(workload_monitor_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Path`, `request.finish_at.astimezone`, `request.start_at.astimezone`, `require_permission`, `router.post`, `row.finish_at.astimezone`, `row.start_at.astimezone`, `service.preview`, `str`

### preview

[Исходник: api/wms_api_server/app/modules/resources/api/workload_monitor_routes.py:9](../../../api/wms_api_server/app/modules/resources/api/workload_monitor_routes.py#L9)

```python
preview(self, ware: int, site: str, start: datetime, end: datetime, minutes: int, windows: list[dict[str, Any]], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### bounded_interval

[Исходник: api/wms_api_server/app/modules/resources/api/workload_monitor_routes.py:19](../../../api/wms_api_server/app/modules/resources/api/workload_monitor_routes.py#L19)

```python
bounded_interval(self) -> 'WindowInput'
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(self.finish_at - self.start_at).total_seconds`, `ValueError`, `model_validator`

### case_read_service

[Исходник: api/wms_api_server/app/modules/resources/contracts_case_read.py:16](../../../api/wms_api_server/app/modules/resources/contracts_case_read.py#L16)

```python
case_read_service() -> CaseReadPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### __init__

[Исходник: api/wms_api_server/app/modules/resources/contracts_case_read.py:5](../../../api/wms_api_server/app/modules/resources/contracts_case_read.py#L5)

```python
__init__(self, code: str, message: str, status: int=403) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `super`, `super().__init__`

### tasks

[Исходник: api/wms_api_server/app/modules/resources/contracts_case_read.py:11](../../../api/wms_api_server/app/modules/resources/contracts_case_read.py#L11)

```python
tasks(self, actor: str, resource: int | None, scope: str, status: str | None, limit: int) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### task

[Исходник: api/wms_api_server/app/modules/resources/contracts_case_read.py:12](../../../api/wms_api_server/app/modules/resources/contracts_case_read.py#L12)

```python
task(self, task: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### shorts

[Исходник: api/wms_api_server/app/modules/resources/contracts_case_read.py:13](../../../api/wms_api_server/app/modules/resources/contracts_case_read.py#L13)

```python
shorts(self, actor: str, status: str | None, limit: int) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### wave_time_service

[Исходник: api/wms_api_server/app/modules/resources/contracts_wave_time.py:7](../../../api/wms_api_server/app/modules/resources/contracts_wave_time.py#L7)

```python
wave_time_service() -> WaveTimePort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### context

[Исходник: api/wms_api_server/app/modules/resources/contracts_wave_time.py:4](../../../api/wms_api_server/app/modules/resources/contracts_wave_time.py#L4)

```python
context(self, wave: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### approve

[Исходник: api/wms_api_server/app/modules/resources/contracts_wave_time.py:5](../../../api/wms_api_server/app/modules/resources/contracts_wave_time.py#L5)

```python
approve(self, operation: str, body: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### workload_config_service

[Исходник: api/wms_api_server/app/modules/resources/contracts_workload.py:12](../../../api/wms_api_server/app/modules/resources/contracts_workload.py#L12)

```python
workload_config_service() -> WorkloadConfigPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### workload_history_service

[Исходник: api/wms_api_server/app/modules/resources/contracts_workload.py:18](../../../api/wms_api_server/app/modules/resources/contracts_workload.py#L18)

```python
workload_history_service() -> WorkloadHistoryPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### __init__

[Исходник: api/wms_api_server/app/modules/resources/contracts_workload.py:5](../../../api/wms_api_server/app/modules/resources/contracts_workload.py#L5)

```python
__init__(self, code: str, message: str, status: int=409) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `super`, `super().__init__`

### command

[Исходник: api/wms_api_server/app/modules/resources/contracts_workload.py:9](../../../api/wms_api_server/app/modules/resources/contracts_workload.py#L9)

```python
command(self, operation: str, action: str, body: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### configuration

[Исходник: api/wms_api_server/app/modules/resources/contracts_workload.py:10](../../../api/wms_api_server/app/modules/resources/contracts_workload.py#L10)

```python
configuration(self, ware: int, actor: str, site: str | None=None, start: datetime | None=None, finish: datetime | None=None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### read

[Исходник: api/wms_api_server/app/modules/resources/contracts_workload.py:16](../../../api/wms_api_server/app/modules/resources/contracts_workload.py#L16)

```python
read(self, ware: int, plan: str, limit: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### forecast_labour

[Исходник: api/wms_api_server/app/modules/resources/domain/forecast_labour.py:5](../../../api/wms_api_server/app/modules/resources/domain/forecast_labour.py#L5)

```python
forecast_labour(series: list[dict[str, Any]], basis: dict[str, Any]) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(Decimal(row['estimated_quantity']) / Decimal(norm['base_per_hour'])).quantize`, `Decimal`, `bool`, `format`, `len`, `localcontext`, `norms.get`, `row.get`, `rows.append`, `sum`

### hours

[Исходник: api/wms_api_server/app/modules/resources/domain/workload_intervals.py:6](../../../api/wms_api_server/app/modules/resources/domain/workload_intervals.py#L6)

```python
hours(start: datetime, finish: datetime) -> Decimal
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`

### union_hours

[Исходник: api/wms_api_server/app/modules/resources/domain/workload_intervals.py:10](../../../api/wms_api_server/app/modules/resources/domain/workload_intervals.py#L10)

```python
union_hours(spans: list[tuple[datetime, datetime]]) -> Decimal
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `hours`, `max`, `sorted`

### interval_load

[Исходник: api/wms_api_server/app/modules/resources/domain/workload_intervals.py:18](../../../api/wms_api_server/app/modules/resources/domain/workload_intervals.py#L18)

```python
interval_load(start: datetime, end: datetime, minutes: int, work: list[dict[str, Any]], attendance: list[dict[str, Any]]) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(required / hours(begin, finish)).to_integral_value`, `Decimal`, `begin.isoformat`, `blocked.append`, `finish.isoformat`, `fmt`, `format`, `hours`, `int`, `item.get`, `len`, `localcontext`, `max`, `min`, `people.setdefault`, `people.setdefault(plan['person_id'], []).append`, `people.values`, `result.append`, `sum`, `timedelta`, `union_hours`, `value.quantize`

### outside_view

[Исходник: api/wms_api_server/app/modules/resources/domain/workload_intervals.py:46](../../../api/wms_api_server/app/modules/resources/domain/workload_intervals.py#L46)

```python
outside_view(start: datetime, end: datetime, work: list[dict[str, Any]]) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `format`, `hours`, `item.get`, `localcontext`, `max`, `min`, `result.append`

### workload_recommendations

[Исходник: api/wms_api_server/app/modules/resources/domain/workload_recommendations.py:7](../../../api/wms_api_server/app/modules/resources/domain/workload_recommendations.py#L7)

```python
workload_recommendations(intervals: list[dict[str, Any]], work: list[dict[str, Any]]) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(gap / span).to_integral_value`, `(required * Decimal(3600000000)).to_integral_value`, `(start + timedelta(microseconds=duration)).isoformat`, `Decimal`, `by_wave.items`, `by_wave.setdefault`, `by_wave.setdefault(int(row['pick_wave_id']), []).append`, `capacity.append`, `datetime.fromisoformat`, `finish.isoformat`, `format`, `hours`, `int`, `iter`, `len`, `localcontext`, `next`, `r.get`, `scenarios.append`, `sorted`, `start.isoformat`, `sum`, `timedelta`, `unresolved.append`

### execute

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/case_actions.py:102](../../../api/wms_api_server/app/modules/resources/infrastructure/case_actions.py#L102)

```python
execute(gateway: Any, task_id: int, action: str, request: Any, event_writer: Callable[..., None]) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CaseActions`, `ValueError`, `getattr`, `getattr(CaseActions(bound, event_writer), action)`, `getattr(CaseActions(gateway, event_writer), action)`, `run_action`

### __init__

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/case_actions.py:9](../../../api/wms_api_server/app/modules/resources/infrastructure/case_actions.py#L9)

```python
__init__(self, gateway: Any, event_writer: Callable[..., None]) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### _event

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/case_actions.py:12](../../../api/wms_api_server/app/modules/resources/infrastructure/case_actions.py#L12)

```python
_event(self, *args: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.event_writer`

### claim_task

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/case_actions.py:15](../../../api/wms_api_server/app/modules/resources/infrastructure/case_actions.py#L15)

```python
claim_task(self, case_pick_task_id: int, request: CasePickTaskActionRequest) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `request.model_copy`, `resource_context`, `self._event`, `self.gateway.execute`

### start_task

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/case_actions.py:45](../../../api/wms_api_server/app/modules/resources/infrastructure/case_actions.py#L45)

```python
start_task(self, case_pick_task_id: int, request: CasePickTaskActionRequest) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `resource_context`, `self._event`, `self.claim_task`, `self.gateway.execute`, `self.gateway.fetch_all`

### transfer_task

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/case_actions.py:67](../../../api/wms_api_server/app/modules/resources/infrastructure/case_actions.py#L67)

```python
transfer_task(self, case_pick_task_id: int, request: CasePickTransferRequest) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `resource_context`, `self._event`, `self.gateway.execute`, `validate_handoff`

### context

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/case_assignment.py:8](../../../api/wms_api_server/app/modules/resources/infrastructure/case_assignment.py#L8)

```python
context(gateway: Any, task_id: int, action: str, request: Any) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `exc.args[0].message.split`, `gateway.fetch_all`, `getattr`, `isinstance`, `json.loads`

### run_action

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/case_assignment.py:30](../../../api/wms_api_server/app/modules/resources/infrastructure/case_assignment.py#L30)

```python
run_action(gateway: Any, task_id: int, action: str, request: Any, handler: Callable[[Any, int, Any], None]) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `TransactionGateway`, `bound.fetch_all`, `cursor.execute`, `cursor.fetchone`, `gateway.transaction`, `getattr`, `handler`, `replay`, `str`, `str(exc.args[0]).split`

### replay

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/case_handoff.py:6](../../../api/wms_api_server/app/modules/resources/infrastructure/case_handoff.py#L6)

```python
replay(gateway: Any, task_id: int, request: Any) -> bool
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `gateway.fetch_all`, `len`, `request.model_dump`, `str`

### validate

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/case_handoff.py:18](../../../api/wms_api_server/app/modules/resources/infrastructure/case_handoff.py#L18)

```python
validate(gateway: Any, task_id: int, request: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `HTTPException`, `gateway.fetch_all`, `len`, `request.model_dump`, `str`

### __init__

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/case_read_model.py:138](../../../api/wms_api_server/app/modules/resources/infrastructure/case_read_model.py#L138)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### list_tasks

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/case_read_model.py:141](../../../api/wms_api_server/app/modules/resources/infrastructure/case_read_model.py#L141)

```python
list_tasks(self, resource_id: int | None=None, scope: str='mine', status: str | None=None, limit: int=100, warehouse_id: int | None=None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `CASE_TASK_LIST_SQL.format`, `conditions.append`, `max`, `min`, `self.gateway.fetch_all`, `status.upper`

### get_task

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/case_read_model.py:174](../../../api/wms_api_server/app/modules/resources/infrastructure/case_read_model.py#L174)

```python
get_task(self, case_pick_task_id: int) -> dict[str, Any] | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `existing_case_tare_snapshot`, `lot.pop`, `self.gateway.fetch_all`

### list_shorts

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/case_read_model.py:253](../../../api/wms_api_server/app/modules/resources/infrastructure/case_read_model.py#L253)

```python
list_shorts(self, status: str | None=None, limit: int=200, warehouse_id: int | None=None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `conditions.append`, `max`, `min`, `self.gateway.fetch_all`, `status.upper`

### actor_scope

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/case_scoped_reads.py:9](../../../api/wms_api_server/app/modules/resources/infrastructure/case_scoped_reads.py#L9)

```python
actor_scope(cur: Any, actor: str) -> tuple[int | None, bool]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CaseReadError`, `cur.execute`, `cur.fetchone`

### native_task_scope

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/case_scoped_reads.py:18](../../../api/wms_api_server/app/modules/resources/infrastructure/case_scoped_reads.py#L18)

```python
native_task_scope(cur: Any, task: int, actor: str, permission: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CaseReadError`, `cur.callproc`, `getattr`, `str`

### task_scope

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/case_scoped_reads.py:33](../../../api/wms_api_server/app/modules/resources/infrastructure/case_scoped_reads.py#L33)

```python
task_scope(cur: Any, task: int, actor: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `actor_scope`, `native_task_scope`

### __init__

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/case_scoped_reads.py:39](../../../api/wms_api_server/app/modules/resources/infrastructure/case_scoped_reads.py#L39)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### tasks

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/case_scoped_reads.py:42](../../../api/wms_api_server/app/modules/resources/infrastructure/case_scoped_reads.py#L42)

```python
tasks(self, actor: str, resource: int | None, scope: str, status: str | None, limit: int) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CaseReadError`, `LegacyCaseReads`, `LegacyCaseReads(TransactionGateway(cur)).list_tasks`, `TransactionGateway`, `actor_scope`, `cur.execute`, `cur.fetchone`, `getattr`, `self.gateway.transaction`

### task

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/case_scoped_reads.py:60](../../../api/wms_api_server/app/modules/resources/infrastructure/case_scoped_reads.py#L60)

```python
task(self, task: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CaseReadError`, `LegacyCaseReads`, `LegacyCaseReads(TransactionGateway(cur)).get_task`, `TransactionGateway`, `cur.execute`, `getattr`, `self.gateway.transaction`, `task_scope`

### shorts

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/case_scoped_reads.py:71](../../../api/wms_api_server/app/modules/resources/infrastructure/case_scoped_reads.py#L71)

```python
shorts(self, actor: str, status: str | None, limit: int) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `CaseReadError`, `LegacyCaseReads`, `LegacyCaseReads(TransactionGateway(cur)).list_shorts`, `TransactionGateway`, `actor_scope`, `cur.execute`, `getattr`, `self.gateway.transaction`

### forecast_norm_basis

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/forecast_norms.py:7](../../../api/wms_api_server/app/modules/resources/infrastructure/forecast_norms.py#L7)

```python
forecast_norm_basis(cur: Any, ware: int, scope: str, keys: list[dict[str, Any]]) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `cur.execute`, `cur.var`, `data.setvalue`, `json.dumps`, `len`, `workload_rows`

### dispatch_warehouse

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/nearest_dispatch.py:6](../../../api/wms_api_server/app/modules/resources/infrastructure/nearest_dispatch.py#L6)

```python
dispatch_warehouse(gateway: Any, task_id: int, actor: str, assign: Callable[[Any, int, Any], None]) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `QualifiedCandidates`, `QualifiedCandidates(bound).warehouse`, `TransactionGateway`, `WarehouseTaskStatusRequest`, `assign`, `cursor.execute`, `cursor.fetchone`, `gateway.transaction`

### __init__

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/qualification_admin.py:6](../../../api/wms_api_server/app/modules/resources/infrastructure/qualification_admin.py#L6)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### qualifications

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/qualification_admin.py:9](../../../api/wms_api_server/app/modules/resources/infrastructure/qualification_admin.py#L9)

```python
qualifications(self, resource_id: int) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### set_qualification

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/qualification_admin.py:13](../../../api/wms_api_server/app/modules/resources/infrastructure/qualification_admin.py#L13)

```python
set_qualification(self, resource_id: int, task_type: str, active: bool, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `cursor.execute`, `cursor.fetchone`, `int`, `self.gateway.transaction`

### position

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/qualification_admin.py:32](../../../api/wms_api_server/app/modules/resources/infrastructure/qualification_admin.py#L32)

```python
position(self, session_id: int, cell: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `cursor.execute`, `cursor.fetchone`, `self.gateway.transaction`

### __init__

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/qualification_service.py:8](../../../api/wms_api_server/app/modules/resources/infrastructure/qualification_service.py#L8)

```python
__init__(self, gateway: Any, assign: Callable[[Any, int, Any], None]) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `super`, `super().__init__`

### warehouse

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/qualification_service.py:12](../../../api/wms_api_server/app/modules/resources/infrastructure/qualification_service.py#L12)

```python
warehouse(self, task_id: int, limit: int) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `QualifiedCandidates`, `QualifiedCandidates(self.gateway).warehouse`

### dispatch

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/qualification_service.py:15](../../../api/wms_api_server/app/modules/resources/infrastructure/qualification_service.py#L15)

```python
dispatch(self, task_id: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `dispatch_warehouse`

### __init__

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/qualified_candidates.py:6](../../../api/wms_api_server/app/modules/resources/infrastructure/qualified_candidates.py#L6)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### candidates

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/qualified_candidates.py:9](../../../api/wms_api_server/app/modules/resources/infrastructure/qualified_candidates.py#L9)

```python
candidates(self, cell: str, task_type: str, limit: int=10) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### warehouse

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/qualified_candidates.py:52](../../../api/wms_api_server/app/modules/resources/infrastructure/qualified_candidates.py#L52)

```python
warehouse(self, task_id: int, limit: int=10) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `self.candidates`, `self.gateway.fetch_all`

### dispatch_inventory

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/qualified_candidates.py:59](../../../api/wms_api_server/app/modules/resources/infrastructure/qualified_candidates.py#L59)

```python
dispatch_inventory(self, short_id: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `QualifiedCandidates`, `QualifiedCandidates(bound).candidates`, `TransactionGateway`, `bound.fetch_all`, `cursor.execute`, `cursor.fetchone`, `self.gateway.transaction`

### __init__

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/reach_shifts.py:7](../../../api/wms_api_server/app/modules/resources/infrastructure/reach_shifts.py#L7)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### read

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/reach_shifts.py:10](../../../api/wms_api_server/app/modules/resources/infrastructure/reach_shifts.py#L10)

```python
read(self, base_shift_id: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### create

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/reach_shifts.py:18](../../../api/wms_api_server/app/modules/resources/infrastructure/reach_shifts.py#L18)

```python
create(self, base_shift_id: int, main_drivers: int, duty_drivers: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `begins.date`, `cursor.execute`, `cursor.fetchall`, `cursor.fetchone`, `self.gateway.transaction`, `self.read`, `timedelta`

### open_session

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/session_lifecycle.py:6](../../../api/wms_api_server/app/modules/resources/infrastructure/session_lifecycle.py#L6)

```python
open_session(gateway: Any, request: Any, create: Callable[[Any, Any], int]) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `TransactionGateway`, `create`, `cursor.execute`, `cursor.fetchone`, `gateway.transaction`

### close_session

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/session_lifecycle.py:27](../../../api/wms_api_server/app/modules/resources/infrastructure/session_lifecycle.py#L27)

```python
close_session(gateway: Any, session_id: int, actor: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `cursor.execute`, `cursor.fetchall`, `cursor.fetchone`, `gateway.transaction`, `int`

### task_resource_context

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/task_assignment.py:8](../../../api/wms_api_server/app/modules/resources/infrastructure/task_assignment.py#L8)

```python
task_resource_context(gateway: Any, task: dict[str, Any], action: str, request: Any, assignee: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `any`, `exc.args[0].message.split`, `gateway.fetch_all`, `getattr`, `json.loads`, `task.get`

### release_cancelled_task

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/task_cancellation.py:7](../../../api/wms_api_server/app/modules/resources/infrastructure/task_cancellation.py#L7)

```python
release_cancelled_task(gateway: TransactionGateway, task: dict[str, Any], actor: str, reason: str | None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`, `cursor.execute`, `cursor.var`, `gateway.execute`, `gateway.fetch_all`, `json.dumps`, `payload_bind.setvalue`, `task.get`

### dispatch_urgent

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/urgent_dispatch.py:6](../../../api/wms_api_server/app/modules/resources/infrastructure/urgent_dispatch.py#L6)

```python
dispatch_urgent(gateway: Any, short_id: int, actor: str, assign: Callable[[Any, int, Any], None]) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `dispatch_warehouse`, `gateway.fetch_all`, `int`

### sync_wave_tasks

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/wave_tasks.py:9](../../../api/wms_api_server/app/modules/resources/infrastructure/wave_tasks.py#L9)

```python
sync_wave_tasks(gateway: Any, wave_id: int, actor: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `TransactionGateway`, `cursor.execute`, `cursor.fetchone`, `gateway.transaction`, `reconcile_existing_shared_arrival`

### wave_time_error

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/wave_time.py:8](../../../api/wms_api_server/app/modules/resources/infrastructure/wave_time.py#L8)

```python
wave_time_error(exc: oracledb.DatabaseError) -> WorkloadError
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `WorkloadError`, `getattr`, `str`, `str(exc.args[0]).split`

### __init__

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/wave_time.py:16](../../../api/wms_api_server/app/modules/resources/infrastructure/wave_time.py#L16)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### context

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/wave_time.py:18](../../../api/wms_api_server/app/modules/resources/infrastructure/wave_time.py#L18)

```python
context(self, wave: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.callproc`, `cur.execute`, `cur.var`, `read_oracle_json`, `result.getvalue`, `self.gateway.transaction`, `wave_time_error`

### approve

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/wave_time.py:27](../../../api/wms_api_server/app/modules/resources/infrastructure/wave_time.py#L27)

```python
approve(self, operation: str, body: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `WorkloadError`, `cur.callproc`, `cur.var`, `json.dumps`, `len`, `read_oracle_json`, `result.getvalue`, `self.gateway.transaction`, `serialized.encode`, `wave_time_error`

### approved_wave_windows

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/wave_time_reader.py:6](../../../api/wms_api_server/app/modules/resources/infrastructure/wave_time_reader.py#L6)

```python
approved_wave_windows(cur: Any, warehouse: int) -> dict[int, dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `WorkloadError`, `cur.execute`, `datetime.fromisoformat`, `int`, `len`, `workload_rows`

### current_warehouse

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/workload_config.py:9](../../../api/wms_api_server/app/modules/resources/infrastructure/workload_config.py#L9)

```python
current_warehouse(cur: Any, ware: int, actor: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `WorkloadError`, `cur.execute`, `cur.fetchone`

### workload_rows

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/workload_config.py:14](../../../api/wms_api_server/app/modules/resources/infrastructure/workload_config.py#L14)

```python
workload_rows(cur: Any) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `col[0].lower`, `cur.fetchall`, `dict`, `zip`

### __init__

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/workload_config.py:18](../../../api/wms_api_server/app/modules/resources/infrastructure/workload_config.py#L18)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### command

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/workload_config.py:21](../../../api/wms_api_server/app/modules/resources/infrastructure/workload_config.py#L21)

```python
command(self, operation: str, action: str, body: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `WorkloadError`, `cur.callproc`, `cur.var`, `getattr`, `json.dumps`, `read_oracle_json`, `result.getvalue`, `self.gateway.transaction`, `str`, `str(exc.args[0]).split`

### configuration

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/workload_config.py:36](../../../api/wms_api_server/app/modules/resources/infrastructure/workload_config.py#L36)

```python
configuration(self, ware: int, actor: str, site: str | None=None, start: datetime | None=None, finish: datetime | None=None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `WorkloadError`, `attendance_params.update`, `cur.execute`, `current_warehouse`, `dict`, `finish.astimezone`, `finish.isoformat`, `len`, `self.gateway.transaction`, `start.astimezone`, `start.isoformat`, `workload_rows`

### __init__

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/workload_history.py:7](../../../api/wms_api_server/app/modules/resources/infrastructure/workload_history.py#L7)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### read

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/workload_history.py:8](../../../api/wms_api_server/app/modules/resources/infrastructure/workload_history.py#L8)

```python
read(self, ware: int, plan: str, limit: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `WorkloadError`, `any`, `cur.execute`, `cur.fetchone`, `current_warehouse`, `len`, `range`, `self.gateway.transaction`, `workload_rows`

### __init__

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/workload_monitor.py:14](../../../api/wms_api_server/app/modules/resources/infrastructure/workload_monitor.py#L14)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### preview

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/workload_monitor.py:16](../../../api/wms_api_server/app/modules/resources/infrastructure/workload_monitor.py#L16)

```python
preview(self, ware: int, site: str, start: datetime, end: datetime, minutes: int, windows: list[dict[str, Any]], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `WorkloadError`, `any`, `approved.get`, `approved_wave_windows`, `by_wave.get`, `cur.execute`, `current_warehouse`, `format`, `int`, `interval_load`, `json.dumps`, `json.dumps([ware, site, public_work, [{**r, 'start': r['start'].isoformat(), 'finish': r['finish'].isoformat()} for r in attendance]], sort_keys=True, separators=(',', ':')).encode`, `len`, `localcontext`, `outside_view`, `r['finish'].isoformat`, `r['start'].isoformat`, `row.items`, `self._attendance`, `self._work`, `self.gateway.transaction`, `set`, `sha256`, `sha256(json.dumps([ware, site, public_work, [{**r, 'start': r['start'].isoformat(), 'finish': r['finish'].isoformat()} for r in attendance]], sort_keys=True, separators=(',', ':')).encode()).hexdigest`, `sum`, `v.isoformat`, `workload_recommendations`, `workload_rows`

### _work

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/workload_monitor.py:52](../../../api/wms_api_server/app/modules/resources/infrastructure/workload_monitor.py#L52)

```python
_work(cur: Any, ware: int, site: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `WorkloadError`, `cur.execute`, `len`, `workload_rows`

### _attendance

[Исходник: api/wms_api_server/app/modules/resources/infrastructure/workload_monitor.py:73](../../../api/wms_api_server/app/modules/resources/infrastructure/workload_monitor.py#L73)

```python
_attendance(cur: Any, ware: int, site: str, start: datetime, end: datetime) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `WorkloadError`, `cur.execute`, `datetime.fromisoformat`, `end.isoformat`, `len`, `start.isoformat`, `workload_rows`

### existing_task_resource_context

[Исходник: api/wms_api_server/app/modules/resources/public.py:6](../../../api/wms_api_server/app/modules/resources/public.py#L6)

```python
existing_task_resource_context(gateway: Any, task: dict[str, Any], action: str, request: Any, assignee: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `task_resource_context`

### sync_existing_wave_tasks

[Исходник: api/wms_api_server/app/modules/resources/public.py:13](../../../api/wms_api_server/app/modules/resources/public.py#L13)

```python
sync_existing_wave_tasks(gateway: Any, wave_id: int, actor: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `sync_wave_tasks`

### build_qualification_service

[Исходник: api/wms_api_server/app/modules/resources/public.py:21](../../../api/wms_api_server/app/modules/resources/public.py#L21)

```python
build_qualification_service(assign: Callable[[Any, int, Any], None]) -> QualificationService
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `QualificationService`

### assign_existing_inventory_auditor

[Исходник: api/wms_api_server/app/modules/resources/public.py:25](../../../api/wms_api_server/app/modules/resources/public.py#L25)

```python
assign_existing_inventory_auditor(gateway: Any, short_id: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `QualifiedCandidates`, `QualifiedCandidates(gateway).dispatch_inventory`

### build_reach_shifts

[Исходник: api/wms_api_server/app/modules/resources/public.py:40](../../../api/wms_api_server/app/modules/resources/public.py#L40)

```python
build_reach_shifts() -> ReachShifts
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `ReachShifts`

### build_workload_config

[Исходник: api/wms_api_server/app/modules/resources/public.py:48](../../../api/wms_api_server/app/modules/resources/public.py#L48)

```python
build_workload_config(gateway: Any) -> WorkloadConfigPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `WorkloadConfig`

### build_workload_monitor

[Исходник: api/wms_api_server/app/modules/resources/public.py:54](../../../api/wms_api_server/app/modules/resources/public.py#L54)

```python
build_workload_monitor(gateway: Any) -> WorkloadMonitorPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `WorkloadMonitor`

### build_wave_time

[Исходник: api/wms_api_server/app/modules/resources/public.py:61](../../../api/wms_api_server/app/modules/resources/public.py#L61)

```python
build_wave_time(gateway: Any) -> WaveTimePort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `WaveTime`

### build_workload_history

[Исходник: api/wms_api_server/app/modules/resources/public.py:68](../../../api/wms_api_server/app/modules/resources/public.py#L68)

```python
build_workload_history(gateway: Any) -> WorkloadHistoryPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `WorkloadHistory`

### legacy_case_reads

[Исходник: api/wms_api_server/app/modules/resources/public.py:76](../../../api/wms_api_server/app/modules/resources/public.py#L76)

```python
legacy_case_reads(gateway: Any) -> LegacyCaseReads
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LegacyCaseReads`
