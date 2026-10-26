"""Original 25 BOX buyout acceptance on one new owned 500 EA receipt; external messages are synthetic."""
from datetime import datetime,timedelta,timezone
import json,os,re,sys,xml.etree.ElementTree as ET
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(ROOT/'scripts'),str(Path(__file__).parent)]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http,expect,CALLS
import live_stock_acceptance as receipt
import live_topup_physical_660 as topup
OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-26/T05';FILE=OUT/'program-25-boxes.json'
s=json.loads(FILE.read_text(encoding='utf-8'))if FILE.exists()else dict(phase='NEW',requests={})
def save():OUT.mkdir(parents=True,exist_ok=True);FILE.write_text(json.dumps(s,indent=2,default=str),encoding='utf-8')
def db(sql,**values):
 with oracle_connection()as c:
  q=c.cursor();q.execute(sql,values);return [tuple(x.read()if hasattr(x,'read')else x for x in row)for row in q.fetchall()]
def tag():return 'B25.'+s['fixture']['tag']
def base():return f"/api/tradecase/warehouses/{s['fixture']['warehouse_id']}"
def stock():return db('select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w',w=s['fixture']['warehouse_id'])[0]
def step(key,path,body=None,method='POST',actor=None,password=None,status=200):
 requests=s['requests']
 if key not in requests:requests[key]=dict(path=path,body=body,method=method,status=status);save()
 request=requests[key]
 if 'result'not in request:request['result']=expect(request['status'],http(request['method'],request['path'],request['body'],actor,password));save()
 return request['result']
def send(key,kind,document,payload,version=1):
 return step(key,'/api/tradecase/messages',dict(schema_version=1,event_id=tag()+'.'+key,source_id='TC03.SAP',warehouse_id=s['fixture']['warehouse_id'],document_id=document,version=version,occurred_at=datetime.now(timezone.utc).isoformat(),payload=dict(entity_type=kind,**payload)))
def new_cell(key,zone):
 f=s['fixture'];cell='B25'+f['tag']+key
 if not db('select count(*)from RRL_CELLS where CELL=:c',c=cell)[0][0]:
  with oracle_connection()as c:
   q=c.cursor();q.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin','warehouse_settings_edit'])
   try:
    q.execute('insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT)values(:c,:w,0,0,0,0,1,0,0)',c=cell,w=f['warehouse_id'])
    q.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:c),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",c=cell);c.commit()
   finally:q.callproc('RRL_STOCK_CONFIG_API.end_change')
 step('cell.'+key,base()+'/stock/cells/'+cell,dict(operation_id=tag()+'.cell.'+key,expected_version=0,zone_kind=zone,reason='Owned 25 BOX acceptance location'),method='PUT');return cell
def receive():
 if 'fixture'not in s:
  if 'planned'not in s:
   uid,ware=topup.plan_fixture();s['planned']=dict(uuid=uid,warehouse=ware);save()
  original=receipt.uuid4;receipt.uuid4=lambda:type('Tag',(),dict(hex=s['planned']['uuid']))()
  try:s['fixture']=receipt.setup();s['fixture']['receipt_quantity']=500;save()
  finally:receipt.uuid4=original
 f=s['fixture'];assert f['warehouse_id']==s['planned']['warehouse']
 if 'received'not in s:
  # Replay the exact recorded exchange sequence if reception is interrupted.
  original_http,original_xml=receipt.http,receipt.xml_call;sequence=[0]
  def recorded(method,path,body=None,actor=None,password=None):
   key='receipt.'+str(sequence[0]);sequence[0]+=1
   if key not in s['requests']:s['requests'][key]=dict(method=method,path=path,body=body);save()
   request=s['requests'][key]
   if 'response'not in request:
    response=http(request['method'],request['path'],request['body'],actor,password)
    if response[0]<500:request['response']=response;save()
    return response
   return tuple(request['response'])
  def recorded_xml(path,element,status):
   key='xml.supply'
   if key not in s['requests']:s['requests'][key]=dict(path=path,xml=ET.tostring(element,encoding='unicode'),status=status);save()
   request=s['requests'][key]
   if 'result'not in request:request['result']=original_xml(request['path'],ET.fromstring(request['xml']),request['status']);save()
   return request['result']
  receipt.http,receipt.xml_call=recorded,recorded_xml
  try:s['received']=receipt.run(f);save()
  finally:receipt.http,receipt.xml_call=original_http,original_xml
 rows=db('select PHYSICAL_UNIT_KEY,VERSION_NO from RRL_TRADE_STOCK_ATTR where CAPTURE_WARE_ID=:w order by PHYSICAL_UNIT_KEY',w=f['warehouse_id']);assert len(rows)==500
 step('valid',base()+'/stock/mark-confirmations',dict(operation_id=tag()+'.valid',skm_id='TC03.SKM',external_event_id=tag()+'.valid',expected_site_version=1,occurred_at=datetime.now(timezone.utc).isoformat(),items=[dict(physical_unit_key=k,expected_attribute_version=v,verdict='VALID')for k,v in rows]))
 s['phase']='RECEIVED';save();assert stock()==(500,0)
