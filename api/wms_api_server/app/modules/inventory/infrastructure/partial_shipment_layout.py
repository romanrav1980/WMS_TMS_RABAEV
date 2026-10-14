"""Amend the existing unassigned ST from approved closed CASE facts; stock is unchanged."""
import hashlib
import json
from decimal import Decimal, localcontext
from fractions import Fraction
from typing import Any
import oracledb
from .metadata_transactions import receipt_task_metadata
from ..domain.fulfillment_fact import physical_composition
from ..domain.stock_quantity import convert_exact


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


class PartialShipmentLayout:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def _read(self, cursor: Any, task_id: int, identifier: str, locked: bool) -> dict:
        suffix = " for update" if locked else ""
        cursor.execute("select CUSTOMER_ORDER_ID,WARE_ID,SSCC,STATUS,CONTENT_VERSION,LEGACY_SBORKA_PALLET_ID "
                       "from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id" + suffix, {"id": task_id})
        case = cursor.fetchone()
        if not case:
            raise LookupError("CASE carrier not found")
        if case[3] not in {"WAIT_CONTROL", "CONTROL_IN_PROGRESS", "CONTROLLED", "READY_TO_SHIP"} or case[5] is not None:
            raise ValueError("Close the carrier and amend its layout before binding the ST")
        cursor.execute("select STATUS from RRL_CUSTOMER_ORDER where CUSTOMER_ORDER_ID=:id", {"id": case[0]})
        order = cursor.fetchone()
        if not order or order[0] == "CANCELLED":
            raise ValueError("Customer order unavailable")
        cursor.execute("select CASE_PICK_LINE_ID,STATUS,to_char(PICKED_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') "
                       " ,ARTICUL,to_char(PLANNED_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=:id order by CASE_PICK_LINE_ID fetch first 201 rows only",
                       {"id": task_id})
        lines = cursor.fetchall()
        if not 1 <= len(lines) <= 200 or any(line[1] not in {"PICKED", "SHORT_PICKED", "CANCELLED"} for line in lines):
            raise ValueError("All picking lines require a confirmed completion or approved shortage")
        cursor.execute("select count(*) from RRL_CASE_PICK_SHORT where CASE_PICK_TASK_ID=:id "
                       "and STATUS in('CREATED','PENDING_APPROVAL')", {"id": task_id})
        if cursor.fetchone()[0]:
            raise ValueError("Approve the pending shortage first")
        cursor.execute("select ID,WARE_ID,CONDITION,RETURN_SUPPLIER_ID,TRANSTASK_ID from RRL_SBORKA_PALLETS "
                       "where PALLET_UID=:p_uid" + suffix, {"p_uid": identifier})
        shipments = cursor.fetchmany(2)
        if len(shipments) != 1:
            raise ValueError("Existing ST missing or ambiguous")
        shipment = shipments[0]
        if shipment[1] != case[1] or (shipment[2] or 0) >= 2 or shipment[3] is not None:
            raise ValueError("ST warehouse/type/state conflict")
        if shipment[4] is not None:
            raise ValueError("Use the existing TMS to remove the ST from its trip before changing its layout")
        cursor.execute("select FULFILLMENT_ID,STATUS from RRL_CUSTOMER_ORDER_FULFILLMENT "
                       "where LEGACY_SBORKA_PALLET_ID=:sid and CUSTOMER_ORDER_ID=:oid and PALLET_UID=:p_uid" + suffix,
                       {"sid": shipment[0], "oid": case[0], "p_uid": identifier})
        fulfillments = cursor.fetchmany(2)
        if len(fulfillments) != 1 or fulfillments[0][1] != "PLANNED":
            raise ValueError("An unshipped prepared fulfillment is required")
        cursor.execute("""select h.LOT_UID,s.CELL,s.STOCK_VERSION,p.ARTICUL,s.BASE_UOM,
            to_char(s.REMAIN,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''),h.CASE_PICK_LINE_ID
            from RRL_CASE_CARRIER_LOT h join RRL_REMAINS s on s.UID_POLETA=h.LOT_UID
            join RRL_PALLETS p on p.UID_PALLET=h.LOT_UID where h.CASE_PICK_TASK_ID=:id and s.REMAIN>0
            order by h.LOT_UID,s.CELL fetch first 201 rows only""", {"id": task_id})
        physical = cursor.fetchall()
        if not 1 <= len(physical) <= 200:
            raise ValueError("Physical carrier composition is empty or exceeds 200 lots")
        with localcontext() as ctx:
            ctx.prec = 96
            by_line: dict[int, Decimal] = {}
            for lot, cell, version, article, base, qty, line_id in physical:
                by_line[line_id] = by_line.get(line_id, Decimal(0)) + Decimal(qty)
            if any(by_line.get(line_id, Decimal(0)) != Decimal(picked or "0") for line_id, status, picked, article, planned in lines):
                raise ValueError("Current physical carrier differs from confirmed picking facts")
        approved: dict[str, Decimal] = {}
        for line_id,status,picked,article,planned in lines:
            if status in {"SHORT_PICKED","CANCELLED"}:
                approved[article]=approved.get(article,Decimal(0))+Decimal(planned)-Decimal(picked or "0")
        composition, _, _ = physical_composition([(p[3], p[4], p[5]) for p in physical])
        cursor.execute("""select r.ID,r.ARTICUL,r.EI,to_char(r.QUANTITY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') QUANTITY,
            to_char(r.ORDER_WEIGHT,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') ORDER_WEIGHT,
            to_char(r.PACK_COUNT,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') PACK_COUNT,
            u.BASE_UOM,u.NUMERATOR,u.DENOMINATOR,u.BASE_SCALE,u.POLICY_VERSION
            from RRL_SBORKA_PALLET_ROWS r left join RRL_STOCK_UOM_CONVERSION u on u.ARTICUL=r.ARTICUL and u.INPUT_UOM=r.EI
             and u.POLICY_VERSION=(select max(POLICY_VERSION) from RRL_STOCK_UOM_CONVERSION where ARTICUL=r.ARTICUL and INPUT_UOM=r.EI)
            where r.PALLET_UID=:p_uid order by r.ID fetch first 201 rows only""", {"p_uid": identifier})
        document = cursor.fetchall()
        if not 1 <= len(document) <= 200 or len({r[1] for r in document}) != len(document):
            raise ValueError("At most one prepared ST row per SKU is supported")
        return {"task_id": task_id, "shipment_id": shipment[0], "fulfillment_id": fulfillments[0][0],
                "carrier_identifier": case[2], "content_version": case[4], "composition": composition,
                "approved_shortages":{a:str(q) for a,q in approved.items()},"physical_signature": _digest(physical), "layout_signature": _digest(document), "document": document}

    def preview(self, task_id: int, identifier: str) -> dict:
        with self.gateway.transaction("Read partial ST layout proposal") as cursor:
            state = self._read(cursor, task_id, identifier, False)
        result={key:value for key,value in state.items() if key!="document"}
        physical={line["article"]:line for line in state["composition"]}
        packages=[]
        for rid,article,unit,qty,weight,packs,base,num,den,scale,policy in state["document"]:
            picked=physical.get(article)
            if not picked:continue
            count=None
            if base and num is not None and den is not None and scale is not None and packs is not None:
                requested=convert_exact(qty,int(num),int(den),int(scale))
                exact=Fraction(Decimal(packs))*Fraction(Decimal(picked["quantity"]))/Fraction(requested)
                if exact.denominator==1 and exact.numerator>0:count=exact.numerator
            packages.append({**picked,"proposed_pack_count":count})
        result["package_counts"]=packages
        return result

    def prepare(self, task_id: int, body: dict, actor: str) -> dict:
        with receipt_task_metadata(self.gateway, "Partial existing ST after approved shortage", actor, "case_pick_short_approve") as cursor:
            cursor.execute("select CASE_PICK_TASK_ID,EVENT_TYPE,CREATED_BY,PAYLOAD_JSON from RRL_CASE_PICK_EVENT "
                           "where OFFLINE_EVENT_ID=:event", {"event": body["operation_id"]})
            old = cursor.fetchone()
            if old:
                if old[:3] != (task_id, "SHIPMENT_LAYOUT_ADJUSTED", actor):
                    raise ValueError("Shipment layout operation identity conflict")
                payload = old[3].read() if hasattr(old[3], "read") else old[3]
                saved = json.loads(payload)
                if saved["request"] != body:
                    raise ValueError("Shipment layout operation content conflict")
                return {**saved["result"], "idempotent": True}
            state = self._read(cursor, task_id, body["pallet_identifier"], True)
            if (state["carrier_identifier"] != body["scan_container"] or state["content_version"] != body["expected_content_version"]
                or state["physical_signature"] != body["expected_physical_signature"]
                or state["layout_signature"] != body["expected_layout_signature"]):
                raise ValueError("Carrier or prepared layout changed; refresh the proposal")
            physical = {line["article"]: line for line in state["composition"]}
            if len(physical)!=len(state["composition"]):
                raise ValueError("A SKU cannot mix different base units")
            actual_packs = body.get("actual_pack_counts", {})
            if set(actual_packs) - set(physical):
                raise ValueError("Package count supplied for an absent physical SKU")
            changes = []
            with localcontext() as ctx:
                ctx.prec = 96
                for rid, article, unit, qty, weight, packs, base, num, den, scale, policy in state["document"]:
                    if not base or num is None or den is None or scale is None:
                        raise ValueError("Prepared ST requires an exact unit policy")
                    requested = convert_exact(qty, int(num), int(den), int(scale))
                    picked = physical.pop(article, None)
                    if picked is None:
                        if Decimal(state["approved_shortages"].get(article,"0"))<requested:
                            raise ValueError("Missing document quantity requires an approved shortage for this carrier")
                        cursor.execute("delete from RRL_SBORKA_PALLET_ROWS where ID=:id", {"id": rid})
                        changes.append({"row_id": rid, "article": article, "removed": True})
                        continue
                    actual = Decimal(picked["quantity"])
                    if picked["base_uom"] != base or actual > requested:
                        raise ValueError("Physical quantity must not exceed the prepared ST demand")
                    if requested-actual>Decimal(state["approved_shortages"].get(article,"0")):
                        raise ValueError("Document reduction exceeds the approved shortage of this carrier")
                    proportion = Fraction(actual) / Fraction(requested)
                    if article in actual_packs:
                        count = actual_packs[article]
                    elif packs is not None:
                        exact_count = Fraction(Decimal(packs)) * proportion
                        if exact_count.denominator != 1:
                            raise ValueError("Specify the actual whole package count for this partial SKU")
                        count = exact_count.numerator
                    else:
                        raise ValueError("Specify the actual whole package count")
                    if not isinstance(count, int) or isinstance(count, bool) or count < 1:
                        raise ValueError("Physical package count must be a positive integer")
                    if weight is None or Decimal(weight) <= 0:
                        raise ValueError("Existing transport weight norm is required")
                    estimated_weight = (Decimal(weight) * actual / requested).quantize(Decimal("0.000000001"))
                    if estimated_weight <= 0:
                        raise ValueError("Transport weight norm cannot represent this quantity")
                    cursor.execute("""update RRL_SBORKA_PALLET_ROWS set ORIGINAL_QUANTITY=case when nvl(ORIGINAL_QUANTITY,0)=0 then QUANTITY else ORIGINAL_QUANTITY end,
                        ORIGINAL_ORDER_WEIGHT=case when nvl(ORIGINAL_ORDER_WEIGHT,0)=0 then ORDER_WEIGHT else ORIGINAL_ORDER_WEIGHT end,EI=:base,QUANTITY=:qty,
                        ORDER_WEIGHT=:weight,PACK_COUNT=:packs where ID=:id""",
                        {"base": base, "qty": actual, "weight": estimated_weight, "packs": count, "id": rid})
                    changes.append({"row_id": rid, "article": article, "unit": base, "quantity": str(actual),
                                    "package_count": count, "estimated_order_weight": str(estimated_weight)})
                if physical:
                    raise ValueError("Physical SKU absent from the prepared ST")
            result = {"case_pick_task_id": task_id, "pallet_identifier": body["pallet_identifier"],
                      "status": "LAYOUT_PREPARED", "composition": state["composition"],
                      "changes": changes, "weight_basis": "PROPORTIONAL_NORM", "idempotent": False}
            event = json.dumps({"request": body, "result": result, "before": state["document"]}, separators=(",", ":"))
            cursor.setinputsizes(payload=oracledb.DB_TYPE_CLOB)
            cursor.execute("insert into RRL_CASE_PICK_EVENT(CASE_PICK_EVENT_ID,CASE_PICK_TASK_ID,EVENT_TYPE,OFFLINE_EVENT_ID,"
                           "PAYLOAD_JSON,CREATED_BY) values(RRL_CASE_PICK_EVENT_SQ.nextval,:id,'SHIPMENT_LAYOUT_ADJUSTED',:event,:payload,:actor)",
                           {"id": task_id, "event": body["operation_id"], "payload": event, "actor": actor})
        return result
