"""Read live quantities/sources, prove immutable evidence and retain bounded SQL diagnostics."""
import hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from tools.mcp.tms_mcp_server import oracle_connection
OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-22/T07'
small=json.loads((OUT/'bulk-small-case.json').read_text(encoding='utf-8'))
load=json.loads((OUT/'bulk-small-loading.json').read_text(encoding='utf-8'))
report=dict(checks=[],sources={},synthetic_measurements=True,external_ack=False)


def expected_error(q,code,command,args):
    try:q.callproc(command,args)
    except Exception as exc:
        assert getattr(exc.args[0],'code',None)==code,str(exc)
        report['checks'].append(dict(command=command,error_code=code,reason=str(exc).split('\n')[0]));return
    raise AssertionError('Expected native rejection: '+command)


with oracle_connection()as c:
    q=c.cursor();q.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual");assert q.fetchone()==('RABAEV','orcl')
    q.execute("select count(*)from USER_OBJECTS where STATUS='INVALID'");assert q.fetchone()[0]==0
    pairs={
        'RRL_CASE_SSCC_API':('case_labels_scoped','001_labels.sql'),
        'RRL_SSCC_ALLOCATOR':('case_labels_scoped','001_labels.sql'),
        'RRL_TRADE_STOCK_GUARD':('bulk_case_carton','001_guard.sql'),
        'RRL_CASE_SCALE_ADMISSION':('manual_case_tare','002_pick_admission.sql'),
        'RRL_WH_FINAL_SCALE_ADMISSION':('manual_case_tare','003_final_admission.sql'),
        'RRL_CASE_MANUAL_TARE_API':('manual_case_tare','001_manual_tare.sql')}
    for name,(folder,file)in pairs.items():
        q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE='PACKAGE BODY'order by LINE",n=name)
        actual=''.join(r[0]for r in q).replace('\r','').rstrip('\n')
        text=(ROOT/'db/migrations'/('2026-10-22_'+folder)/file).read_text(encoding='utf-8')
        pattern=r'create or replace (package body '+name+r'\b.*?)(?:\n/\n)'
        expected=re.search(pattern,text,re.S|re.I)[1].rstrip('\n');assert actual==expected,name
        report['sources'][name]=hashlib.sha256(actual.encode()).hexdigest()
    q.execute('select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w',w=220793322)
    report['stock']=list(q.fetchone());assert report['stock']==[8,4]
    q.execute("select OPERATION_ID,STATE from RRL_STOCK_OPERATION where OPERATION_ID in(:a,:b)",a='BS22.LOAD.1163',b='BULK22.LOAD.BOX.1161');report['operations']=list(q);assert dict(report['operations'])['BS22.LOAD.1163']=='APPLIED';assert dict(report['operations']).get('BULK22.LOAD.BOX.1161')!='APPLIED'
    q.execute("select ROOT_UID,ROOT_CASE_TASK_ID,STATUS,GROSS_WEIGHT_KG from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID='BS22.LOAD.1163'");report['load']=list(q.fetchone());assert report['load'][1:]==[1163,'LOADED',2.1]
    q.execute('select count(*)from RRL_CASE_MANUAL_TARE where CASE_PICK_TASK_ID=1163');assert q.fetchone()[0]==1
    q.execute("select UNIT_ID,PHYSICAL_UNIT_KEY,CURRENT_UID,CURRENT_CELL,STOCK_STATUS,BASE_QTY from RRL_WMS_RECEIPT_UNIT where UID_PALLET='690000000630906379'order by UNIT_ID")
    report['physical_units']=[list(row)for row in q]
    assert {row[0]for row in report['physical_units']if row[4]=='ISSUED'}=={'7','9'}
    assert {row[0]for row in report['physical_units']if row[4]=='AVAILABLE'and row[3]=='B22E220793322'}=={'2','3','4','5'}
    assert len({row[1]for row in report['physical_units']})==10
    for actor in [small['actor'],load['actor']]:
        q.execute('select DELETED from RUSERS where ID=:a',a=actor);assert q.fetchone()[0]==1
        q.execute('select count(*)from RRL_ACCESS_ASSIGNMENT where ASSIGNMENT_ID=:a and REVOKED_AT is null',a=actor);assert q.fetchone()[0]==0
        q.execute("select CAN_VIEW,CAN_OPERATE from RRL_TRADE_OWNER_GRANT where USERNAME=:a and WARE_ID=220793322 and OWNER_ID='SNS'",a=actor);assert q.fetchone()==(0,0)
    result=q.var(str,32000)
    expected_error(q,20882,'RRL_CASE_MANUAL_TARE_API.record_tare',[1163,json.dumps(small['manual_tare_body']),small['actor'],result])
    # Same operation cannot be taken over by another actor, even GLOBAL_ADMIN.
    expected_error(q,20873,'RRL_CASE_MANUAL_TARE_API.record_tare',[1163,json.dumps(small['manual_tare_body']),'admin',result])
    expected_error(q,20882,'RRL_CASE_SSCC_API.issue',[1163,json.dumps(small['small_label_body']),small['actor'],result])
    try:q.execute("update RRL_CASE_MANUAL_TARE set TARE_KG=0.2 where CASE_PICK_TASK_ID=1163")
    except Exception as exc:assert getattr(exc.args[0],'code',None)==20882;report['checks'].append('append-only update denied')
    else:raise AssertionError('Manual tare was mutable')
    c.rollback()
    request=json.dumps(dict(metadata=dict(quality_kind='WEIGHT',gross_weight='2.1',wood_weight='0.2',measurement_origin='MANUAL_CONFIRMED')))
    expected_error(q,6550,'RRL_WH_FINAL_SCALE_ADMISSION.assert_capture',[request,json.dumps(dict(case_task=1163))])
    report['limitations']=['Final-scale helper rejects direct invocation through ACCESSIBLE BY. Tare mismatch negative branch not exercised here; positive manual QC was executed through the real API.']
    q.execute("select LOG_ID,CREATED_AT,API_PATH,ELAPSED_MS,SQL_TEXT_HASH,dbms_lob.substr(SQL_TEXT,1500,1),ERROR_TEXT from RRL_SQL_SLOW_LOG where CREATED_AT>=cast(systimestamp as timestamp)-interval '2'hour and(API_PATH like '/api/transport/loading/%'or API_PATH like '/api/case-pick/%'or API_PATH like '/api/inventory/warehouse-scales/%'or API_PATH like '/api/outgoing-quality/%')order by LOG_ID desc fetch first 40 rows only")
    report['slow_sql']=[list(row)for row in q]
    report['slow_sql_decision']='Keep existing fences/rights. Review retained cold CASE queue outliers separately in T12; no new unproven index.'
    c.rollback()
report['status']='PASS';(OUT/'bulk-carton-verification.json').write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
print(json.dumps(dict(status=report['status'],stock=report['stock'],sources=len(report['sources']),checks=len(report['checks']),slow_sql_rows=len(report['slow_sql']))))
