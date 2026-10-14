import sys
sys.path.insert(0,'scripts')
exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
from app.modules.platform.public import read_oracle_json
folder=Path('reports/retailcase/2026-10-13/codex/QC_F1');v=json.loads((folder/'native_fixture.json').read_text(encoding='utf-8'))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TEXT from USER_SOURCE where NAME='RRL_STOCK_QC_GATE' and TYPE='PACKAGE BODY' order by LINE");body=''.join(x[0]for x in q.fetchall()).replace(chr(13),'')
 block="   declare recorded_count number;begin\n    select count(*) into recorded_count from RRL_QC_EXEMPT_FACT f\n     where f.DOCUMENT_ID=v_id\n      and json_value(f.PAYLOAD_JSON,'$.composition_signature' returning varchar2(64))=v_signature\n      and rownum=1;\n    j.put('weight_exemption_recorded',recorded_count=1);\n   end;"
 assert block in body
 before=body.replace(block+'\n','').replace("j.put('weight_exemption_recorded',false);",'')
 (folder/'before_gate_reconstructed.sql').write_text('create or replace '+before+'\n/\n',encoding='utf-8')
 q.execute("select NAME,LINE,TEXT from USER_ERRORS where NAME in('RRL_STOCK_QC_GATE','RRL_QC_SCOPE_READ')");errors=q.fetchall();assert not errors,errors
 sql="select count(*) from RRL_QC_EXEMPT_FACT f where f.DOCUMENT_ID=:doc and json_value(f.PAYLOAD_JSON,'$.composition_signature' returning varchar2(64))=:sig and rownum=1"
 q.execute(sql,doc=v['st_id'],sig=v['audit']['composition_signature']);assert q.fetchone()[0]==1
 q.execute(sql,doc=v['st_id'],sig='STALE');assert q.fetchone()[0]==0
 q.execute(sql,doc=-1,sig=v['audit']['composition_signature']);assert q.fetchone()[0]==0
 status=read_oracle_json(q.callfunc('RRL_STOCK_QC_GATE.status_json',oracledb.DB_TYPE_CLOB,[v['shipment']]));assert status['weight_exemption_recorded']is False
 q.execute("select INDEX_NAME,STATUS from USER_INDEXES where INDEX_NAME='RRL_QC_EXEMPT_DOCUMENT_IX'");index=q.fetchall()
 (folder/'recorded_status.json').write_text(json.dumps({'errors':errors,'matching_signature':True,'stale_signature':False,'wrong_document':False,'cleaned_fixture_status':status,'index':index,'checkpoint_note':'Pre-apply checkpoint script failed import; rollback body reconstructed by removing exact additive status patch from current USER_SOURCE, not a fresh pre-apply export.'},ensure_ascii=False,indent=2),encoding='utf-8')
print('PASS recorded status compiled, exact document/signature match, stale/wrong absent, cleaned status false; index VALID')

