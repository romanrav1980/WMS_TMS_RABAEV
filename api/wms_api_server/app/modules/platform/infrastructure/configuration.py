"""Shared configuration transaction; Oracle authorizes the exclusive warehouse fence."""
from contextlib import contextmanager
from typing import Any,Iterator

@contextmanager
def stock_configuration_transaction(gateway: Any,label: str,actor: str,permission: str) -> Iterator[Any]:
    with gateway.transaction(label) as cursor:
        entered=False
        try:
            cursor.execute("begin RRL_STOCK_CONFIG_API.begin_change(:actor,:permission);end;",
                           {"actor":actor,"permission":permission})
            entered=True
            yield cursor
        finally:
            if entered:cursor.execute("begin RRL_STOCK_CONFIG_API.end_change;end;")
