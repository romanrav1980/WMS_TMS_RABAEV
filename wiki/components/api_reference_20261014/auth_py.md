# Методы: auth.py

### get_current_admin

[Исходник: api/wms_api_server/app/auth.py:116](../../../api/wms_api_server/app/auth.py#L116)

```python
get_current_admin(credentials: HTTPBasicCredentials | None=Depends(security), settings: Settings=Depends(get_settings)) -> AdminUser
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `AdminUser`, `Depends`, `load_admin_user`, `raise_unauthorized`

### require_permission

[Исходник: api/wms_api_server/app/auth.py:137](../../../api/wms_api_server/app/auth.py#L137)

```python
require_permission(permission: str)
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`

### serialize_admin_user

[Исходник: api/wms_api_server/app/auth.py:149](../../../api/wms_api_server/app/auth.py#L149)

```python
serialize_admin_user(user: AdminUser) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `sorted`

### load_admin_user

[Исходник: api/wms_api_server/app/auth.py:158](../../../api/wms_api_server/app/auth.py#L158)

```python
load_admin_user(username: str, password: str) -> AdminUser | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `AdminUser`, `HTTPException`, `OracleGateway`, `OracleGateway().fetch_all`, `int`, `load_group_permissions`, `permissions.add`, `row.get`, `str`, `str(row.get('user_group') or '').strip`, `user_group.upper`

### load_group_permissions

[Исходник: api/wms_api_server/app/auth.py:193](../../../api/wms_api_server/app/auth.py#L193)

```python
load_group_permissions(user_group: str) -> set[str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `OracleGateway().fetch_all`, `row.get`, `set`, `str`, `str(row.get('right1')).strip`

### raise_unauthorized

[Исходник: api/wms_api_server/app/auth.py:208](../../../api/wms_api_server/app/auth.py#L208)

```python
raise_unauthorized() -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `HTTPException`

### dependency

[Исходник: api/wms_api_server/app/auth.py:138](../../../api/wms_api_server/app/auth.py#L138)

```python
dependency(user: AdminUser=Depends(get_current_admin)) -> AdminUser
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`
