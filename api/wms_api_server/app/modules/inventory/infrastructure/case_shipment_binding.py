from __future__ import annotations
from ....oracle_gateway import OracleGateway
from ....transaction_gateway import TransactionGateway
"""Attach the scanned physical carrier to an existing prepared ST; never create another ST."""
import json
from decimal import Decimal
import oracledb
from .metadata_transactions import receipt_task_metadata
from ..domain.fulfillment_fact import physical_composition
from ..domain.carrier_shipment import assert_matching_composition


def bind_case_shipment(gateway: OracleGateway | TransactionGateway, task_id: int, pallet_identifier: str, scan_container: str,
                       expected_version: int, actor: str) -> dict:
    with receipt_task_metadata(gateway, "Bind physical CASE carrier to existing ST", actor,
                               "case_pick_execute") as cur:
        cur.execute("select CASE_PICK_TASK_ID,CUSTOMER_ORDER_ID,WARE_ID,SSCC,STATUS,"
                    "CONTENT_VERSION,LEGACY_SBORKA_PALLET_ID from RRL_CASE_PICK_TASK "
                    "where CASE_PICK_TASK_ID=:id for update", {"id": task_id})
        task = cur.fetchone()
        if not task:
            raise LookupError("Case-pick task not found")
        if scan_container != task[3]:
            raise ValueError("Scan the actual carrier identifier")
        cur.execute("select ID,WARE_ID,CONDITION,RETURN_SUPPLIER_ID from RRL_SBORKA_PALLETS "
                    "where PALLET_UID=:p_uid for update", {"p_uid": pallet_identifier})
        shipments = cur.fetchmany(2)
        if len(shipments) > 1:
            raise ValueError("ST pallet identifier is ambiguous")
        shipment = shipments[0] if shipments else None
        if not shipment:
            raise LookupError("Existing ST pallet not found")
        cur.execute("select FULFILLMENT_ID,STATUS,PICKED_CASE_TASK_ID,PICKED_CONTENT_VERSION,FACT_COMPOSITION_JSON "
                    "from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=:sid "
                    "and PALLET_UID=:p_uid and CUSTOMER_ORDER_ID=:customer order by FULFILLMENT_ID for update",
                    {"sid":shipment[0],"p_uid":pallet_identifier,"customer":task[1]})
        fulfillments=cur.fetchmany(2)
        if len(fulfillments)!=1:
            raise ValueError("ST must have one fulfillment for this customer order")
        fulfillment=fulfillments[0]
        if task[6] is not None:
            if task[6] != shipment[0]:
                raise ValueError("Carrier is already bound to another ST pallet")
            if fulfillment[2]!=task_id or fulfillment[3]!=expected_version:
                raise ValueError("Bound physical composition version differs; reload the carrier")
            saved=fulfillment[4]
            saved=saved.read() if hasattr(saved,"read") else saved
            return {"case_pick_task_id":task_id,"pallet_identifier":pallet_identifier,
                    "status":"BOUND","fulfillment_status":fulfillment[1],
                    "physical_composition":json.loads(saved or "[]"),"idempotent":True}
        if task[4] not in {"WAIT_CONTROL", "CONTROL_IN_PROGRESS", "CONTROLLED", "READY_TO_SHIP"}:
            raise ValueError("Close the picked carrier before binding its shipment")
        if task[5] != expected_version:
            raise ValueError("Carrier content changed; reload it before binding")
        if shipment[1] != task[2] or shipment[3] is not None or (shipment[2] or 0) >= 2:
            raise ValueError("ST pallet warehouse/type/state does not match the carrier")
        cur.execute("select count(*) from RRL_CUSTOMER_ORDER_FULFILLMENT "
                    "where LEGACY_SBORKA_PALLET_ID=:sid and PALLET_UID=:p_uid "
                    "and CUSTOMER_ORDER_ID=:customer and STATUS in('PLANNED','PICKED')",
                    {"sid": shipment[0], "p_uid": pallet_identifier, "customer": task[1]})
        if cur.fetchone()[0] != 1:
            raise ValueError("ST pallet must be prepared for this customer order")
        cur.execute("select count(*) from RRL_CASE_PICK_TASK where LEGACY_SBORKA_PALLET_ID=:sid",
                    {"sid": shipment[0]})
        if cur.fetchone()[0]:
            raise ValueError("ST pallet is already bound to another physical carrier")
        cur.execute("select p.ARTICUL,s.BASE_UOM,to_char(s.REMAIN,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') "
                    "from RRL_CASE_CARRIER_LOT h join RRL_REMAINS s on s.UID_POLETA=h.LOT_UID "
                    "join RRL_PALLETS p on p.UID_PALLET=h.LOT_UID "
                    "where h.CASE_PICK_TASK_ID=:id and s.REMAIN>0 "
                    "order by h.LOT_UID,s.CELL fetch first 201 rows only", {"id": task_id})
        physical = cur.fetchall()
        cur.execute("select r.ARTICUL,to_char(r.QUANTITY,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''),"
                    "u.BASE_UOM,u.NUMERATOR,u.DENOMINATOR,u.BASE_SCALE "
                    "from RRL_SBORKA_PALLET_ROWS r left join RRL_STOCK_UOM_CONVERSION u "
                    "on u.ARTICUL=r.ARTICUL and u.INPUT_UOM=r.EI and u.POLICY_VERSION="
                    "(select max(p.POLICY_VERSION) from RRL_STOCK_UOM_CONVERSION p "
                    "where p.ARTICUL=r.ARTICUL and p.INPUT_UOM=r.EI) "
                    "where r.PALLET_UID=:p_uid order by r.ID fetch first 201 rows only",
                    {"p_uid": pallet_identifier})
        assert_matching_composition(physical, cur.fetchall())
        composition, quantity, unit=physical_composition(physical)
        if fulfillment[1]!="PLANNED":
            raise ValueError("Only a prepared unshipped fulfillment may receive a physical carrier")
        cur.execute("update RRL_CASE_PICK_TASK set LEGACY_SBORKA_PALLET_ID=:sid,"
                    "UPDATED_AT=systimestamp,UPDATED_BY=:actor where CASE_PICK_TASK_ID=:id",
                    {"sid": shipment[0], "actor": actor, "id": task_id})
        cur.setinputsizes(composition_json=oracledb.DB_TYPE_CLOB)
        cur.execute("update RRL_CUSTOMER_ORDER_FULFILLMENT set STATUS='PICKED',FACT_QTY=:qty,FACT_UOM=:unit,"
                    "FACT_COMPOSITION_JSON=:composition_json,PICKED_CASE_TASK_ID=:task_id,"
                    "PICKED_CONTENT_VERSION=:version,PICKED_AT=systimestamp,PICKED_BY=:actor,"
                    "UPDATED_AT=sysdate,UPDATED_BY=:actor where FULFILLMENT_ID=:fid",
                    {"qty":None if quantity is None else Decimal(quantity),"unit":unit,
                     "composition_json":json.dumps(composition,separators=(",",":")),"task_id":task_id,
                     "version":expected_version,"actor":actor,"fid":fulfillment[0]})
        event=json.dumps({"fulfillment_id":fulfillment[0],"pallet_identifier":pallet_identifier,
                          "content_version":expected_version,"composition":composition},separators=(",",":"))
        cur.setinputsizes(event_json=oracledb.DB_TYPE_CLOB)
        cur.execute("insert into RRL_CASE_PICK_EVENT(CASE_PICK_EVENT_ID,CASE_PICK_TASK_ID,EVENT_TYPE,"
                    "OFFLINE_EVENT_ID,PAYLOAD_JSON,CREATED_BY) values(RRL_CASE_PICK_EVENT_SQ.nextval,:task_id,"
                    "'SHIPMENT_BOUND',:event_id,:event_json,:actor)",
                    {"task_id":task_id,"event_id":f"CASE.BIND:{task_id}:{expected_version}:{shipment[0]}",
                     "event_json":event,"actor":actor})
        return {"case_pick_task_id":task_id,"pallet_identifier":pallet_identifier,"status":"BOUND",
                "fulfillment_status":"PICKED","physical_composition":composition,"idempotent":False}
