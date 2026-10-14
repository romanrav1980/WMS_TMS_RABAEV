# Методы: config.py

### _split_origins

[Исходник: api/wms_api_server/app/config.py:28](../../../api/wms_api_server/app/config.py#L28)

```python
_split_origins(value: str) -> list[str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `item.strip`, `value.split`

### _bool_env

[Исходник: api/wms_api_server/app/config.py:32](../../../api/wms_api_server/app/config.py#L32)

```python
_bool_env(name: str, default: str) -> bool
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `os.getenv`, `os.getenv(name, default).strip`, `os.getenv(name, default).strip().lower`

### _project_local_defaults

[Исходник: api/wms_api_server/app/config.py:36](../../../api/wms_api_server/app/config.py#L36)

```python
_project_local_defaults() -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Path`, `Path(__file__).resolve`, `config_path.read_text`, `json.loads`

### get_settings

[Исходник: api/wms_api_server/app/config.py:41](../../../api/wms_api_server/app/config.py#L41)

```python
get_settings() -> Settings
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Settings`, `_bool_env`, `_project_local_defaults`, `_split_origins`, `int`, `os.getenv`, `str`
