"""Actual current nonadmin inventory UNIT scanning and immutable settings snapshot."""
import json,sys
from pathlib import Path
from copy import deepcopy
from uuid import uuid4
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'api/wms_api_server'))
from app.config import get_settings
cfg=get_settings();tag=uuid4().hex[:10];actor='QU128'+tag;group=actor.upper();secret=uuid4().hex
article='QUNIT'+tag.upper();uid='UNIT.CAPTURE:'+tag;ware=10828603;cell='QMa3b49b8174';revision=225
admin=httpx.Client(auth=('admin','admin123'),timeout=35);user=httpx.Client(auth=(actor,secret),timeout=35);base='http://127.0.0.1:8088'
def api(client,method,path,body=None,status=200):
 r=client.request(method,base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:1800]);return r.json()
with oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn)as c:
 c.call_timeout=15000;q=c.cursor()
 def meta(sql,**binds):
  q.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin','warehouse_settings_edit'])
  try:q.execute(sql,binds);c.commit()
  except BaseException:c.rollback();raise
  finally:q.callproc('RRL_STOCK_CONFIG_API.end_change')
 old='QMANA3B49B8174'
 meta('declare r RRL_ARTICULS%rowtype;begin select * into r from RRL_ARTICULS where ACTICUL=:old;r.ACTICUL:=:a;insert into RRL_ARTICULS values r;end;',old=old,a=article)
 meta("insert into RRL_STOCK_UOM_CONVERSION(ARTICUL,INPUT_UOM,BASE_UOM,POLICY_VERSION,NUMERATOR,DENOMINATOR,BASE_SCALE,PROVENANCE)select :a,INPUT_UOM,BASE_UOM,POLICY_VERSION,NUMERATOR,DENOMINATOR,BASE_SCALE,'Own UNIT fixture'from RRL_STOCK_UOM_CONVERSION where ARTICUL=:old",a=article,old=old)
 meta("insert into RRL_SKU_RECEIPT_POLICY(ARTICUL,POLICY_VERSION,MARKING_REQUIRED,UPDATED_BY)values(:a,1,1,'admin')",a=article)
 meta("insert into RRL_SKU_RECEIPT_PROFILE(ARTICUL,SYSTEM_CODE,PROFILE_CODE,PROFILE_VERSION,SCAN_MODE)select :a,SYSTEM_CODE,PROFILE_CODE,'QR1','UNIT'from RRL_SKU_RECEIPT_PROFILE where ARTICUL=:old",a=article,old=old)
 meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('SKU',:a),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",a=article)
 q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:secret,'Own unit receiver',:grp,:ware,0,0)",id=actor,secret=secret,grp=group,ware=ware);c.commit()
 api(admin,'POST','/api/admin/rights/groups',{'id':group,'name':'Own direct unit capture'})
 api(admin,'POST',f'/api/admin/rights/groups/{group}/rights',{'right_name':'stock_inventory_count','description':'Own direct capture'})
 try:
  context_body={'source_document_id':revision,'article':article,'cell':cell,'pallet_identifier':uid}
  ctx=api(user,'POST','/api/inventory/trace-manifests/inventory-context',context_body)
  assert ctx['base_uom']=='EA' and all(p['mode']=='UNIT'for p in ctx['profile_versions'])
  q.execute('select BARCODE_SHT from RRL_ARTICULS where ACTICUL=:a',a=article);gtin=str(q.fetchone()[0]).zfill(14)
  units=[{'unit_id':str(i),'quantity':'1','codes':[{'system_code':'CRPT','profile_code':'TOBACCO','code':gtin+tag[:5]+str(i).zfill(2)},{'system_code':'EGAIS','profile_code':'ALCOHOL','code':('QA'+tag+str(i)).ljust(68,'X')}]}for i in range(1,4)]
  capture={'units':units,'aggregations':[],'expected_policy_version':ctx['policy_version'],'expected_profile_versions':ctx['profile_versions']}
  body={'operation_id':'UNIT128.BIRTH:'+tag,'revision_id':revision,'uid':uid,'cell':cell,'article':article,'quantity':'3','expiry_date':'2030-01-01','price':'0','reason':'Own physical unit scanning','capture':capture};path='/api/inventory/stock-posting/inventory/lots'
  meta("update RRL_SKU_RECEIPT_PROFILE set PROFILE_VERSION='QR2' where ARTICUL=:a and SYSTEM_CODE='CRPT'",a=article)
  refused=api(user,'POST',path,body,409);assert refused['detail']['outcome_confirmed'] is True
  q.execute('select count(*)from RRL_PALLETS where UID_PALLET=:lot_id',lot_id=uid);assert q.fetchone()[0]==0
  ctx=api(user,'POST','/api/inventory/trace-manifests/inventory-context',context_body);capture['expected_profile_versions']=ctx['profile_versions']
  born=api(user,'POST',path,body);assert api(user,'POST',path,body)==born
  q.execute('select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:lot_id and CELL=:cell',lot_id=uid,cell=cell);assert q.fetchone()==(3,0)
  for table,count in [('RRL_WMS_RECEIPT_UNIT',3),('RRL_WMS_RECEIPT_CODE',6),('RRL_TRACE_MANIFEST_USE',0)]:
   q.execute('select count(*)from '+table+' where UID_PALLET=:lot_id',lot_id=uid);assert q.fetchone()[0]==count
  q.execute('update RUSERS set WARE_ID=9104 where ID=:id',id=actor);c.commit()
  api(user,'POST','/api/inventory/trace-manifests/inventory-context',context_body,403)
  api(user,'POST',path,body,403)
  api(user,'GET',f'/api/inventory/stock-posting/inventory/{revision}/lots?cell={cell}&article={article}',status=403)
  api(user,'POST','/api/inventory/stock-posting/inventory/revisions',{'warehouse_id':ware},403)
  api(user,'POST','/api/inventory/stock-posting/inventory/counts',{'operation_id':'UNIT128.COUNT:'+tag,'revision_id':revision,'reason':'Foreign warehouse deny','counts':[{'uid':uid,'cell':cell,'article':article,'unit':'EA','quantity':'0','expected_stock_version':1}]},403)
  q.execute('select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:lot_id and CELL=:cell',lot_id=uid,cell=cell);assert q.fetchone()==(3,0)
  print('PASS128/129 source/current snapshot/native UNIT profiles/physical3 codes6/P3H0/no manifest/replay/stale snapshot409; current actor foreign context/read/birth/replay/count/create403; '+body['operation_id'],flush=True)
 finally:
  q.execute('update RUSERS set DELETED=1 where ID=:id',id=actor);c.commit()