def native_order(key,customer,quantity):
 if key not in s:
  f=s['fixture']
  with oracle_connection()as c:
   q=c.cursor();q.callproc('RRL_STOCK_METADATA_TX.begin_change',['admin','warehouse_settings_edit'])
   try:
    q.execute('select RRL_CUSTOMER_ORDER_SQ.nextval,RRL_CUSTOMER_ORDER_ROW_SQ.nextval from dual');order,row=q.fetchone()
    q.execute("insert into RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID,ORDER_NO,CUSTOMER_ID,WARE_ID,SHIPMENT_DATE,STATUS,SOURCE_SYSTEM,CREATED_BY)values(:o,:code,:c,:w,trunc(sysdate)+1,'OPEN','QA_TRADECASE_ONLY','admin')",o=order,code=tag()+'.'+key,c=customer,w=f['warehouse_id'])
    q.execute("insert into RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,LINE_NO,ARTICUL,PRODUCT_NAME,UNIT_CODE,ORDER_QTY,WARE_ID,STATUS,CREATED_BY)values(:r,:o,1,:a,'Original 25 BOX buyout QA','EA',:qty,:w,'OPEN','admin')",r=row,o=order,a=f['article'],qty=quantity,w=f['warehouse_id']);c.commit()
   finally:q.callproc('RRL_STOCK_METADATA_TX.end_change')
  s[key]=dict(order=order,row=row);save()
 return s[key]
def prepare_after():
 f=s['fixture'];w=f['warehouse_id'];quantity=250
 customer=step('customer','/api/customers',dict(customer_code=tag(),customer_name='Original 25 BOX acceptance',customer_type='LEGAL_ENTITY'))['customer_id']
 send('recipient.after','RECIPIENT','AFTER.C',dict(title='25 BOX after picking',wms_customer_id=customer,target_owner_id='BLC',permitted_source_owners=['SNS'],buyout_mode='AFTER_PICK',min_osg_days=0,lead_time_days=0,allow_broken_box=False,allow_partial_pick=False,allow_partial_ship=False))
 day=(datetime.now(ZoneInfo('Europe/Moscow')).date()+timedelta(days=1)).isoformat();s.setdefault('day',day);save();day=s['day']
 send('order.after','ORDER','AFTER',dict(recipient_id='AFTER.C',planned_ship_at=day+'T12:00:00+03:00',lines=[dict(line_id='1',sku_id='A',source_owner_id='SNS',target_owner_id='BLC',mrc='200',quantity='250',uom='EA',min_osg_days=0)]))
 native=native_order('native_after',customer,quantity)
 step('binding.after',base()+'/orders/AFTER/binding',dict(operation_id=tag()+'.after.bind',expected_order_version=1,customer_order_id=native['order'],lines=[dict(line_id='1',customer_order_row_id=native['row'])]))
 route=step('route','/api/picking/routes',dict(route_code=tag(),route_name='Original 25 BOX QA',ware_id=w))['pick_route_id']
 rc=step('route.cell','/api/picking/route-cells',dict(pick_route_id=route,cell_code=f['pick'],pick_sequence=1))['pick_route_cell_id']
 face=step('face','/api/picking/pick-faces',dict(ware_id=w,cell_code=f['pick'],pick_face_code=tag(),pick_route_id=route,pick_route_cell_id=rc,pick_sequence=1,min_case_qty=0,max_case_qty=25,replenishment_trigger_qty=1))['pick_face_id']
 step('face.article',f'/api/picking/pick-faces/{face}/articuls',dict(articul=f['article'],priority='1',min_qty='0',max_qty='250',replenishment_method='IMMEDIATE',replenishment_qty_mode='FILL_TO_VOLUME',use_articul_replenish_rule=0,boxes_per_layer='5',boxes_per_pallet='25',box_volume_m3='0.1'))
 plan=step('plan.after','/api/picking/plans',dict(operation_id=tag()+'.after.plan',customer_order_id=native['order']))['pick_plan_id']
 tasks=db('select TASK_TYPE,QTY from RRL_PICK_TASK where PICK_PLAN_ID=:p',p=plan);assert tasks==[('CASE_PICK',250)],tasks
 wave=step('wave.after','/api/picking/waves',dict(wave_code=tag()+'.AFTER',wave_name='25 BOX after picking',ware_id=w,planned_start_at=day+'T08:00:00+03:00',planned_finish_at=day+'T09:00:00+03:00'))['pick_wave_id']
 s['wave_after']=wave;save()
 for key,suffix,body in [('add','plans',dict(pick_plan_id=plan)),('calculate','calculate',{}),('launch','launch',dict(operation_id=tag()+'.after.launch'))]:step('wave.after.'+key,f'/api/picking/waves/{wave}/'+suffix,body)
 for tid,pallet,src,dst,qty in db("select TASK_ID,UID_PALLET,FROM_CELL,TO_CELL,QTY from RRL_WAREHOUSE_TASK where TASK_SOURCE='WAVE' and SOURCE_DOC_ID=:w and TASK_TYPE='REPLENISHMENT'",w=wave):
  units=[k for(k,)in db("select u.PHYSICAL_UNIT_KEY from RRL_WMS_RECEIPT_UNIT u join RRL_STOCK_RESERVATION r on r.RESERVATION_ID=u.HARD_RESERVATION_ID where u.CURRENT_UID=:p and u.CURRENT_CELL=:c and r.SOURCE_DOC_TYPE='PICK_WAVE' and r.SOURCE_DOC_ID=:w order by u.PHYSICAL_UNIT_KEY",p=pallet,c=src,w=wave)][:int(qty)]
  physical=db('select REMAIN from RRL_REMAINS where UID_POLETA=:p and CELL=:c',p=pallet,c=src)[0][0]
  if int(qty)==physical:
   units=[k for(k,)in db("select PHYSICAL_UNIT_KEY from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:p and CURRENT_CELL=:c and STOCK_STATUS='AVAILABLE'order by PHYSICAL_UNIT_KEY",p=pallet,c=src)]
  assert len(units)==int(qty),(tid,qty,len(units))
  step('repl.'+str(tid),f'/api/warehouse-tasks/{tid}/complete',dict(operation_id=tag()+'.repl.'+str(tid),scanned_pallet=pallet,scanned_from_cell=src,scanned_to_cell=dst,fact_qty=str(qty),unit_keys=units))
 step('release.after',f'/api/picking/waves/{wave}/release-picking',dict(operation_id=tag()+'.after.release'))
 rows=db('select CASE_PICK_TASK_ID,CASE_PICK_LINE_ID,PICK_TASK_ID from RRL_CASE_PICK_LINE where PICK_WAVE_ID=:w',w=wave);assert len(rows)==1,rows
 s['case_after'],s['line_after'],s['pick_task_after']=rows[0];s['phase']='AFTER_PREPARED';save()
