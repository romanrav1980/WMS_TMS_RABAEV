"""Keyset drill-down over the same stock predicates, with no repair or repeated COUNT."""
import base64
import binascii
import json
from typing import Any
from ..contracts import LogisticsCostError
from .cost_access import require_warehouse
from .reconciliation_stock_documents import SOURCES


def decode_cursor(value: str | None, ware: int, metric: str) -> tuple[str,str] | None:
    if value is None:return None
    try:
        raw=base64.b64decode(value.encode('ascii'),altchars=b'-_',validate=True)
        data=json.loads(raw.decode('utf-8'))
        if not isinstance(data,list) or len(data)!=4 or data[:2]!=[ware,metric]:raise ValueError()
        uid,cell=data[2:]
        if not isinstance(uid,str) or not 1<=len(uid)<=200 or not isinstance(cell,str) or not 1<=len(cell)<=60:raise ValueError()
        return uid,cell
    except (ValueError,TypeError,UnicodeError,binascii.Error) as exc:
        raise LogisticsCostError('STOCK_CURSOR_INVALID','Курсор не соответствует складу и типу конфликта',422) from exc


def stock_conflict_page(gateway: Any,ware: int,metric: str,after: str | None,limit: int,actor: str) -> dict[str,Any]:
    if metric not in SOURCES or not 1<=limit<=100:
        raise LogisticsCostError('STOCK_PAGE_INVALID','Выберите вид конфликта и размер страницы от1 до100',422)
    cursor=decode_cursor(after,ware,metric)
    source=SOURCES[metric]
    params: dict[str,Any]={'ware':ware,'page_limit':limit+1}
    if cursor:
        source+=' and (r.UID_POLETA>:after_uid or (r.UID_POLETA=:after_uid and r.CELL>:after_cell))'
        params.update(after_uid=cursor[0],after_cell=cursor[1])
    with gateway.transaction('Current stock conflict page READ ONLY') as cur:
        cur.execute('set transaction read only')
        require_warehouse(cur,ware,actor,'transport_dispatch_view')
        cur.execute("select r.UID_POLETA,r.CELL,r.BASE_UOM,"
            "to_char(r.REMAIN,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''),"
            "to_char(r.HARD_RESERVED_BASE,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') "
            +source+' order by r.UID_POLETA,r.CELL fetch first :page_limit rows only',params)
        found=cur.fetchall()
    rows=[{'uid_pallet':uid,'cell':cell,'base_uom':unit,'physical_quantity':physical,'hard_quantity':hard}
          for uid,cell,unit,physical,hard in found[:limit]]
    more=len(found)>limit
    token=None
    if more:
        last=rows[-1]
        token=base64.urlsafe_b64encode(json.dumps([ware,metric,last['uid_pallet'],last['cell']],
            ensure_ascii=False,separators=(',',':')).encode('utf-8')).decode('ascii')
    return {'warehouse_id':ware,'metric':metric,'scope':'CURRENT_STOCK_SNAPSHOT','rows':rows,
            'limit':limit,'has_more':more,'next_cursor':token,'cross_page_snapshot':False,'stock_changed':False}
