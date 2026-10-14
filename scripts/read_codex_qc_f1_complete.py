exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
from app.modules.platform.public import read_oracle_json
from time import perf_counter
import hashlib
folder=Path('reports/nicora/2026-10-13/codex/QC_F1');file=folder/'native_fixture.json';v=json.loads(file.read_text(encoding='utf-8'));operation='QCF1.PLAN:'+v['tag']
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute('select RESULT_JSON,STATE from RRL_STOCK_OPERATION where OPERATION_ID=:op',op=operation);wire,state=q.fetchone();saved=read_oracle_json(wire);assert state=='APPLIED'and saved['control_status']['ready']
 q.execute('select PAYLOAD_JSON from RRL_QC_EXEMPT_FACT where OPERATION_ID=:op and DOCUMENT_ID=:doc',op=operation,doc=v['st_id']);audit=read_oracle_json(q.fetchone()[0]);assert audit['storage_pick_task_id']==v['task_id']and audit['base_quantity']=='3'and audit['exemption_basis']=='SCANNED_ORIGINAL_STORAGE_IDENTIFIER'
 command={'contract_version':2,'operation_id':operation,'command_type':'OUTGOING_PALLET_CHECK','actor':'admin','source':{'pallet_identifier':v['shipment']},'lines':[],'units':[],'metadata':{'quality_kind':'PLAN'}}
 inp=q.var(oracledb.DB_TYPE_CLOB);inp.setvalue(0,json.dumps(command));out=q.var(oracledb.DB_TYPE_CLOB);c.rollback();start=perf_counter()
 try:q.callproc('RRL_STOCK_POSTING_API.prepare_command',[inp,'admin',out,None]);repeated=read_oracle_json(out.getvalue());assert repeated==saved;c.commit()
 finally:q.callproc('RRL_STOCK_POSTING_API.reset_connection')
 q.execute('select count(*)from RRL_QC_EXEMPT_FACT where OPERATION_ID=:op and DOCUMENT_ID=:doc',op=operation,doc=v['st_id']);assert q.fetchone()[0]==1
 q.execute('select nvl(sum(REMAIN),0),nvl(sum(HARD_RESERVED_BASE),0)from RRL_REMAINS where UID_POLETA=:p_uid',p_uid=v['lot']);assert q.fetchone()==(0,0)
 q.execute("select ACTIVE_FLAG from RRL_QC_SCOPE_RULE where WARE_ID=:w and STORE_ADDR=:a and PLACE_CATEGORY='STOCK'",w=v['warehouse'],a='QCF1.ADDR.'+v['tag']);assert q.fetchone()[0]==0
 v.update(qc=saved,audit=audit,replay_exact=True,replay_after_cleanup_ms=round((perf_counter()-start)*1000,2),cleanup_P=0,cleanup_H=0,stage='PASS')
 q.execute("select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),BUFFER_GETS,substr(SQL_TEXT,1,250)from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and(SQL_TEXT like 'SELECT WH.TASK_ID,M.OPERATION_ID,M.FROM_CELL%'or SQL_TEXT like 'SELECT NVL(SUM(REMAIN),0) INTO%'or SQL_TEXT like 'SELECT RRL_QC_SCOPE_READ.EXEMPTION_JSON%')order by LAST_ACTIVE_TIME desc fetch first 8 rows only");v['sql']=q.fetchall()
 q.execute("select OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where STATUS='INVALID'and OBJECT_NAME not like 'BIN$%'");v['invalid']=q.fetchall();assert not v['invalid']
 v['reader_sha256']=hashlib.sha256(Path('db/migrations/2026-10-14_ni051_scoped_quality/002_reader.sql').read_bytes()).hexdigest()
file.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8');print('PASS native storage-only QC PLAN ready/audit1/exact replay; own cleanup P0H0; SQL',v['sql'])