def pick_after():
 import live_factory_case as case
 f=s['fixture'];w=f['warehouse_id'];cs=s.setdefault('case_state',dict(warehouse_id=w,article=f['article'],pick=f['pick'],quantity=250,case=s['case_after'],line=s['line_after'],pick_task=s['pick_task_after'],history=[]))
 def case_save():s['case_state']=case.s;save()
 def case_step(key,path,body,method='POST',actor=None,password=None):
  result=step('case.'+key,path,body,method,actor,password);case.s[key]=result;case_save();return result
 case.s=cs;case.tag=tag()+'.CASE';case.w=w;case.base=base();case.save=case_save;case.step=case_step
 case.execute(return_after=False)
 wait=new_cell('W','WAIT')
 status,version,carrier=db('select STATUS,CONTENT_VERSION,SSCC from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t',t=s['case_after'])[0]
 step('after.wait',f"/api/case-pick/tasks/{s['case_after']}/move-carrier",dict(operation_id=tag()+'.after.wait',scan_container=carrier,scanned_to_cell=wait,expected_content_version=version))
 s['after_keys']=[k for(k,)in db('select u.PHYSICAL_UNIT_KEY from RRL_WMS_RECEIPT_UNIT u join RRL_CASE_CARRIER_LOT h on h.LOT_UID=u.CURRENT_UID where h.CASE_PICK_TASK_ID=:t order by u.PHYSICAL_UNIT_KEY',t=s['case_after'])];assert len(s['after_keys'])==250
 s['phase']='AFTER_PICKED';save()
