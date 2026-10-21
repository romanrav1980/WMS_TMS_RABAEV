"""Read one versioned recipient snapshot and its matching masters in a read-only transaction."""
from datetime import datetime,timezone
from hashlib import sha256
import json
from typing import Any
import oracledb
from pydantic import ValidationError
from ...platform.public import read_oracle_json
from ..contracts_tradecase import TradecaseError
from ..contracts_trade_need import TradeNeed
from ..domain.trade_need import net_need


def need_snapshot(cur:Any,ware:int,key:str,max_age:int,now:datetime)->dict:
    def document(kind:str,identity:str)->tuple[dict,int,str,str]:
        cur.execute("select BODY_JSON,VERSION_NO,CONTENT_HASH,SOURCE_ID from RRL_TRADE_DOCUMENT where WARE_ID=:w and ENTITY_TYPE=:k and EXTERNAL_ID=:id and STATUS='ACCEPTED'",w=ware,k=kind,id=identity)
        row=cur.fetchone()
        if row is None:raise TradecaseError('NEED_SOURCE_MISSING',404)
        value=read_oracle_json(row[0])
        if value.get('active')is False:raise TradecaseError('NEED_MASTER_INACTIVE')
        return value,int(row[1]),row[2],row[3]
    raw,version,content_hash,source=document('NEED',key);body=TradeNeed.model_validate(raw)
    recipient,rv,_,_=document('RECIPIENT',body.recipient_id)
    sku,sv,_,_=document('SKU',body.sku_id)
    if rv!=body.recipient_version or sv!=body.sku_version:raise TradecaseError('NEED_MASTER_VERSION_CHANGED')
    result=net_need(body.model_dump(),sku['units_per_box'],now,max_age)
    result.update(warehouse_id=ware,document_id=key,document_version=version,source_id=source,recipient_id=body.recipient_id,recipient_title=recipient['title'],sku_id=body.sku_id,sku_title=sku['title'],recipient_version=rv,sku_version=sv,
                  period_from=body.period_from.isoformat(),period_until=body.period_until.isoformat(),units_per_box=sku['units_per_box'],input_uom=body.uom,input_hash=content_hash,
                  provenance='EXTERNAL_RECIPIENT_SNAPSHOT',sender_stock_checked=False,route_checked=False,topup_order_created=False)
    result['calculation_signature']=sha256(json.dumps(dict(input_hash=content_hash,recipient_version=rv,sku_version=sv,max_age_minutes=max_age),sort_keys=True).encode()).hexdigest()
    return result


def need_preview(gateway:Any,ware:int,key:str,max_age:int,actor:str)->dict:
    try:
        with gateway.transaction('TRADECASE recipient demand READ ONLY')as cur:
            cur.execute('set transaction read only')
            cur.execute("select RRL_ACCESS_API.allowed(:a,'tradecase_view','WAREHOUSE',:w)from dual",a=actor,w=str(ware))
            if cur.fetchone()[0]!=1:raise TradecaseError('TRADECASE_ACCESS_DENIED',403)
            return need_snapshot(cur,ware,key,max_age,datetime.now(timezone.utc))
    except ValueError as exc:
        if isinstance(exc,ValidationError):raise TradecaseError('NEED_STORED_SNAPSHOT_INVALID',409)from exc
        raise TradecaseError(str(exc),409)from exc
    except oracledb.DatabaseError as exc:raise TradecaseError('NEED_READ_FAILED',503)from exc
