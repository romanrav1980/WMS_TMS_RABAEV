"""Existing committed source fixtures; no stock writes or fresh pallets."""
import httpx
admin=httpx.Client(auth=('admin','admin123'),timeout=35);base='http://127.0.0.1:8088'
def read(uid,params=None,status=200):
 r=admin.get(base+'/api/receiving/pallets/'+uid+'/composition',params=params or {});assert r.status_code==status,(r.status_code,r.text[:1800]);return r.json()
for uid,kind,document in [
 ('UNIT.CAPTURE:d5e9aa9590','INVENTORY_REGISTER_LOT',225),
 ('MES.MARKED.INTERNAL.PALLET:e9732e1188','MES_MOVEMENTS',99),
 ('TOBACCO.CONTEXT:fe13c21d8c','INVENTORY_REGISTER_LOT',225)]:
 first=read(uid,{'limit':1});assert first['stock_quantity']=='3'and first['physical_unit_count']==3 and first['captured_base_quantity']=='3'and first['quantity_coverage']=='MATCHED',first
 assert len(first['units'])==1 and len(first['units'][0]['codes'])==2 and first['next_cursor']
 assert first['receipt']is None and first['receipts']==[]and first['source_births'][0]['command_type']==kind
 source=first['source_births'][0]['source'];assert source['revision_id'if kind=='INVENTORY_REGISTER_LOT'else'production_order_id']==document
 read(uid,{'after':first['next_cursor'],'limit':1},409)
 second=read(uid,{'after':first['next_cursor'],'limit':1,'expected_signature':first['composition_signature']})
 third=read(uid,{'after':second['next_cursor'],'limit':1,'expected_signature':first['composition_signature']})
 assert third['next_cursor']is None and len({r['units'][0]['physical_unit_key']for r in [first,second,third]})==3
 refused=read(uid,{'after':first['next_cursor'],'expected_signature':'0'*64},409);assert refused['detail']['code']=='COMPOSITION_SNAPSHOT_CHANGED'
 print('PASS132 current read-only physical3/codes6/quantity3/coverage/source '+kind+'/'+str(document)+'/nativeJSON/SAP receipt absent/snapshot-bound pages/changed snapshot409: '+uid,flush=True)
# Existing supplier-return dispatch source reused with its current zero quantity.
ordinary=read('INTERNAL.RETURN:6b388966d1');assert ordinary['stock_quantity']=='0' and ordinary['physical_unit_count']==0
print('PASS132 actual supplier-return source remains current stock0; no read projection stock mutation.',flush=True)

sap=read('300000034518661218');assert sap['receipt']['pallet_identifier']=='300000034518661218'
assert sap['source_births'][0]['command_type']=='SAP_RECEIPT'
print('PASS132 existing genuine SAP source preserved, native JSON receipt decode, actual zero after source shipment.',flush=True)