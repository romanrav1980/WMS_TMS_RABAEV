from collections.abc import Iterator
import oracledb
from ....oracle_gateway import OracleGateway
from ....transaction_gateway import TransactionGateway
"""Placement metadata serializes with posting before taking legacy row locks."""
from contextlib import contextmanager


def begin_wave_metadata(gateway: OracleGateway | TransactionGateway, cursor: oracledb.Cursor,
                        wave: int, actor: str) -> bool:
    """Nested projection joins a native, source-bound step; ordinary callers keep legacy gates."""
    if getattr(gateway, "wave_continuation_scope", None) == (wave, actor):
        cursor.callproc("RRL_WAVE_CONTINUE_API.assert_context", [wave, actor])
        return False
    cursor.execute("begin RRL_STOCK_METADATA_TX.begin_change(:actor,'pick_wave_launch');end;", {"actor": actor})
    return True


@contextmanager
def receipt_task_metadata(gateway: OracleGateway | TransactionGateway, purpose: str, actor: str, permission: str) -> Iterator[oracledb.Cursor]:
    with gateway.transaction(purpose) as cursor:
        try:
            cursor.execute(
                "begin RRL_STOCK_METADATA_TX.begin_change(:actor,:permission); end;",
                {"actor": actor, "permission": permission},
            )
            # CONFIG X blocks stock admission before legacy document/slot writes.
            # It grants no effect context, so direct stock writes remain forbidden.
            yield cursor
        finally:
            cursor.execute("begin RRL_STOCK_METADATA_TX.end_change; end;")
