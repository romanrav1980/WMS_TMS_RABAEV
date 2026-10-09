"""NS00 live assertions and bounded diagnostics, with no synthetic PASS fallback."""
from __future__ import annotations
import base64
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import time
from urllib.request import Request, urlopen
from .fixture_plan import ROOT, WARE_ID
from .oracle_fixture import METRICS, oracle_connection, query, target, serial


def api(path: str, payload: dict | None=None) -> object:
    token = base64.b64encode((os.getenv('WMS_ADMIN_USER','admin')+':'+
                             os.getenv('WMS_ADMIN_PASSWORD','admin123')).encode()).decode()
    body = json.dumps(payload).encode() if payload is not None else None
    req = Request('http://127.0.0.1:8088'+path,data=body,
                  method='PATCH' if payload is not None else 'GET',
                  headers={'Authorization':'Basic '+token,'Content-Type':'application/json'})
    with urlopen(req,timeout=30) as response:
        if response.status!=200:
            raise RuntimeError('Non-200 API response')
        return json.loads(response.read())


def readiness() -> dict:
    checks = {}
    for label,url in [('API','http://127.0.0.1:8088/health'),('ARM','http://127.0.0.1:3000'),
                      ('TSD','http://127.0.0.1:3010')]:
        with urlopen(url,timeout=15) as response:
            if response.status!=200:
                raise RuntimeError(f'{label} unavailable')
            checks[label] = {'status':response.status,'bytes':len(response.read())}
    checks['oracle'] = api('/db/ping')
    if checks['oracle']!={'user_name':'RABAEV','service_name':'orcl','db_name':'ORCL'}:
        raise RuntimeError('Wrong API Oracle target')
    return checks


def assertions() -> dict:
    with oracle_connection() as connection:
        cursor = connection.cursor()
        actual = target(cursor)
        invalid = query(cursor,"select count(*) n from user_objects where status='INVALID' and object_name not like 'BIN$%'")[0]['N']
        errors = query(cursor,"select count(*) n from user_errors where name not like 'BIN$%' and attribute='ERROR'")[0]['N']
        if invalid or errors:
            raise RuntimeError('Oracle compile gate failed')
        balances = query(cursor,"select p.uid_pallet,p.articul,p.expiry_date,r.cell,r.remain "
                         "from RRL_PALLETS p join RRL_REMAINS r on r.uid_poleta=p.uid_pallet "
                         "where p.uid_pallet in ('DS-BASE-B1','DS-BASE-B2') order by p.uid_pallet")
        if len(balances)!=2 or any(r['REMAIN']!=1200 for r in balances):
            raise RuntimeError('Expected exactly two pallets / 2400 pieces')
        orders = query(cursor,"select o.order_no,r.order_qty,r.pack_count from RRL_CUSTOMER_ORDER o "
                       "join RRL_CUSTOMER_ORDER_ROW r on r.customer_order_id=o.customer_order_id "
                       "where o.customer_order_id in (-980711,-980712,-980713) order by o.order_no")
        if [(r['ORDER_QTY'],r['PACK_COUNT']) for r in orders]!=[(960,40),(720,30),(720,30)]:
            raise RuntimeError('Order BOX->PCS binding mismatch')
    live = api(f'/api/finished-goods/remains?ware_id={WARE_ID}&limit=10&only_available=0')
    if len(live)!=2 or sum(r['qty'] for r in live)!=2400:
        raise RuntimeError('API balance differs from Oracle')
    return {'status':'PASS_LIVE_ORACLE_API','target':actual,'invalid':invalid,'errors':errors,
            'stock':balances,'orders':orders,'api_stock':live}


def fact() -> dict:
    records = api('/api/admin/product-shipment-settings?articul_like=DS-BASE-D10&limit=5')
    if len(records)!=1 or records[0]['acticul']!='DS-BASE-D10':
        raise RuntimeError('Ambiguous synthetic SKU')
    with oracle_connection() as connection:
        direct = query(connection.cursor(),"select shipment_aging_hours,shipment_aging_comment from RRL_ARTICULS where acticul='DS-BASE-D10'")
    if len(direct)!=1 or direct[0]['SHIPMENT_AGING_HOURS']!=records[0]['shipment_aging_hours'] or direct[0]['SHIPMENT_AGING_COMMENT']!=records[0]['shipment_aging_comment']:
        raise RuntimeError('API fact differs from Oracle')
    return records[0]


def markers() -> dict:
    with oracle_connection() as connection:
        return query(connection.cursor(),"select (select nvl(max(log_id),0) from RRL_SQL_SLOW_LOG) slow_id, "
                     "(select nvl(max(api_call_id),0) from RRL_API_CALL_LOG) api_id from dual")[0]


def sql_review(start: dict) -> dict:
    with oracle_connection() as connection:
        cursor = connection.cursor()
        slow = query(cursor,"select * from (select log_id,elapsed_ms,api_path,sql_text from RRL_SQL_SLOW_LOG "
                     "where log_id>:marker order by elapsed_ms desc) where rownum<=20",{'marker':start['SLOW_ID']})
        top = query(cursor,"select * from (select sql_id,executions,round(elapsed_time/1000,2) elapsed_ms," 
                    "round(elapsed_time/1000/nullif(executions,0),2) avg_ms,substr(sql_text,1,1000) sql_text "
                    "from v$sql where module='NICORA_NS00' and executions>0 order by elapsed_time desc) where rownum<=10")
    local = sorted(METRICS,key=lambda r:r['elapsed_ms'],reverse=True)[:20]
    return {'start':start,'oracle_slow_after_marker':slow,'oracle_top_ns00':top,'local_top':local,
            'api_slow':api(f'/api/admin/slow-sql?from_log_id={start["SLOW_ID"]+1}&limit=20'),
            'api_audit':api(f'/api/admin/api-calls?from_call_id={start["API_ID"]+1}&limit=100'),
            'decision':'Bound preservation to full non-fixture stock plus active pallet metadata; arraysize 1000, cap 150000. Diagnostics use rownum windows. No index added by environment smoke; NS02 owns query plans for actual functional load.'}


def write_report(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,default=serial,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