def buyout_after():
 keys=s['after_keys'];url=base()+'/buyouts';before=stock()
 send('basis.after','ORDER','AFTER.FIN',dict(recipient_id='AFTER.C',order_kind='BUYOUT',buyout_mode='AFTER_PICK',planned_ship_at=s['day']+'T12:00:00+03:00',lines=[dict(line_id='1',sku_id='A',source_owner_id='SNS',target_owner_id='BLC',mrc='200',quantity='250',uom='EA',min_osg_days=0)]))
 request=dict(operation_id=tag()+'.after.buyout',buyout_id=tag()+'.AFTER',basis_order_id='AFTER.FIN',basis_line_id='1',expected_basis_version=1,unit_keys=keys,demand_order_id='AFTER',demand_line_id='1')
 result=step('buyout.after',url,request);assert result['pending_units']==250 and result['owner_changes']==0
 for label,version,items,confirmed,pending in [('20',1,keys[:200],200,50),('5',2,keys[200:],250,0)]:
  body=dict(operation_id=tag()+'.after.result.'+label,buyout_id=tag()+'.AFTER',expected_version=version,skm_id='TC03.SKM',external_event_id=tag()+'.after.result.'+label,external_document_id=tag()+'.AFTER.DOC',occurred_at=datetime.now(timezone.utc).isoformat(),items=[dict(physical_unit_key=k,outcome='CONFIRMED')for k in items])
  answer=step('buyout.after.'+label,url+'/results',body);assert(answer['confirmed_units'],answer['pending_units'])==(confirmed,pending)
  original=s['requests']['buyout.after.'+label]['body'];replay=expect(200,http('POST',url+'/results',original));assert replay['replayed'] and {k:v for k,v in replay.items()if k!='replayed'}=={k:v for k,v in answer.items()if k!='replayed'}
 assert stock()==before
 owners=db('select OWNER_ID,count(*)from RRL_TRADE_STOCK_ATTR where CAPTURE_WARE_ID=:w group by OWNER_ID order by OWNER_ID',w=s['fixture']['warehouse_id']);assert owners==[('BLC',250),('SNS',250)],owners
 s['after_buyout_stock']=stock();s['phase']='AFTER_BOUGHT';save()
def prepare_transit():
 f=s['fixture'];w=f['warehouse_id'];customer=s['requests']['customer']['result']['customer_id']
 send('recipient.transit','RECIPIENT','TRANSIT.C',dict(title='25 BOX in transit',wms_customer_id=customer,target_owner_id='BLC',permitted_source_owners=['SNS'],buyout_mode='IN_TRANSIT',min_osg_days=0,lead_time_days=0,allow_broken_box=False,allow_partial_pick=False,allow_partial_ship=False))
 send('order.transit','ORDER','TRANSIT',dict(recipient_id='TRANSIT.C',planned_ship_at=s['day']+'T12:00:00+03:00',lines=[dict(line_id='1',sku_id='A',source_owner_id='SNS',target_owner_id='BLC',mrc='200',quantity='250',uom='EA',min_osg_days=0)]))
 native=native_order('native_transit',customer,250)
 step('binding.transit',base()+'/orders/TRANSIT/binding',dict(operation_id=tag()+'.transit.bind',expected_order_version=1,customer_order_id=native['order'],lines=[dict(line_id='1',customer_order_row_id=native['row'])]))
 expedition=new_cell('E','EXPEDITION');s['expedition']=expedition;save()
 plan=step('plan.transit','/api/picking/plans',dict(operation_id=tag()+'.transit.plan',customer_order_id=native['order']))['pick_plan_id']
 types=db('select TASK_TYPE,QTY from RRL_PICK_TASK where PICK_PLAN_ID=:p',p=plan);assert types==[('FULL_PALLET',250)],types
 wave=step('wave.transit','/api/picking/waves',dict(wave_code=tag()+'.TRANSIT',wave_name='25 BOX in transit',ware_id=w,planned_start_at=s['day']+'T08:00:00+03:00',planned_finish_at=s['day']+'T09:00:00+03:00'))['pick_wave_id'];s['wave_transit']=wave;save()
 for key,suffix,body in [('add','plans',dict(pick_plan_id=plan)),('calculate','calculate',{}),('launch','launch',dict(operation_id=tag()+'.transit.launch')),('staging','staging/release',dict(to_cell=expedition)),('release','release-picking',dict(operation_id=tag()+'.transit.release'))]:step('wave.transit.'+key,f'/api/picking/waves/{wave}/'+suffix,body)
 tasks=db("select TASK_ID,UID_PALLET,FROM_CELL,TO_CELL,QTY from RRL_WAREHOUSE_TASK where TASK_SOURCE='WAVE'and SOURCE_DOC_ID=:w and TASK_TYPE='PICKING_MOVE'",w=wave);assert len(tasks)==1 and tasks[0][4]==250,tasks
 tid,pallet,src,dst,qty=tasks[0]
 step('transit.move',f'/api/warehouse-tasks/{tid}/complete',dict(operation_id=tag()+'.transit.move',scanned_pallet=pallet,scanned_from_cell=src,scanned_to_cell=dst,fact_qty=str(qty)))
 s['transit_task']=tid;s['transit_pallet']=pallet;s['phase']='TRANSIT_PICKED';save()

