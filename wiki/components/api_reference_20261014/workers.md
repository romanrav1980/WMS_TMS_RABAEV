# Методы: workers

### process_batch

[Исходник: api/wms_api_server/app/workers/outbox_worker.py:12](../../../api/wms_api_server/app/workers/outbox_worker.py#L12)

```python
process_batch(worker_id: str, target_system: str | None, limit: int, sleep_seconds: float, loop: bool) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OutboxService`, `print_status`, `result.get`, `service.process_next`, `time.sleep`

### print_status

[Исходник: api/wms_api_server/app/workers/outbox_worker.py:42](../../../api/wms_api_server/app/workers/outbox_worker.py#L42)

```python
print_status(payload: dict[str, Any]) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `datetime.now`, `datetime.now(UTC).isoformat`, `print`

### build_parser

[Исходник: api/wms_api_server/app/workers/outbox_worker.py:47](../../../api/wms_api_server/app/workers/outbox_worker.py#L47)

```python
build_parser() -> argparse.ArgumentParser
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `argparse.ArgumentParser`, `parser.add_argument`, `socket.gethostname`

### main

[Исходник: api/wms_api_server/app/workers/outbox_worker.py:57](../../../api/wms_api_server/app/workers/outbox_worker.py#L57)

```python
main() -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `build_parser`, `build_parser().parse_args`, `max`, `process_batch`

### process_batch

[Исходник: api/wms_api_server/app/workers/production_exchange_worker.py:14](../../../api/wms_api_server/app/workers/production_exchange_worker.py#L14)

```python
process_batch(worker_id: str, root_dir: str | None, limit: int, sleep_seconds: float, loop: bool) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Path`, `ProductionExchangeService`, `dataclasses.asdict`, `print_status`, `service.process_once`, `str`, `time.sleep`

### print_status

[Исходник: api/wms_api_server/app/workers/production_exchange_worker.py:38](../../../api/wms_api_server/app/workers/production_exchange_worker.py#L38)

```python
print_status(payload: dict[str, Any]) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `datetime.now`, `datetime.now(UTC).isoformat`, `print`

### build_parser

[Исходник: api/wms_api_server/app/workers/production_exchange_worker.py:43](../../../api/wms_api_server/app/workers/production_exchange_worker.py#L43)

```python
build_parser() -> argparse.ArgumentParser
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `argparse.ArgumentParser`, `parser.add_argument`, `socket.gethostname`

### main

[Исходник: api/wms_api_server/app/workers/production_exchange_worker.py:53](../../../api/wms_api_server/app/workers/production_exchange_worker.py#L53)

```python
main() -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `build_parser`, `build_parser().parse_args`, `max`, `process_batch`

### process_batch

[Исходник: api/wms_api_server/app/workers/sap_artmas_worker.py:11](../../../api/wms_api_server/app/workers/sap_artmas_worker.py#L11)

```python
process_batch(root: Path, limit: int=20, min_age: int=2, kind: str='artmas') -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `build_acknowledgements`, `build_artmas_service`, `build_store_admission_service`, `build_store_order_service`, `build_supply_service`, `receive_gateway_files`

### main

[Исходник: api/wms_api_server/app/workers/sap_artmas_worker.py:16](../../../api/wms_api_server/app/workers/sap_artmas_worker.py#L16)

```python
main() -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `argparse.ArgumentParser`, `json.dumps`, `parser.add_argument`, `parser.error`, `parser.parse_args`, `print`, `process_batch`, `str`, `time.sleep`

### main

[Исходник: api/wms_api_server/app/workers/sap_receipt_outbox_worker.py:9](../../../api/wms_api_server/app/workers/sap_receipt_outbox_worker.py#L9)

```python
main() -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Path`, `Path(__file__).resolve`, `argparse.ArgumentParser`, `build_receipt_exporter`, `exporter.export`, `json.dumps`, `parser.add_argument`, `parser.error`, `parser.parse_args`, `print`, `str`, `time.sleep`

### main

[Исходник: api/wms_api_server/app/workers/sap_store_return_worker.py:19](../../../api/wms_api_server/app/workers/sap_store_return_worker.py#L19)

```python
main() -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ConfiguredReceiver`, `Path`, `Path(__file__).resolve`, `argparse.ArgumentParser`, `json.dumps`, `parser.add_argument`, `parser.parse_args`, `print`, `receive_gateway_files`, `time.sleep`

### __init__

[Исходник: api/wms_api_server/app/workers/sap_store_return_worker.py:11](../../../api/wms_api_server/app/workers/sap_store_return_worker.py#L11)

```python
__init__(self, actor: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `build_sap_store_returns`

### receive

[Исходник: api/wms_api_server/app/workers/sap_store_return_worker.py:15](../../../api/wms_api_server/app/workers/sap_store_return_worker.py#L15)

```python
receive(self, raw: bytes, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.service.receive`

### main

[Исходник: api/wms_api_server/app/workers/warehouse_forecast_worker.py:7](../../../api/wms_api_server/app/workers/warehouse_forecast_worker.py#L7)

```python
main() -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `argparse.ArgumentParser`, `forecast_service`, `json.dumps`, `parser.add_argument`, `parser.error`, `parser.parse_args`, `print`, `service.project`, `time.sleep`
