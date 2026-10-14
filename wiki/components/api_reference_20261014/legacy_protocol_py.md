# Методы: legacy_protocol.py

### parse_legacy_payload

[Исходник: api/wms_api_server/app/legacy_protocol.py:16](../../../api/wms_api_server/app/legacy_protocol.py#L16)

```python
parse_legacy_payload(payload: str) -> list[LegacyBlock]
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LegacyBlock`, `blocks.append`, `part.split`, `payload.split`

### encode_legacy_blocks

[Исходник: api/wms_api_server/app/legacy_protocol.py:33](../../../api/wms_api_server/app/legacy_protocol.py#L33)

```python
encode_legacy_blocks(blocks: list[LegacyBlock]) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `''.join`, `encode_legacy_block`

### encode_legacy_block

[Исходник: api/wms_api_server/app/legacy_protocol.py:37](../../../api/wms_api_server/app/legacy_protocol.py#L37)

```python
encode_legacy_block(block: LegacyBlock) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `'|'.join`, `_escape`, `block.values.items`, `parts.append`

### fault

[Исходник: api/wms_api_server/app/legacy_protocol.py:44](../../../api/wms_api_server/app/legacy_protocol.py#L44)

```python
fault(reason: str) -> LegacyBlock
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LegacyBlock`

### zero

[Исходник: api/wms_api_server/app/legacy_protocol.py:48](../../../api/wms_api_server/app/legacy_protocol.py#L48)

```python
zero() -> LegacyBlock
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `LegacyBlock`

### decode_tcp_frame

[Исходник: api/wms_api_server/app/legacy_protocol.py:52](../../../api/wms_api_server/app/legacy_protocol.py#L52)

```python
decode_tcp_frame(data: bytes) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `data[40:40 + payload_length].decode`, `data[:40].decode`, `int`

### encode_tcp_frame

[Исходник: api/wms_api_server/app/legacy_protocol.py:58](../../../api/wms_api_server/app/legacy_protocol.py#L58)

```python
encode_tcp_frame(payload: str) -> bytes
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `len`, `payload.encode`, `str`, `str(len(payload_bytes)).zfill`, `str(len(payload_bytes)).zfill(20).encode`

### _escape

[Исходник: api/wms_api_server/app/legacy_protocol.py:64](../../../api/wms_api_server/app/legacy_protocol.py#L64)

```python
_escape(value: object) -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `str`, `str(value if value is not None else '').replace`, `str(value if value is not None else '').replace('|', '!').replace`

### get

[Исходник: api/wms_api_server/app/legacy_protocol.py:12](../../../api/wms_api_server/app/legacy_protocol.py#L12)

```python
get(self, key: str, default: str='') -> str
```

Docstring отсутствует. Назначение уточняется по реализации и сценарию вызывающего блока.

Вызывает: `self.values.get`
