"""Recipient-bound whole-box and partial-trip negatives; no physical goods are changed."""
import sys,os,json
from pathlib import Path
from uuid import uuid4
from datetime import datetime,timezone
sys.path[:0]=['.','tests/tradecase']
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http,expect,CALLS
w=211559882;tag='TBX'+uuid4().hex[:8];bodies=[];checks=[]
def send(kind,id,payload,status=200):
 b=dict(schema_version=1,event_id=id+'.EVENT',source_id='TC03.SAP',warehouse_id=w,document_id=id,version=1,occurred_at=datetime.now(timezone.utc).isoformat(),payload=dict(entity_type=kind,**payload));bodies.append(b);return expect(status,http('POST','/api/tradecase/messages',b))
try:
 with oracle_connection()as c:
  q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=q.fetchone()[0]
 for suffix,broken,partial in [('F',False,False),('T',True,True)]:send('RECIPIENT',tag+'.'+suffix,dict(title='QA package profile '+suffix,target_owner_id='BLC',permitted_source_owners=['SNS'],buyout_mode='BEFORE_PICK',min_osg_days=0,lead_time_days=0,allow_broken_box=broken,allow_partial_ship=partial))
 def order(id,recipient,qty,status=200,financial=False):
  extra=dict(order_kind='BUYOUT',buyout_mode='BEFORE_PICK')if financial else {}
  return send('ORDER',id,dict(recipient_id=tag+'.'+recipient,planned_ship_at='2026-11-01T10:00:00+03:00',lines=[dict(line_id='1',sku_id='A',source_owner_id='SNS',target_owner_id='BLC',mrc='200',quantity=str(qty),uom='EA',min_osg_days=0)],**extra),status)
 bad=order(tag+'.BAD3','F',3,409);assert bad['detail']['code']=='BROKEN_BOX_NOT_ALLOWED';assert expect(409,http('POST','/api/tradecase/messages',bodies[-1]))==bad;checks+=['false_profile3_rejected','rejected_packet_exact_replay']
 order(tag+'.GOOD3','T',3);order(tag+'.GOOD7','T',7);checks+=['true_profile3_and7_accepted']
 order(tag+'.FIN3','F',3,financial=True);checks+=['financial_basis_not_subject_to_shipment_box_multiple']
 order(tag+'.F100','F',100);order(tag+'.T100','T',100)
 def trip(id,orderid,qty,status=200):return send('TRIP',id,dict(vehicle_id='QA_METADATA_ONLY',planning_source='SAP',planned_departure_at='2026-11-01T10:00:00+03:00',capacity_kg='8000',capacity_m3='66',orders=[dict(order_id=orderid,line_id='1',quantity=str(qty))]),status)
 result=trip(tag+'.TRIP.BAD',tag+'.F100',90,409);assert result['detail']['code']=='PARTIAL_SHIPMENT_NOT_ALLOWED';checks+=['false_partial90of100_rejected']
 trip(tag+'.TRIP.GOOD',tag+'.T100',90);checks+=['true_partial90of100_accepted']
 with oracle_connection()as c:
  q=c.cursor();q.execute('select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w',w=w);stock=list(q.fetchone());assert stock==[250,1]
 s=dict(status='PASS',checks=checks,stock=stock,physical_writes=0,limits='Quantity divisibility only; factory BOX aggregation not proven')
 print(json.dumps(s))
except Exception as e:s=dict(status='FAIL',checks=checks,error=str(e));raise
finally:
 s.update(http=CALLS,requests=bodies);Path('runtime/test-evidence/tradecase/2026-10-19/T06/box-policy-'+tag+'.json').write_text(json.dumps(s,indent=2,default=str))
