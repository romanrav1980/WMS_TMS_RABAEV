"""Atomic SAP/SKM shipment snapshots on a fresh 80 BOX fixture; never reopen the prior proof.

Reuse the original receipt/pick/load/defer/finish stages. Probe full native departure before rollback,
then lose the HTTP response after a real commit and repeat the same operation.
"""
import json
import os
import re
import socket
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.request import Request, urlopen

sys.path.insert(0,str(Path(__file__).parent))
import live_program_partial_80 as p
import live_document_acceptance as api
import oracledb

qa=p.qa
qa.OUT=qa.ROOT/'runtime/test-evidence/tradecase/2026-10-26/T02/shipment-events'
qa.STATE=qa.OUT/'state.json'
qa.s={}
if qa.STATE.exists():qa.s.update(json.loads(qa.STATE.read_text(encoding='utf-8')))
p.s=qa.s
s=qa.s


def parsed(value):
    value=value.read()if hasattr(value,'read')else value
    return json.loads(value)if isinstance(value,str)else value


def events(cursor,operation):
    cursor.execute("select EVENT_OUTBOX_ID,EVENT_TYPE,IDEMPOTENCY_KEY,PAYLOAD_JSON,STATUS from RRL_EVENT_OUTBOX where CORRELATION_ID=:o and EVENT_TYPE in('TRADECASE_SHIPMENT_SAP','TRADECASE_SHIPMENT_SKM')order by EVENT_TYPE",o=operation)
    return [dict(id=id,kind=kind,key=key,payload=parsed(wire),status=status)for id,kind,key,wire,status in cursor.fetchall()]


def check(rows,quantity):
    assert len(rows)==2 and {x['kind']for x in rows}=={'TRADECASE_SHIPMENT_SAP','TRADECASE_SHIPMENT_SKM'},rows
    keys=set()
    for row in rows:
        body=row['payload'];assert body['unit_count']==len(body['units'])==quantity and body['quantity']==str(quantity)
        assert len(row['key'])==76
        current={u['physical_unit_key']for u in body['units']};assert len(current)==quantity
        assert body['lines']==[dict(line_id='1',sku_id='A',quantity=str(quantity),base_uom='EA')]
        assert all(u['owner_id']=='SNS'and u['quantity']=='1'and len(u['codes'])==1 for u in body['units'])
        if keys:assert keys==current
        keys=current
    return keys


def rollback_probe():
    assert s['phase']=='DOCUMENT_READY'
    op=qa.tag()+'.depart';trip=s['transport']['transport_task_id']
    report={}
    with qa.oracle_connection()as c:
        assert not c.autocommit
        q=c.cursor();request=dict(actor='admin',command_type='TRIP_DEPART',contract_version=2,lines=[],metadata={},operation_id=op,source=dict(task_id=trip),units=[])
        report['request']=request
        q.execute('select CONDITION from RRL_TRANSPORT_TASK where ID=:t',t=trip);before=q.fetchone()[0]
        assert events(q,op)==[]
        result=q.var(oracledb.DB_TYPE_CLOB);wire=q.var(oracledb.DB_TYPE_CLOB);wire.setvalue(0,json.dumps(request));replay=q.var(oracledb.DB_TYPE_CLOB)
        try:
            q.callproc('RRL_STOCK_POSTING_API.prepare_command',[wire,'admin',replay]);assert replay.getvalue()is None
            q.callproc('RRL_STOCK_POSTING_API.execute_prepared',[result]);report['result']=parsed(result.getvalue())
            report['events_before_rollback']=events(q,op);check(report['events_before_rollback'],600)
            q.execute("select count(*)from RRL_TT_HU_LOAD_FACT where TT_ID=:t and STATUS='DEPARTED'",t=trip);assert q.fetchone()[0]==3
        finally:
            c.rollback();q.callproc('RRL_STOCK_POSTING_API.reset_connection',[])
        assert events(q,op)==[]
        q.execute('select CONDITION from RRL_TRANSPORT_TASK where ID=:t',t=trip);assert q.fetchone()[0]==before
        q.execute("select count(*)from RRL_TT_HU_LOAD_FACT where TT_ID=:t and STATUS='LOADED'",t=trip);assert q.fetchone()[0]==3
        q.execute('select count(*)from RRL_STOCK_OPERATION where OPERATION_ID=:o',o=op);assert q.fetchone()[0]==0
    report['status']='PASS';report['departure_and_events_rolled_back']=True
    (qa.OUT/'native-rollback.json').write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
    print('Native departure and two events rolled back together: PASS')


