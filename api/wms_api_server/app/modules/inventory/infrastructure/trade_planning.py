from hashlib import sha256
import json
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..contracts_trade_planning import TradeOrderBind, TradePlanningError

class OracleTradePlanning:
    def __init__(self,gateway:Any)->None:
        self.gateway=gateway

    def bind(self,warehouse:int,order:str,body:TradeOrderBind,actor:str)->dict[str,Any]:
        value=dict(body.model_dump(mode="json"),order_id=order)
        raw=json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True)
        value["payload_hash"]=sha256(raw.encode()).hexdigest()
        try:
            with self.gateway.transaction("TRADECASE native order binding")as cur:
                payload=cur.var(oracledb.DB_TYPE_CLOB);payload.setvalue(0,json.dumps(value))
                result=cur.var(oracledb.DB_TYPE_CLOB)
                cur.callproc("RRL_TRADE_ORDER_API.bind_order",[warehouse,actor,payload,result])
                return read_oracle_json(result.getvalue())
        except oracledb.DatabaseError as exc:
            code=getattr(exc.args[0],"code",0)
            status=403 if code in{20851,20882}else 404 if code==1403 else 409 if 20900<=code<=20999 else 503
            reason=str(exc.args[0]).split("\n",1)[0].split(":",1)[-1].strip()if status!=503 else"TRADE_ORDER_RESULT_UNKNOWN"
            raise TradePlanningError(reason,status)from exc
