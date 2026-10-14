# Методы: integrations

### acknowledgement_service

[Исходник: api/wms_api_server/app/modules/integrations/api/receipt_event_routes.py:12](../../../api/wms_api_server/app/modules/integrations/api/receipt_event_routes.py#L12)

```python
acknowledgement_service() -> ReceiptAcknowledgements
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### list_receipt_events

[Исходник: api/wms_api_server/app/modules/integrations/api/receipt_event_routes.py:17](../../../api/wms_api_server/app/modules/integrations/api/receipt_event_routes.py#L17)

```python
list_receipt_events(limit: int=Query(100, ge=1, le=200), user: AdminUser=Depends(require_permission('sap_supply_view')), service: ReceiptAcknowledgements=Depends(acknowledgement_service)) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `Query`, `require_permission`, `router.get`, `service.list_events`

### receive_ack

[Исходник: api/wms_api_server/app/modules/integrations/api/receipt_event_routes.py:23](../../../api/wms_api_server/app/modules/integrations/api/receipt_event_routes.py#L23)

```python
receive_ack(request: Request, user: AdminUser=Depends(require_permission('sap_supply_import')), service: ReceiptAcknowledgements=Depends(acknowledgement_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `bytearray`, `bytes`, `len`, `raw.extend`, `request.stream`, `require_permission`, `router.post`, `run_in_threadpool`, `str`

### retry_receipt_event

[Исходник: api/wms_api_server/app/modules/integrations/api/receipt_event_routes.py:41](../../../api/wms_api_server/app/modules/integrations/api/receipt_event_routes.py#L41)

```python
retry_receipt_event(event_id: str, user: AdminUser=Depends(require_permission('sap_supply_import')), service: ReceiptAcknowledgements=Depends(acknowledgement_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.post`, `service.retry`, `str`

### regulatory_runtime_service

[Исходник: api/wms_api_server/app/modules/integrations/api/regulatory_runtime_routes.py:6](../../../api/wms_api_server/app/modules/integrations/api/regulatory_runtime_routes.py#L6)

```python
regulatory_runtime_service() -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### runtime

[Исходник: api/wms_api_server/app/modules/integrations/api/regulatory_runtime_routes.py:10](../../../api/wms_api_server/app/modules/integrations/api/regulatory_runtime_routes.py#L10)

```python
runtime(user: AdminUser=Depends(require_permission('external_outbox_view')), status: dict[str, Any]=Depends(regulatory_runtime_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `require_permission`, `router.get`

### artmas_service

[Исходник: api/wms_api_server/app/modules/integrations/api/routes.py:13](../../../api/wms_api_server/app/modules/integrations/api/routes.py#L13)

```python
artmas_service() -> ArtmasIngestion
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### receive_artmas

[Исходник: api/wms_api_server/app/modules/integrations/api/routes.py:18](../../../api/wms_api_server/app/modules/integrations/api/routes.py#L18)

```python
receive_artmas(request: Request, user: AdminUser=Depends(require_permission('sap_article_import')), service: ArtmasIngestion=Depends(artmas_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `bytearray`, `bytes`, `len`, `raw.extend`, `request.stream`, `require_permission`, `router.post`, `run_in_threadpool`, `str`

### get_artmas

[Исходник: api/wms_api_server/app/modules/integrations/api/routes.py:34](../../../api/wms_api_server/app/modules/integrations/api/routes.py#L34)

```python
get_artmas(inbox_id: str, user: AdminUser=Depends(require_permission('sap_article_import')), service: ArtmasIngestion=Depends(artmas_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.get`, `service.get`, `str`

### receive

[Исходник: api/wms_api_server/app/modules/integrations/api/store_return_routes.py:14](../../../api/wms_api_server/app/modules/integrations/api/store_return_routes.py#L14)

```python
receive(request: Request, user: AdminUser=Depends(require_permission('sap_return_import')), service: SapStoreReturnsPort=Depends(sap_store_returns_service)) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `bytearray`, `bytes`, `len`, `raw.extend`, `request.stream`, `require_permission`, `router.post`, `run_in_threadpool`, `str`

### supply_service

[Исходник: api/wms_api_server/app/modules/integrations/api/supply_routes.py:16](../../../api/wms_api_server/app/modules/integrations/api/supply_routes.py#L16)

```python
supply_service() -> SupplyOrders
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### import_supply

[Исходник: api/wms_api_server/app/modules/integrations/api/supply_routes.py:21](../../../api/wms_api_server/app/modules/integrations/api/supply_routes.py#L21)

```python
import_supply(request: Request, user: AdminUser=Depends(require_permission('sap_supply_import')), service: SupplyOrders=Depends(supply_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `bytearray`, `bytes`, `len`, `raw.extend`, `request.stream`, `require_permission`, `router.post`, `run_in_threadpool`, `str`

### list_supplies

[Исходник: api/wms_api_server/app/modules/integrations/api/supply_routes.py:40](../../../api/wms_api_server/app/modules/integrations/api/supply_routes.py#L40)

```python
list_supplies(warehouse_id: int | None=None, limit: int=Query(100, ge=1, le=200), user: AdminUser=Depends(require_permission('sap_supply_view')), service: SupplyOrders=Depends(supply_service)) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Query`, `require_permission`, `router.get`, `service.list`, `str`

### supply_by_document

[Исходник: api/wms_api_server/app/modules/integrations/api/supply_routes.py:50](../../../api/wms_api_server/app/modules/integrations/api/supply_routes.py#L50)

```python
supply_by_document(document_id: int, user: AdminUser=Depends(require_permission('sap_supply_view')), service: SupplyOrders=Depends(supply_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.get`, `service.by_receipt_document`, `str`

### supply_detail

[Исходник: api/wms_api_server/app/modules/integrations/api/supply_routes.py:66](../../../api/wms_api_server/app/modules/integrations/api/supply_routes.py#L66)

```python
supply_detail(order_id: str, user: AdminUser=Depends(require_permission('sap_supply_view')), service: SupplyOrders=Depends(supply_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `require_permission`, `router.get`, `service.get`, `str`

### supply_pallet_plan

[Исходник: api/wms_api_server/app/modules/integrations/api/supply_routes.py:88](../../../api/wms_api_server/app/modules/integrations/api/supply_routes.py#L88)

```python
supply_pallet_plan(order_id: str, body: PalletPlan, user: AdminUser=Depends(require_permission('sap_supply_view')), service: SupplyOrders=Depends(supply_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `body.model_dump`, `require_permission`, `router.post`, `service.pallet_plan`, `str`

### history

[Исходник: api/wms_api_server/app/modules/integrations/api/supply_routes.py:102](../../../api/wms_api_server/app/modules/integrations/api/supply_routes.py#L102)

```python
history(order_id: str, limit: int=Query(50, ge=1, le=100), after_operation: str | None=Query(None, min_length=1, max_length=100), user: AdminUser=Depends(require_permission('sap_supply_view')), service: SupplyOrders=Depends(supply_service)) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Depends`, `HTTPException`, `Query`, `require_permission`, `router.get`, `service.receipt_history`, `str`

### receive

[Исходник: api/wms_api_server/app/modules/integrations/application/ingestion.py:11](../../../api/wms_api_server/app/modules/integrations/application/ingestion.py#L11)

```python
receive(self, envelope: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### get

[Исходник: api/wms_api_server/app/modules/integrations/application/ingestion.py:12](../../../api/wms_api_server/app/modules/integrations/application/ingestion.py#L12)

```python
get(self, inbox_id: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### apply

[Исходник: api/wms_api_server/app/modules/integrations/application/ingestion.py:16](../../../api/wms_api_server/app/modules/integrations/application/ingestion.py#L16)

```python
apply(self, inbox_id: str, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### __init__

[Исходник: api/wms_api_server/app/modules/integrations/application/ingestion.py:20](../../../api/wms_api_server/app/modules/integrations/application/ingestion.py#L20)

```python
__init__(self, inbox: InboxStore, articles: ArticleApply) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### receive

[Исходник: api/wms_api_server/app/modules/integrations/application/ingestion.py:24](../../../api/wms_api_server/app/modules/integrations/application/ingestion.py#L24)

```python
receive(self, raw: bytes, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `read_artmas10`, `self.articles.apply`, `self.inbox.receive`

### get

[Исходник: api/wms_api_server/app/modules/integrations/application/ingestion.py:29](../../../api/wms_api_server/app/modules/integrations/application/ingestion.py#L29)

```python
get(self, inbox_id: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.inbox.get`

### receive

[Исходник: api/wms_api_server/app/modules/integrations/application/receipt_ports.py:5](../../../api/wms_api_server/app/modules/integrations/application/receipt_ports.py#L5)

```python
receive(self, raw: bytes, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### list

[Исходник: api/wms_api_server/app/modules/integrations/application/receipt_ports.py:6](../../../api/wms_api_server/app/modules/integrations/application/receipt_ports.py#L6)

```python
list(self, warehouse_id: int | None, limit: int, actor: str) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### get

[Исходник: api/wms_api_server/app/modules/integrations/application/receipt_ports.py:7](../../../api/wms_api_server/app/modules/integrations/application/receipt_ports.py#L7)

```python
get(self, order_id: str, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### pallet_plan

[Исходник: api/wms_api_server/app/modules/integrations/application/receipt_ports.py:8](../../../api/wms_api_server/app/modules/integrations/application/receipt_ports.py#L8)

```python
pallet_plan(self, order_id: str, body: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### by_receipt_document

[Исходник: api/wms_api_server/app/modules/integrations/application/receipt_ports.py:9](../../../api/wms_api_server/app/modules/integrations/application/receipt_ports.py#L9)

```python
by_receipt_document(self, document_id: int, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### receipt_history

[Исходник: api/wms_api_server/app/modules/integrations/application/receipt_ports.py:11](../../../api/wms_api_server/app/modules/integrations/application/receipt_ports.py#L11)

```python
receipt_history(self, order_id: str, limit: int, after: str | None, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### receive

[Исходник: api/wms_api_server/app/modules/integrations/application/receipt_ports.py:15](../../../api/wms_api_server/app/modules/integrations/application/receipt_ports.py#L15)

```python
receive(self, raw: bytes, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### list_events

[Исходник: api/wms_api_server/app/modules/integrations/application/receipt_ports.py:16](../../../api/wms_api_server/app/modules/integrations/application/receipt_ports.py#L16)

```python
list_events(self, limit: int) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### retry

[Исходник: api/wms_api_server/app/modules/integrations/application/receipt_ports.py:17](../../../api/wms_api_server/app/modules/integrations/application/receipt_ports.py#L17)

```python
retry(self, event_id: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### send

[Исходник: api/wms_api_server/app/modules/integrations/contracts_regulatory.py:13](../../../api/wms_api_server/app/modules/integrations/contracts_regulatory.py#L13)

```python
send(self, event: dict[str, Any]) -> RegulatoryResponse
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### sap_store_returns_service

[Исходник: api/wms_api_server/app/modules/integrations/contracts_returns.py:8](../../../api/wms_api_server/app/modules/integrations/contracts_returns.py#L8)

```python
sap_store_returns_service() -> SapStoreReturnsPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### receive

[Исходник: api/wms_api_server/app/modules/integrations/contracts_returns.py:5](../../../api/wms_api_server/app/modules/integrations/contracts_returns.py#L5)

```python
receive(self, raw: bytes, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### adapter_request_evidence

[Исходник: api/wms_api_server/app/modules/integrations/domain/adapter_evidence.py:4](../../../api/wms_api_server/app/modules/integrations/domain/adapter_evidence.py#L4)

```python
adapter_request_evidence(row: dict[str, Any]) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `any`, `row.get`, `signature.startswith`, `str`, `str(row.get('signature_status') or '').upper`, `str(row.get(key) or '').upper`, `value.startswith`

### positive_measure

[Исходник: api/wms_api_server/app/modules/integrations/domain/article_logistics.py:10](../../../api/wms_api_server/app/modules/integrations/domain/article_logistics.py#L10)

```python
positive_measure(raw: str, factor: Decimal) -> Decimal
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `Fraction`, `ValueError`, `isinstance`, `len`, `str`, `str(count % 10 ** 9).zfill`, `value.is_finite`

### factor

[Исходник: api/wms_api_server/app/modules/integrations/domain/article_logistics.py:24](../../../api/wms_api_server/app/modules/integrations/domain/article_logistics.py#L24)

```python
factor(data: dict[str, str], name: str, iso: str, units: dict[str, Decimal]) -> Decimal
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `code.upper`, `data.get`, `len`, `set`, `values.append`

### box_logistics

[Исходник: api/wms_api_server/app/modules/integrations/domain/article_logistics.py:36](../../../api/wms_api_server/app/modules/integrations/domain/article_logistics.py#L36)

```python
box_logistics(records: list[dict[str, Any]]) -> dict[str, Decimal]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `bool`, `changed.intersection`, `data.get`, `factor`, `flags[0].items`, `len`, `list`, `positive_measure`, `r['fields'].get`

### positive

[Исходник: api/wms_api_server/app/modules/integrations/domain/article_mapping.py:8](../../../api/wms_api_server/app/modules/integrations/domain/article_mapping.py#L8)

```python
positive(value: str) -> Decimal
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `ValueError`, `result.is_finite`

### map_articles

[Исходник: api/wms_api_server/app/modules/integrations/domain/article_mapping.py:18](../../../api/wms_api_server/app/modules/integrations/domain/article_mapping.py#L18)

```python
map_articles(envelope: dict) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `ValueError`, `box_logistics`, `d.get`, `data.get`, `data.items`, `descriptions.append`, `descriptions.sort`, `int`, `len`, `map_units`, `next`, `r['fields'].get`, `result.append`, `values.get`, `values.update`, `{'BASE_UOM', 'BASE_UOM_ISO'}.intersection`, `{'RU': 0, 'R': 0, 'EN': 1, 'E': 1}.get`

### rational

[Исходник: api/wms_api_server/app/modules/integrations/domain/article_units.py:6](../../../api/wms_api_server/app/modules/integrations/domain/article_units.py#L6)

```python
rational(numerator: str, denominator: str) -> Fraction
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `Fraction`, `ValueError`, `d.is_finite`, `len`, `n.is_finite`

### decimal_ratio

[Исходник: api/wms_api_server/app/modules/integrations/domain/article_units.py:18](../../../api/wms_api_server/app/modules/integrations/domain/article_units.py#L18)

```python
decimal_ratio(value: Fraction) -> str | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `str`, `str(ticks.numerator).zfill`

### map_units

[Исходник: api/wms_api_server/app/modules/integrations/domain/article_units.py:24](../../../api/wms_api_server/app/modules/integrations/domain/article_units.py#L24)

```python
map_units(records: list[dict[str, Any]]) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `bool`, `changed.intersection`, `data.get`, `decimal_ratio`, `flags[0].items`, `len`, `r['fields'].get`, `rational`, `seen.add`, `set`, `units.append`

### merge_units

[Исходник: api/wms_api_server/app/modules/integrations/domain/article_units.py:52](../../../api/wms_api_server/app/modules/integrations/domain/article_units.py#L52)

```python
merge_units(previous: list[dict], patches: list[dict], base: str) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `Fraction`, `ValueError`, `decimal_ratio`, `dict`, `int`, `known.get`, `old.get`, `sorted`

### local_name

[Исходник: api/wms_api_server/app/modules/integrations/domain/artmas.py:8](../../../api/wms_api_server/app/modules/integrations/domain/artmas.py#L8)

```python
local_name(tag: str) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `tag.rsplit`

### fields

[Исходник: api/wms_api_server/app/modules/integrations/domain/artmas.py:12](../../../api/wms_api_server/app/modules/integrations/domain/artmas.py#L12)

```python
fields(node: ET.Element) -> dict[str, str]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(child.text or '').strip`, `ValueError`, `len`, `local_name`

### read_artmas10

[Исходник: api/wms_api_server/app/modules/integrations/domain/artmas.py:24](../../../api/wms_api_server/app/modules/integrations/domain/artmas.py#L24)

```python
read_artmas10(raw: bytes) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ET.fromstring`, `ValueError`, `any`, `control.get`, `control['DOCNUM'].isdigit`, `data.get`, `dict`, `fields`, `idoc.iter`, `len`, `local_name`, `materials.add`, `raw.decode`, `records.append`, `root.iter`, `set`, `sha256`, `sha256(raw).hexdigest`, `sorted`, `tag.startswith`, `xml.upper`

### regulatory_delivery_decision

[Исходник: api/wms_api_server/app/modules/integrations/domain/regulatory_delivery.py:20](../../../api/wms_api_server/app/modules/integrations/domain/regulatory_delivery.py#L20)

```python
regulatory_delivery_decision(response: RegulatoryResponse) -> RegulatoryDeliveryDecision
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RegulatoryDeliveryDecision`, `isinstance`, `response.status.strip`, `response.status.strip().upper`

### read_store_return

[Исходник: api/wms_api_server/app/modules/integrations/domain/store_return.py:10](../../../api/wms_api_server/app/modules/integrations/domain/store_return.py#L10)

```python
read_store_return(raw: bytes) -> dict[str, object]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(sender + '\x00' + message).encode`, `ET.fromstring`, `ValueError`, `any`, `base64.b64encode`, `base64.b64encode(raw).decode`, `int`, `len`, `next`, `quantity.attrib['unit'].encode`, `raw.decode`, `re.fullmatch`, `root.attrib.get`, `set`, `sha256`, `sha256((sender + '\x00' + message).encode()).hexdigest`, `sha256(raw).hexdigest`, `text.encode`, `text.strip`, `values.get`, `values['OriginalLineNumber'].isdigit`, `values['WarehouseId'].isdigit`, `xml.upper`

### read_supply_order

[Исходник: api/wms_api_server/app/modules/integrations/domain/supply_order.py:11](../../../api/wms_api_server/app/modules/integrations/domain/supply_order.py#L11)

```python
read_supply_order(raw: bytes) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(found[0].text or '').strip`, `Decimal`, `ET.fromstring`, `ValueError`, `any`, `int`, `len`, `lines.append`, `local_name`, `materials.add`, `next`, `numbers.add`, `qty.as_tuple`, `qty.is_finite`, `quantity_node.get`, `quantity_node.get('unit', '').strip`, `raw.decode`, `read_supply_aggregations`, `revision.isdigit`, `root.get`, `set`, `sha256`, `sha256(raw).hexdigest`, `str`, `text.encode`, `value`, `warehouse.isdigit`, `xml.upper`

### read_supply_aggregations

[Исходник: api/wms_api_server/app/modules/integrations/domain/supply_order.py:74](../../../api/wms_api_server/app/modules/integrations/domain/supply_order.py#L74)

```python
read_supply_aggregations(root: ET.Element, numbers: set[str], value: Callable[[ET.Element, str, int], str]) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `ValueError`, `aggregations.append`, `amount.is_finite`, `amount.normalize`, `amount.normalize().as_tuple`, `base64.b64decode`, `base64.b64decode(result, validate=True).decode`, `code`, `found[0].get`, `identities.add`, `len`, `local_name`, `member_ids.add`, `members.append`, `result.encode`, `set`, `str`, `value`

### value

[Исходник: api/wms_api_server/app/modules/integrations/domain/supply_order.py:24](../../../api/wms_api_server/app/modules/integrations/domain/supply_order.py#L24)

```python
value(node: ET.Element, name: str, maximum: int) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(found[0].text or '').strip`, `ValueError`, `len`, `local_name`, `text.encode`

### code

[Исходник: api/wms_api_server/app/modules/integrations/domain/supply_order.py:83](../../../api/wms_api_server/app/modules/integrations/domain/supply_order.py#L83)

```python
code(node: ET.Element) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `base64.b64decode`, `base64.b64decode(result, validate=True).decode`, `found[0].get`, `len`, `local_name`, `result.encode`

### __init__

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/article_master.py:15](../../../api/wms_api_server/app/modules/integrations/infrastructure/article_master.py#L15)

```python
__init__(self, gateway: OracleGateway) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### apply

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/article_master.py:18](../../../api/wms_api_server/app/modules/integrations/infrastructure/article_master.py#L18)

```python
apply(self, inbox_id: str, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self._apply`, `self.gateway.execute`, `str`

### _apply

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/article_master.py:26](../../../api/wms_api_server/app/modules/integrations/infrastructure/article_master.py#L26)

```python
_apply(self, inbox_id: str, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LookupError`, `ValueError`, `applied.append`, `configuration_transaction`, `control.get`, `cur.execute`, `cur.fetchone`, `cur.setinputsizes`, `datetime.strptime`, `envelope['docnum'].zfill`, `json.dumps`, `len`, `map_articles`, `older.append`, `previous[1].zfill`, `read_oracle_json`, `self._article`, `stamp.isdigit`

### _article

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/article_master.py:62](../../../api/wms_api_server/app/modules/integrations/infrastructure/article_master.py#L62)

```python
_article(self, cur: oracledb.Cursor, item: dict, previous: tuple | None, envelope: dict, stamp: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `','.join`, `Decimal`, `Fraction`, `ValueError`, `bool`, `columns.items`, `cur.execute`, `cur.fetchall`, `cur.setinputsizes`, `int`, `item.get`, `json.dumps`, `len`, `merge_units`, `read_oracle_json`, `unit.upper`

### __init__

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/artmas_inbox.py:11](../../../api/wms_api_server/app/modules/integrations/infrastructure/artmas_inbox.py#L11)

```python
__init__(self, gateway: OracleGateway) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### receive

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/artmas_inbox.py:14](../../../api/wms_api_server/app/modules/integrations/infrastructure/artmas_inbox.py#L14)

```python
receive(self, envelope: dict, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cursor.execute`, `cursor.setinputsizes`, `envelope.items`, `json.dumps`, `self._find`, `self._repeat`, `self.gateway.transaction`, `uuid4`

### _find

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/artmas_inbox.py:42](../../../api/wms_api_server/app/modules/integrations/infrastructure/artmas_inbox.py#L42)

```python
_find(self, sender: str, docnum: str) -> dict | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### _repeat

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/artmas_inbox.py:48](../../../api/wms_api_server/app/modules/integrations/infrastructure/artmas_inbox.py#L48)

```python
_repeat(self, old: dict, envelope: dict) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `IdocConflict`

### get

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/artmas_inbox.py:54](../../../api/wms_api_server/app/modules/integrations/infrastructure/artmas_inbox.py#L54)

```python
get(self, inbox_id: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LookupError`, `self.gateway.fetch_all`

### directory_owner

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/file_gateway.py:16](../../../api/wms_api_server/app/modules/integrations/infrastructure/file_gateway.py#L16)

```python
directory_owner(root: Path) -> Iterator[bool]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `fcntl.flock`, `handle.fileno`, `handle.flush`, `handle.read`, `handle.seek`, `handle.write`, `msvcrt.locking`, `path.is_symlink`, `path.open`

### receive_files

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/file_gateway.py:51](../../../api/wms_api_server/app/modules/integrations/infrastructure/file_gateway.py#L51)

```python
receive_files(root: Path, receiver: XmlReceiver, limit: int=20, min_age: int=2) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(root / n).resolve`, `ValueError`, `abandoned.is_file`, `abandoned.is_symlink`, `abandoned.rename`, `claimed.open`, `claimed.rename`, `destination.with_suffix`, `destination.with_suffix('.result.json').write_text`, `directory_owner`, `folders.values`, `folders['inbox'].glob`, `handle.read`, `json.dumps`, `path.is_relative_to`, `path.is_symlink`, `path.mkdir`, `path.rename`, `path.resolve`, `path.resolve().is_relative_to`, `path.stat`, `path.with_suffix`, `receiver.receive`, `result.update`, `results.append`, `root.mkdir`, `root.resolve`, `sorted`, `str`, `time.time`, `uuid4`

### receive

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/file_gateway.py:12](../../../api/wms_api_server/app/modules/integrations/infrastructure/file_gateway.py#L12)

```python
receive(self, raw: bytes, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### __init__

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/outbox_delivery.py:9](../../../api/wms_api_server/app/modules/integrations/infrastructure/outbox_delivery.py#L9)

```python
__init__(self, gateway: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### claim

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/outbox_delivery.py:12](../../../api/wms_api_server/app/modules/integrations/infrastructure/outbox_delivery.py#L12)

```python
claim(self, worker: str, target: str | None, seconds: int=300) -> dict[str, Any] | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.callproc`, `cur.var`, `read_oracle_json`, `result.getvalue`, `self.gateway.transaction`

### event

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/outbox_delivery.py:21](../../../api/wms_api_server/app/modules/integrations/infrastructure/outbox_delivery.py#L21)

```python
event(self, event_id: int) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### begin

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/outbox_delivery.py:28](../../../api/wms_api_server/app/modules/integrations/infrastructure/outbox_delivery.py#L28)

```python
begin(self, claim: dict[str, Any], event: dict[str, Any], adapter: RegulatoryAdapter) -> int
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.callproc`, `cur.var`, `event.get`, `int`, `payload.setvalue`, `request.getvalue`, `self.gateway.transaction`, `str`, `str(event.get('target_system') or 'INTERNAL').upper`

### finish

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/outbox_delivery.py:40](../../../api/wms_api_server/app/modules/integrations/infrastructure/outbox_delivery.py#L40)

```python
finish(self, claim: dict[str, Any], request_id: int, body: dict[str, Any]) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.callproc`, `cur.var`, `json.dumps`, `payload.setvalue`, `read_oracle_json`, `result.getvalue`, `self.gateway.transaction`

### retry

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/outbox_delivery.py:50](../../../api/wms_api_server/app/modules/integrations/infrastructure/outbox_delivery.py#L50)

```python
retry(self, event_id: int, actor: str, reason: str | None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `cur.callproc`, `self.gateway.transaction`

### __init__

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/outbox_response_journal.py:15](../../../api/wms_api_server/app/modules/integrations/infrastructure/outbox_response_journal.py#L15)

```python
__init__(self, root: Path | None=None) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Path`, `Path(__file__).resolve`, `ValueError`, `os.getenv`, `self.root.is_symlink`, `self.root.resolve`, `str`

### ready

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/outbox_response_journal.py:24](../../../api/wms_api_server/app/modules/integrations/infrastructure/outbox_response_journal.py#L24)

```python
ready(self) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`, `ValueError`, `entry.name.endswith`, `handle.fileno`, `handle.flush`, `handle.write`, `linked.exists`, `linked.unlink`, `os.fsync`, `os.link`, `os.scandir`, `path.is_symlink`, `path.mkdir`, `probe.open`, `probe.unlink`, `probe.with_suffix`, `uuid4`

### _owner

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/outbox_response_journal.py:48](../../../api/wms_api_server/app/modules/integrations/infrastructure/outbox_response_journal.py#L48)

```python
_owner(self, key: str) -> Path
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `directory.is_symlink`, `directory.mkdir`

### save

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/outbox_response_journal.py:55](../../../api/wms_api_server/app/modules/integrations/infrastructure/outbox_response_journal.py#L55)

```python
save(self, claim: dict[str, Any], request_id: int, target: str, body: dict[str, Any], simulation: bool, real_ack: bool) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`, `ValueError`, `f"{claim['event_outbox_id']}:{claim['claim_version']}:{request_id}".encode`, `handle.fileno`, `handle.flush`, `handle.write`, `json.dumps`, `json.dumps(record, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode`, `len`, `os.fsync`, `os.link`, `path.is_symlink`, `path.read_bytes`, `range`, `sha256`, `sha256(f"{claim['event_outbox_id']}:{claim['claim_version']}:{request_id}".encode()).hexdigest`, `temporary.exists`, `temporary.open`, `temporary.unlink`, `uuid4`

### finalize

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/outbox_response_journal.py:91](../../../api/wms_api_server/app/modules/integrations/infrastructure/outbox_response_journal.py#L91)

```python
finalize(self, key: str, delivery: OutboxDelivery) -> dict[str, Any] | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`, `ValueError`, `any`, `delivery.finish`, `directory_owner`, `f"{claim['event_outbox_id']}:{claim['claim_version']}:{record['request_id']}".encode`, `handle.read`, `json.loads`, `len`, `path.exists`, `path.is_symlink`, `path.open`, `path.unlink`, `record['body'].get`, `self._owner`, `sha256`, `sha256(f"{claim['event_outbox_id']}:{claim['claim_version']}:{record['request_id']}".encode()).hexdigest`

### recover_one

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/outbox_response_journal.py:117](../../../api/wms_api_server/app/modules/integrations/infrastructure/outbox_response_journal.py#L117)

```python
recover_one(self, delivery: OutboxDelivery, target: str | None) -> dict[str, Any] | None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Path`, `RuntimeError`, `ValueError`, `entry.is_symlink`, `entry.name.endswith`, `handle.read`, `json.loads`, `len`, `os.scandir`, `path.open`, `record['target_system'].upper`, `self.finalize`, `self.pending.exists`, `target.upper`

### __init__

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/receipt_acknowledgements.py:12](../../../api/wms_api_server/app/modules/integrations/infrastructure/receipt_acknowledgements.py#L12)

```python
__init__(self, gateway: OracleGateway) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### receive

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/receipt_acknowledgements.py:15](../../../api/wms_api_server/app/modules/integrations/infrastructure/receipt_acknowledgements.py#L15)

```python
receive(self, raw: bytes, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(node.text or '').strip`, `ET.fromstring`, `IdocConflict`, `LookupError`, `ValueError`, `cur.execute`, `cur.fetchone`, `cur.setinputsizes`, `fields.get`, `fields.get('ExternalDocumentId', '').encode`, `fields[name].encode`, `json.dumps`, `json.loads`, `len`, `local_name`, `payload.get`, `raw.decode`, `root.get`, `self._text`, `self.gateway.transaction`, `sha256`, `sha256(raw).hexdigest`, `xml.upper`

### list_events

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/receipt_acknowledgements.py:69](../../../api/wms_api_server/app/modules/integrations/infrastructure/receipt_acknowledgements.py#L69)

```python
list_events(self, limit: int) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.gateway.fetch_all`

### retry

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/receipt_acknowledgements.py:72](../../../api/wms_api_server/app/modules/integrations/infrastructure/receipt_acknowledgements.py#L72)

```python
retry(self, event_id: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `IdocConflict`, `self.gateway.execute`

### _text

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/receipt_acknowledgements.py:79](../../../api/wms_api_server/app/modules/integrations/infrastructure/receipt_acknowledgements.py#L79)

```python
_text(value: Any) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `hasattr`, `value.read`

### __init__

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/receipt_outbox.py:13](../../../api/wms_api_server/app/modules/integrations/infrastructure/receipt_outbox.py#L13)

```python
__init__(self, gateway: OracleGateway) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### export

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/receipt_outbox.py:16](../../../api/wms_api_server/app/modules/integrations/infrastructure/receipt_outbox.py#L16)

```python
export(self, directory: Path, limit: int=20, event_ids: tuple[str, ...] | None=None) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `''.join`, `','.join`, `(raw if isinstance(raw, dict) else json.loads(raw)).items`, `ET.Element`, `ET.SubElement`, `ET.tostring`, `ValueError`, `any`, `child.set`, `cur.execute`, `cur.fetchone`, `directory.mkdir`, `directory.resolve`, `enumerate`, `exported.append`, `file.fileno`, `file.flush`, `file.write`, `hasattr`, `isinstance`, `json.dumps`, `json.loads`, `key.split`, `len`, `os.fsync`, `os.replace`, `part.capitalize`, `range`, `row[0].encode`, `row[2].read`, `self.gateway.transaction`, `sha256`, `sha256(body).hexdigest`, `sha256(row[0].encode()).hexdigest`, `str` (остальные вызовы — в исходнике)

### build_regulatory_adapter

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/regulatory_runtime.py:41](../../../api/wms_api_server/app/modules/integrations/infrastructure/regulatory_runtime.py#L41)

```python
build_regulatory_adapter() -> RegulatoryAdapter
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `DisabledRegulatoryAdapter`, `MockRegulatoryAdapter`, `os.environ.get`, `os.environ.get('RETAILCASE_REGULATORY_MODE', 'DISABLED').strip`, `os.environ.get('RETAILCASE_REGULATORY_MODE', 'DISABLED').strip().upper`

### regulatory_runtime_status

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/regulatory_runtime.py:47](../../../api/wms_api_server/app/modules/integrations/infrastructure/regulatory_runtime.py#L47)

```python
regulatory_runtime_status() -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `build_regulatory_adapter`, `getattr`, `os.environ.get`, `os.environ.get('RETAILCASE_REGULATORY_MODE', 'DISABLED').strip`, `os.environ.get('RETAILCASE_REGULATORY_MODE', 'DISABLED').strip().upper`

### __init__

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/regulatory_runtime.py:14](../../../api/wms_api_server/app/modules/integrations/infrastructure/regulatory_runtime.py#L14)

```python
__init__(self, requested_mode: str='DISABLED') -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `{'DISABLED': ('REGULATORY_DISABLED', 'Обмен отключён. Реальная отправка будет доступна после реализации интеграционного шлюза.'), 'REAL': ('PRODUCTION_CONNECTOR_NOT_IMPLEMENTED', 'Настроить интеграционный шлюз после его реализации. По решению владельца шлюз реализуется отдельно позже; одного URL или сертификата сейчас недостаточно.'), 'MOCK': ('MOCK_NOT_ALLOWED', 'Имитация не разрешена. Только для тестового стенда требуются RETAILCASE_REGULATORY_MODE=MOCK и RETAILCASE_ALLOW_REGULATORY_MOCK=1.')}.get`

### send

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/regulatory_runtime.py:23](../../../api/wms_api_server/app/modules/integrations/infrastructure/regulatory_runtime.py#L23)

```python
send(self, event: dict[str, Any]) -> RegulatoryResponse
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RuntimeError`

### send

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/regulatory_runtime.py:33](../../../api/wms_api_server/app/modules/integrations/infrastructure/regulatory_runtime.py#L33)

```python
send(self, event: dict[str, Any]) -> RegulatoryResponse
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `RegulatoryResponse`, `datetime.now`, `datetime.now(UTC).isoformat`, `event.get`, `json.dumps`, `str`, `str(event.get('target_system') or 'INTERNAL').upper`

### __init__

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/store_returns.py:7](../../../api/wms_api_server/app/modules/integrations/infrastructure/store_returns.py#L7)

```python
__init__(self, post: Callable[[str, str, dict[str, Any], dict[str, Any], str], dict[str, Any]]) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### receive

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/store_returns.py:10](../../../api/wms_api_server/app/modules/integrations/infrastructure/store_returns.py#L10)

```python
receive(self, raw: bytes, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `read_store_return`, `self.post`, `str`

### __init__

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/supply_amendments.py:8](../../../api/wms_api_server/app/modules/integrations/infrastructure/supply_amendments.py#L8)

```python
__init__(self, cursor: oracledb.Cursor) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### prepare

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/supply_amendments.py:11](../../../api/wms_api_server/app/modules/integrations/infrastructure/supply_amendments.py#L11)

```python
prepare(self, order_id: str, naklad_id: int, order: dict) -> dict[str, tuple]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `IdocConflict`, `cur.execute`, `cur.fetchall`, `cur.fetchone`, `previous.items`

### validate_quantity

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/supply_amendments.py:43](../../../api/wms_api_server/app/modules/integrations/infrastructure/supply_amendments.py#L43)

```python
validate_quantity(self, order_id: str, line_number: str, base: str, quantity: Decimal) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `IdocConflict`, `self.cur.execute`, `self.cur.fetchone`

### refresh_header

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/supply_amendments.py:53](../../../api/wms_api_server/app/modules/integrations/infrastructure/supply_amendments.py#L53)

```python
refresh_header(self, order_id: str, naklad_id: int) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `int`, `self.cur.execute`, `self.cur.fetchone`

### __init__

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/supply_line_writer.py:11](../../../api/wms_api_server/app/modules/integrations/infrastructure/supply_line_writer.py#L11)

```python
__init__(self, cursor: Any) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### normalize

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/supply_line_writer.py:14](../../../api/wms_api_server/app/modules/integrations/infrastructure/supply_line_writer.py#L14)

```python
normalize(self, order: str, lines: list[dict], previous: dict, sender: str) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `IdocConflict`, `SupplyAmendments`, `SupplyAmendments(self.cur).validate_quantity`, `ValueError`, `convert_sap_source_quantity`, `len`, `normalized.append`, `previous.get`, `read_oracle_json`, `self.cur.execute`, `self.cur.fetchall`, `self.cur.fetchone`

### write

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/supply_line_writer.py:34](../../../api/wms_api_server/app/modules/integrations/infrastructure/supply_line_writer.py#L34)

```python
write(self, order: str, document: int, lines: list[dict], previous: dict, sender: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `Decimal`, `IdocConflict`, `ValueError`, `dict`, `grouped.items`, `grouped.setdefault`, `len`, `previous.get`, `self.cur.execute`, `self.cur.fetchall`, `self.cur.fetchone`, `self.normalize`

### __init__

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/supply_orders.py:19](../../../api/wms_api_server/app/modules/integrations/infrastructure/supply_orders.py#L19)

```python
__init__(self, gateway: OracleGateway) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: 

### receive

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/supply_orders.py:22](../../../api/wms_api_server/app/modules/integrations/infrastructure/supply_orders.py#L22)

```python
receive(self, raw: bytes, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `IdocConflict`, `RuntimeError`, `range`, `self._receive`, `str`

### _receive

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/supply_orders.py:33](../../../api/wms_api_server/app/modules/integrations/infrastructure/supply_orders.py#L33)

```python
_receive(self, raw: bytes, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `IdocConflict`, `SupplyAmendments`, `SupplyAmendments(cur).prepare`, `SupplyAmendments(cur).refresh_header`, `aggregate['code'].encode`, `assert_supply_scope`, `cur.execute`, `cur.fetchone`, `cur.setinputsizes`, `json.dumps`, `len`, `read_oracle_json`, `read_supply_order`, `self._destination`, `self._lines`, `sha256`, `sha256(aggregate['code'].encode()).hexdigest`, `supply_transaction`, `uuid4`

### _destination

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/supply_orders.py:94](../../../api/wms_api_server/app/modules/integrations/infrastructure/supply_orders.py#L94)

```python
_destination(self, cur: oracledb.Cursor, order: dict) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `cur.execute`, `cur.fetchall`, `len`

### _lines

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/supply_orders.py:106](../../../api/wms_api_server/app/modules/integrations/infrastructure/supply_orders.py#L106)

```python
_lines(self, cur: oracledb.Cursor, order_id: str, naklad_id: int, lines: list[dict], previous: dict, sender: str) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `SupplyLineWriter`, `SupplyLineWriter(cur).write`

### _text

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/supply_orders.py:111](../../../api/wms_api_server/app/modules/integrations/infrastructure/supply_orders.py#L111)

```python
_text(value: Any) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `hasattr`, `value.read`

### list

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/supply_orders.py:114](../../../api/wms_api_server/app/modules/integrations/infrastructure/supply_orders.py#L114)

```python
list(self, warehouse_id: int | None, limit: int, actor: str) -> list[dict]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `list_supplies`

### by_receipt_document

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/supply_orders.py:118](../../../api/wms_api_server/app/modules/integrations/infrastructure/supply_orders.py#L118)

```python
by_receipt_document(self, document_id: int, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `supply_detail`

### get

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/supply_orders.py:122](../../../api/wms_api_server/app/modules/integrations/infrastructure/supply_orders.py#L122)

```python
get(self, order_id: str, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `supply_detail`

### receipt_history

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/supply_orders.py:126](../../../api/wms_api_server/app/modules/integrations/infrastructure/supply_orders.py#L126)

```python
receipt_history(self, order_id: str, limit: int, after: str | None, actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `receipt_history`

### pallet_plan

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/supply_orders.py:130](../../../api/wms_api_server/app/modules/integrations/infrastructure/supply_orders.py#L130)

```python
pallet_plan(self, order_id: str, body: dict[str, Any], actor: str) -> dict
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `pallet_plan`

### rows

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/supply_reads.py:6](../../../api/wms_api_server/app/modules/integrations/infrastructure/supply_reads.py#L6)

```python
rows(cur: Any) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `column[0].lower`, `cur.fetchall`, `dict`, `zip`

### scope

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/supply_reads.py:11](../../../api/wms_api_server/app/modules/integrations/infrastructure/supply_reads.py#L11)

```python
scope(cur: Any, actor: str) -> tuple[int | None, bool]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `PermissionError`, `bool`, `cur.execute`, `cur.fetchone`

### allowed

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/supply_reads.py:20](../../../api/wms_api_server/app/modules/integrations/infrastructure/supply_reads.py#L20)

```python
allowed(ware: int | None, own: int | None, global_admin: bool) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `PermissionError`

### list_supplies

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/supply_reads.py:25](../../../api/wms_api_server/app/modules/integrations/infrastructure/supply_reads.py#L25)

```python
list_supplies(gateway: Any, warehouse: int | None, limit: int, actor: str) -> list[dict[str, Any]]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `allowed`, `cur.execute`, `gateway.transaction`, `getattr`, `rows`, `scope`

### supply_detail

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/supply_reads.py:44](../../../api/wms_api_server/app/modules/integrations/infrastructure/supply_reads.py#L44)

```python
supply_detail(gateway: Any, order: str | None, document: int | None, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `(remaining / norm).to_integral_value`, `Decimal`, `LookupError`, `ValueError`, `allowed`, `cur.execute`, `cur.fetchall`, `gateway.transaction`, `getattr`, `header.get`, `int`, `len`, `line.pop`, `max`, `min`, `rows`, `scope`, `str`

### pallet_plan

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/supply_reads.py:94](../../../api/wms_api_server/app/modules/integrations/infrastructure/supply_reads.py#L94)

```python
pallet_plan(gateway: Any, order: str, body: dict[str, Any], actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ValueError`, `body.get`, `json.dumps`, `json.dumps([source['order_id'], source['revision'], source['ware_id'], line['line_number'], line['planned_qty'], line['accepted_qty'], line['norma_ukladki']], separators=(',', ':'), ensure_ascii=False).encode`, `len`, `propose_receipt_layout`, `sha256`, `sha256(json.dumps([source['order_id'], source['revision'], source['ware_id'], line['line_number'], line['planned_qty'], line['accepted_qty'], line['norma_ukladki']], separators=(',', ':'), ensure_ascii=False).encode()).hexdigest`, `supply_detail`

### receipt_history

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/supply_receipt_history.py:7](../../../api/wms_api_server/app/modules/integrations/infrastructure/supply_receipt_history.py#L7)

```python
receipt_history(gateway: Any, order: str, limit: int, after: str | None, actor: str) -> dict[str, Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `TransactionGateway`, `ValueError`, `cur.execute`, `cur.fetchone`, `gateway.transaction`, `getattr`, `len`, `rows`, `supply_detail`

### supply_transaction

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/supply_scope.py:7](../../../api/wms_api_server/app/modules/integrations/infrastructure/supply_scope.py#L7)

```python
supply_transaction(gateway: Any, actor: str, warehouse: int, sender: str, order: str, message: str) -> Iterator[Any]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `PermissionError`, `cur.callproc`, `gateway.transaction`, `getattr`

### assert_supply_scope

[Исходник: api/wms_api_server/app/modules/integrations/infrastructure/supply_scope.py:22](../../../api/wms_api_server/app/modules/integrations/infrastructure/supply_scope.py#L22)

```python
assert_supply_scope(cur: Any, actor: str, warehouse: int) -> None
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `PermissionError`, `cur.callproc`, `getattr`

### build_artmas_service

[Исходник: api/wms_api_server/app/modules/integrations/public.py:14](../../../api/wms_api_server/app/modules/integrations/public.py#L14)

```python
build_artmas_service() -> ArtmasIngestion
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `ArticleMasterApply`, `ArtmasInbox`, `ArtmasIngestion`, `OracleGateway`

### build_supply_service

[Исходник: api/wms_api_server/app/modules/integrations/public.py:19](../../../api/wms_api_server/app/modules/integrations/public.py#L19)

```python
build_supply_service() -> SupplyOrders
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `SupplyOrders`

### build_receipt_exporter

[Исходник: api/wms_api_server/app/modules/integrations/public.py:23](../../../api/wms_api_server/app/modules/integrations/public.py#L23)

```python
build_receipt_exporter() -> ReceiptOutbox
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `ReceiptOutbox`

### build_acknowledgements

[Исходник: api/wms_api_server/app/modules/integrations/public.py:27](../../../api/wms_api_server/app/modules/integrations/public.py#L27)

```python
build_acknowledgements() -> ReceiptAcknowledgements
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `OracleGateway`, `ReceiptAcknowledgements`

### build_sap_store_returns

[Исходник: api/wms_api_server/app/modules/integrations/public.py:40](../../../api/wms_api_server/app/modules/integrations/public.py#L40)

```python
build_sap_store_returns(post: Callable[[str, str, dict[str, Any], dict[str, Any], str], dict[str, Any]]) -> SapStoreReturnsPort
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `SapStoreReturns`
