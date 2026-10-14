"""Actual HTTP marked inventory birth: internal UID distinct from regulatory SSCC."""
import sys,json
from pathlib import Path
from uuid import uuid4
from copy import deepcopy
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'api/wms_api_server'))
from app.config import get_settings
from app.modules.platform.public import read_oracle_json
s=get_settings();tag=uuid4().hex[:10];actor='QM125'+tag;group=actor.upper();secret=uuid4().hex
admin=httpx.Client(auth=('admin','admin123'),timeout=35);user=httpx.Client(auth=(actor,secret),timeout=35);base='http://127.0.0.1:8088'
def api(client,method,path,body=None,status=200):
 r=client.request(method,base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:1800]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 c.call_timeout=15000;q=c.cursor();q.execute("select RAW_JSON from RRL_TRACE_SENDER_MANIFEST where OPERATION_ID='MANIFEST.IMPORT:a3b49b8174.CURRENT'");original=read_oracle_json(q.fetchone()[0])
 ware=original['warehouse_id'];q.execute('select CELL from RRL_CELLS where WARE_ID=:w',w=ware);cell=q.fetchone()[0]
 q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:secret,'Own marked receiver',:grp,:ware,0,0)",id=actor,secret=secret,grp=group,ware=ware);c.commit()
 api(admin,'POST','/api/admin/rights/groups',{'id':group,'name':'Own marked receiver'})
 for right in ['trace_manifest_import','stock_inventory_count']:
  api(admin,'POST',f'/api/admin/rights/groups/{group}/rights',{'right_name':right,'description':'Own sender fixture'})
 try:
  api(user,'GET','/api/inventory/trace-manifests/warehouses/9104',status=403)
  for index,explicit in enumerate([False,True]):
   doc=deepcopy(original);uid='INTERNAL.MARKED.LONG.PALLET:'+tag+str(index);assert 32<len(uid)<=50
   doc['pallet_identifier']=uid;doc['document_reference']='Own125:'+tag+str(index)
   for unit in doc['units']:
    for code in unit['codes']:
     code['code']=code['code'][:14]+tag[:5]+str(index)+unit['unit_id'] if code['system_code']=='CRPT' else ('QA'+tag+str(index)+unit['unit_id']).ljust(68,'X')
   for agg in doc['aggregations']:agg['code']=agg['aggregation_id']+':'+tag+str(index)
   prefix='200'+str(int(tag,16)).zfill(14)
   sscc=prefix+str((10-sum(int(n)*(3 if i%2==0 else 1)for i,n in enumerate(reversed(prefix)))%10)%10)
   if explicit:doc['aggregations'][2]['code']='(00)'+sscc
   imp={'operation_id':'MANIFEST125:'+tag+str(index),'manifest_json':json.dumps(doc,separators=(',',':'))}
   imported=api(user,'POST','/api/inventory/trace-manifests',imp)
   assert imported['physical_unit_count']==3 and imported['stock_changed'] is False
   assert api(user,'POST','/api/inventory/trace-manifests',imp)==imported
   api(user,'POST','/api/inventory/trace-manifests',{**imp,'manifest_json':imp['manifest_json']+' '},409)
   scans=[{k:a[k]for k in ['system_code','profile_code','level','code']}for a in doc['aggregations']if a['aggregation_id']in ['CRPT.PALLET','EGAIS.BOX']]
   body={'operation_id':'MANIFEST125.BIRTH:'+tag+str(index),'revision_id':doc['source_document_id'],'uid':uid,'cell':cell,'article':doc['article'],'quantity':'3','expiry_date':'2030-01-01','price':'0','reason':'Internal identifier distinct from regulatory SSCC','capture':{'manifest_operation_id':imp['operation_id'],'units':[],'aggregations':scans}}
   bad=deepcopy(body);bad['operation_id']+='.BAD';bad['capture']['aggregations'][0]['level']='BOX'
   refused=api(user,'POST','/api/inventory/stock-posting/inventory/lots',bad,409);assert refused['detail']['outcome_confirmed'] is True
   born=api(user,'POST','/api/inventory/stock-posting/inventory/lots',body)
   assert api(user,'POST','/api/inventory/stock-posting/inventory/lots',body)==born
   q.execute('select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:lot_id and CELL=:cell',lot_id=uid,cell=cell);assert q.fetchone()==(3,0)
   q.execute('select PARENT_SSCC,count(*)from RRL_CRPT_CODES where UID_PALLET=:lot_id group by PARENT_SSCC',lot_id=uid);assert q.fetchone()==(sscc if explicit else None,3)
   q.execute('select SSCC from RRL_CRPT_AGGREGATION where UID_PALLET=:lot_id',lot_id=uid);assert q.fetchall()==([(sscc,)]if explicit else [])
   q.execute('select count(*)from RRL_WMS_RECEIPT_UNIT where UID_PALLET=:lot_id',lot_id=uid);assert q.fetchone()==(3,)
   print('PASS125 current nonadmin/WARE/foreign403/HTTP replay/changed raw409/wrong mode409/internal UID'+str(len(uid))+'/P3H0/physical3/regulatorySSCC '+('explicit'if explicit else 'absent')+'; '+body['operation_id'],flush=True)
 finally:
  q.execute('update RUSERS set DELETED=1 where ID=:id',id=actor);c.commit()
