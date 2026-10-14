# Методы: resource_composition.py

### assign_warehouse

[Исходник: api/wms_api_server/app/resource_composition.py:7](../../../api/wms_api_server/app/resource_composition.py#L7)

```python
assign_warehouse(gateway: Any, task_id: int, request: WarehouseTaskStatusRequest) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `WarehouseTaskService`, `WarehouseTaskService(gateway).assign_task`

### build_resource_qualification

[Исходник: api/wms_api_server/app/resource_composition.py:10](../../../api/wms_api_server/app/resource_composition.py#L10)

```python
build_resource_qualification() -> QualificationService
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `build_qualification_service`
