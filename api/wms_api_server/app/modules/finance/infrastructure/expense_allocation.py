from hashlib import sha256
from decimal import Decimal
from typing import Any
import json,oracledb
from ...platform.public import read_oracle_json
from ..contracts import LogisticsCostError
from ..domain.allocation import allocate_cents
from .finance_outbox import enqueue
from .cost_access import require_warehouse
from .expense_manifest import actual_goods

class ExpenseAllocation:
    def __init__(self,gateway: Any) -> None:
        self.gateway=gateway

    def allocate(self,operation_id: str,expense_id: str,actor: str) -> dict[str,Any]:
        try:return self._allocate(operation_id,expense_id,actor)
        except oracledb.DatabaseError as exc:
            code=getattr(exc.args[0],"code",0)
            if code==1:
                try:return self._allocate(operation_id,expense_id,actor)
                except oracledb.IntegrityError as conflict:raise LogisticsCostError("EXPENSE_ALREADY_ALLOCATED","Расход уже распределён") from conflict
            if 20800<=code<=20999:raise LogisticsCostError("EXPENSE_ALLOCATION_REJECTED",str(exc.args[0]).split("\n",1)[0],403 if code==20882 else 409) from exc
            raise

    def _allocate(self,op: str,expense: str,actor: str) -> dict[str,Any]:
        digest=sha256(json.dumps([expense,actor],separators=(",",":")).encode()).digest()
        with self.gateway.transaction("Allocate original confirmed trip expense") as cur:
            cur.execute("select OBJECT_KIND,OBJECT_ID,WARE_ID,to_char(AMOUNT,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''),CURRENCY,ADJUSTMENT_SIGN from RRL_LOGISTICS_EXPENSE where OPERATION_ID=:id for update",{"id":expense});source=cur.fetchone()
            if not source:raise LogisticsCostError("EXPENSE_NOT_FOUND","Расход не найден",404)
            kind,trip,ware,amount,currency,sign=source;amount=Decimal(amount);require_warehouse(cur,ware,actor,"calc_tt_price")
            cur.execute("select PAYLOAD_HASH,RESULT_JSON from RRL_LOGISTICS_EXP_ALLOCATION where OPERATION_ID=:op",{"op":op});old=cur.fetchone()
            if old:
                if old[0]!=digest:raise LogisticsCostError("EXPENSE_ALLOCATION_PAYLOAD_CONFLICT","Операция уже имеет другое содержание")
                return read_oracle_json(old[1])
            if kind!="TRIP":raise LogisticsCostError("EXPENSE_VEHICLE_NOT_ALLOCATED","Расход только автомобиля нельзя распределять на товар")
            cur.execute("select count(*)from RRL_LOGISTICS_EXP_ALLOCATION where EXPENSE_OPERATION_ID=:id",{"id":expense})
            if cur.fetchone()[0]:raise LogisticsCostError("EXPENSE_ALREADY_ALLOCATED","Расход уже распределён")
            cur.execute("select OPERATION_ID,DISTRIBUTION_BASIS from RRL_LOGISTICS_EXP_DECISION where EXPENSE_OPERATION_ID=:id and PHASE='FINANCE' and OUTCOME='APPROVE'",{"id":expense});decision=cur.fetchone()
            if not decision:raise LogisticsCostError("EXPENSE_FINANCE_APPROVAL_REQUIRED","Нужно подтверждение финансового контроля")
            finance,basis=decision;goods=actual_goods(cur,int(trip),int(ware),basis)
            shares=allocate_cents(Decimal(str(amount)),[(row["key"],row["basis_value"])for row in goods])
            lines=[{"load_operation_id":row["load_operation_id"],"pallet_identifier":row["uid"],"article":row["article"],"quantity":str(row["quantity"]),"base_uom":row["base_uom"],"weight_kg":str(row["weight_kg"]) if row["weight_kg"]is not None else None,"basis_value":str(row["basis_value"]),"amount":str(shares[row["key"]]*sign),"weight_source":row["weight_source"],"weight_box_uid":row["weight_box_uid"]}for row in goods]
            result={"operation_id":op,"expense_operation_id":expense,"status":"ALLOCATED","trip_id":trip,"amount":format(amount*sign,".2f"),"currency":currency,"basis":basis,"finance_operation_id":finance,"lines":lines,"stock_changed":False}
            cur.setinputsizes(result_body=oracledb.DB_TYPE_CLOB)
            cur.execute("insert into RRL_LOGISTICS_EXP_ALLOCATION(OPERATION_ID,PAYLOAD_HASH,EXPENSE_OPERATION_ID,FINANCE_OPERATION_ID,DISTRIBUTION_BASIS,AMOUNT,CURRENCY,ACTOR,RESULT_JSON)values(:op,:hash_value,:expense,:finance,:basis,:amount,:currency,:actor,:result_body)",{"op":op,"hash_value":digest,"expense":expense,"finance":finance,"basis":basis,"amount":amount,"currency":currency,"actor":actor,"result_body":json.dumps(result)})
            for row in goods:
                cur.execute("insert into RRL_LOGISTICS_EXP_ALLOC_LINE(OPERATION_ID,LOAD_OPERATION_ID,UID_PALLET,ARTICLE,BASE_QTY,BASE_UOM,WEIGHT_KG,BASIS_VALUE,AMOUNT,CURRENCY,WEIGHT_SOURCE,WEIGHT_BOX_UID)values(:op,:load_id,:lot_id,:article,:quantity,:unit,:weight,:basis_value,:amount,:currency,:weight_source,:weight_box_uid)",{"op":op,"load_id":row["load_operation_id"],"lot_id":row["uid"],"article":row["article"],"quantity":row["quantity"],"unit":row["base_uom"],"weight":row["weight_kg"],"basis_value":row["basis_value"],"amount":shares[row["key"]],"currency":currency,"weight_source":row["weight_source"],"weight_box_uid":row["weight_box_uid"]})
            cur.execute("select to_char(sum(AMOUNT),'TM9','NLS_NUMERIC_CHARACTERS=''.,''')from RRL_LOGISTICS_EXP_ALLOC_LINE where OPERATION_ID=:op",{"op":op})
            if Decimal(cur.fetchone()[0])!=amount:raise LogisticsCostError("EXPENSE_AMOUNT_NOT_CONSERVED","Распределение не сохраняет исходную сумму")
            enqueue(cur,'EXTRA_EXPENSE_ALLOCATED',op,{**result,'allocated_by':actor},'ALLOCATION_ONLY')
            return result

    def invoice(self,invoice_id: int,actor: str) -> list[dict[str,Any]]:
        from .expense_basis_read import invoice_expenses
        return invoice_expenses(self.gateway,invoice_id,actor)
