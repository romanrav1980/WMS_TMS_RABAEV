"""Original native planner, with an optional same-transaction idempotent receipt."""
import oracledb
from fastapi import HTTPException
from ....oracle_gateway import OracleGateway
from ....schemas import PickingPlanCreateRequest

def create_existing_plan(gateway: OracleGateway,request: PickingPlanCreateRequest)->int:
    try:
        if request.operation_id:
            with gateway.transaction("Idempotent original pick plan creation")as cur:
                old_timeout=cur.connection.call_timeout
                try:
                    cur.connection.call_timeout=min(old_timeout,15000)if old_timeout else 15000
                    return int(cur.callfunc("RRL_PICK_PLAN_CREATE_API.create_command",oracledb.DB_TYPE_NUMBER,
                                           [request.operation_id,request.customer_order_id,request.plan_strategy,request.created_by]))
                finally:
                    try:cur.connection.call_timeout=old_timeout
                    except oracledb.Error:pass
        return gateway.call_number_plsql(
            """begin :result := RRL_PICKING_API.create_plan(
              p_customer_order_id => :customer_order_id,
              p_plan_strategy => :plan_strategy, p_created_by => :created_by); end;""",
            request.model_dump(exclude={"operation_id"}),
        )
    except oracledb.Error as exc:
        detail=exc.args[0];code=getattr(detail,"code",None)
        if code in {1013,3113,3114,3135,12170,12537}or str(getattr(detail,"full_code","")).startswith("DPY-"):
            raise HTTPException(503,detail={"code":"PICK_CREATE_OUTCOME_UNCERTAIN","operation_id":request.operation_id,
                "message":"Повторите сохранённую команду с тем же идентификатором.","outcome_confirmed":False})from exc
        if code in {1403,1422}:
            raise HTTPException(422 if code==1403 else 409,detail={"code":"PICK_PLAN_REFERENCE_REQUIRED"if code==1403 else"PICK_PLAN_REFERENCE_AMBIGUOUS",
                "message":"Проверьте справочники товара, единицы измерения и настройки обеспечения.","outcome_confirmed":True})from exc
        if code==20882:status=403
        elif code==20886 and "PICK_ORDER_IDENTITY_MISSING"in str(detail):status=404
        elif code in {1,20840,20846,20850,20860,20873,20881,20886,20890}:status=409
        elif code in {20868,20980}:status=422
        else:raise
        raise HTTPException(status,detail=str(detail).split("\n",1)[0])from exc
