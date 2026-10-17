"""Driver return queue and current account authority in one read snapshot."""
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..contracts import StoreReceiptError


def driver_pending(gateway: Any, actor: str, task_id: int | None) -> list[dict[str, Any]]:
    try:
        with gateway.transaction("Current bound driver return queue READ ONLY") as cursor:
            cursor.execute("set transaction read only")
            cursor.execute("""select count(*) from RRL_TRANSPORT_DRIVER_USER b where b.USER_ID=:actor
                and b.ACTIVE=1 and RRL_DRIVER_SCOPE.allowed_account(:actor,b.DRIVER_ID)=1""", actor=actor)
            if cursor.fetchone()[0] == 0:
                raise StoreReceiptError("RETURN_CURRENT_BOUND_DRIVER_REQUIRED", "Нет текущего допуска водителя", 403)
            cursor.execute("""select h.OPERATION_ID HANDOVER_OPERATION_ID,h.PALLET_IDENTIFIER,t.TT_ID,t.VEHICLE_NUMBER,t.STORE_ADDR,t.RECEIVING_WARE_ID,
                RRL_STORE_RETURN_UNIT_CORE.approved_proof(t.APPROVAL_OPERATION_ID) MARKED_UNIT_CONTROL,
                to_char(h.GROSS_WEIGHT_KG,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') GROSS_WEIGHT_KG,h.PHYSICAL_PLACES,h.HANDED_BY
                from RRL_STORE_RETURN_HANDOVER h join RRL_STORE_RETURN_TRANSPORT t on t.OPERATION_ID=h.TRANSPORT_OPERATION_ID
                join RRL_TRANSPORT_DRIVER_USER b on b.DRIVER_ID=t.DRIVER_ID and b.ACTIVE=1 and b.USER_ID=:actor
                join RRL_TRANSPORT_TASK tt on tt.ID=t.TT_ID and tt.VODITEL_ID=t.DRIVER_ID
                    and tt.TRANSPORT=t.VEHICLE_NUMBER and nvl(tt.DELETED,0)=0
                where RRL_DRIVER_SCOPE.allowed_account(:actor,t.DRIVER_ID)=1 and(:trip is null or t.TT_ID=:trip)
                and not exists(select 1 from RRL_STORE_RETURN_PICKUP p where p.HANDOVER_OPERATION_ID=h.OPERATION_ID)
                order by h.HANDED_AT,h.OPERATION_ID fetch first 101 rows only""", actor=actor, trip=task_id)
            names = [column[0].lower() for column in cursor.description]
            rows = [dict(zip(names, row)) for row in cursor.fetchall()]
            if len(rows) > 100:
                raise StoreReceiptError("DRIVER_RETURN_BOUND_100", "Уточните рейс: более100 возвратов", 409)
            for row in rows:
                row["marked_unit_control"] = read_oracle_json(row["marked_unit_control"]) if row["marked_unit_control"] else None
            return rows
    except oracledb.DatabaseError as error:
        raise StoreReceiptError("DRIVER_RETURN_READ_UNAVAILABLE", "Очередь возвратов недоступна", 503) from error
