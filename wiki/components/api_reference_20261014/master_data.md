# Методы: master_data

### allocation_policy_view

[Исходник: api/wms_api_server/app/modules/master_data/api/allocation_routes.py:20](../../../api/wms_api_server/app/modules/master_data/api/allocation_routes.py#L20)

```python
allocation_policy_view() -> AllocationUser
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### allocation_policy_edit

[Исходник: api/wms_api_server/app/modules/master_data/api/allocation_routes.py:23](../../../api/wms_api_server/app/modules/master_data/api/allocation_routes.py#L23)

```python
allocation_policy_edit() -> AllocationUser
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### allocation_policy_service

[Исходник: api/wms_api_server/app/modules/master_data/api/allocation_routes.py:26](../../../api/wms_api_server/app/modules/master_data/api/allocation_routes.py#L26)

```python
allocation_policy_service() -> AllocationPolicyPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### get_policy

[Исходник: api/wms_api_server/app/modules/master_data/api/allocation_routes.py:32](../../../api/wms_api_server/app/modules/master_data/api/allocation_routes.py#L32)

```python
get_policy(warehouse: int=Path(gt=0), article: str=Path(min_length=1, max_length=160), user: AllocationUser=Depends(allocation_policy_view), service: AllocationPolicyPort=Depends(allocation_policy_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Path`, `router.get`, `service.get`

### set_policy

[Исходник: api/wms_api_server/app/modules/master_data/api/allocation_routes.py:37](../../../api/wms_api_server/app/modules/master_data/api/allocation_routes.py#L37)

```python
set_policy(request: AllocationPolicyInput, warehouse: int=Path(gt=0), article: str=Path(min_length=1, max_length=160), user: AllocationUser=Depends(allocation_policy_edit), service: AllocationPolicyPort=Depends(allocation_policy_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Path`, `router.put`, `service.set`

### get

[Исходник: api/wms_api_server/app/modules/master_data/api/allocation_routes.py:17](../../../api/wms_api_server/app/modules/master_data/api/allocation_routes.py#L17)

```python
get(self, warehouse: int, article: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### set

[Исходник: api/wms_api_server/app/modules/master_data/api/allocation_routes.py:18](../../../api/wms_api_server/app/modules/master_data/api/allocation_routes.py#L18)

```python
set(self, warehouse: int, article: str, request: AllocationPolicyInput, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### quality_weight_service

[Исходник: api/wms_api_server/app/modules/master_data/api/quality_weight_routes.py:16](../../../api/wms_api_server/app/modules/master_data/api/quality_weight_routes.py#L16)

```python
quality_weight_service() -> WeightPolicyPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### get_policy

[Исходник: api/wms_api_server/app/modules/master_data/api/quality_weight_routes.py:24](../../../api/wms_api_server/app/modules/master_data/api/quality_weight_routes.py#L24)

```python
get_policy(warehouse: int=Path(gt=0), article: str=Path(min_length=1, max_length=160), _user: AdminUser=Depends(require_permission('finished_goods_view')), service: WeightPolicyPort=Depends(quality_weight_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Path`, `require_permission`, `router.get`, `service.get`

### set_policy

[Исходник: api/wms_api_server/app/modules/master_data/api/quality_weight_routes.py:31](../../../api/wms_api_server/app/modules/master_data/api/quality_weight_routes.py#L31)

```python
set_policy(body: WeightPolicyInput, warehouse: int=Path(gt=0), article: str=Path(min_length=1, max_length=160), user: AdminUser=Depends(require_permission('warehouse_settings_edit')), service: WeightPolicyPort=Depends(quality_weight_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Path`, `require_permission`, `router.put`, `service.set`

### get

[Исходник: api/wms_api_server/app/modules/master_data/api/quality_weight_routes.py:10](../../../api/wms_api_server/app/modules/master_data/api/quality_weight_routes.py#L10)

```python
get(self, warehouse: int, article: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### set

[Исходник: api/wms_api_server/app/modules/master_data/api/quality_weight_routes.py:11](../../../api/wms_api_server/app/modules/master_data/api/quality_weight_routes.py#L11)

```python
set(self, warehouse: int, article: str, request: WeightPolicyInput, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### policy_service

[Исходник: api/wms_api_server/app/modules/master_data/api/routes.py:10](../../../api/wms_api_server/app/modules/master_data/api/routes.py#L10)

```python
policy_service() -> ReceiptPolicyService
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### get_receiving_policy

[Исходник: api/wms_api_server/app/modules/master_data/api/routes.py:15](../../../api/wms_api_server/app/modules/master_data/api/routes.py#L15)

```python
get_receiving_policy(articul: str, user: AdminUser=Depends(require_permission('finished_goods_view')), service: ReceiptPolicyService=Depends(policy_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.get`, `service.get`, `str`

### save_receiving_policy

[Исходник: api/wms_api_server/app/modules/master_data/api/routes.py:24](../../../api/wms_api_server/app/modules/master_data/api/routes.py#L24)

```python
save_receiving_policy(articul: str, request: ReceiptPolicyUpdate, user: AdminUser=Depends(require_permission('finished_goods_edit')), service: ReceiptPolicyService=Depends(policy_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `len`, `require_permission`, `router.put`, `service.replace`, `str`

### store_reader

[Исходник: api/wms_api_server/app/modules/master_data/api/store_directory_routes.py:10](../../../api/wms_api_server/app/modules/master_data/api/store_directory_routes.py#L10)

```python
store_reader(user: AdminUser=Depends(get_current_user)) -> AdminUser
```

Достаточно одного из прав: настройки складов или просмотр диспетчеризации.

Вызывает: `' or '.join`, `Depends`, `HTTPException`, `any`

### search_stores

[Исходник: api/wms_api_server/app/modules/master_data/api/store_directory_routes.py:18](../../../api/wms_api_server/app/modules/master_data/api/store_directory_routes.py#L18)

```python
search_stores(q: str | None=Query(default=None, max_length=100), after: str | None=Query(default=None, min_length=1, max_length=255), limit: int=Query(default=30, ge=1, le=50), _user: AdminUser=Depends(store_reader), service: StoreDirectoryPort=Depends(store_directory_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Query`, `router.get`, `service.search`

### store_card

[Исходник: api/wms_api_server/app/modules/master_data/api/store_directory_routes.py:25](../../../api/wms_api_server/app/modules/master_data/api/store_directory_routes.py#L25)

```python
store_card(addr: str=Query(min_length=1, max_length=255), user: AdminUser=Depends(store_reader), service: StoreDirectoryPort=Depends(store_directory_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Query`, `router.get`, `service.card`

### read_profile

[Исходник: api/wms_api_server/app/modules/master_data/api/store_profile_routes.py:11](../../../api/wms_api_server/app/modules/master_data/api/store_profile_routes.py#L11)

```python
read_profile(addr: str=Query(min_length=1, max_length=255), _user: AdminUser=Depends(store_reader), service: StoreProfilePort=Depends(store_profile_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Query`, `router.get`, `service.read`

### save_profile

[Исходник: api/wms_api_server/app/modules/master_data/api/store_profile_routes.py:17](../../../api/wms_api_server/app/modules/master_data/api/store_profile_routes.py#L17)

```python
save_profile(body: StoreProfileInput, user: AdminUser=Depends(require_permission('warehouse_settings_edit')), service: StoreProfilePort=Depends(store_profile_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `body.model_dump`, `require_permission`, `router.put`, `service.save`, `str`

### warehouse_options_service

[Исходник: api/wms_api_server/app/modules/master_data/api/warehouse_options_routes.py:10](../../../api/wms_api_server/app/modules/master_data/api/warehouse_options_routes.py#L10)

```python
warehouse_options_service() -> WarehouseOptionsPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### warehouse_options

[Исходник: api/wms_api_server/app/modules/master_data/api/warehouse_options_routes.py:19](../../../api/wms_api_server/app/modules/master_data/api/warehouse_options_routes.py#L19)

```python
warehouse_options(q: str | None=Query(default=None, max_length=100), after: int | None=Query(default=None, gt=0), limit: int=Query(default=100, ge=1, le=100), _user: AdminUser=Depends(require_permission('warehouse_settings_view')), service: WarehouseOptionsPort=Depends(warehouse_options_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Query`, `require_permission`, `router.get`, `service.list`

### list

[Исходник: api/wms_api_server/app/modules/master_data/api/warehouse_options_routes.py:7](../../../api/wms_api_server/app/modules/master_data/api/warehouse_options_routes.py#L7)

```python
list(self, query: str | None, after: int | None, limit: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### get

[Исходник: api/wms_api_server/app/modules/master_data/application/policy.py:11](../../../api/wms_api_server/app/modules/master_data/application/policy.py#L11)

```python
get(self, articul: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### replace

[Исходник: api/wms_api_server/app/modules/master_data/application/policy.py:12](../../../api/wms_api_server/app/modules/master_data/application/policy.py#L12)

```python
replace(self, articul: str, request: ReceiptPolicyUpdate, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### __init__

[Исходник: api/wms_api_server/app/modules/master_data/application/policy.py:16](../../../api/wms_api_server/app/modules/master_data/application/policy.py#L16)

```python
__init__(self, store: PolicyStore) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### get

[Исходник: api/wms_api_server/app/modules/master_data/application/policy.py:19](../../../api/wms_api_server/app/modules/master_data/application/policy.py#L19)

```python
get(self, articul: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.store.get`

### replace

[Исходник: api/wms_api_server/app/modules/master_data/application/policy.py:22](../../../api/wms_api_server/app/modules/master_data/application/policy.py#L22)

```python
replace(self, articul: str, request: ReceiptPolicyUpdate, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.store.replace`

### _profile_storage_value

[Исходник: api/wms_api_server/app/modules/master_data/contracts.py:7](../../../api/wms_api_server/app/modules/master_data/contracts.py#L7)

```python
_profile_storage_value(value: str) -> str
```

Native profile identity columns and resolvers use VARCHAR2(80 BYTE).

Вызывает: `ValueError`, `len`, `value.encode`

### consistent_profiles

[Исходник: api/wms_api_server/app/modules/master_data/contracts.py:36](../../../api/wms_api_server/app/modules/master_data/contracts.py#L36)

```python
consistent_profiles(self) -> 'ReceiptPolicyUpdate'
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `bool`, `len`, `model_validator`, `set`

### store_directory_service

[Исходник: api/wms_api_server/app/modules/master_data/contracts_store_directory.py:11](../../../api/wms_api_server/app/modules/master_data/contracts_store_directory.py#L11)

```python
store_directory_service() -> StoreDirectoryPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### search

[Исходник: api/wms_api_server/app/modules/master_data/contracts_store_directory.py:7](../../../api/wms_api_server/app/modules/master_data/contracts_store_directory.py#L7)

```python
search(self, query: str | None, after: str | None, limit: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### card

[Исходник: api/wms_api_server/app/modules/master_data/contracts_store_directory.py:8](../../../api/wms_api_server/app/modules/master_data/contracts_store_directory.py#L8)

```python
card(self, address: str, actor: str) -> dict[str, Any] | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### store_profile_service

[Исходник: api/wms_api_server/app/modules/master_data/contracts_store_profile.py:48](../../../api/wms_api_server/app/modules/master_data/contracts_store_profile.py#L48)

```python
store_profile_service() -> StoreProfilePort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### __init__

[Исходник: api/wms_api_server/app/modules/master_data/contracts_store_profile.py:38](../../../api/wms_api_server/app/modules/master_data/contracts_store_profile.py#L38)

```python
__init__(self, code: str, status: int=409, message: str | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `super`, `super().__init__`

### read

[Исходник: api/wms_api_server/app/modules/master_data/contracts_store_profile.py:44](../../../api/wms_api_server/app/modules/master_data/contracts_store_profile.py#L44)

```python
read(self, address: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### save

[Исходник: api/wms_api_server/app/modules/master_data/contracts_store_profile.py:45](../../../api/wms_api_server/app/modules/master_data/contracts_store_profile.py#L45)

```python
save(self, actor: str, body: dict[str, Any]) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### normalize_windows

[Исходник: api/wms_api_server/app/modules/master_data/domain/store_profile.py:26](../../../api/wms_api_server/app/modules/master_data/domain/store_profile.py#L26)

```python
normalize_windows(windows: list[dict[str, Any]], mode: str='WEEKLY') -> list[dict[str, int]]
```

Окна приёма WEEKLY: день недели ISO 1–7, полуоткрытые интервалы [from,to) в минутах, без пересечений.

Отсутствующий день при WEEKLY означает «закрыто»; при UNCONFIGURED строк окон нет вовсе.
Ночной интервал задаётся явно двумя днями. Превышение лимитов отклоняется, а не обрезается.

Вызывает: `StoreProfileInvalid`, `all`, `isinstance`, `len`, `range`, `rows.append`, `rows.sort`, `sum`, `window.get`, `zip`

### normalize_profile

[Исходник: api/wms_api_server/app/modules/master_data/domain/store_profile.py:56](../../../api/wms_api_server/app/modules/master_data/domain/store_profile.py#L56)

```python
normalize_profile(values: dict[str, Any]) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreProfileInvalid`, `isinstance`, `len`, `values.get`

### __init__

[Исходник: api/wms_api_server/app/modules/master_data/domain/store_profile.py:21](../../../api/wms_api_server/app/modules/master_data/domain/store_profile.py#L21)

```python
__init__(self, code: str, message: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `super`, `super().__init__`

### __init__

[Исходник: api/wms_api_server/app/modules/master_data/infrastructure/allocation_policy.py:7](../../../api/wms_api_server/app/modules/master_data/infrastructure/allocation_policy.py#L7)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### get

[Исходник: api/wms_api_server/app/modules/master_data/infrastructure/allocation_policy.py:10](../../../api/wms_api_server/app/modules/master_data/infrastructure/allocation_policy.py#L10)

```python
get(self, warehouse: int, article: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `bool`, `self.gateway.fetch_all`

### set

[Исходник: api/wms_api_server/app/modules/master_data/infrastructure/allocation_policy.py:21](../../../api/wms_api_server/app/modules/master_data/infrastructure/allocation_policy.py#L21)

```python
set(self, warehouse: int, article: str, request: Any, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `cursor.execute`, `cursor.fetchone`, `int`, `self.get`, `stock_configuration_transaction`

### __init__

[Исходник: api/wms_api_server/app/modules/master_data/infrastructure/quality_weight_policy.py:10](../../../api/wms_api_server/app/modules/master_data/infrastructure/quality_weight_policy.py#L10)

```python
__init__(self, gateway: OracleGateway | TransactionGateway) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### get

[Исходник: api/wms_api_server/app/modules/master_data/infrastructure/quality_weight_policy.py:13](../../../api/wms_api_server/app/modules/master_data/infrastructure/quality_weight_policy.py#L13)

```python
get(self, warehouse: int, article: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `self.gateway.fetch_all`

### set

[Исходник: api/wms_api_server/app/modules/master_data/infrastructure/quality_weight_policy.py:24](../../../api/wms_api_server/app/modules/master_data/infrastructure/quality_weight_policy.py#L24)

```python
set(self, warehouse: int, article: str, request: WeightPolicyInput, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`, `cursor.execute`, `cursor.fetchone`, `self.get`, `stock_configuration_transaction`

### assert_weighted_sku

[Исходник: api/wms_api_server/app/modules/master_data/infrastructure/receipt_policy.py:98](../../../api/wms_api_server/app/modules/master_data/infrastructure/receipt_policy.py#L98)

```python
assert_weighted_sku(cursor: oracledb.Cursor, article: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `cursor.callproc`

### __init__

[Исходник: api/wms_api_server/app/modules/master_data/infrastructure/receipt_policy.py:12](../../../api/wms_api_server/app/modules/master_data/infrastructure/receipt_policy.py#L12)

```python
__init__(self, gateway: OracleGateway) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### get

[Исходник: api/wms_api_server/app/modules/master_data/infrastructure/receipt_policy.py:15](../../../api/wms_api_server/app/modules/master_data/infrastructure/receipt_policy.py#L15)

```python
get(self, articul: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `LookupError`, `any`, `bool`, `format`, `int`, `len`, `self.gateway.fetch_all`, `str`

### replace

[Исходник: api/wms_api_server/app/modules/master_data/infrastructure/receipt_policy.py:43](../../../api/wms_api_server/app/modules/master_data/infrastructure/receipt_policy.py#L43)

```python
replace(self, articul: str, request: ReceiptPolicyUpdate, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `LookupError`, `PolicyConflict`, `any`, `assert_weighted_sku`, `bool`, `configuration_transaction`, `cursor.execute`, `cursor.fetchall`, `cursor.fetchone`, `cursor.setinputsizes`, `format`, `int`, `json.dumps`, `len`, `p.model_dump`, `profile.model_dump`, `str`

### _pattern

[Исходник: api/wms_api_server/app/modules/master_data/infrastructure/store_directory.py:46](../../../api/wms_api_server/app/modules/master_data/infrastructure/store_directory.py#L46)

```python
_pattern(query: str | None) -> str | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(query or '').strip`, `(query or '').strip().upper`, `text.replace`, `text.replace('!', '!!').replace`, `text.replace('!', '!!').replace('%', '!%').replace`

### __init__

[Исходник: api/wms_api_server/app/modules/master_data/infrastructure/store_directory.py:54](../../../api/wms_api_server/app/modules/master_data/infrastructure/store_directory.py#L54)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### search

[Исходник: api/wms_api_server/app/modules/master_data/infrastructure/store_directory.py:57](../../../api/wms_api_server/app/modules/master_data/infrastructure/store_directory.py#L57)

```python
search(self, query: str | None, after: str | None, limit: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_pattern`, `len`, `self.gateway.fetch_all`

### card

[Исходник: api/wms_api_server/app/modules/master_data/infrastructure/store_directory.py:63](../../../api/wms_api_server/app/modules/master_data/infrastructure/store_directory.py#L63)

```python
card(self, address: str, actor: str) -> dict[str, Any] | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `dict`, `len`, `self.gateway.fetch_all`, `single.get`

### _not_installed

[Исходник: api/wms_api_server/app/modules/master_data/infrastructure/store_profile.py:16](../../../api/wms_api_server/app/modules/master_data/infrastructure/store_profile.py#L16)

```python
_not_installed(error: oracledb.DatabaseError) -> bool
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `getattr`

### read_profile

[Исходник: api/wms_api_server/app/modules/master_data/infrastructure/store_profile.py:20](../../../api/wms_api_server/app/modules/master_data/infrastructure/store_profile.py#L20)

```python
read_profile(cur: Any, address: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreProfileError`, `bool`, `cur.execute`, `cur.fetchall`, `cur.fetchone`, `dict`, `len`, `zip`

### __init__

[Исходник: api/wms_api_server/app/modules/master_data/infrastructure/store_profile.py:40](../../../api/wms_api_server/app/modules/master_data/infrastructure/store_profile.py#L40)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### read

[Исходник: api/wms_api_server/app/modules/master_data/infrastructure/store_profile.py:43](../../../api/wms_api_server/app/modules/master_data/infrastructure/store_profile.py#L43)

```python
read(self, address: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_not_installed`, `cur.execute`, `read_profile`, `self.gateway.transaction`

### save

[Исходник: api/wms_api_server/app/modules/master_data/infrastructure/store_profile.py:53](../../../api/wms_api_server/app/modules/master_data/infrastructure/store_profile.py#L53)

```python
save(self, actor: str, body: dict[str, Any]) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `StoreProfileError`, `_not_installed`, `body.get`, `hashlib.sha256`, `hashlib.sha256(wire.encode('utf-8')).hexdigest`, `json.dumps`, `normalize_profile`, `normalize_windows`, `self._save`, `str`, `wire.encode`

### _save

[Исходник: api/wms_api_server/app/modules/master_data/infrastructure/store_profile.py:70](../../../api/wms_api_server/app/modules/master_data/infrastructure/store_profile.py#L70)

```python
_save(self, actor: str, op: str, canonical: dict[str, Any], profile: dict[str, Any], windows: list[dict[str, int]], wire: str, digest: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `','.join`, `COLUMNS.split`, `StoreProfileError`, `cur.execute`, `cur.executemany`, `cur.fetchall`, `cur.fetchone`, `int`, `json.dumps`, `len`, `read_oracle_json`, `read_profile`, `stock_configuration_transaction`, `zip`

### published_cell_coverage

[Исходник: api/wms_api_server/app/modules/master_data/infrastructure/topology_coverage.py:9](../../../api/wms_api_server/app/modules/master_data/infrastructure/topology_coverage.py#L9)

```python
published_cell_coverage(cur: Any, ware: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `','.join`, `cur.execute`, `cur.fetchall`, `cur.fetchone`, `enumerate`, `int`, `len`, `range`, `str`

### _pattern

[Исходник: api/wms_api_server/app/modules/master_data/infrastructure/warehouse_options.py:11](../../../api/wms_api_server/app/modules/master_data/infrastructure/warehouse_options.py#L11)

```python
_pattern(query: str | None) -> str | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(query or '').strip`, `(query or '').strip().upper`, `text.replace`, `text.replace('!', '!!').replace`, `text.replace('!', '!!').replace('%', '!%').replace`

### __init__

[Исходник: api/wms_api_server/app/modules/master_data/infrastructure/warehouse_options.py:19](../../../api/wms_api_server/app/modules/master_data/infrastructure/warehouse_options.py#L19)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### list

[Исходник: api/wms_api_server/app/modules/master_data/infrastructure/warehouse_options.py:22](../../../api/wms_api_server/app/modules/master_data/infrastructure/warehouse_options.py#L22)

```python
list(self, query: str | None, after: int | None, limit: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `_pattern`, `len`, `self.gateway.fetch_all`

### build_policy_service

[Исходник: api/wms_api_server/app/modules/master_data/public.py:7](../../../api/wms_api_server/app/modules/master_data/public.py#L7)

```python
build_policy_service() -> ReceiptPolicyService
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `ReceiptPolicyRepository`, `ReceiptPolicyService`

### build_allocation_policy

[Исходник: api/wms_api_server/app/modules/master_data/public.py:16](../../../api/wms_api_server/app/modules/master_data/public.py#L16)

```python
build_allocation_policy() -> AllocationPolicy
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `AllocationPolicy`, `OracleGateway`

### build_quality_weight_policy

[Исходник: api/wms_api_server/app/modules/master_data/public.py:23](../../../api/wms_api_server/app/modules/master_data/public.py#L23)

```python
build_quality_weight_policy() -> QualityWeightPolicy
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `QualityWeightPolicy`

### build_store_directory

[Исходник: api/wms_api_server/app/modules/master_data/public.py:33](../../../api/wms_api_server/app/modules/master_data/public.py#L33)

```python
build_store_directory() -> StoreDirectory
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `StoreDirectory`

### build_warehouse_options

[Исходник: api/wms_api_server/app/modules/master_data/public.py:40](../../../api/wms_api_server/app/modules/master_data/public.py#L40)

```python
build_warehouse_options() -> WarehouseOptions
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `WarehouseOptions`

### build_store_profile

[Исходник: api/wms_api_server/app/modules/master_data/public.py:48](../../../api/wms_api_server/app/modules/master_data/public.py#L48)

```python
build_store_profile() -> StoreProfile
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `StoreProfile`
