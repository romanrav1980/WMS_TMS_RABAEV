# Методы: transport

### configure

[Исходник: api/wms_api_server/app/modules/transport/api/driver_binding_routes.py:19](../../../api/wms_api_server/app/modules/transport/api/driver_binding_routes.py#L19)

```python
configure(driver_id: int, body: DriverBindingRequest, user: AdminUser=Depends(require_permission('warehouse_settings_edit')), service: DriverBindingPort=Depends(driver_binding_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.put`, `service.configure`, `str`

### get

[Исходник: api/wms_api_server/app/modules/transport/api/driver_binding_routes.py:30](../../../api/wms_api_server/app/modules/transport/api/driver_binding_routes.py#L30)

```python
get(driver_id: int, user: AdminUser=Depends(require_permission('warehouse_settings_edit')), service: DriverBindingPort=Depends(driver_binding_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `require_permission`, `router.get`, `service.get`

### failure

[Исходник: api/wms_api_server/app/modules/transport/api/driver_workspace_routes.py:11](../../../api/wms_api_server/app/modules/transport/api/driver_workspace_routes.py#L11)

```python
failure(exc: TransportPlanError) -> HTTPException
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `str`

### trips

[Исходник: api/wms_api_server/app/modules/transport/api/driver_workspace_routes.py:15](../../../api/wms_api_server/app/modules/transport/api/driver_workspace_routes.py#L15)

```python
trips(driver_id: int=Query(..., gt=0), trip_date: date | None=None, user: AdminUser=Depends(get_current_user), service: DriverWorkspacePort=Depends(driver_workspace_service)) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Query`, `date.today`, `failure`, `router.get`, `service.trips`

### stops

[Исходник: api/wms_api_server/app/modules/transport/api/driver_workspace_routes.py:24](../../../api/wms_api_server/app/modules/transport/api/driver_workspace_routes.py#L24)

```python
stops(task_id: int, driver_id: int=Query(..., gt=0), user: AdminUser=Depends(get_current_user), service: DriverWorkspacePort=Depends(driver_workspace_service)) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Query`, `failure`, `router.get`, `service.details`

### operations

[Исходник: api/wms_api_server/app/modules/transport/api/driver_workspace_routes.py:32](../../../api/wms_api_server/app/modules/transport/api/driver_workspace_routes.py#L32)

```python
operations(task_id: int, driver_id: int=Query(..., gt=0), user: AdminUser=Depends(get_current_user), service: DriverWorkspacePort=Depends(driver_workspace_service)) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Query`, `failure`, `router.get`, `service.details`

### start

[Исходник: api/wms_api_server/app/modules/transport/api/driver_workspace_routes.py:40](../../../api/wms_api_server/app/modules/transport/api/driver_workspace_routes.py#L40)

```python
start(op_id: int, driver_id: int=Query(..., gt=0), user: AdminUser=Depends(get_current_user), service: DriverWorkspacePort=Depends(driver_workspace_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Query`, `failure`, `router.post`, `service.mark`

### done

[Исходник: api/wms_api_server/app/modules/transport/api/driver_workspace_routes.py:48](../../../api/wms_api_server/app/modules/transport/api/driver_workspace_routes.py#L48)

```python
done(op_id: int, driver_id: int=Query(..., gt=0), user: AdminUser=Depends(get_current_user), service: DriverWorkspacePort=Depends(driver_workspace_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Query`, `failure`, `router.post`, `service.mark`

### forecast

[Исходник: api/wms_api_server/app/modules/transport/api/forecast_routes.py:17](../../../api/wms_api_server/app/modules/transport/api/forecast_routes.py#L17)

```python
forecast(ware_id: int, body: ForecastRequest, user: AdminUser=Depends(require_permission('transport_dispatch_view')), service: WarehouseForecastPort=Depends(warehouse_forecast_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `ForecastQuery`, `HTTPException`, `body.model_dump`, `require_permission`, `router.post`, `service.get`, `str`

### project

[Исходник: api/wms_api_server/app/modules/transport/api/forecast_routes.py:23](../../../api/wms_api_server/app/modules/transport/api/forecast_routes.py#L23)

```python
project(ware_id: int, limit: int=50, user: AdminUser=Depends(require_permission('transport_dispatch_edit')), service: WarehouseForecastPort=Depends(warehouse_forecast_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.post`, `service.project`, `str`

### project_source

[Исходник: api/wms_api_server/app/modules/transport/api/forecast_routes.py:33](../../../api/wms_api_server/app/modules/transport/api/forecast_routes.py#L33)

```python
project_source(body: ProjectLoad, user: AdminUser=Depends(require_permission('transport_dispatch_edit')), service: WarehouseForecastPort=Depends(warehouse_forecast_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.post`, `service.project_load`, `str`

### failure

[Исходник: api/wms_api_server/app/modules/transport/api/loading_routes.py:64](../../../api/wms_api_server/app/modules/transport/api/loading_routes.py#L64)

```python
failure(exc: TransportLoadingError) -> HTTPException
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `bool`, `str`

### status

[Исходник: api/wms_api_server/app/modules/transport/api/loading_routes.py:70](../../../api/wms_api_server/app/modules/transport/api/loading_routes.py#L70)

```python
status(task_id: int, user: AdminUser=Depends(require_permission('transport_dispatch_view')), service: TransportLoadingPort=Depends(transport_loading_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `failure`, `require_permission`, `router.get`, `service.status`

### confirm

[Исходник: api/wms_api_server/app/modules/transport/api/loading_routes.py:79](../../../api/wms_api_server/app/modules/transport/api/loading_routes.py#L79)

```python
confirm(body: LoadingRequest, user: AdminUser=Depends(require_permission('stock_posting_shipping')), service: TransportLoadingPort=Depends(transport_loading_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `body.measurements.model_dump`, `body.model_dump`, `body.temperature_confirmation.model_dump`, `failure`, `item.model_dump`, `require_permission`, `router.post`, `service.load`

### depart

[Исходник: api/wms_api_server/app/modules/transport/api/loading_routes.py:96](../../../api/wms_api_server/app/modules/transport/api/loading_routes.py#L96)

```python
depart(task_id: int, body: DepartureRequest, user: AdminUser=Depends(require_permission('transport_dispatch_close')), service: TransportLoadingPort=Depends(transport_loading_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `body.temperature_confirmation.model_dump`, `failure`, `require_permission`, `router.post`, `service.depart`

### single_preview

[Исходник: api/wms_api_server/app/modules/transport/api/loading_routes.py:114](../../../api/wms_api_server/app/modules/transport/api/loading_routes.py#L114)

```python
single_preview(shipment_identifier: str, user: AdminUser=Depends(require_permission('stock_posting_shipping')), service: TransportLoadingPort=Depends(transport_loading_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `failure`, `len`, `require_permission`, `router.get`, `service.preview_single`

### confirm_single

[Исходник: api/wms_api_server/app/modules/transport/api/loading_routes.py:126](../../../api/wms_api_server/app/modules/transport/api/loading_routes.py#L126)

```python
confirm_single(body: SingleLoadingRequest, user: AdminUser=Depends(require_permission('stock_posting_shipping')), service: TransportLoadingPort=Depends(transport_loading_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `body.measurements.model_dump`, `body.model_dump`, `body.temperature_confirmation.model_dump`, `failure`, `item.model_dump`, `require_permission`, `router.post`, `service.load_single`

### reconciliation_preview

[Исходник: api/wms_api_server/app/modules/transport/api/loading_routes.py:147](../../../api/wms_api_server/app/modules/transport/api/loading_routes.py#L147)

```python
reconciliation_preview(shipping_operation_id: str, user: AdminUser=Depends(require_permission('stock_posting_shipping')), service: TransportLoadingPort=Depends(transport_loading_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `failure`, `len`, `require_permission`, `router.get`, `service.preview_reconciliation`

### confirm_reconciliation

[Исходник: api/wms_api_server/app/modules/transport/api/loading_routes.py:159](../../../api/wms_api_server/app/modules/transport/api/loading_routes.py#L159)

```python
confirm_reconciliation(body: ReconciliationLoadingRequest, user: AdminUser=Depends(require_permission('stock_posting_shipping')), service: TransportLoadingPort=Depends(transport_loading_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `body.measurements.model_dump`, `body.model_dump`, `body.temperature_confirmation.model_dump`, `failure`, `item.model_dump`, `require_permission`, `router.post`, `service.reconcile`

### update_operation_fact

[Исходник: api/wms_api_server/app/modules/transport/api/operation_fact_routes.py:12](../../../api/wms_api_server/app/modules/transport/api/operation_fact_routes.py#L12)

```python
update_operation_fact(op_id: int, data: OperationFactUpdate, user: AdminUser=Depends(require_permission('transport_dispatch_edit')), service: OperationFactPort=Depends(operation_fact_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `data.model_dump`, `require_permission`, `router.patch`, `service.write`, `str`

### time_context

[Исходник: api/wms_api_server/app/modules/transport/api/preflight_routes.py:30](../../../api/wms_api_server/app/modules/transport/api/preflight_routes.py#L30)

```python
time_context(trip_id: int, user: AdminUser=Depends(require_permission('transport_dispatch_edit')), service: TransportPreflightPort=Depends(transport_preflight_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.get`, `service.time_context`, `str`

### coordination_preflight

[Исходник: api/wms_api_server/app/modules/transport/api/preflight_routes.py:41](../../../api/wms_api_server/app/modules/transport/api/preflight_routes.py#L41)

```python
coordination_preflight(trip_id: int, user: AdminUser=Depends(require_permission('transport_dispatch_edit')), service: TransportPreflightPort=Depends(transport_preflight_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.get`, `service.coordination`, `str`

### approve_time

[Исходник: api/wms_api_server/app/modules/transport/api/preflight_routes.py:52](../../../api/wms_api_server/app/modules/transport/api/preflight_routes.py#L52)

```python
approve_time(body: TimeApproval, user: AdminUser=Depends(require_permission('transport_dispatch_edit')), service: TransportPreflightPort=Depends(transport_preflight_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `body.model_dump`, `require_permission`, `router.post`, `service.approve_time`, `str`

### trip_time_preflight

[Исходник: api/wms_api_server/app/modules/transport/api/preflight_routes.py:61](../../../api/wms_api_server/app/modules/transport/api/preflight_routes.py#L61)

```python
trip_time_preflight(trip_id: int, body: TimePreflight, user: AdminUser=Depends(require_permission('transport_dispatch_edit')), service: TransportPreflightPort=Depends(transport_preflight_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.post`, `service.trip_time`, `str`

### plan_preflight

[Исходник: api/wms_api_server/app/modules/transport/api/preflight_routes.py:73](../../../api/wms_api_server/app/modules/transport/api/preflight_routes.py#L73)

```python
plan_preflight(plan_id: int, user: AdminUser=Depends(require_permission('transport_dispatch_edit')), service: TransportPreflightPort=Depends(transport_preflight_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.get`, `service.plan`, `str`

### trip_preflight

[Исходник: api/wms_api_server/app/modules/transport/api/preflight_routes.py:84](../../../api/wms_api_server/app/modules/transport/api/preflight_routes.py#L84)

```python
trip_preflight(trip_id: int, body: ManualPreflight, user: AdminUser=Depends(require_permission('transport_dispatch_edit')), service: TransportPreflightPort=Depends(transport_preflight_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `any`, `len`, `number.strip`, `require_permission`, `router.post`, `service.trip`, `str`

### route_context

[Исходник: api/wms_api_server/app/modules/transport/api/preflight_routes.py:108](../../../api/wms_api_server/app/modules/transport/api/preflight_routes.py#L108)

```python
route_context(trip_id: int, user: AdminUser=Depends(require_permission('transport_dispatch_edit')), service: TransportPreflightPort=Depends(transport_preflight_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.get`, `service.route_context`, `str`

### route_input

[Исходник: api/wms_api_server/app/modules/transport/api/preflight_routes.py:119](../../../api/wms_api_server/app/modules/transport/api/preflight_routes.py#L119)

```python
route_input(body: RouteInput, user: AdminUser=Depends(require_permission('transport_dispatch_edit')), service: TransportPreflightPort=Depends(transport_preflight_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `body.model_dump`, `require_permission`, `router.post`, `service.apply_route_input`, `str`

### road_legs

[Исходник: api/wms_api_server/app/modules/transport/api/preflight_routes.py:127](../../../api/wms_api_server/app/modules/transport/api/preflight_routes.py#L127)

```python
road_legs(trip_id: int, depot_address: str=Query(default='', max_length=200), max_age_hours: int=Query(default=24, ge=1, le=720), user: AdminUser=Depends(require_permission('transport_dispatch_edit')), service: TransportPreflightPort=Depends(transport_preflight_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Query`, `depot_address.strip`, `require_permission`, `router.get`, `service.road_legs`, `str`

### delivery_windows

[Исходник: api/wms_api_server/app/modules/transport/api/preflight_routes.py:136](../../../api/wms_api_server/app/modules/transport/api/preflight_routes.py#L136)

```python
delivery_windows(trip_id: int, time_zone: Literal['UTC', 'Europe/Moscow', 'Asia/Tbilisi'], depot_address: str=Query(default='', max_length=200), max_age_hours: int=Query(default=24, ge=1, le=720), user: AdminUser=Depends(require_permission('transport_dispatch_edit')), service: TransportPreflightPort=Depends(transport_preflight_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Query`, `depot_address.strip`, `require_permission`, `router.get`, `service.delivery_windows`, `str`

### context

[Исходник: api/wms_api_server/app/modules/transport/api/st_deferral_routes.py:21](../../../api/wms_api_server/app/modules/transport/api/st_deferral_routes.py#L21)

```python
context(st_number: str=Query(min_length=1, max_length=100), user: AdminUser=Depends(require_permission('transport_dispatch_view')), service: StDeferralPort=Depends(st_deferral_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Query`, `require_permission`, `router.get`, `service.context`, `str`

### defer

[Исходник: api/wms_api_server/app/modules/transport/api/st_deferral_routes.py:27](../../../api/wms_api_server/app/modules/transport/api/st_deferral_routes.py#L27)

```python
defer(body: DeferralBody, user: AdminUser=Depends(require_permission('transport_dispatch_edit')), service: StDeferralPort=Depends(st_deferral_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `body.model_dump`, `require_permission`, `router.post`, `service.defer`, `str`

### history

[Исходник: api/wms_api_server/app/modules/transport/api/st_deferral_routes.py:33](../../../api/wms_api_server/app/modules/transport/api/st_deferral_routes.py#L33)

```python
history(st_number: str=Query(min_length=1, max_length=100), after_version: int=Query(default=0, ge=0), user: AdminUser=Depends(require_permission('transport_dispatch_view')), service: StDeferralPort=Depends(st_deferral_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Query`, `require_permission`, `router.get`, `service.history`, `str`

### trip_candidates

[Исходник: api/wms_api_server/app/modules/transport/api/st_deferral_routes.py:40](../../../api/wms_api_server/app/modules/transport/api/st_deferral_routes.py#L40)

```python
trip_candidates(st_number: str=Query(min_length=1, max_length=100), date_from: date | None=None, date_to: date | None=None, district: str | None=Query(default=None, max_length=80), store_code: str | None=Query(default=None, max_length=80), after_date: datetime | None=None, after_trip_id: int=Query(default=0, ge=0), limit: int=Query(default=50, ge=1, le=100), purpose: Literal['DEFER', 'ASSIGN']='DEFER', user: AdminUser=Depends(require_permission('transport_dispatch_view')), service: StDeferralPort=Depends(st_deferral_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Query`, `require_permission`, `router.get`, `service.candidates`, `str`

### unload

[Исходник: api/wms_api_server/app/modules/transport/api/unloading_routes.py:29](../../../api/wms_api_server/app/modules/transport/api/unloading_routes.py#L29)

```python
unload(body: UnloadingRequest, user: AdminUser=Depends(require_permission('stock_posting_shipping')), service: TransportLoadingPort=Depends(transport_loading_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `body.model_dump`, `failure`, `require_permission`, `router.post`, `service.unload`

### failure

[Исходник: api/wms_api_server/app/modules/transport/api/vehicle_profile_routes.py:65](../../../api/wms_api_server/app/modules/transport/api/vehicle_profile_routes.py#L65)

```python
failure(exc: VehicleProfileError, operation: str | None=None) -> HTTPException
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `str`

### configure

[Исходник: api/wms_api_server/app/modules/transport/api/vehicle_profile_routes.py:69](../../../api/wms_api_server/app/modules/transport/api/vehicle_profile_routes.py#L69)

```python
configure(body: VehicleProfileRequest, user: AdminUser=Depends(require_permission('transport_fleet_edit')), service: VehicleProfilePort=Depends(vehicle_profile_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `body.model_dump`, `failure`, `require_permission`, `router.post`, `service.configure`

### read

[Исходник: api/wms_api_server/app/modules/transport/api/vehicle_profile_routes.py:75](../../../api/wms_api_server/app/modules/transport/api/vehicle_profile_routes.py#L75)

```python
read(vehicle_id: int, user: AdminUser=Depends(require_permission('transport_dispatch_view')), service: VehicleProfilePort=Depends(vehicle_profile_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `failure`, `require_permission`, `router.get`, `service.read`

### tare_types

[Исходник: api/wms_api_server/app/modules/transport/api/vehicle_profile_routes.py:83](../../../api/wms_api_server/app/modules/transport/api/vehicle_profile_routes.py#L83)

```python
tare_types(user: AdminUser=Depends(require_permission('transport_dispatch_view')), service: VehicleProfilePort=Depends(vehicle_profile_service)) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `failure`, `require_permission`, `router.get`, `service.tare_types`

### unique_types

[Исходник: api/wms_api_server/app/modules/transport/api/vehicle_profile_routes.py:20](../../../api/wms_api_server/app/modules/transport/api/vehicle_profile_routes.py#L20)

```python
unique_types(self) -> 'FloorLoadingVariant'
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `len`, `model_validator`, `set`

### unique_variants

[Исходник: api/wms_api_server/app/modules/transport/api/vehicle_profile_routes.py:46](../../../api/wms_api_server/app/modules/transport/api/vehicle_profile_routes.py#L46)

```python
unique_variants(self) -> 'VehicleProfileRequest'
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `len`, `model_validator`, `set`

### temperature_pair

[Исходник: api/wms_api_server/app/modules/transport/api/vehicle_profile_routes.py:56](../../../api/wms_api_server/app/modules/transport/api/vehicle_profile_routes.py#L56)

```python
temperature_pair(self) -> 'VehicleProfileRequest'
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `ValueError`, `model_validator`

### context

[Исходник: api/wms_api_server/app/modules/transport/api/warehouse_depot_routes.py:15](../../../api/wms_api_server/app/modules/transport/api/warehouse_depot_routes.py#L15)

```python
context(warehouse_id: int, user: AdminUser=Depends(require_permission('warehouse_settings_edit')), service: WarehouseDepotPort=Depends(warehouse_depot_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.get`, `service.context`, `str`

### configure

[Исходник: api/wms_api_server/app/modules/transport/api/warehouse_depot_routes.py:21](../../../api/wms_api_server/app/modules/transport/api/warehouse_depot_routes.py#L21)

```python
configure(body: DepotSetting, user: AdminUser=Depends(require_permission('warehouse_settings_edit')), service: WarehouseDepotPort=Depends(warehouse_depot_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `body.model_dump`, `require_permission`, `router.post`, `service.apply`, `str`

### resolve

[Исходник: api/wms_api_server/app/modules/transport/api/warehouse_depot_routes.py:27](../../../api/wms_api_server/app/modules/transport/api/warehouse_depot_routes.py#L27)

```python
resolve(body: DepotSetting, user: AdminUser=Depends(require_permission('warehouse_settings_edit')), service: WarehouseDepotPort=Depends(warehouse_depot_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `body.model_dump`, `require_permission`, `router.post`, `service.resolve`, `str`

### transport_loading_service

[Исходник: api/wms_api_server/app/modules/transport/contracts.py:24](../../../api/wms_api_server/app/modules/transport/contracts.py#L24)

```python
transport_loading_service() -> TransportLoadingPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### __init__

[Исходник: api/wms_api_server/app/modules/transport/contracts.py:6](../../../api/wms_api_server/app/modules/transport/contracts.py#L6)

```python
__init__(self, code: str, message: str, operation_id: str='', status: int=409) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `super`, `super().__init__`

### unload

[Исходник: api/wms_api_server/app/modules/transport/contracts.py:14](../../../api/wms_api_server/app/modules/transport/contracts.py#L14)

```python
unload(self, operation_id: str, load_operation_id: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### preview_reconciliation

[Исходник: api/wms_api_server/app/modules/transport/contracts.py:15](../../../api/wms_api_server/app/modules/transport/contracts.py#L15)

```python
preview_reconciliation(self, shipping_operation_id: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### reconcile

[Исходник: api/wms_api_server/app/modules/transport/contracts.py:16](../../../api/wms_api_server/app/modules/transport/contracts.py#L16)

```python
reconcile(self, operation_id: str, shipping_operation_id: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### preview_single

[Исходник: api/wms_api_server/app/modules/transport/contracts.py:17](../../../api/wms_api_server/app/modules/transport/contracts.py#L17)

```python
preview_single(self, shipment_identifier: str, actor: str | None=None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### load_single

[Исходник: api/wms_api_server/app/modules/transport/contracts.py:18](../../../api/wms_api_server/app/modules/transport/contracts.py#L18)

```python
load_single(self, operation_id: str, shipment_identifier: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### status

[Исходник: api/wms_api_server/app/modules/transport/contracts.py:19](../../../api/wms_api_server/app/modules/transport/contracts.py#L19)

```python
status(self, task_id: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### load

[Исходник: api/wms_api_server/app/modules/transport/contracts.py:20](../../../api/wms_api_server/app/modules/transport/contracts.py#L20)

```python
load(self, operation_id: str, identifier: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### depart

[Исходник: api/wms_api_server/app/modules/transport/contracts.py:21](../../../api/wms_api_server/app/modules/transport/contracts.py#L21)

```python
depart(self, operation_id: str, task_id: int, actor: str, temperature_confirmation: dict[str, Any] | None=None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### warehouse_depot_service

[Исходник: api/wms_api_server/app/modules/transport/contracts_depot.py:6](../../../api/wms_api_server/app/modules/transport/contracts_depot.py#L6)

```python
warehouse_depot_service() -> WarehouseDepotPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### resolve

[Исходник: api/wms_api_server/app/modules/transport/contracts_depot.py:3](../../../api/wms_api_server/app/modules/transport/contracts_depot.py#L3)

```python
resolve(self, operation: str, body: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### context

[Исходник: api/wms_api_server/app/modules/transport/contracts_depot.py:4](../../../api/wms_api_server/app/modules/transport/contracts_depot.py#L4)

```python
context(self, ware: int, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### apply

[Исходник: api/wms_api_server/app/modules/transport/contracts_depot.py:5](../../../api/wms_api_server/app/modules/transport/contracts_depot.py#L5)

```python
apply(self, operation: str, body: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### driver_binding_service

[Исходник: api/wms_api_server/app/modules/transport/contracts_driver_binding.py:9](../../../api/wms_api_server/app/modules/transport/contracts_driver_binding.py#L9)

```python
driver_binding_service() -> DriverBindingPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### configure

[Исходник: api/wms_api_server/app/modules/transport/contracts_driver_binding.py:5](../../../api/wms_api_server/app/modules/transport/contracts_driver_binding.py#L5)

```python
configure(self, driver_id: int, user_id: str, active: bool, expected_version: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### get

[Исходник: api/wms_api_server/app/modules/transport/contracts_driver_binding.py:6](../../../api/wms_api_server/app/modules/transport/contracts_driver_binding.py#L6)

```python
get(self, driver_id: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### driver_workspace_service

[Исходник: api/wms_api_server/app/modules/transport/contracts_driver_workspace.py:9](../../../api/wms_api_server/app/modules/transport/contracts_driver_workspace.py#L9)

```python
driver_workspace_service() -> DriverWorkspacePort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### trips

[Исходник: api/wms_api_server/app/modules/transport/contracts_driver_workspace.py:5](../../../api/wms_api_server/app/modules/transport/contracts_driver_workspace.py#L5)

```python
trips(self, driver: int, day: date, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### details

[Исходник: api/wms_api_server/app/modules/transport/contracts_driver_workspace.py:6](../../../api/wms_api_server/app/modules/transport/contracts_driver_workspace.py#L6)

```python
details(self, driver: int, trip: int, kind: str, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### mark

[Исходник: api/wms_api_server/app/modules/transport/contracts_driver_workspace.py:7](../../../api/wms_api_server/app/modules/transport/contracts_driver_workspace.py#L7)

```python
mark(self, driver: int, operation: int, action: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### warehouse_forecast_service

[Исходник: api/wms_api_server/app/modules/transport/contracts_forecast.py:23](../../../api/wms_api_server/app/modules/transport/contracts_forecast.py#L23)

```python
warehouse_forecast_service() -> WarehouseForecastPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### __init__

[Исходник: api/wms_api_server/app/modules/transport/contracts_forecast.py:5](../../../api/wms_api_server/app/modules/transport/contracts_forecast.py#L5)

```python
__init__(self, code: str, message: str, status: int=409) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `super`, `super().__init__`

### project

[Исходник: api/wms_api_server/app/modules/transport/contracts_forecast.py:19](../../../api/wms_api_server/app/modules/transport/contracts_forecast.py#L19)

```python
project(self, ware: int, limit: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### project_load

[Исходник: api/wms_api_server/app/modules/transport/contracts_forecast.py:20](../../../api/wms_api_server/app/modules/transport/contracts_forecast.py#L20)

```python
project_load(self, load_id: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### get

[Исходник: api/wms_api_server/app/modules/transport/contracts_forecast.py:21](../../../api/wms_api_server/app/modules/transport/contracts_forecast.py#L21)

```python
get(self, ware: int, query: ForecastQuery, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### operation_fact_service

[Исходник: api/wms_api_server/app/modules/transport/contracts_operation_fact.py:6](../../../api/wms_api_server/app/modules/transport/contracts_operation_fact.py#L6)

```python
operation_fact_service() -> OperationFactPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### write

[Исходник: api/wms_api_server/app/modules/transport/contracts_operation_fact.py:4](../../../api/wms_api_server/app/modules/transport/contracts_operation_fact.py#L4)

```python
write(self, operation: int, fields: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### transport_preflight_service

[Исходник: api/wms_api_server/app/modules/transport/contracts_preflight.py:19](../../../api/wms_api_server/app/modules/transport/contracts_preflight.py#L19)

```python
transport_preflight_service() -> TransportPreflightPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### delivery_windows

[Исходник: api/wms_api_server/app/modules/transport/contracts_preflight.py:7](../../../api/wms_api_server/app/modules/transport/contracts_preflight.py#L7)

```python
delivery_windows(self, trip: int, depot: str, max_age: int, zone: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### road_legs

[Исходник: api/wms_api_server/app/modules/transport/contracts_preflight.py:8](../../../api/wms_api_server/app/modules/transport/contracts_preflight.py#L8)

```python
road_legs(self, trip: int, depot: str, max_age: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### plan

[Исходник: api/wms_api_server/app/modules/transport/contracts_preflight.py:9](../../../api/wms_api_server/app/modules/transport/contracts_preflight.py#L9)

```python
plan(self, plan: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### trip

[Исходник: api/wms_api_server/app/modules/transport/contracts_preflight.py:10](../../../api/wms_api_server/app/modules/transport/contracts_preflight.py#L10)

```python
trip(self, trip: int, additions: list[str], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### trip_time

[Исходник: api/wms_api_server/app/modules/transport/contracts_preflight.py:11](../../../api/wms_api_server/app/modules/transport/contracts_preflight.py#L11)

```python
trip_time(self, trip: int, zone: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### time_context

[Исходник: api/wms_api_server/app/modules/transport/contracts_preflight.py:12](../../../api/wms_api_server/app/modules/transport/contracts_preflight.py#L12)

```python
time_context(self, trip: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### approve_time

[Исходник: api/wms_api_server/app/modules/transport/contracts_preflight.py:13](../../../api/wms_api_server/app/modules/transport/contracts_preflight.py#L13)

```python
approve_time(self, operation: str, body: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### coordination

[Исходник: api/wms_api_server/app/modules/transport/contracts_preflight.py:14](../../../api/wms_api_server/app/modules/transport/contracts_preflight.py#L14)

```python
coordination(self, trip: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### route_context

[Исходник: api/wms_api_server/app/modules/transport/contracts_preflight.py:15](../../../api/wms_api_server/app/modules/transport/contracts_preflight.py#L15)

```python
route_context(self, trip: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### apply_route_input

[Исходник: api/wms_api_server/app/modules/transport/contracts_preflight.py:16](../../../api/wms_api_server/app/modules/transport/contracts_preflight.py#L16)

```python
apply_route_input(self, operation: str, body: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### st_deferral_service

[Исходник: api/wms_api_server/app/modules/transport/contracts_st_deferral.py:10](../../../api/wms_api_server/app/modules/transport/contracts_st_deferral.py#L10)

```python
st_deferral_service() -> StDeferralPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### candidates

[Исходник: api/wms_api_server/app/modules/transport/contracts_st_deferral.py:5](../../../api/wms_api_server/app/modules/transport/contracts_st_deferral.py#L5)

```python
candidates(self, st: str, actor: str, start: date | None, end: date | None, district: str | None, store: str | None, after_date: datetime | None, after_id: int, limit: int, purpose: str='DEFER') -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### history

[Исходник: api/wms_api_server/app/modules/transport/contracts_st_deferral.py:6](../../../api/wms_api_server/app/modules/transport/contracts_st_deferral.py#L6)

```python
history(self, st: str, after: int, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### context

[Исходник: api/wms_api_server/app/modules/transport/contracts_st_deferral.py:7](../../../api/wms_api_server/app/modules/transport/contracts_st_deferral.py#L7)

```python
context(self, st: str, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### defer

[Исходник: api/wms_api_server/app/modules/transport/contracts_st_deferral.py:8](../../../api/wms_api_server/app/modules/transport/contracts_st_deferral.py#L8)

```python
defer(self, operation: str, body: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### vehicle_profile_service

[Исходник: api/wms_api_server/app/modules/transport/contracts_vehicle_profile.py:13](../../../api/wms_api_server/app/modules/transport/contracts_vehicle_profile.py#L13)

```python
vehicle_profile_service() -> VehicleProfilePort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### __init__

[Исходник: api/wms_api_server/app/modules/transport/contracts_vehicle_profile.py:4](../../../api/wms_api_server/app/modules/transport/contracts_vehicle_profile.py#L4)

```python
__init__(self, code: str, message: str, status: int=409) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `super`, `super().__init__`

### configure

[Исходник: api/wms_api_server/app/modules/transport/contracts_vehicle_profile.py:9](../../../api/wms_api_server/app/modules/transport/contracts_vehicle_profile.py#L9)

```python
configure(self, body: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### tare_types

[Исходник: api/wms_api_server/app/modules/transport/contracts_vehicle_profile.py:10](../../../api/wms_api_server/app/modules/transport/contracts_vehicle_profile.py#L10)

```python
tare_types(self, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### read

[Исходник: api/wms_api_server/app/modules/transport/contracts_vehicle_profile.py:11](../../../api/wms_api_server/app/modules/transport/contracts_vehicle_profile.py#L11)

```python
read(self, vehicle: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### planned_day_drive

[Исходник: api/wms_api_server/app/modules/transport/domain/driver_day.py:8](../../../api/wms_api_server/app/modules/transport/domain/driver_day.py#L8)

```python
planned_day_drive(operations: list[dict[str, Any]], start_at: str, end_at: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(min(end, finish) - max(start, begin)).total_seconds`, `Decimal`, `datetime.fromisoformat`, `max`, `min`, `str`, `unknown.append`

### planned_day_continuity

[Исходник: api/wms_api_server/app/modules/transport/domain/driver_day.py:31](../../../api/wms_api_server/app/modules/transport/domain/driver_day.py#L31)

```python
planned_day_continuity(operations: list[dict[str, Any]], start_at: str, end_at: str) -> dict[str, Any]
```

Continue across trip boundaries; midnight and other work are not rest.

Вызывает: `chain.append`, `chain.sort`, `datetime.fromisoformat`, `datetime.fromisoformat(op['plan_start_at']).timestamp`, `evaluate_driver_rest`, `intersecting.add`, `item.get`, `min`, `min(end, finish).isoformat`, `seen.add`, `set`

### evaluate_driver_rest

[Исходник: api/wms_api_server/app/modules/transport/domain/driver_rest.py:12](../../../api/wms_api_server/app/modules/transport/domain/driver_rest.py#L12)

```python
evaluate_driver_rest(operations: list[dict[str, Any]]) -> dict[str, Any]
```

Only explicit REST resets continuity; work and unknown gaps do not.

Вызывает: `(end - start).total_seconds`, `Decimal`, `datetime.fromisoformat`, `str`, `unknown.append`, `violations.append`

### history_window

[Исходник: api/wms_api_server/app/modules/transport/domain/forecast_quantity.py:6](../../../api/wms_api_server/app/modules/transport/domain/forecast_quantity.py#L6)

```python
history_window(now: datetime, days: int, current: bool) -> tuple[datetime, datetime, Decimal]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `localcontext`, `now.astimezone`, `now.replace`, `timedelta`

### forecast_quantity

[Исходник: api/wms_api_server/app/modules/transport/domain/forecast_quantity.py:17](../../../api/wms_api_server/app/modules/transport/domain/forecast_quantity.py#L17)

```python
forecast_quantity(series: dict[str, Any], exposure: Decimal, horizon: int, minimum: int, complete: bool) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(rate * Decimal(horizon)).quantize`, `Decimal`, `format`, `int`, `localcontext`, `rate.quantize`

### __init__

[Исходник: api/wms_api_server/app/modules/transport/domain/plan_error.py:2](../../../api/wms_api_server/app/modules/transport/domain/plan_error.py#L2)

```python
__init__(self, code: str, message: str, status: int=409) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `super`, `super().__init__`

### plan_routes

[Исходник: api/wms_api_server/app/modules/transport/domain/preflight_routes.py:6](../../../api/wms_api_server/app/modules/transport/domain/preflight_routes.py#L6)

```python
plan_routes(document: dict[str, Any]) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TransportPlanError`, `document.get`, `isinstance`, `len`, `number.strip`, `route.get`, `seen.add`, `set`, `type`, `vehicles.add`

### ordered_stops

[Исходник: api/wms_api_server/app/modules/transport/domain/road_legs.py:4](../../../api/wms_api_server/app/modules/transport/domain/road_legs.py#L4)

```python
ordered_stops(members: list[dict]) -> tuple[list[str], list[str]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `issues.append`, `len`, `m.get`, `min`, `n.is_finite`, `n.to_integral_value`, `set`, `sorted`, `str`, `values.get`, `values.values`

### summarise_legs

[Исходник: api/wms_api_server/app/modules/transport/domain/road_legs.py:18](../../../api/wms_api_server/app/modules/transport/domain/road_legs.py#L18)

```python
summarise_legs(depot: str, stops: list[str], costs: dict, issues: list[str]) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `back.to_integral_value`, `bool`, `costs.get`, `enumerate`, `int`, `legs.append`, `len`, `outbound.to_integral_value`, `str`, `zip`

### number

[Исходник: api/wms_api_server/app/modules/transport/domain/road_matrix.py:5](../../../api/wms_api_server/app/modules/transport/domain/road_matrix.py#L5)

```python
number(value: Any, maximum: int) -> float
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `ValueError`, `d.is_finite`, `float`, `isinstance`, `str`

### matrix

[Исходник: api/wms_api_server/app/modules/transport/domain/road_matrix.py:13](../../../api/wms_api_server/app/modules/transport/domain/road_matrix.py#L13)

```python
matrix(values: Any, size: int, maximum: int) -> list[list[float]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `isinstance`, `len`, `number`, `result.append`

### osrm_costs

[Исходник: api/wms_api_server/app/modules/transport/domain/road_matrix.py:22](../../../api/wms_api_server/app/modules/transport/domain/road_matrix.py#L22)

```python
osrm_costs(data: dict, size: int) -> tuple[list[list[float]], list[list[float]]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(Decimal(str(v)) / Decimal(60)).quantize`, `Decimal`, `ValueError`, `data.get`, `float`, `matrix`, `round`, `str`

### valhalla_costs

[Исходник: api/wms_api_server/app/modules/transport/domain/road_matrix.py:31](../../../api/wms_api_server/app/modules/transport/domain/road_matrix.py#L31)

```python
valhalla_costs(data: dict, size: int) -> tuple[list[list[float]], list[list[float]]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(Decimal(str(v)) / 60).quantize`, `Decimal`, `ValueError`, `cell.get`, `d.append`, `data.get`, `distances.append`, `enumerate`, `float`, `isinstance`, `len`, `number`, `seconds.append`, `str`, `t.append`

### validate_points

[Исходник: api/wms_api_server/app/modules/transport/domain/road_matrix.py:45](../../../api/wms_api_server/app/modules/transport/domain/road_matrix.py#L45)

```python
validate_points(points: list[tuple[float, float]]) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `any`, `isinstance`, `len`

### temperature_preflight

[Исходник: api/wms_api_server/app/modules/transport/domain/temperature_preflight.py:4](../../../api/wms_api_server/app/modules/transport/domain/temperature_preflight.py#L4)

```python
temperature_preflight(requirements: dict, vehicle_profile: dict | None) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(vehicle_profile.get('profile') or {}).get`, `Decimal`, `ValueError`, `any`, `isinstance`, `max`, `min`, `requirements.get`, `result.update`, `str`, `vehicle_profile.get`, `x.is_finite`

### normalize_transport_type

[Исходник: api/wms_api_server/app/modules/transport/domain/transport_type.py:4](../../../api/wms_api_server/app/modules/transport/domain/transport_type.py#L4)

```python
normalize_transport_type(value: str | None) -> str | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `aliases.get`, `normalized.lower`, `value.strip`

### distance_costs

[Исходник: api/wms_api_server/app/modules/transport/domain/vrp_distance_costs.py:5](../../../api/wms_api_server/app/modules/transport/domain/vrp_distance_costs.py#L5)

```python
distance_costs(orders: list[Any], cache: dict | None, origin: dict | None, haversine: Callable) -> tuple[list[list[int]], str | None]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(cache or {}).get`, `float`, `haversine`, `int`, `km`, `len`, `math.isfinite`, `origin.get`, `range`, `sum`

### km

[Исходник: api/wms_api_server/app/modules/transport/domain/vrp_distance_costs.py:11](../../../api/wms_api_server/app/modules/transport/domain/vrp_distance_costs.py#L11)

```python
km(i: int, j: int) -> float
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(cache or {}).get`, `haversine`, `math.isfinite`

### utilization_pct

[Исходник: api/wms_api_server/app/modules/transport/domain/vrp_models.py:48](../../../api/wms_api_server/app/modules/transport/domain/vrp_models.py#L48)

```python
utilization_pct(self) -> float
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `round`

### schedule_evidence

[Исходник: api/wms_api_server/app/modules/transport/domain/vrp_presentation.py:13](../../../api/wms_api_server/app/modules/transport/domain/vrp_presentation.py#L13)

```python
schedule_evidence(route: VrpRoute) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### route_payload

[Исходник: api/wms_api_server/app/modules/transport/domain/vrp_presentation.py:24](../../../api/wms_api_server/app/modules/transport/domain/vrp_presentation.py#L24)

```python
route_payload(route: VrpRoute) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `schedule_evidence`

### route_response

[Исходник: api/wms_api_server/app/modules/transport/domain/vrp_presentation.py:34](../../../api/wms_api_server/app/modules/transport/domain/vrp_presentation.py#L34)

```python
route_response(route: VrpRoute) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `int`, `schedule_evidence`, `stops.append`, `sum`, `timing.get`, `timings.get`

### planner_constraint_evidence

[Исходник: api/wms_api_server/app/modules/transport/domain/vrp_presentation.py:67](../../../api/wms_api_server/app/modules/transport/domain/vrp_presentation.py#L67)

```python
planner_constraint_evidence(routes: list[VrpRoute], fallback_windows: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `all`, `bool`

### travel_times

[Исходник: api/wms_api_server/app/modules/transport/domain/vrp_travel_time.py:5](../../../api/wms_api_server/app/modules/transport/domain/vrp_travel_time.py#L5)

```python
travel_times(addresses: list[str], distances: list[list[int]], depot: int, cache: dict[tuple[str, str], float] | None, depot_address: str | None=None) -> tuple[list[list[int]], list[list[str]]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(cache or {}).get`, `basis.append`, `br.append`, `len`, `math.ceil`, `math.isfinite`, `range`, `times.append`, `tr.append`

### planned_operations

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/approved_schedule.py:5](../../../api/wms_api_server/app/modules/transport/infrastructure/approved_schedule.py#L5)

```python
planned_operations(context: dict[str, Any], original: list[dict[str, Any]]) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `any`, `approval.get`, `approval.get('route_schedule', {}).get`, `context.get`, `enumerate`, `op.get`

### assignment_picker_source

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/assignment_picker_source.py:8](../../../api/wms_api_server/app/modules/transport/infrastructure/assignment_picker_source.py#L8)

```python
assignment_picker_source(cur: Any, st: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TransportPlanError`, `any`, `cur.execute`, `current_sources`, `iter`, `json.dumps`, `json.dumps({'sources': rows, 'members': members}, sort_keys=True, default=str).encode`, `len`, `max`, `next`, `r[2].isoformat`, `sha256`, `sha256(json.dumps({'sources': rows, 'members': members}, sort_keys=True, default=str).encode()).hexdigest`

### _window

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/available_sts_page.py:3](../../../api/wms_api_server/app/modules/transport/infrastructure/available_sts_page.py#L3)

```python
_window(sql: str) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### page_available_sts

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/available_sts_page.py:7](../../../api/wms_api_server/app/modules/transport/infrastructure/available_sts_page.py#L7)

```python
page_available_sts(sql: str, where_sql: str, has_having: bool, page: int | None, size: int | None, params: dict[str, Any]) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_window`, `params.update`, `sql.replace`

### available_sts_query

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/available_sts_query.py:16](../../../api/wms_api_server/app/modules/transport/infrastructure/available_sts_query.py#L16)

```python
available_sts_query(stdate: date | None=None, date_to: date | None=None, unassigned_only: bool=True, ware_id: int | None=None, ware_ids: list[int] | None=None, addr_mask: str | None=None, st_mask: str | None=None, st_mask_exclude: bool=False, transport_type: str | None=None, assembled_only: bool=False, not_assembled_only: bool=False, max_weight_kg: float | None=None, max_volume_m3: float | None=None, articul: str | None=None, raion: str | None=None, page: int | None=None, page_size: int | None=None) -> tuple[str, dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' AND '.join`, `', '.join`, `QUERY.format`, `bool`, `conditions.append`, `enumerate`, `having.append`, `len`, `page_available_sts`, `range`, `timedelta`

### create_existing_cluster

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/cluster_creation.py:11](../../../api/wms_api_server/app/modules/transport/infrastructure/cluster_creation.py#L11)

```python
create_existing_cluster(gateway: Any, district: str, day: date, transport_type: str, fields: dict[str, Any], numbers: list[str], actor: str, operation_id: str, warehouse_ids: list[int] | None=None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TransportPlanError`, `body.encode`, `cursor.callproc`, `cursor.var`, `day.isoformat`, `fields.get`, `gateway.transaction`, `json.dumps`, `len`, `read_oracle_json`, `result.getvalue`, `set`, `sorted`, `trip_error`

### coordination

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/coordination_preflight.py:13](../../../api/wms_api_server/app/modules/transport/infrastructure/coordination_preflight.py#L13)

```python
coordination(gateway: Any, trip: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TransportPlanError`, `cur.execute`, `gateway.transaction`, `read_coordination`, `str`

### read_coordination

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/coordination_preflight.py:22](../../../api/wms_api_server/app/modules/transport/infrastructure/coordination_preflight.py#L22)

```python
read_coordination(cur: Any, trip: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `any`, `blockers.append`, `blockers.extend`, `datetime.fromisoformat`, `dispatcher`, `int`, `len`, `plan.get`, `read_delivery_windows`, `read_loading_status`, `read_optional_interwarehouse_incoming_snapshot`, `read_time_context`, `read_trip_time`, `sum`, `x.get`

### delivery_window_preview

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/delivery_window_preview.py:9](../../../api/wms_api_server/app/modules/transport/infrastructure/delivery_window_preview.py#L9)

```python
delivery_window_preview(gateway: Any, trip: int, depot: str, max_age: int, zone: str, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.execute`, `gateway.transaction`, `read_delivery_windows`, `trip_error`

### read_delivery_windows

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/delivery_window_preview.py:16](../../../api/wms_api_server/app/modules/transport/infrastructure/delivery_window_preview.py#L16)

```python
read_delivery_windows(cur: Any, trip: int, depot: str, max_age: int, zone: str, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TransportPlanError`, `context['source'].get`, `cur.callproc`, `cur.var`, `json.dumps`, `out.getvalue`, `profile.get`, `profiles.get`, `read_oracle_json`, `result.get`, `result.update`, `stop.get`, `wire.setvalue`

### matrix_merge_statements

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/distance_matrix_rows.py:4](../../../api/wms_api_server/app/modules/transport/infrastructure/distance_matrix_rows.py#L4)

```python
matrix_merge_statements(addrs: list[dict], matrix: list[list[float]], durations: list[list[float]] | None, fresh_pair_keys: set, source: str) -> tuple[list, int, int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `len`, `range`, `round`, `statements.append`, `str`

### __init__

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/driver_binding.py:8](../../../api/wms_api_server/app/modules/transport/infrastructure/driver_binding.py#L8)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### configure

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/driver_binding.py:11](../../../api/wms_api_server/app/modules/transport/infrastructure/driver_binding.py#L11)

```python
configure(self, driver_id: int, user_id: str, active: bool, expected_version: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TransportLoadingError`, `cursor.execute`, `cursor.fetchall`, `getattr`, `int`, `stock_configuration_transaction`, `str`, `str(exc.args[0]).split`

### get

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/driver_binding.py:30](../../../api/wms_api_server/app/modules/transport/infrastructure/driver_binding.py#L30)

```python
get(self, driver_id: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### day_window

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/driver_day.py:11](../../../api/wms_api_server/app/modules/transport/infrastructure/driver_day.py#L11)

```python
day_window(cur: Any, local_day: date, zone: str) -> tuple[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.execute`, `cur.fetchone`, `local_day.isoformat`

### read_driver_days

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/driver_day.py:19](../../../api/wms_api_server/app/modules/transport/infrastructure/driver_day.py#L19)

```python
read_driver_days(cur: Any, trip: int, actor: str, zone: str, driver: int | None, current_ops: list[dict[str, Any]]) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TransportPlanError`, `all_ops.extend`, `any`, `base['days'].append`, `cur.execute`, `cur.fetchall`, `datetime.fromisoformat`, `day_window`, `ids.append`, `len`, `local_day.isoformat`, `max`, `max((datetime.fromisoformat(op['plan_end_at']) for op in spans)).date`, `min`, `min((datetime.fromisoformat(op['plan_start_at']) for op in spans)).date`, `original_operations`, `planned_day_continuity`, `planned_day_drive`, `planned_operations`, `range`, `read_time_context`, `sources.append`, `timedelta`, `trip_scope`, `unresolved.append`

### rows

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/driver_workspace.py:9](../../../api/wms_api_server/app/modules/transport/infrastructure/driver_workspace.py#L9)

```python
rows(cur: Any, maximum: int) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TransportPlanError`, `cur.fetchall`, `dict`, `len`, `x[0].lower`, `zip`

### __init__

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/driver_workspace.py:17](../../../api/wms_api_server/app/modules/transport/infrastructure/driver_workspace.py#L17)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### trips

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/driver_workspace.py:20](../../../api/wms_api_server/app/modules/transport/infrastructure/driver_workspace.py#L20)

```python
trips(self, driver: int, day: date, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.callproc`, `cur.execute`, `rows`, `self.gateway.transaction`, `trip_error`

### details

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/driver_workspace.py:38](../../../api/wms_api_server/app/modules/transport/infrastructure/driver_workspace.py#L38)

```python
details(self, driver: int, trip: int, kind: str, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TransportPlanError`, `ValueError`, `cur.callproc`, `cur.execute`, `cur.fetchone`, `rows`, `self.gateway.transaction`, `trip_error`

### mark

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/driver_workspace.py:65](../../../api/wms_api_server/app/modules/transport/infrastructure/driver_workspace.py#L65)

```python
mark(self, driver: int, operation: int, action: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TransportPlanError`, `cur.callproc`, `cur.var`, `getattr`, `read_oracle_json`, `result.getvalue`, `self.gateway.transaction`, `trip_error`

### require_forecast_warehouse

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/forecast_access.py:4](../../../api/wms_api_server/app/modules/transport/infrastructure/forecast_access.py#L4)

```python
require_forecast_warehouse(cur: Any, ware: int, actor: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `WarehouseForecastError`, `cur.execute`, `cur.fetchone`

### forecast_rows

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/forecast_access.py:9](../../../api/wms_api_server/app/modules/transport/infrastructure/forecast_access.py#L9)

```python
forecast_rows(cur: Any) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `column[0].lower`, `cur.fetchall`, `dict`, `zip`

### __init__

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/forecast_projection.py:9](../../../api/wms_api_server/app/modules/transport/infrastructure/forecast_projection.py#L9)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### project_load

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/forecast_projection.py:12](../../../api/wms_api_server/app/modules/transport/infrastructure/forecast_projection.py#L12)

```python
project_load(self, load_id: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `WarehouseForecastError`, `cur.callproc`, `cur.var`, `getattr`, `read_oracle_json`, `result.getvalue`, `self.gateway.transaction`, `str`, `str(exc.args[0]).split`

### project

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/forecast_projection.py:26](../../../api/wms_api_server/app/modules/transport/infrastructure/forecast_projection.py#L26)

```python
project(self, ware: int, limit: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.execute`, `cur.fetchall`, `errors.append`, `len`, `max`, `min`, `require_forecast_warehouse`, `results.append`, `self.gateway.transaction`, `self.project_load`, `str`

### gantt_rows

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/gantt_rows.py:8](../../../api/wms_api_server/app/modules/transport/infrastructure/gantt_rows.py#L8)

```python
gantt_rows(gateway: Any, gantt_date: date) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `datetime.combine`, `gateway.fetch_all`, `timedelta`

### list_address_geofences

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/geofences.py:5](../../../api/wms_api_server/app/modules/transport/infrastructure/geofences.py#L5)

```python
list_address_geofences(gateway: Any, addr_mask: str | None=None) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `float`, `gateway.fetch_all`, `int`

### update_address_geofence

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/geofences.py:23](../../../api/wms_api_server/app/modules/transport/infrastructure/geofences.py#L23)

```python
update_address_geofence(gateway: Any, address: str, radius: int, actor: str) -> dict | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.callproc`, `cur.execute`, `cur.fetchone`, `gateway.transaction`

### ingest_gps

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/gps_ingestion.py:10](../../../api/wms_api_server/app/modules/transport/infrastructure/gps_ingestion.py#L10)

```python
ingest_gps(gateway: Any, vehicle_id: int, lat: float, lon: float, speed: float, timestamp: datetime | None) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `GpsVehicleMissing`, `cur.execute`, `cur.fetchone`, `gateway.transaction`, `observed_at.isoformat`

### __init__

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/loading.py:11](../../../api/wms_api_server/app/modules/transport/infrastructure/loading.py#L11)

```python
__init__(self, gateway: Any, post: Callable[[str, str, dict[str, Any], dict[str, Any], str], dict[str, Any]]) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### status

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/loading.py:15](../../../api/wms_api_server/app/modules/transport/infrastructure/loading.py#L15)

```python
status(self, task_id: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `loading_status`

### load

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/loading.py:19](../../../api/wms_api_server/app/modules/transport/infrastructure/loading.py#L19)

```python
load(self, operation_id: str, identifier: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.post`

### unload

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/loading.py:22](../../../api/wms_api_server/app/modules/transport/infrastructure/loading.py#L22)

```python
unload(self, operation_id: str, load_operation_id: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.post`

### depart

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/loading.py:25](../../../api/wms_api_server/app/modules/transport/infrastructure/loading.py#L25)

```python
depart(self, operation_id: str, task_id: int, actor: str, temperature_confirmation: dict[str, Any] | None=None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.post`

### preview_single

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/loading.py:30](../../../api/wms_api_server/app/modules/transport/infrastructure/loading.py#L30)

```python
preview_single(self, shipment_identifier: str, actor: str | None=None) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TransportLoadingError`, `abs`, `getattr`, `q.execute`, `q.fetchone`, `read_oracle_json`, `self.gateway.transaction`, `str`, `str(exc.args[0]).split`

### load_single

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/loading.py:45](../../../api/wms_api_server/app/modules/transport/infrastructure/loading.py#L45)

```python
load_single(self, operation_id: str, shipment_identifier: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.post`

### preview_reconciliation

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/loading.py:48](../../../api/wms_api_server/app/modules/transport/infrastructure/loading.py#L48)

```python
preview_reconciliation(self, shipping_operation_id: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TransportLoadingError`, `abs`, `getattr`, `isinstance`, `json.loads`, `self.gateway.fetch_all`, `str`, `str(exc.args[0]).split`

### reconcile

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/loading.py:59](../../../api/wms_api_server/app/modules/transport/infrastructure/loading.py#L59)

```python
reconcile(self, operation_id: str, shipping_operation_id: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.post`

### loading_floor_read

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/loading_floor_read.py:5](../../../api/wms_api_server/app/modules/transport/infrastructure/loading_floor_read.py#L5)

```python
loading_floor_read(cur: Any, load_ids: list[str], trip: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `','.join`, `ValueError`, `cur.execute`, `cur.fetchone`, `departure.get`, `enumerate`, `len`, `read_oracle_json`, `str`

### loading_status

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/loading_status.py:7](../../../api/wms_api_server/app/modules/transport/infrastructure/loading_status.py#L7)

```python
loading_status(gateway: Any, trip: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.execute`, `gateway.transaction`, `read_loading_status`

### read_loading_status

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/loading_status.py:12](../../../api/wms_api_server/app/modules/transport/infrastructure/loading_status.py#L12)

```python
read_loading_status(cur: Any, trip: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TransportLoadingError`, `bool`, `cur.execute`, `cur.fetchall`, `cur.fetchone`, `dict`, `len`, `loading_floor_read`, `loading_thermal_read`, `physically_loaded`, `str`, `str(user[1] or '').strip`, `str(user[1] or '').strip().upper`, `sum`, `zip`

### physically_loaded

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/loading_status.py:61](../../../api/wms_api_server/app/modules/transport/infrastructure/loading_status.py#L61)

```python
physically_loaded(row: dict[str, Any]) -> bool
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### loading_thermal_read

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/loading_thermal_read.py:6](../../../api/wms_api_server/app/modules/transport/infrastructure/loading_thermal_read.py#L6)

```python
loading_thermal_read(cur: Any, plate: str | None, load_ids: list[str], trip: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `','.join`, `ValueError`, `cur.callfunc`, `cur.execute`, `cur.fetchall`, `cur.fetchone`, `departed.get`, `enumerate`, `len`, `read_oracle_json`, `str`

### update_existing_operation_fact

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/operation_fact.py:8](../../../api/wms_api_server/app/modules/transport/infrastructure/operation_fact.py#L8)

```python
update_existing_operation_fact(gateway: Any, operation: int, fields: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.callproc`, `cur.var`, `gateway.transaction`, `json.dumps`, `read_oracle_json`, `result.getvalue`, `trip_error`

### __init__

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/operation_fact_service.py:8](../../../api/wms_api_server/app/modules/transport/infrastructure/operation_fact_service.py#L8)

```python
__init__(self, gateway: OracleGateway, on_success: Callable[[], None]) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### write

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/operation_fact_service.py:10](../../../api/wms_api_server/app/modules/transport/infrastructure/operation_fact_service.py#L10)

```python
write(self, operation: int, fields: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.on_success`, `update_existing_operation_fact`

### generate_existing_operations

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/operation_plan.py:7](../../../api/wms_api_server/app/modules/transport/infrastructure/operation_plan.py#L7)

```python
generate_existing_operations(gateway: Any, trip: int, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`, `cur.callproc`, `cur.var`, `gateway.transaction`, `isinstance`, `read_oracle_json`, `result.getvalue`, `trip_error`

### apply_existing_plan

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/plan_application.py:9](../../../api/wms_api_server/app/modules/transport/infrastructure/plan_application.py#L9)

```python
apply_existing_plan(gateway: Any, plan: int, shipment_day: date, dock: str | None, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TransportPlanError`, `cur.callproc`, `cur.var`, `gateway.transaction`, `getattr`, `read_oracle_json`, `result.getvalue`, `str`, `str(exc.args[0]).split`

### assign_validated_sts

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/plan_application.py:21](../../../api/wms_api_server/app/modules/transport/infrastructure/plan_application.py#L21)

```python
assign_validated_sts(gateway: Any, trip: int, numbers: list[str], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TransportPlanError`, `cur.callproc`, `cur.var`, `gateway.transaction`, `getattr`, `json.dumps`, `len`, `read_oracle_json`, `result.getvalue`, `set`, `sorted`, `str`, `str(exc.args[0]).split`

### native_check

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/plan_preflight.py:16](../../../api/wms_api_server/app/modules/transport/infrastructure/plan_preflight.py#L16)

```python
native_check(cur: Any, vehicle: int | None, numbers: list[str], complete: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.callproc`, `cur.var`, `getattr`, `json.dumps`, `message.partition`, `message.partition(':')[2].strip`, `read_oracle_json`, `result.getvalue`, `str`, `str(exc.args[0]).split`

### current_sources

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/plan_preflight.py:32](../../../api/wms_api_server/app/modules/transport/infrastructure/plan_preflight.py#L32)

```python
current_sources(cur: Any, numbers: list[str], actor: str, trip: int | None) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `','.join`, `TransportPlanError`, `cur.callproc`, `cur.execute`, `cur.fetchall`, `dict`, `enumerate`, `getattr`, `len`, `range`, `rows.extend`, `rows.sort`, `sorted`, `zip`

### route_result

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/plan_preflight.py:73](../../../api/wms_api_server/app/modules/transport/infrastructure/plan_preflight.py#L73)

```python
route_result(cur: Any, route: dict[str, Any], rows: list[dict[str, Any]], trip: int | None, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TransportPlanError`, `blockers.append`, `cur.callfunc`, `cur.execute`, `cur.fetchone`, `int`, `native_check`, `read_oracle_json`, `read_shipping_temperature_requirements`, `route.get`, `str`, `temperature_preflight`

### __init__

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/plan_preflight.py:112](../../../api/wms_api_server/app/modules/transport/infrastructure/plan_preflight.py#L112)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### trip_time

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/plan_preflight.py:115](../../../api/wms_api_server/app/modules/transport/infrastructure/plan_preflight.py#L115)

```python
trip_time(self, trip: int, zone: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `trip_time_preview`

### time_context

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/plan_preflight.py:119](../../../api/wms_api_server/app/modules/transport/infrastructure/plan_preflight.py#L119)

```python
time_context(self, trip: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `time_context`

### coordination

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/plan_preflight.py:123](../../../api/wms_api_server/app/modules/transport/infrastructure/plan_preflight.py#L123)

```python
coordination(self, trip: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `coordination`

### approve_time

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/plan_preflight.py:127](../../../api/wms_api_server/app/modules/transport/infrastructure/plan_preflight.py#L127)

```python
approve_time(self, operation: str, body: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `approve_time`

### route_context

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/plan_preflight.py:131](../../../api/wms_api_server/app/modules/transport/infrastructure/plan_preflight.py#L131)

```python
route_context(self, trip: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `route_context`

### apply_route_input

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/plan_preflight.py:135](../../../api/wms_api_server/app/modules/transport/infrastructure/plan_preflight.py#L135)

```python
apply_route_input(self, operation: str, body: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `apply_route_input`

### plan

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/plan_preflight.py:139](../../../api/wms_api_server/app/modules/transport/infrastructure/plan_preflight.py#L139)

```python
plan(self, plan: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TransportPlanError`, `any`, `cur.execute`, `cur.fetchone`, `current_sources`, `dispatcher`, `isinstance`, `json.loads`, `len`, `plan_routes`, `raw.encode`, `route_result`, `row[0].read`, `self.gateway.transaction`, `sha256`, `sha256(raw.encode()).hexdigest`

### trip

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/plan_preflight.py:164](../../../api/wms_api_server/app/modules/transport/infrastructure/plan_preflight.py#L164)

```python
trip(self, trip: int, additions: list[str], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TransportPlanError`, `cur.execute`, `cur.fetchall`, `cur.fetchone`, `current_sources`, `dispatcher`, `len`, `result['source_blockers'].append`, `route_result`, `self.gateway.transaction`, `set`, `sorted`

### delivery_windows

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/plan_preflight.py:185](../../../api/wms_api_server/app/modules/transport/infrastructure/plan_preflight.py#L185)

```python
delivery_windows(self, trip: int, depot: str, max_age: int, zone: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `delivery_window_preview`

### road_legs

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/plan_preflight.py:189](../../../api/wms_api_server/app/modules/transport/infrastructure/plan_preflight.py#L189)

```python
road_legs(self, trip: int, depot: str, max_age: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `road_leg_estimate`

### dispatcher

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/preflight_scope.py:4](../../../api/wms_api_server/app/modules/transport/infrastructure/preflight_scope.py#L4)

```python
dispatcher(cur: Any, actor: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TransportPlanError`, `cur.execute`, `cur.fetchone`

### read_cost_cache

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/profile_duration_cache.py:7](../../../api/wms_api_server/app/modules/transport/infrastructure/profile_duration_cache.py#L7)

```python
read_cost_cache(cur: Any, addresses: list[str]) -> tuple[dict, dict, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `cur.execute`, `cur.fetchall`, `cur.var`, `float`, `iter`, `json.dumps`, `len`, `next`, `payload.setvalue`, `set`, `sorted`, `sources.add`, `str`

### profile_duration_cache

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/profile_duration_cache.py:25](../../../api/wms_api_server/app/modules/transport/infrastructure/profile_duration_cache.py#L25)

```python
profile_duration_cache(gateway: Any, addresses: list[str]) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `planner_cost_cache`

### planner_cost_cache

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/profile_duration_cache.py:28](../../../api/wms_api_server/app/modules/transport/infrastructure/profile_duration_cache.py#L28)

```python
planner_cost_cache(gateway: Any, addresses: list[str]) -> tuple[dict, dict, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.execute`, `gateway.transaction`, `read_cost_cache`

### planner_inputs

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/profile_duration_cache.py:32](../../../api/wms_api_server/app/modules/transport/infrastructure/profile_duration_cache.py#L32)

```python
planner_inputs(gateway: Any, orders: list[Any]) -> tuple[dict, dict, str, dict | None]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.callproc`, `cur.execute`, `cur.var`, `gateway.transaction`, `iter`, `len`, `next`, `out.getvalue`, `read_cost_cache`, `read_oracle_json`

### road_leg_estimate

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/road_leg_estimate.py:10](../../../api/wms_api_server/app/modules/transport/infrastructure/road_leg_estimate.py#L10)

```python
road_leg_estimate(gateway: Any, trip: int, depot: str, max_age: int, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.execute`, `gateway.transaction`, `read_snapshot`, `trip_error`

### read_snapshot

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/road_leg_estimate.py:17](../../../api/wms_api_server/app/modules/transport/infrastructure/road_leg_estimate.py#L17)

```python
read_snapshot(cur: Any, trip: int, depot: str, max_age: int, actor: str, context: dict | None=None) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `context['source'].get`, `cur.callproc`, `cur.execute`, `cur.fetchall`, `cur.var`, `issues.append`, `json.dumps`, `json.dumps(result, sort_keys=True, separators=(',', ':')).encode`, `len`, `list`, `ordered_stops`, `origins[0].get`, `out.getvalue`, `payload.setvalue`, `read_oracle_json`, `result.update`, `sha256`, `sha256(json.dumps(result, sort_keys=True, separators=(',', ':')).encode()).hexdigest`, `summarise_legs`, `zip`

### route_context

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/route_input.py:9](../../../api/wms_api_server/app/modules/transport/infrastructure/route_input.py#L9)

```python
route_context(gateway: Any, trip: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.callproc`, `cur.execute`, `cur.var`, `gateway.transaction`, `read_oracle_json`, `result.getvalue`, `trip_error`

### apply_route_input

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/route_input.py:20](../../../api/wms_api_server/app/modules/transport/infrastructure/route_input.py#L20)

```python
apply_route_input(gateway: Any, operation: str, body: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.callproc`, `cur.var`, `gateway.transaction`, `json.dumps`, `payload.setvalue`, `read_oracle_json`, `result.getvalue`, `trip_error`

### _lock_trip

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/st_assignment.py:6](../../../api/wms_api_server/app/modules/transport/infrastructure/st_assignment.py#L6)

```python
_lock_trip(cursor: oracledb.Cursor, task_id: int) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `cursor.execute`, `cursor.fetchone`

### _lock_members

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/st_assignment.py:15](../../../api/wms_api_server/app/modules/transport/infrastructure/st_assignment.py#L15)

```python
_lock_members(cursor: oracledb.Cursor, task_id: int, numbers: list[str], removing: bool) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `','.join`, `ValueError`, `cursor.execute`, `cursor.fetchall`, `cursor.fetchone`, `enumerate`, `len`, `set`, `str`

### _write_members

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/st_assignment.py:33](../../../api/wms_api_server/app/modules/transport/infrastructure/st_assignment.py#L33)

```python
_write_members(cursor: oracledb.Cursor, target: int, numbers: list[str]) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `cursor.callfunc`, `str`, `str(result or '').lower`, `str(result or '').lower().startswith`

### assign_sts

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/st_assignment.py:40](../../../api/wms_api_server/app/modules/transport/infrastructure/st_assignment.py#L40)

```python
assign_sts(gateway: OracleGateway, task_id: int, st_numbers: list[str], actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `assign_validated_sts`

### unassign_st

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/st_assignment.py:45](../../../api/wms_api_server/app/modules/transport/infrastructure/st_assignment.py#L45)

```python
unassign_st(gateway: OracleGateway, task_id: int, st_number: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_lock_members`, `_lock_trip`, `_write_members`, `cursor.callfunc`, `gateway.transaction`

### cancel_trip

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/st_assignment.py:52](../../../api/wms_api_server/app/modules/transport/infrastructure/st_assignment.py#L52)

```python
cancel_trip(gateway: OracleGateway, task_id: int, actor: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `_lock_members`, `_lock_trip`, `_write_members`, `any`, `cursor.execute`, `cursor.fetchall`, `cursor.fetchone`, `gateway.transaction`, `len`, `sorted`

### __init__

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/st_deferral.py:10](../../../api/wms_api_server/app/modules/transport/infrastructure/st_deferral.py#L10)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### candidates

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/st_deferral.py:11](../../../api/wms_api_server/app/modules/transport/infrastructure/st_deferral.py#L11)

```python
candidates(self, st: str, actor: str, start: date | None, end: date | None, district: str | None, store: str | None, after_date: datetime | None, after_id: int, limit: int, purpose: str='DEFER') -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `candidates`, `trip_error`

### context

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/st_deferral.py:18](../../../api/wms_api_server/app/modules/transport/infrastructure/st_deferral.py#L18)

```python
context(self, st: str, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.callproc`, `cur.execute`, `cur.var`, `out.getvalue`, `read_oracle_json`, `self.gateway.transaction`, `trip_error`

### defer

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/st_deferral.py:24](../../../api/wms_api_server/app/modules/transport/infrastructure/st_deferral.py#L24)

```python
defer(self, operation: str, body: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.callproc`, `cur.var`, `json.dumps`, `out.getvalue`, `payload.setvalue`, `read_oracle_json`, `self.gateway.transaction`, `trip_error`

### history

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/st_deferral.py:31](../../../api/wms_api_server/app/modules/transport/infrastructure/st_deferral.py#L31)

```python
history(self, st: str, after: int, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.callproc`, `cur.execute`, `cur.var`, `out.getvalue`, `read_oracle_json`, `self.gateway.transaction`, `trip_error`

### trip_time_preview

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/time_preflight.py:13](../../../api/wms_api_server/app/modules/transport/infrastructure/time_preflight.py#L13)

```python
trip_time_preview(gateway: Any, trip: int, zone: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TransportPlanError`, `cur.execute`, `gateway.transaction`, `read_trip_time`

### read_trip_time

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/time_preflight.py:21](../../../api/wms_api_server/app/modules/transport/infrastructure/time_preflight.py#L21)

```python
read_trip_time(cur: Any, trip: int, zone: str, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(datetime.fromisoformat(finish_at) - datetime.fromisoformat(start_at)).total_seconds`, `TransportPlanError`, `bool`, `conflicts.append`, `cur.execute`, `cur.fetchall`, `datetime.fromisoformat`, `evaluate_driver_rest`, `issues.append`, `len`, `max`, `min`, `original_operations`, `planned_operations`, `read_driver_days`, `read_time_context`, `trip_scope`, `valid.append`

### trip_scope

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/time_snapshot.py:5](../../../api/wms_api_server/app/modules/transport/infrastructure/time_snapshot.py#L5)

```python
trip_scope(cur: Any, trip: int, actor: str) -> tuple[Any, ...]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TransportPlanError`, `cur.callproc`, `cur.execute`, `cur.fetchall`, `cur.fetchone`, `dispatcher`, `getattr`, `len`

### original_operations

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/time_snapshot.py:33](../../../api/wms_api_server/app/modules/transport/infrastructure/time_snapshot.py#L33)

```python
original_operations(cur: Any, trip: int, zone: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TransportPlanError`, `cur.execute`, `cur.fetchall`, `dict`, `len`, `zip`

### trip_error

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/trip_edit.py:8](../../../api/wms_api_server/app/modules/transport/infrastructure/trip_edit.py#L8)

```python
trip_error(exc: oracledb.DatabaseError) -> TransportPlanError
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TransportPlanError`, `getattr`, `str`, `str(exc.args[0]).split`

### create_existing_trip

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/trip_edit.py:15](../../../api/wms_api_server/app/modules/transport/infrastructure/trip_edit.py#L15)

```python
create_existing_trip(gateway: Any, transport_type: str, day: date, actor: str) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.callproc`, `cur.var`, `gateway.transaction`, `int`, `result.getvalue`, `trip_error`

### update_existing_trip

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/trip_edit.py:23](../../../api/wms_api_server/app/modules/transport/infrastructure/trip_edit.py#L23)

```python
update_existing_trip(gateway: Any, trip: int, fields: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.callproc`, `cur.var`, `gateway.transaction`, `json.dumps`, `read_oracle_json`, `result.getvalue`, `trip_error`

### _window

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/trip_selector.py:8](../../../api/wms_api_server/app/modules/transport/infrastructure/trip_selector.py#L8)

```python
_window(context: dict, start: date | None, end: date | None) -> tuple[date, date, date]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TransportPlanError`, `context['source_trip'].get`, `date.fromisoformat`, `max`, `member.get`, `minimum.isoformat`, `timedelta`

### _headers

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/trip_selector.py:23](../../../api/wms_api_server/app/modules/transport/infrastructure/trip_selector.py#L23)

```python
_headers(cur: oracledb.Cursor, context: dict, start: date, end: date, district: str | None, store: str | None, after_date: datetime | None, after_id: int, limit: int) -> list
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `' and '.join`, `binds.update`, `conditions.append`, `cur.execute`, `cur.fetchall`, `stop.append`, `timedelta`

### _stops

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/trip_selector.py:51](../../../api/wms_api_server/app/modules/transport/infrastructure/trip_selector.py#L51)

```python
_stops(cur: oracledb.Cursor, ids: list[int]) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `','.join`, `TransportPlanError`, `cur.execute`, `enumerate`, `result.setdefault`, `set`, `values['districts'].add`, `values['stores'].add`

### candidates

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/trip_selector.py:69](../../../api/wms_api_server/app/modules/transport/infrastructure/trip_selector.py#L69)

```python
candidates(gateway: OracleGateway, st: str, actor: str, start: date | None, end: date | None, district: str | None, store: str | None, after_date: datetime | None, after_id: int, limit: int, purpose: str='DEFER') -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(district or '').strip`, `(store or '').strip`, `TransportPlanError`, `_headers`, `_stops`, `_window`, `assignment_picker_source`, `cur.callproc`, `cur.execute`, `cur.var`, `day.date`, `day.date().isoformat`, `day.isoformat`, `end.isoformat`, `gateway.transaction`, `len`, `minimum.isoformat`, `out.getvalue`, `read_oracle_json`, `rows.append`, `set`, `sorted`, `start.isoformat`, `stops.get`, `str`

### read_time_context

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/trip_time_approval.py:8](../../../api/wms_api_server/app/modules/transport/infrastructure/trip_time_approval.py#L8)

```python
read_time_context(cur: Any, trip: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.callproc`, `cur.var`, `read_oracle_json`, `result.getvalue`

### time_context

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/trip_time_approval.py:13](../../../api/wms_api_server/app/modules/transport/infrastructure/trip_time_approval.py#L13)

```python
time_context(gateway: Any, trip: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.execute`, `gateway.transaction`, `read_time_context`, `trip_error`

### approve_time

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/trip_time_approval.py:21](../../../api/wms_api_server/app/modules/transport/infrastructure/trip_time_approval.py#L21)

```python
approve_time(gateway: Any, operation: str, body: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TransportPlanError`, `cur.callproc`, `cur.var`, `gateway.transaction`, `json.dumps`, `len`, `read_oracle_json`, `request_bind.setvalue`, `result.getvalue`, `trip_error`

### __init__

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/vehicle_profile.py:9](../../../api/wms_api_server/app/modules/transport/infrastructure/vehicle_profile.py#L9)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### failure

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/vehicle_profile.py:13](../../../api/wms_api_server/app/modules/transport/infrastructure/vehicle_profile.py#L13)

```python
failure(exc: oracledb.DatabaseError) -> VehicleProfileError
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `VehicleProfileError`, `getattr`, `str`, `str(exc.args[0]).split`

### configure

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/vehicle_profile.py:20](../../../api/wms_api_server/app/modules/transport/infrastructure/vehicle_profile.py#L20)

```python
configure(self, body: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cursor.callproc`, `cursor.var`, `json.dumps`, `read_oracle_json`, `result.getvalue`, `self.failure`, `self.gateway.transaction`

### read

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/vehicle_profile.py:30](../../../api/wms_api_server/app/modules/transport/infrastructure/vehicle_profile.py#L30)

```python
read(self, vehicle: int, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `VehicleProfileError`, `cursor.callfunc`, `cursor.execute`, `cursor.fetchone`, `read_oracle_json`, `self.failure`, `self.gateway.transaction`

### tare_types

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/vehicle_profile.py:42](../../../api/wms_api_server/app/modules/transport/infrastructure/vehicle_profile.py#L42)

```python
tare_types(self, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `VehicleProfileError`, `cursor.execute`, `cursor.fetchall`, `cursor.fetchone`, `dict`, `len`, `self.gateway.transaction`, `zip`

### extract_solver_routes

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/vrp_schedule.py:7](../../../api/wms_api_server/app/modules/transport/infrastructure/vrp_schedule.py#L7)

```python
extract_solver_routes(orders: list[VrpOrder], vehicles: list[VrpVehicle], distances: list[list[int]], depot: int, manager: Any, routing: Any, solution: Any, time_matrix: list[list[int]] | None=None, time_basis: list[list[str]] | None=None) -> tuple[list[VrpRoute], list[VrpOrder], int]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `VrpRoute`, `dimension.CumulVar`, `enumerate`, `int`, `len`, `manager.IndexToNode`, `math.ceil`, `max`, `range`, `remaining.discard`, `round`, `routes.append`, `routing.GetDimensionOrDie`, `routing.IsEnd`, `routing.NextVar`, `routing.Start`, `schedule.append`, `set`, `solution.Value`, `sorted`, `stops.append`, `sum`

### __init__

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/warehouse_depot.py:9](../../../api/wms_api_server/app/modules/transport/infrastructure/warehouse_depot.py#L9)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### context

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/warehouse_depot.py:10](../../../api/wms_api_server/app/modules/transport/infrastructure/warehouse_depot.py#L10)

```python
context(self, ware: int, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.callproc`, `cur.execute`, `cur.var`, `out.getvalue`, `read_oracle_json`, `self.gateway.transaction`, `trip_error`

### apply

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/warehouse_depot.py:16](../../../api/wms_api_server/app/modules/transport/infrastructure/warehouse_depot.py#L16)

```python
apply(self, operation: str, body: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.callproc`, `cur.var`, `json.dumps`, `out.getvalue`, `payload.setvalue`, `read_oracle_json`, `self.gateway.transaction`, `trip_error`

### resolve

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/warehouse_depot.py:24](../../../api/wms_api_server/app/modules/transport/infrastructure/warehouse_depot.py#L24)

```python
resolve(self, operation: str, body: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TransportPlanError`, `cur.callproc`, `cur.execute`, `cur.fetchone`, `cur.var`, `json.dumps`, `read_oracle_json`, `self.gateway.transaction`, `trip_error`

### get

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/warehouse_forecast.py:13](../../../api/wms_api_server/app/modules/transport/infrastructure/warehouse_forecast.py#L13)

```python
get(self, ware: int, query: ForecastQuery, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `any`, `cur.execute`, `cur.fetchone`, `datetime.fromisoformat`, `end.date`, `end.date().isoformat`, `end.isoformat`, `forecast_labour`, `forecast_norm_basis`, `forecast_quantity`, `forecast_rows`, `format`, `history_window`, `int`, `json.dumps`, `json.dumps([ware, start.date().isoformat(), end.date().isoformat(), query.include_current_day, query.scope, days, series, missing], sort_keys=True, separators=(',', ':')).encode`, `json.dumps(norm_basis, sort_keys=True, separators=(',', ':')).encode`, `require_forecast_warehouse`, `self._series`, `self.gateway.transaction`, `sha256`, `sha256(json.dumps([ware, start.date().isoformat(), end.date().isoformat(), query.include_current_day, query.scope, days, series, missing], sort_keys=True, separators=(',', ':')).encode()).hexdigest`, `sha256(json.dumps(norm_basis, sort_keys=True, separators=(',', ':')).encode()).hexdigest`, `start.date`, `start.date().isoformat`, `start.isoformat`

### _series

[Исходник: api/wms_api_server/app/modules/transport/infrastructure/warehouse_forecast.py:45](../../../api/wms_api_server/app/modules/transport/infrastructure/warehouse_forecast.py#L45)

```python
_series(cur: Any, window: dict[str, Any], scope: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `WarehouseForecastError`, `cur.execute`, `forecast_rows`, `len`

### build_loading_service

[Исходник: api/wms_api_server/app/modules/transport/public.py:14](../../../api/wms_api_server/app/modules/transport/public.py#L14)

```python
build_loading_service(gateway: Any, post: Callable[[str, str, dict[str, Any], dict[str, Any], str], dict[str, Any]]) -> TransportLoadingPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TransportLoading`

### build_driver_binding

[Исходник: api/wms_api_server/app/modules/transport/public.py:21](../../../api/wms_api_server/app/modules/transport/public.py#L21)

```python
build_driver_binding(gateway: Any) -> DriverBindingPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `DriverBinding`

### build_warehouse_forecast

[Исходник: api/wms_api_server/app/modules/transport/public.py:28](../../../api/wms_api_server/app/modules/transport/public.py#L28)

```python
build_warehouse_forecast(gateway: Any) -> WarehouseForecastPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `WarehouseForecast`

### build_st_deferral

[Исходник: api/wms_api_server/app/modules/transport/public.py:53](../../../api/wms_api_server/app/modules/transport/public.py#L53)

```python
build_st_deferral(gateway: Any) -> StDeferralPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StDeferral`

### build_warehouse_depot

[Исходник: api/wms_api_server/app/modules/transport/public.py:67](../../../api/wms_api_server/app/modules/transport/public.py#L67)

```python
build_warehouse_depot(gateway: Any) -> WarehouseDepotPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `WarehouseDepot`

### build_vehicle_profiles

[Исходник: api/wms_api_server/app/modules/transport/public.py:76](../../../api/wms_api_server/app/modules/transport/public.py#L76)

```python
build_vehicle_profiles(gateway: Any) -> VehicleProfilePort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `VehicleProfiles`

### build_driver_workspace

[Исходник: api/wms_api_server/app/modules/transport/public.py:83](../../../api/wms_api_server/app/modules/transport/public.py#L83)

```python
build_driver_workspace(gateway: Any) -> DriverWorkspacePort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `DriverWorkspace`
