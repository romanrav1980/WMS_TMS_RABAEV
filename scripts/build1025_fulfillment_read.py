from pathlib import Path
import ast,json,textwrap
read=lambda p:Path(p).read_text(encoding="utf-8");files={}
p="api/wms_api_server/app/services/customer_order_service.py";v=read(p);tree=ast.parse(v)
cls=next(x for x in tree.body if isinstance(x,ast.ClassDef)and x.name=="CustomerOrderService")
method=next(x for x in cls.body if isinstance(x,ast.FunctionDef)and x.name=="get_fulfillment")
lines=v.splitlines();original="\n".join(lines[method.lineno-1:method.end_lineno])
query=next(x for x in ast.walk(method)if isinstance(x,ast.Call)and isinstance(x.func,ast.Attribute)and x.func.attr=="fetch_all").args[0].value
inner=query.strip().replace("FACT_QTY,","FACT_QTY,to_char(FACT_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') FACT_QTY_EXACT,",1).replace("FACT_WEIGHT,","FACT_WEIGHT,to_char(FACT_WEIGHT,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') FACT_WEIGHT_EXACT,",1)
sql="""select f.*,ct.SSCC CASE_IDENTIFIER,ct.CURRENT_CELL CASE_CURRENT_CELL,
 ct.CONTENT_VERSION CASE_CURRENT_VERSION,ct.STATUS CASE_CURRENT_STATUS
 from ("""+inner+""") f left join RRL_CASE_PICK_TASK ct
 on ct.CASE_PICK_TASK_ID=f.PICKED_CASE_TASK_ID and ct.CUSTOMER_ORDER_ID=f.CUSTOMER_ORDER_ID
 and ct.WARE_ID=:p_warehouse order by f.FULFILLMENT_ID"""
body=textwrap.dedent(original).split("\n",1)[1].replace(query,sql,1)
body=body.replace('{"customer_order_id": customer_order_id}','{"customer_order_id": customer_order_id,"p_warehouse": warehouse}',1)
body=body.replace('    return rows','''    for row in rows:
        row["case_binding_version_matches"] = (row.get("case_current_version") is not None
            and row.get("case_current_version") == row.get("picked_content_version"))
        row["case_place_current"] = (row.get("status") == "PICKED"
            and row.get("case_current_status") in ("WAIT_CONTROL","CONTROL_IN_PROGRESS","CONTROLLED","READY_TO_SHIP")
            and row.get("case_current_cell") is not None and row["case_binding_version_matches"])
    return rows''',1)
new='''"""One current authorised order snapshot; reuse the original fulfillment facts."""
from typing import Any
import json
from fastapi import HTTPException
from ....transaction_gateway import TransactionGateway
from .store_source_scope import assert_store_scope


class OrderFulfillmentRead:
    def __init__(self,gateway: Any)->None:
        self.gateway=gateway

    def get(self,customer_order_id: int,actor: str)->list[dict]:
        if customer_order_id<1:
            raise ValueError("Positive order ID required")
        with self.gateway.transaction("Order fulfillment READ ONLY current warehouse")as cur:
            if not getattr(self.gateway,"transaction_bound",False):
                cur.execute("set transaction read only")
            cur.execute("select WARE_ID from RRL_CUSTOMER_ORDER where CUSTOMER_ORDER_ID=:id",id=customer_order_id)
            header=cur.fetchone()
            if header is None:
                raise LookupError("Customer order not found")
            assert_store_scope(cur,actor,"customer_fulfillment_view",header[0])
            return OrderFulfillmentRead(TransactionGateway(cur))._rows(customer_order_id,header[0])

    def _rows(self,customer_order_id: int,warehouse: int)->list[dict]:
'''+textwrap.indent(body,"    ")+"\n"
files["api/wms_api_server/app/modules/fulfillment/infrastructure/order_fulfillment_read.py"]=new
replacement='''    def get_fulfillment(self, customer_order_id: int, actor: str) -> list[dict[str, Any]]:
        from ..modules.fulfillment.public import build_fulfillment_read_service
        return build_fulfillment_read_service(self.gateway).get(customer_order_id, actor)'''
v=v.replace(original,replacement,1);files[p]=v
p="api/wms_api_server/app/modules/fulfillment/public.py";files[p]=read(p)+'''
from .infrastructure.order_fulfillment_read import OrderFulfillmentRead


def build_fulfillment_read_service(gateway=None) -> OrderFulfillmentRead:
    return OrderFulfillmentRead(gateway if gateway is not None else OracleGateway())


__all__.append("build_fulfillment_read_service")
'''
p="api/wms_api_server/app/routers/customer_orders.py";v=read(p)
old='''    if CustomerOrderService().get_customer_order(customer_order_id) is None:
        raise HTTPException(status_code=404, detail="Customer order not found.")
    return CustomerOrderService().get_fulfillment(customer_order_id)'''
assert v.count(old)==1
v=v.replace(old,'''    try:
        return CustomerOrderService().get_fulfillment(customer_order_id, _user.username)
    except PermissionError as exc:
        raise HTTPException(403, str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc''',1);files[p]=v
print(json.dumps(files,ensure_ascii=True))
