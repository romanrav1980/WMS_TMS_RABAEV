"""Unambiguous wire keys sorted by rank and UTF-8 bytes, never database NLS."""
from dataclasses import dataclass

RESOURCE_RANKS = {"OP": 10, "ROW": 20, "HU": 30, "SLOT": 40,
                  "STOCK": 50, "UNIT": 60, "ALIAS": 70, "UNIQUE": 70}


@dataclass(frozen=True)
class StockResource:
    kind: str
    parts: tuple[str, ...]

    def encoded(self) -> bytes:
        if self.kind not in RESOURCE_RANKS or not self.parts:
            raise ValueError("Unknown or empty resource key")
        result = b""
        for component in ("2", self.kind, *self.parts):
            if not isinstance(component, str) or not component or "\x00" in component:
                raise ValueError("Resource components must be nonempty strings")
            raw = component.encode("utf-8")
            result += str(len(raw)).encode("ascii") + b":" + raw
        if len(result) > 1000:
            raise ValueError("Resource key exceeds 1000 bytes; truncation forbidden")
        return result

    def wire(self) -> dict:
        return {"rank": RESOURCE_RANKS[self.kind], "key_hex": self.encoded().hex().upper()}


def ordered_resources(resources: list[StockResource]) -> list[dict]:
    keys = {(RESOURCE_RANKS[item.kind], item.encoded()) for item in resources}
    return [{"rank": rank, "key_hex": key.hex().upper()} for rank, key in sorted(keys)]
