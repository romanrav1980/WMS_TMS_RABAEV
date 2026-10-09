"""Configuration writers take the exclusive fence before any row lock or write."""
from contextlib import contextmanager


@contextmanager
def configuration_transaction(gateway, label: str, actor: str, permission: str):
    with gateway.transaction(label) as cursor:
        entered = False
        try:
            cursor.execute("begin RRL_STOCK_CONFIG_API.begin_change(:actor,:permission);end;",
                           actor=actor, permission=permission)
            entered = True
            yield cursor
        finally:
            if entered:
                cursor.execute("begin RRL_STOCK_CONFIG_API.end_change;end;")
