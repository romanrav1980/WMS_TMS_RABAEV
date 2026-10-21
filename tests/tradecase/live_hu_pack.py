"""Retained TRADECASE SORT lot: zero-quantity nested packing and exact retries."""
import json
import os
from pathlib import Path
import re
import sys
from uuid import uuid4
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from live_document_acceptance import http,expect,CALLS
from tools.mcp.tms_mcp_server import oracle_connection
OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-22/T06'
STATE=OUT/'hu-pack-state.json'
os.environ['TRADECASE_ADMIN_USER']='admin'
os.environ['TRADECASE_ADMIN_PASSWORD']=re.search(r'PASS=(\S+?)[`,)\s]',(ROOT/'AGENTS.md').read_text(encoding='utf-8'))[1]


def save(value):STATE.write_text(json.dumps(value,indent=2,default=str),encoding='utf-8')


def composition(uid):return expect(200,http('GET','/api/warehouse-hus/composition?identifier='+uid))


def prepare():
    assert not STATE.exists(),'Use the retained state, never create the same fixture twice'
    with oracle_connection()as c:
        q=c.cursor();q.execute("select r.UID_POLETA,r.CELL,r.REMAIN from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=219023232 and r.REMAIN=3");rows=q.fetchall();assert len(rows)==1
        uid,cell,qty=rows[0]
    tag='HU22'+uuid4().hex[:10]
    state=dict(tag=tag,warehouse=219023232,stock_uid=uid,cell=cell,quantity=qty,containers=[],calls=[])
    save(state)
    for level in ['PALLET','BOX','BOX']:
        target=tag+'.'+str(len(state['containers']))
        body=dict(operation_id=target+'.create',identifier=target,cell=cell,warehouse=state['warehouse'],
                  container_type=level,tare_weight_kg='0.1',scan_container=target,scan_cell=cell)
        result=expect(200,http('POST','/api/warehouse-hus/create',body))
        state['containers'].append(dict(uid=target,result=result));save(state)
    inner=state['containers'][-1]['uid']
    parent,child=composition(inner),composition(uid)
    state['parent_snapshot']=parent;state['child_snapshot']=child
    body=dict(operation_id=tag+'.stock.attach',identifier=inner,child_uid=uid,
              expected_version=parent['nodes'][0]['version'],expected_child_version=child['nodes'][0]['version'],
              scan_container=inner,scan_child=uid)
    state['first_attach']=body;save(state)
    denial=http('POST','/api/warehouse-hus/attach',body)
    assert denial[0]==409 and 'TRADE_ORDER_BINDING_REQUIRED' in json.dumps(denial),denial
    state.update(baseline_denial=denial,calls=list(CALLS),prepared=True);save(state)
    print(json.dumps(dict(status='PREPARED',tag=tag,denial=denial[0],stock_quantity=qty)))


if __name__=='__main__':prepare()