def bind_and_load():
 import subprocess
 from full_pallet_fixture import prepare_shipment
 f=s['fixture'];w=f['warehouse_id'];st='B25.'+str(w)
 s.setdefault('shipments',{});save()
 for key,native in [('after',s['native_after']),('transit',s['native_transit'])]:
  if key not in s['shipments']:s['shipments'][key]=prepare_shipment(dict(fixture=f,native_order=native['order'],shipment_quantity=250,shipment_identifier=tag()+'.ST.'+key,st_number=st));save()
 case=s['case_after'];carrier,version=db('select SSCC,CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t',t=case)[0]
 step('after.expedition',f'/api/case-pick/tasks/{case}/move-carrier',dict(operation_id=tag()+'.after.expedition',scan_container=carrier,scanned_to_cell=s['expedition'],expected_content_version=version))
 version=db('select CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t',t=case)[0][0]
 step('bind.after.shipment',f'/api/case-pick/tasks/{case}/bind-shipment',dict(pallet_identifier=s['shipments']['after']['shipment_identifier'],scan_container=carrier,expected_content_version=version))
 path=f"/api/warehouse-tasks/{s['transit_task']}/full-pallet-shipment"
 if 'bind.transit.shipment'not in s['requests']:
  current=expect(200,http('GET',path))
  step('bind.transit.shipment',path,dict(operation_id=tag()+'.transit.shipment',shipment_identifier=s['shipments']['transit']['shipment_identifier'],scanned_pallet=current['pallet_identifier'],expected_stock_version=current['stock_version']))
 if 'floor.transit'not in s['requests']:
  floor=expect(200,http('GET','/api/inventory/pallet-floor-types?identifier='+s['transit_pallet']))
  step('floor.transit','/api/inventory/pallet-floor-types',dict(operation_id=tag()+'.transit.floor',identifier=s['transit_pallet'],pallet_type_id=1,expected_version=floor['version'],scan_pallet=s['transit_pallet'],scan_cell=floor['cell'],evidence_reference='OWN_SYNTHETIC_CARRIER_NOT_HARDWARE'))
 if 'vehicle'not in s:s['vehicle']=step('vehicle.created','/api/admin/transport/vehicles',dict(num_plat='B25V'+str(w),transtype_id='10',max_weight_kg=1000,max_pallets=2,sobstvennyy=True),status=201)['id'];save()
 if 'vehicle.profile'not in s['requests']:
  p=expect(200,http('GET',f"/api/admin/transport/vehicles/{s['vehicle']}/profile"))
  step('vehicle.profile','/api/admin/transport/vehicle-profiles',dict(operation_id=tag()+'.vehicle.profile',vehicle_id=s['vehicle'],expected_source_hash=p['base_hash'],expected_version=p['version'],vehicle_size_class='QA_BUYOUT_25',cargo_length_mm=6000,cargo_width_mm=2500,cargo_height_mm=3000,outer_height_mm=4000,outer_length_mm=8000,floor_variants=[dict(code='QA_TWO_EURO',limits=[dict(pallet_type_id=1,max_places=2)])],reason='Owned synthetic 25 BOX financial-context test, not industrial vehicle',evidence_reference='TEST_NOT_HARDWARE'))
 file=OUT/'program-25-transport.json'
 if not file.exists():file.write_text(json.dumps(dict(warehouse_id=w,case_id=w,st_number=st,vehicle_id=s['vehicle'],vehicle_number='B25V'+str(w),dock='B25D'+str(w),shipment_date=s['day'],http=[]),indent=2),encoding='utf-8')
 if 'transport'not in s:
  process=subprocess.run([sys.executable,'tests/tradecase/prepare_transport_task.py'],cwd=ROOT,env=dict(os.environ,TRADECASE_TRANSPORT_FIXTURE=str(file)),capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=120)
  assert process.returncode==0,(process.stdout+process.stderr)[-2000:]
  s['transport']={k:v for k,v in json.loads(file.read_text()).items()if k!='http'};save()
 transport=s['transport']
 for key,ship in s['shipments'].items():
  ident=ship['shipment_identifier']
  if 'qc.'+key not in s['requests']:
   quality=expect(200,http('GET','/api/outgoing-quality/'+ident))
   if key=='after':keys=s['after_keys']
   else:keys=[k for(k,)in db("select PHYSICAL_UNIT_KEY from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:p and STOCK_STATUS='AVAILABLE'order by PHYSICAL_UNIT_KEY",p=s['transit_pallet'])];s['transit_keys']=keys;save()
   assert len(keys)==250
   codes=db("select u.PHYSICAL_UNIT_KEY,c.SYSTEM_CODE,c.RAW_CODE from RRL_WMS_RECEIPT_UNIT u join RRL_WMS_RECEIPT_CODE c on c.UID_PALLET=u.UID_PALLET and c.UNIT_ID=u.UNIT_ID where u.PHYSICAL_UNIT_KEY in(select PHYSICAL_UNIT_KEY from RRL_TRADE_STOCK_ATTR where CAPTURE_WARE_ID=:w)order by u.PHYSICAL_UNIT_KEY",w=w)
   scans=[dict(system_code=system,profile_code='TOBACCO',code=code)for unit,system,code in codes if unit in set(keys)];assert len(scans)==250
   step('qc.'+key,'/api/outgoing-quality/'+ident+'/scan',dict(operation_id=tag()+'.qc.'+key,expected_composition_signature=quality['composition_signature'],error_count=0,scans=scans))
  step('composition.before.'+key,'/api/tradecase/order-compositions/report',dict(warehouse_id=w,order_id=key.upper()))
  if 'load.'+key not in s['requests']:
   p=expect(200,http('GET','/api/transport/loading/single-preview?shipment_identifier='+ident))
   body=dict(operation_id=tag()+'.load.'+key,identifier=ident,expected_version=p['expected_version'],expected_composition_signature=p['composition_signature'],scan_container=p['snapshot']['root'],scan_cell=p['snapshot']['cell'],transport_task_id=transport['transport_task_id'],scan_vehicle=transport['vehicle_number'],scan_dock=transport['dock'],measurements=dict(origin='MANUAL_CONFIRMED',content_version=p['expected_version'],gross_weight_kg='300',width_m='1.2',depth_m='1.0',height_m='2.7'))
  else:body=s['requests']['load.'+key]['body']
  loaded=step('load.'+key,'/api/transport/loading/confirm-single',body);assert expect(200,http('POST','/api/transport/loading/confirm-single',s['requests']['load.'+key]['body']))==loaded
  card=step('composition.loaded.'+key,'/api/tradecase/order-compositions/report',dict(warehouse_id=w,order_id=key.upper()))
  assert card['units']==card['codes']==250
  for system,sender in [('SAP','TC03.SAP'),('SKM','TC03.SKM')]:
   step('composition.ack.'+key+'.'+system,'/api/tradecase/order-compositions/acknowledgments',dict(schema_version=1,warehouse_id=w,order_id=key.upper(),system_code=system,sender_id=sender,event_id=tag()+'.ack.'+key+'.'+system,composition_no=card['composition_no'],signature=card['signature'],outcome='ACCEPTED',occurred_at=datetime.now(timezone.utc).isoformat()))
 assert stock()==(0,0),stock();s['phase']='LOADED';save()

