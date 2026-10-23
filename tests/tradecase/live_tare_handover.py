"""Two different participants hand over one booked test pallet; no driver identity shortcut."""
import sys,os,json,secrets
from pathlib import Path
sys.path[:0]=['.','tests/tradecase']
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http,expect,CALLS
P=Path('runtime/test-evidence/tradecase/2026-10-19/T07/tare-1155.json');s=json.loads(P.read_text())if P.exists()else dict(actor='TC7DR1155',group='TC7DR1155',history=[])
f=json.loads(Path('runtime/test-evidence/tradecase/2026-10-19/T07/fixture-1155.json').read_text())
def save():P.write_text(json.dumps(s,indent=2,default=str))
try:
 with oracle_connection()as c:
  q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=q.fetchone()[0]
  q.execute('select PASS from RUSERS where ID=:a',a=s['actor']);r=q.fetchone()
  if r:password=r[0]
  else:
   password=secrets.token_hex(24)
   q.execute('insert into USER_GROUP(ID,NAME)values(:g,:g)',g=s['group'])
   for right in ['wms_admin_login','tare_accept']:q.execute('insert into RIGHTS(USER_GROUP,RIGHT1)values(:g,:r)',g=s['group'],r=right)
   q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED)values(:a,:p,'TRADECASE QA driver',:g,:w,0)",a=s['actor'],p=password,g=s['group'],w=f['warehouse_id']);c.commit()
 if 'binding'not in s:s['binding']=expect(200,http('PUT','/api/transport/driver-bindings/'+str(f['driver_id']),dict(user_id=s['actor'],active=True,expected_version=0)));save()
 if 'offer'not in s:
  s['offer_body']=dict(operation_id='T7.TARE.OFFER.1155',task_id=f['transport_task_id'],owner_ware_id=f['warehouse_id'],pallet_type_id=1,condition='GOOD',from_kind='WAREHOUSE',from_id=str(f['warehouse_id']),to_kind='VEHICLE',to_id=str(f['vehicle_id']),quantity='1',scan_vehicle=f['vehicle_number'],booking_operation_ids=['T6.tare.book.1155']);save()
  s['offer']=expect(200,http('POST','/api/inventory/tare/offer',s['offer_body']));save()
 if 'accept'not in s:
  s['accept_body']=dict(operation_id='T7.TARE.ACCEPT.1155',offer_operation_id='T7.TARE.OFFER.1155',accepted_quantity='1',scan_vehicle=f['vehicle_number']);save()
  expect(403,http('POST','/api/inventory/tare/accept',dict(s['accept_body'],operation_id='T7.TARE.SAME.1155')))
  s['accept']=expect(200,http('POST','/api/inventory/tare/accept',s['accept_body'],actor=s['actor'],password=password));save()
 assert expect(200,http('POST','/api/inventory/tare/offer',s['offer_body']))==s['offer']
 assert expect(200,http('POST','/api/inventory/tare/accept',s['accept_body'],actor=s['actor'],password=password))==s['accept']
 if 'binding_closed'not in s:s['binding_closed']=expect(200,http('PUT','/api/transport/driver-bindings/'+str(f['driver_id']),dict(user_id=s['actor'],active=False,expected_version=1)));save()
 s['balances']=expect(200,http('GET',f"/api/inventory/tare/warehouses/{f['warehouse_id']}/balances"));s['status']='PASS';print(json.dumps(s['balances']))
 with oracle_connection()as c:
  q=c.cursor();q.execute("update RUSERS set DELETED=1 where ID=:a and USER_GROUP=:g",a=s['actor'],g=s['group']);c.commit()
 s['actor_retired']=True;save()
finally:s['history']+=CALLS;save()
