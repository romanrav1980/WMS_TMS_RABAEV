"""Delegate metadata to the existing fenced native command owner; never post goods."""
from hashlib import sha256
import json
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..contracts_trade_transport import TripBinding,TransportDocumentResult,TradeTransportError

class OracleTradeTransport:
    def __init__(self,gateway:Any)->None:
        self.gateway=gateway

    def _command(self,ware:int,trip:str,kind:str,body:dict[str,Any],actor:str)->dict[str,Any]:
        value=dict(body,trip_id=trip)
        encode=lambda v:json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False)
        value["business_hash"]=sha256(encode({k:v for k,v in value.items()if k!="operation_id"}).encode()).hexdigest()
        value["command_type"]=kind
        raw=encode(value)
        if len(raw.encode())>2*1024*1024:raise TradeTransportError("TRADE_TRANSPORT_MESSAGE_TOO_LARGE",413)
        value["payload_hash"]=sha256(raw.encode()).hexdigest()
        try:
            with self.gateway.transaction("TRADECASE transport "+kind)as cur:
                wire=cur.var(oracledb.DB_TYPE_CLOB);wire.setvalue(0,encode(value))
                codes=cur.var(oracledb.DB_TYPE_CLOB);codes.setvalue(0,"[]")
                result=cur.var(oracledb.DB_TYPE_CLOB)
                cur.callproc("RRL_TRADE_STOCK_API.execute_command",[ware,actor,wire,codes,result])
                return read_oracle_json(result.getvalue())
        except oracledb.DatabaseError as exc:
            number=getattr(exc.args[0],"code",0)
            status=403 if number in{20851,20882}else 404 if number==1403 else 409 if 20800<=number<=20999 else 503
            code=str(exc.args[0]).split("\n",1)[0].split(":",1)[-1].strip()if status!=503 else"TRADE_TRANSPORT_RESULT_UNKNOWN"
            raise TradeTransportError(code,status)from exc

    def bind(self,ware:int,trip:str,body:TripBinding,actor:str)->dict[str,Any]:
        return self._command(ware,trip,"BIND_TRIP",body.model_dump(mode="json"),actor)

    def result(self,ware:int,trip:str,body:TransportDocumentResult,actor:str)->dict[str,Any]:
        return self._command(ware,trip,"TRANSPORT_RESULT",body.model_dump(mode="json"),actor)

    def state(self,ware:int,trip:str,actor:str)->dict[str,Any]:
        return self._command(ware,trip,"TRIP_STATE",{},actor)