def depart():
 import secrets
 from uuid import uuid4
 f=s['fixture'];w=f['warehouse_id'];transport=s['transport'];trip_id=transport['transport_task_id']
 send('basis.transit','ORDER','TRANSIT.FIN',dict(recipient_id='TRANSIT.C',order_kind='BUYOUT',buyout_mode='IN_TRANSIT',planned_ship_at=s['day']+'T12:00:00+03:00',lines=[dict(line_id='1',sku_id='A',source_owner_id='SNS',target_owner_id='BLC',mrc='200',quantity='250',uom='EA',min_osg_days=0)]))
 load=s['requests']['load.transit']['body']['operation_id']
 early=dict(operation_id=tag()+'.transit.early',buyout_id=tag()+'.TRANSIT.EARLY',basis_order_id='TRANSIT.FIN',basis_line_id='1',expected_basis_version=1,unit_keys=s['transit_keys'],demand_order_id='TRANSIT',demand_line_id='1',load_operation_id=load)
 step('buyout.transit.early',base()+'/buyouts',early,status=409)
 assert db("select OWNER_ID,count(*)from RRL_TRADE_STOCK_ATTR where CAPTURE_WARE_ID=:w group by OWNER_ID order by OWNER_ID",w=w)==[('BLC',250),('SNS',250)]
 if 'tare_driver'not in s:s['tare_driver']=dict(username='BD25'+uuid4().hex[:9],password=secrets.token_hex(24));save()
 driver=s['tare_driver'];actor=driver['username']
 if 'driver_created'not in s:
  with oracle_connection()as c:
   q=c.cursor();q.execute('select count(*)from RUSERS where ID=:a',a=actor)
   if q.fetchone()[0]==0:
    q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Own 25 BOX tare driver',:a,:w,0,1)",a=actor,p=driver['password'],w=w)
    for permission in ['tare_accept','tare_offer','driver_return_accept']:q.execute('insert into RIGHTS(USER_GROUP,RIGHT1)values(:a,:r)',a=actor,r=permission)
    c.commit()
  s['driver_created']=True;save()
 step('driver.binding',f"/api/transport/driver-bindings/{transport['driver_id']}",dict(user_id=actor,active=True,expected_version=0),method='PUT')
 booking=s['requests']['case.tare_book']['body']['operation_id']
 step('tare.offer','/api/inventory/tare/offer',dict(operation_id=tag()+'.tare.offer',task_id=trip_id,owner_ware_id=w,pallet_type_id=1,condition='GOOD',from_kind='WAREHOUSE',from_id=str(w),to_kind='VEHICLE',to_id=str(s['vehicle']),quantity='1',scan_vehicle=transport['vehicle_number'],booking_operation_ids=[booking]))
 step('tare.accept','/api/inventory/tare/accept',dict(operation_id=tag()+'.tare.accept',offer_operation_id=tag()+'.tare.offer',accepted_quantity='1',scan_vehicle=transport['vehicle_number']),actor=actor,password=driver['password'])
 send('trip','TRIP','RUN',dict(vehicle_id=transport['vehicle_number'],planning_source='SAP',planned_departure_at=s['day']+'T10:00:00+03:00',capacity_kg='1000',capacity_m3='45',orders=[dict(order_id=key,line_id='1',quantity='250')for key in ['AFTER','TRANSIT']]))
 path=base()+'/trips/RUN'
 step('trip.binding',path+'/binding',dict(operation_id=tag()+'.trip.binding',native_task_id=trip_id,expected_trip_version=1,expected_binding_version=0))
 if 'document.ready'not in s['requests']:
  state=expect(200,http('GET',path+'/execution'))
  step('document.ready',path+'/transport-document',dict(operation_id=tag()+'.document.ready',source_id='TC03.SAP',external_event_id=tag()+'.document.ready',expected_trip_version=1,expected_binding_version=1,document_version=1,document_status='READY',external_document_id='TEST_NOT_INDUSTRIAL_'+tag(),manifest_signature=state['manifest_signature'],occurred_at=datetime.now(timezone.utc).isoformat()))
 answer=step('depart',f'/api/transport/loading/{trip_id}/depart',dict(operation_id=tag()+'.depart'))
 assert expect(200,http('POST',f'/api/transport/loading/{trip_id}/depart',s['requests']['depart']['body']))==answer
 assert db("select STATUS,count(*)from RRL_TT_HU_LOAD_FACT where TT_ID=:t group by STATUS",t=trip_id)==[('DEPARTED',2)]
 s['phase']='DEPARTED';save()
