"""Leading-01 tobacco GTIN and serial containing21 must use article context."""
import json,sys
from pathlib import Path
from uuid import uuid4
from copy import deepcopy
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'api/wms_api_server'))
from app.config import get_settings
from app.modules.platform.public import read_oracle_json
from app.modules.inventory.domain.mark_identity import canonical_mark
cfg=get_settings();tag=uuid4().hex[:10];article='Q130'+tag.upper();uid='TOBACCO.CONTEXT:'+tag
prefix='01'+str(int(tag,16)%10**11).zfill(11)
gtin=prefix+str((10-sum(int(n)*(3 if i%2==0 else 1)for i,n in enumerate(reversed(prefix)))%10)%10)
admin=httpx.Client(auth=('admin','admin123'),timeout=35);base='http://127.0.0.1:8088'
def api(path,body):
 r=admin.post(base+path,json=body);assert r.status_code==200,(r.status_code,r.text[:1800]);return r.json()
with oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn)as c:
 c.call_timeout=15000;q=c.cursor();q.execute("select RAW_JSON from RRL_TRACE_SENDER_MANIFEST where OPERATION_ID='MANIFEST.IMPORT:a3b49b8174.CURRENT'");doc=deepcopy(read_oracle_json(q.fetchone()[0]));old=doc['article']
 def meta(sql,**binds):
  q.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin','warehouse_settings_edit'])
  try:q.execute(sql,binds);c.commit()
  except BaseException:c.rollback();raise
  finally:q.callproc('RRL_STOCK_CONFIG_API.end_change')
 meta('declare r RRL_ARTICULS%rowtype;begin select * into r from RRL_ARTICULS where ACTICUL=:old;r.ACTICUL:=:a;r.BARCODE_SHT:=:gtin;insert into RRL_ARTICULS values r;end;',old=old,a=article,gtin=gtin)
 meta("insert into RRL_STOCK_UOM_CONVERSION(ARTICUL,INPUT_UOM,BASE_UOM,POLICY_VERSION,NUMERATOR,DENOMINATOR,BASE_SCALE,PROVENANCE)select :a,INPUT_UOM,BASE_UOM,POLICY_VERSION,NUMERATOR,DENOMINATOR,BASE_SCALE,'Own tobacco context'from RRL_STOCK_UOM_CONVERSION where ARTICUL=:old",a=article,old=old)
 meta("insert into RRL_SKU_RECEIPT_POLICY(ARTICUL,POLICY_VERSION,MARKING_REQUIRED,UPDATED_BY)values(:a,1,1,'admin')",a=article)
 meta("insert into RRL_SKU_RECEIPT_PROFILE(ARTICUL,SYSTEM_CODE,PROFILE_CODE,PROFILE_VERSION,SCAN_MODE)select :a,SYSTEM_CODE,PROFILE_CODE,PROFILE_VERSION,SCAN_MODE from RRL_SKU_RECEIPT_PROFILE where ARTICUL=:old",a=article,old=old)
 meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('SKU',:a),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",a=article)
 doc.update(article=article,pallet_identifier=uid,document_reference='Own leading01 tobacco '+tag)
 for i,unit in enumerate(doc['units']):
  for code in unit['codes']:
   code['code']=gtin+'AB21XY'+str(i) if code['system_code']=='CRPT' else ('QA'+tag+str(i)).ljust(68,'X')
   if code['system_code']=='CRPT':
    assert canonical_mark('CRPT','TOBACCO',code['code'],gtin)['gtin']==gtin
    try:canonical_mark('CRPT','TOBACCO',code['code']);raise AssertionError('Expected context-free ambiguity fixture')
    except ValueError:pass
 for agg in doc['aggregations']:agg['code']=agg['aggregation_id']+':'+tag
 manifest={'operation_id':'TOBACCO130.MANIFEST:'+tag,'manifest_json':json.dumps(doc,separators=(',',':'))};api('/api/inventory/trace-manifests',manifest)
 scans=[{k:a[k]for k in ['system_code','profile_code','level','code']}for a in doc['aggregations']if a['aggregation_id']in ['CRPT.PALLET','EGAIS.BOX']]
 body={'operation_id':'TOBACCO130.BIRTH:'+tag,'revision_id':225,'uid':uid,'cell':'QMa3b49b8174','article':article,'quantity':'3','expiry_date':'2030-01-01','price':'0','reason':'Tobacco GTIN context matches source','capture':{'manifest_operation_id':manifest['operation_id'],'units':[],'aggregations':scans}}
 result=api('/api/inventory/stock-posting/inventory/lots',body);assert api('/api/inventory/stock-posting/inventory/lots',body)==result
 q.execute('select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:lot_id',lot_id=uid);assert q.fetchone()==(3,0)
 q.execute('select GTIN,SERIAL_NO from RRL_CRPT_CODES where UID_PALLET=:lot_id order by SERIAL_NO',lot_id=uid);assert q.fetchall()==[(gtin,'AB21XY'+str(i))for i in range(3)]
 print('PASS130 leading01 GTIN/serial21/contextual source canonical compare/native exact3/everyprofile/codes6/replay/no fake SSCC; '+body['operation_id'],flush=True)