def lost_depart():
    assert s['phase']=='DOCUMENT_READY'
    op=qa.tag()+'.depart';path=f"/api/transport/loading/{s['transport']['transport_task_id']}/depart";report={}
    class DropCommittedResponse(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_POST(self):
            assert self.path==path
            request=Request('http://127.0.0.1:8088'+path,data=self.rfile.read(int(self.headers['Content-Length'])),headers={'Authorization':self.headers['Authorization'],'Content-Type':'application/json'},method='POST')
            with urlopen(request,timeout=35)as response:
                report['upstream_status']=response.status;report['upstream_body']=json.loads(response.read())
            self.connection.shutdown(socket.SHUT_RDWR);self.connection.close()
    server=HTTPServer(('127.0.0.1',0),DropCommittedResponse);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    previous=api.BASE
    try:
        api.BASE='http://127.0.0.1:'+str(server.server_port)
        try:qa.http('POST',path,dict(operation_id=op));raise AssertionError('Proxy must drop the response')
        except (OSError,ConnectionError)as exc:report['client_error']=type(exc).__name__
    finally:
        api.BASE=previous;server.shutdown();server.server_close();thread.join(timeout=5)
    assert report['upstream_status']==200,report
    with qa.oracle_connection()as c:
        q=c.cursor();report['before_replay']=events(q,op);check(report['before_replay'],600)
    p.depart()
    with qa.oracle_connection()as c:
        q=c.cursor();report['after_replay']=events(q,op);assert report['before_replay']==report['after_replay']
    report['status']='PASS';(qa.OUT/'lost-response.json').write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
    print('Lost response after commit, same-operation repeat, same two outbox rows: PASS')


def verify():
    assert s['phase']=='CLOSED'
    with qa.oracle_connection()as c:
        q=c.cursor();first=events(q,s['steps']['depart']['body']['operation_id']);second=events(q,s['steps']['remaining.depart']['body']['operation_id'])
        rollback=json.loads((qa.OUT/'native-rollback.json').read_text())
        q.execute('select CANONICAL_REQUEST from RRL_STOCK_OPERATION where OPERATION_ID=:o',o=s['steps']['depart']['body']['operation_id']);assert parsed(q.fetchone()[0])==rollback['request']
        first_keys=check(first,600);second_keys=check(second,200);assert not first_keys&second_keys
        q.execute("select PHYSICAL_UNIT_KEY from RRL_TRADE_STOCK_ATTR where CAPTURE_WARE_ID=:w",w=s['fixture']['warehouse_id']);assert first_keys|second_keys=={x[0]for x in q}
        q.execute('select u.PHYSICAL_UNIT_KEY,c.SYSTEM_CODE,c.RAW_CODE from RRL_TRADE_STOCK_ATTR a join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=a.PHYSICAL_UNIT_KEY join RRL_WMS_RECEIPT_CODE c on c.UID_PALLET=u.UID_PALLET and c.UNIT_ID=u.UNIT_ID where a.CAPTURE_WARE_ID=:w',w=s['fixture']['warehouse_id'])
        expected={}
        for key,system,wire in q:expected.setdefault(key,set()).add((system,wire.read()if hasattr(wire,'read')else wire))
        for row in first+second:
            for unit in row['payload']['units']:assert {(code['system_code'],code['code'])for code in unit['codes']}==expected[unit['physical_unit_key']]
        try:q.callproc('RRL_TRADE_SHIP_EVENT.publish',['BLOCKED_DIRECT_PROBE',0]);raise AssertionError('Direct publisher access must be denied')
        except oracledb.DatabaseError as exc:assert 'PLS-00904'in str(exc)
    report=dict(status='PASS',warehouse=s['fixture']['warehouse_id'],stock=qa.stock(),first=first,second=second,direct_publisher_denied=True)
    assert tuple(report['stock'])==(0,0,0)
    report['same_canonical_after_rollback']=True
    report['exact_receipt_codes_checked']=True
    (qa.OUT/'final.json').write_text(json.dumps(report,indent=2,default=str),encoding='utf-8');print('Separate SAP/SKM snapshots of 600 and 200 exact codes: PASS')


def main():
    os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=re.search(r'PASS=(\S+?)[\x60,)\s]',(qa.ROOT/'AGENTS.md').read_text(encoding='utf-8'))[1]
    phase=sys.argv[1]
    if phase not in {'rollback_probe','lost_depart','verify'}:p.main();return
    try:globals()[phase]()
    finally:s.setdefault('http',[]).extend(qa.CALLS);qa.save()


if __name__=='__main__':main()