def buyout_transit():
 url=base()+'/buyouts';w=s['fixture']['warehouse_id'];load=s['requests']['load.transit']['body']['operation_id']
 before=stock();events_before=db('select count(*),nvl(sum(BASE_QTY),0)from RRL_EVENTS where OPERATION_ID like :o',o=tag()+'.load.%')
 request=dict(operation_id=tag()+'.transit.buyout',buyout_id=tag()+'.TRANSIT',basis_order_id='TRANSIT.FIN',basis_line_id='1',expected_basis_version=1,unit_keys=s['transit_keys'],demand_order_id='TRANSIT',demand_line_id='1',load_operation_id=load)
 result=step('buyout.transit',url,request);assert result['pending_units']==250 and result['owner_changes']==0
 for label,version,keys,confirmed,pending in [('20',1,s['transit_keys'][:200],200,50),('5',2,s['transit_keys'][200:],250,0)]:
  body=dict(operation_id=tag()+'.transit.result.'+label,buyout_id=tag()+'.TRANSIT',expected_version=version,skm_id='TC03.SKM',external_event_id=tag()+'.transit.result.'+label,external_document_id=tag()+'.TRANSIT.DOC',occurred_at=datetime.now(timezone.utc).isoformat(),items=[dict(physical_unit_key=k,outcome='CONFIRMED')for k in keys])
  answer=step('buyout.transit.'+label,url+'/results',body);assert(answer['confirmed_units'],answer['pending_units'])==(confirmed,pending)
  replay=expect(200,http('POST',url+'/results',s['requests']['buyout.transit.'+label]['body']));assert replay['replayed'] and {k:v for k,v in replay.items()if k!='replayed'}=={k:v for k,v in answer.items()if k!='replayed'}
 assert stock()==before==(0,0)
 assert db('select count(*),nvl(sum(BASE_QTY),0)from RRL_EVENTS where OPERATION_ID like :o',o=tag()+'.load.%')==events_before
 owners=db('select OWNER_ID,count(*)from RRL_TRADE_STOCK_ATTR where CAPTURE_WARE_ID=:w group by OWNER_ID',w=w);assert owners==[('BLC',500)],owners
 assert db("select STATUS,count(*)from RRL_TT_HU_LOAD_FACT where TT_ID=:t group by STATUS",t=s['transport']['transport_task_id'])==[('DEPARTED',2)]
 s['phase']='TRANSIT_BOUGHT';s['final_stock']=stock();save()

