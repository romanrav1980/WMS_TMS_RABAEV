"""Read original accepted tare returns and immutable load recovery lineage."""
from typing import Any
from ..contracts_tare import TareError


def recovery_candidates(gateway: Any, load_operation_id: str, actor: str) -> list[dict[str, Any]]:
    rows = gateway.fetch_all("""
        select distinct lf.LOAD_OPERATION_ID,lf.CONTENT_VERSION EXPECTED_LOAD_VERSION,
               lf.WARE_ID,lf.STATUS LOAD_STATUS,b.OPERATION_ID ORIGINAL_BOOKING_OPERATION_ID,
               b.PALLET_TYPE_ID,typ.PALLET_TYPE_NAME,b.PLACE_KIND,b.PLACE_ID,
               coalesce(ct.SSCC,json_value(lf.COMPOSITION_JSON,'$.nodes[0].sscc'),b.PLACE_ID) PLACE_IDENTIFIER,back.OPERATION_ID RETURN_OFFER_OPERATION_ID,
               accepted.OPERATION_ID RETURN_ACCEPT_OPERATION_ID,
               accepted.ACCEPTED_BY,accepted.ACCEPTED_AT,
               recovery.OPERATION_ID RECOVERY_OPERATION_ID,replacement.STATUS RECOVERY_BOOK_STATUS
          from RRL_TT_HU_LOAD_FACT lf join RRL_TARE_OFFER_BOOK association
            on association.LOAD_OPERATION_ID=lf.LOAD_OPERATION_ID
          join RRL_TARE_BOOK b on b.OPERATION_ID=association.BOOK_OPERATION_ID
          join RRL_PALLET_TYPE typ on typ.PALLET_TYPE_ID=b.PALLET_TYPE_ID
          left join RRL_CASE_PICK_TASK ct on b.PLACE_KIND='CASE'
            and b.PLACE_ID=to_char(ct.CASE_PICK_TASK_ID,'TM9')
          join RRL_TARE_ACCEPT original_accept on original_accept.OPERATION_ID=b.CLOSED_OPERATION_ID
            and original_accept.OFFER_OPERATION_ID=association.OFFER_OPERATION_ID
          join RRL_TARE_OFFER outgoing on outgoing.OPERATION_ID=association.OFFER_OPERATION_ID
          join RRL_TARE_OFFER back on back.TT_ID=lf.TT_ID and back.VEHICLE_ID=lf.VEHICLE_ID
            and back.FROM_KIND='VEHICLE' and back.TO_KIND='WAREHOUSE'
            and back.FROM_BALANCE_KEY=outgoing.TO_BALANCE_KEY and back.TO_BALANCE_KEY=b.BALANCE_KEY
            and back.OWNER_WARE_ID=b.OWNER_WARE_ID and back.PALLET_TYPE_ID=b.PALLET_TYPE_ID
            and back.CONDITION_CODE='GOOD' and back.QUANTITY=1
            and back.OFFERED_AT>=original_accept.ACCEPTED_AT
          join RRL_TARE_ACCEPT accepted on accepted.OFFER_OPERATION_ID=back.OPERATION_ID
            and accepted.ACCEPTED_QTY=1 and accepted.SHORT_QTY=0
          left join RRL_TARE_LOAD_RECOVERY recovery
            on recovery.ORIGINAL_BOOK_OPERATION_ID=b.OPERATION_ID
            and recovery.RETURN_OFFER_OPERATION_ID=back.OPERATION_ID
          left join RRL_TARE_BOOK replacement on replacement.OPERATION_ID=recovery.OPERATION_ID
         where lf.LOAD_OPERATION_ID=:load_op and b.STATUS='TRANSFERRED'
           and exists(select 1 from RUSERS u where u.ID=:actor and nvl(u.DELETED,0)=0
             and (upper(trim(u.USER_GROUP))='GLOBAL_ADMIN' or u.WARE_ID=lf.WARE_ID
               or RRL_HAS_WRIGHT(u.ID,'tare_manage')=1))
         order by ORIGINAL_BOOKING_OPERATION_ID,RETURN_OFFER_OPERATION_ID fetch first 101 rows only
    """, {"load_op": load_operation_id, "actor": actor})
    if len(rows) > 100:
        raise TareError("TARE_RECOVERY_WINDOW_REQUIRED", "Разделите список подтверждённых возвратов", 409)
    return rows
