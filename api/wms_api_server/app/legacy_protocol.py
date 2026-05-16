from dataclasses import dataclass, field


FUNC_KEY = "FUNC"


@dataclass
class LegacyBlock:
    function_name: str
    values: dict[str, str] = field(default_factory=dict)

    def get(self, key: str, default: str = "") -> str:
        return self.values.get(key, default)


def parse_legacy_payload(payload: str) -> list[LegacyBlock]:
    blocks: list[LegacyBlock] = []
    current: LegacyBlock | None = None

    for part in payload.split("|"):
        if not part or "=" not in part:
            continue
        key, value = part.split("=", 1)
        if key == FUNC_KEY:
            current = LegacyBlock(function_name=value)
            blocks.append(current)
        elif current is not None:
            current.values[key] = value

    return blocks


def encode_legacy_blocks(blocks: list[LegacyBlock]) -> str:
    return "".join(encode_legacy_block(block) for block in blocks)


def encode_legacy_block(block: LegacyBlock) -> str:
    parts = [f"{FUNC_KEY}={_escape(block.function_name)}"]
    for key, value in block.values.items():
        parts.append(f"{_escape(key)}={_escape(value)}")
    return "|".join(parts) + "|"


def fault(reason: str) -> LegacyBlock:
    return LegacyBlock("FAULT", {"REASON": reason})


def zero() -> LegacyBlock:
    return LegacyBlock("ZERO", {})


def decode_tcp_frame(data: bytes) -> str:
    header = data[:40].decode("utf-16-le")
    payload_length = int(header)
    return data[40 : 40 + payload_length].decode("utf-16-le")


def encode_tcp_frame(payload: str) -> bytes:
    payload_bytes = payload.encode("utf-16-le")
    header = str(len(payload_bytes)).zfill(20).encode("utf-16-le")
    return header + payload_bytes


def _escape(value: object) -> str:
    return str(value if value is not None else "").replace("|", "!").replace("=", "#")