def finish():
 f=s['fixture'];w=f['warehouse_id'];transport=s['transport'];driver=s['tare_driver'];actor=driver['username']
 for name in ['after','transit']:
  wave=s['wave_'+name]
  preview=expect(200,http('GET',f'/api/picking/waves/{wave}/execution'));assert preview['ready'],preview
  step('finish.'+name,f'/api/picking/waves/{wave}/finish-execution',dict(operation_id=tag()+'.finish.'+name))
 step('tare.return.offer','/api/inventory/tare/offer',dict(operation_id=tag()+'.tare.return.offer',task_id=transport['transport_task_id'],owner_ware_id=w,pallet_type_id=1,condition='GOOD',from_kind='VEHICLE',from_id=str(s['vehicle']),to_kind='WAREHOUSE',to_id=str(w),quantity='1',scan_vehicle=transport['vehicle_number']),actor=actor,password=driver['password'])
 step('tare.return.accept','/api/inventory/tare/accept',dict(operation_id=tag()+'.tare.return.accept',offer_operation_id=tag()+'.tare.return.offer',accepted_quantity='1',scan_vehicle=transport['vehicle_number']))
 if 'tare.close'not in s['requests']:
  balances=expect(200,http('GET',f'/api/inventory/tare/warehouses/{w}/balances'))
  rows=[r for r in balances if r['custodian_kind']=='WAREHOUSE'and r['custodian_id']==str(w)and r['pallet_type_id']==1 and r['condition_code']=='GOOD'];assert len(rows)==1 and rows[0]['quantity']=='1',balances
  step('tare.close','/api/inventory/tare/count',dict(operation_id=tag()+'.tare.close',owner_ware_id=w,pallet_type_id=1,condition='GOOD',observed_quantity='0',expected_version=rows[0]['balance_version'],reason='Close synthetic QA tare after recorded native return',decision_reference='TEST_NOT_PHYSICAL_TARE_SURVEY'))
 cs=s['case_state'];resource=cs['resource']['id'];session=cs['session']['id'];picker=cs['actor']
 step('session.logout',f'/api/resources/sessions/{session}/logout',dict(reason='End original 25 BOX acceptance'))
 step('qualification.off',f'/api/resources/{resource}/qualifications',dict(task_type='CASE_PICK',active=False),method='PUT')
 step('picker.owner.off',base()+'/stock/owner-grants',dict(operation_id=tag()+'.picker.owner.off',expected_version=1,username=picker,owner_id='SNS',can_view=False,can_operate=False,reason='Close original 25 BOX acceptance'),method='PUT')
 step('driver.binding.off',f"/api/transport/driver-bindings/{transport['driver_id']}",dict(user_id=actor,active=False,expected_version=1),method='PUT')
 with oracle_connection()as c:
  q=c.cursor()
  for user in [f['actor'],picker]:
   q.execute("update RUSERS set DELETED=1 where ID=:a and USER_GROUP='TC03QA'and WARE_ID=:w",a=user,w=w);assert q.rowcount==1
   q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where USERNAME=:a and REVOKED_AT is null',a=user)
  q.execute('update RUSERS set DELETED=1 where ID=:a and USER_GROUP=:a and WARE_ID=:w',a=actor,w=w);assert q.rowcount==1
  q.execute('delete from RIGHTS where USER_GROUP=:a',a=actor);c.commit()
 assert stock()==(0,0)
 assert db("select STATUS,count(*)from RRL_PICK_WAVE where PICK_WAVE_ID in(:a,:b)group by STATUS",a=s['wave_after'],b=s['wave_transit'])==[('DONE',2)]
 assert db("select STATUS,count(*),sum(FACT_QTY)from RRL_CUSTOMER_ORDER_FULFILLMENT where CUSTOMER_ORDER_ID in(:a,:b)group by STATUS",a=s['native_after']['order'],b=s['native_transit']['order'])==[('SHIPPED',2,500)]
 assert db("select count(*)from USER_OBJECTS where STATUS='INVALID'")==[(0,)]
 s['slow_sql']=db('select LOG_ID,ELAPSED_MS,API_PATH,SQL_TEXT from RRL_SQL_SLOW_LOG where LOG_ID>:n order by ELAPSED_MS desc fetch first 25 rows only',n=f['slow_marker'])
 s['phase']='CLOSED';s['status']='PASS';s['providers']='LOCAL_SYNTHETIC_SAP_SKM_AND_MANUAL_MEASUREMENTS';save()

def main():
 os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=re.search(r'PASS=(\S+?)[`,)\s]',(ROOT/'AGENTS.md').read_text(encoding='utf-8'))[1]
 assert s.get('phase')!='CLOSED','Never reopen closed acceptance'
 try:globals()[sys.argv[1]]();print(json.dumps(dict(phase=s['phase'],warehouse=s.get('fixture',{}).get('warehouse_id'))))
 finally:s.setdefault('http',[]).extend(CALLS);save()
if __name__=='__main__':main()
