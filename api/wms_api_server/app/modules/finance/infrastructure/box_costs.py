from hashlib import sha256
from decimal import Decimal
from typing import Any
import json,oracledb
from ...platform.public import read_oracle_json
from ..contracts import LogisticsCostError
from ..domain.physical_boxes import physical_box_count
from .finance_outbox import enqueue
from .cost_access import require_warehouse
from .period_policy import current_policy
from .cost_period_lines import load_period_lines

def calculate_box_cost(gateway: Any,op: str,trip: int,ware: int,currency: str,actor: str) -> dict[str,Any]:
    digest=sha256(json.dumps([trip,ware,currency,actor],separators=(",",":")).encode()).digest()
    try:
        with gateway.transaction("Conduct actual departed warehouse BOX cost") as cur:
            require_warehouse(cur,ware,actor,"calc_tt_price")
            cur.execute("select ID from RRL_TRANSPORT_TASK where ID=:id for update",{"id":trip})
            if not cur.fetchone():raise LogisticsCostError("COST_TRIP_NOT_FOUND","Рейс не найден",404)
            require_warehouse(cur,ware,actor,"calc_tt_price")
            cur.execute("select PAYLOAD_HASH,RESULT_JSON from RRL_LOGISTICS_COST_RUN where OPERATION_ID=:op",{"op":op});old=cur.fetchone()
            if old:
                if old[0]!=digest:raise LogisticsCostError("COST_PAYLOAD_CONFLICT","Идентификатор расчёта уже имеет другое содержание")
                return read_oracle_json(old[1])
            policy=current_policy(cur,ware,lock=True)
            cur.execute("""select l.LOAD_OPERATION_ID,l.COMPOSITION_JSON,to_char(cast(sys_extract_utc(l.LOADED_AT) as date),'YYYY-MM-DD'),
            (select count(*)from RRL_TT_LOAD_BOX_WEIGHT b where b.LOAD_OPERATION_ID=l.LOAD_OPERATION_ID),l.STATUS
            from RRL_TT_HU_LOAD_FACT l where l.TT_ID=:trip and l.WARE_ID=:ware order by l.LOAD_OPERATION_ID fetch first 201 rows only""",{"trip":trip,"ware":ware})
            loads=cur.fetchall()
            if not loads or len(loads)>200:raise LogisticsCostError("COST_LOAD_BOUND","Нужны от 1 до 200 фактических мест выбранного склада")
            lines=[];total=Decimal("0")
            for load,composition,day,boxes,status in loads:
                if status!="DEPARTED":raise LogisticsCostError("COST_ACTUAL_DEPARTURE_REQUIRED","Есть место без фактического выезда")
                tree=read_oracle_json(composition)
                cur.execute("""select BOX_UID,BOX_CONTENT_VERSION,CASE_BOX_TASK_ID,MEASUREMENT_ORIGIN,
                  FINAL_SCALE_CAPTURE,WAREHOUSE_QC_OPERATION,GROSS_WEIGHT_KG,TARE_WEIGHT_KG,NET_WEIGHT_KG,
                  SIGNATURE_VERSION,MEASURED_CONTENT_VERSION,COVERAGE_COMPLETE
                  from RRL_TT_LOAD_BOX_WEIGHT where LOAD_OPERATION_ID=:load_id order by BOX_UID fetch first 201 rows only""",load_id=load)
                columns=[x[0].lower()for x in cur.description]
                proofs=[dict(zip(columns,row))for row in cur.fetchall()]
                try:physical=physical_box_count(tree,proofs)
                except ValueError as exc:raise LogisticsCostError("COST_COMPLETE_PHYSICAL_BOX_PROOF_REQUIRED",str(exc))from exc
                if physical!=boxes:raise LogisticsCostError("COST_COMPLETE_PHYSICAL_BOX_PROOF_REQUIRED","Количество физических коробок изменилось")
                period_lines=load_period_lines(cur,tree,int(boxes),load,day,ware,currency,policy)
                lines.extend(period_lines)
                if len(lines)>500:
                    raise LogisticsCostError("COST_DETAIL_BOUND","Не более 500 расчётных строк в одном проведении")
                total+=sum((Decimal(line["amount"])for line in period_lines),Decimal(0))
            result={"operation_id":op,"trip_id":trip,"warehouse_id":ware,"currency":currency,"amount":str(total),"lines":lines,"status":"CALCULATED","carrier_invoice_amount_changed":False}
            cur.setinputsizes(result_body=oracledb.DB_TYPE_CLOB)
            cur.execute("insert into RRL_LOGISTICS_COST_RUN(OPERATION_ID,PAYLOAD_HASH,TT_ID,WARE_ID,CURRENCY,ACTOR,RESULT_JSON)values(:op,:hash_value,:trip,:ware,:currency,:actor,:result_body)",{"op":op,"hash_value":digest,"trip":trip,"ware":ware,"currency":currency,"actor":actor,"result_body":json.dumps(result)})
            for load in sorted({line["load_operation_id"]for line in lines}):
                cur.execute("insert into RRL_LOG_COST_SOURCE_CLAIM(LOAD_OPERATION_ID,COST_CODE,CURRENCY,OPERATION_ID)values(:load_id,'WAREHOUSE_PICKING',:currency,:op)",load_id=load,currency=currency,op=op)
            for line in lines:
                cur.execute("insert into RRL_LOGISTICS_COST_LINE(OPERATION_ID,LOAD_OPERATION_ID,COST_CODE,CURRENCY,RATE_KEY,VERSION_NO,QUANTITY,RATE_VALUE,AMOUNT,BASIS,RATE_DATE,PERIOD_MODE,PERIOD_TIME_ZONE,PERIOD_POLICY_VERSION,PERIOD_KEY)values(:op,:load_id,'WAREHOUSE_PICKING',:currency,:key,:version,:quantity,:rate,:amount,'BOX',to_date(:rate_date,'FXYYYY-MM-DD'),:period_mode,:period_zone,:period_version,:period_key)",{"op":op,"load_id":line["load_operation_id"],"currency":currency,"key":line["rate_key"],"version":line["version"],"quantity":line["quantity"],"rate":Decimal(line["rate"]),"amount":Decimal(line["amount"]),"rate_date":line["rate_date"],"period_mode":line["period_mode"],"period_zone":line["period_timezone"],"period_version":line["period_policy_version"],"period_key":line["rate_date"]})
            enqueue(cur,'WAREHOUSE_COST_RECOGNIZED',op,{**result,'calculated_by':actor},'MONETARY_RECOGNITION')
            return result
    except oracledb.DatabaseError as exc:
        code=getattr(exc.args[0],"code",0)
        if code==1:raise LogisticsCostError("COST_ALREADY_CHARGED","Складская работа по этому месту уже начислена") from exc
        if 20800<=code<=20999:raise LogisticsCostError("COST_REJECTED",str(exc.args[0]).split("\n",1)[0],403 if code==20882 else 409) from exc
        raise
