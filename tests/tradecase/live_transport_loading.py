"""Real standalone LOAD and a blocked departure until transport business proof exists."""
from pathlib import Path
import json,os,sys
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http,expect,CALLS
P=Path(os.environ.get('TRADECASE_TRANSPORT_FIXTURE',str(ROOT/'runtime/test-evidence/tradecase/2026-10-19/T07/fixture-1155.json')));s=json.loads(P.read_text())
def save():P.write_text(json.dumps(s,indent=2,default=str),encoding='utf-8')
try:
 with oracle_connection()as c:
  q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=q.fetchone()[0]
 if 'profile_configured'not in s:
  profile=expect(200,http('GET',f"/api/admin/transport/vehicles/{s['vehicle_id']}/profile"))
  body=dict(operation_id='T7.vehicle.profile.'+str(s['case_id']),vehicle_id=s['vehicle_id'],expected_source_hash=profile['base_hash'],vehicle_size_class='QA_VAN',cargo_length_mm=3000,cargo_width_mm=2400,cargo_height_mm=2400,outer_height_mm=3000,outer_length_mm=6000,expected_version=profile['version'],floor_variants=[dict(code='QA_TWO_EURO',limits=[dict(pallet_type_id=1,max_places=2)])],reason='Isolated synthetic test fleet profile, no road vehicle claim',evidence_reference='TEST_FIXTURE_NOT_HARDWARE:T7.1155')
  s['profile_configured']=expect(200,http('POST','/api/admin/transport/vehicle-profiles',body));save()
 if 'load_body'not in s:
  preview=expect(200,http('GET','/api/transport/loading/single-preview?shipment_identifier='+s['st_pallet']));s['load_body']=dict(operation_id='T7.LOAD.'+str(s['case_id']),identifier=s['st_pallet'],expected_version=preview['expected_version'],expected_composition_signature=preview['composition_signature'],scan_container=s.get('carrier','CP595000000001155'),scan_cell=preview['snapshot']['cell'],transport_task_id=s['transport_task_id'],scan_vehicle=s['vehicle_number'],scan_dock=s['dock'],measurements=dict(origin='MANUAL_CONFIRMED',content_version=preview['expected_version'],gross_weight_kg='32',width_m='1.2',depth_m='0.8',height_m='1.5'));save()
 if 'loaded'not in s:s['loaded']=expect(200,http('POST','/api/transport/loading/confirm-single',s['load_body']));save()
 assert expect(200,http('POST','/api/transport/loading/confirm-single',s['load_body']))==s['loaded']
 s['departure_without_document']=expect(409,http('POST',f"/api/transport/loading/{s['transport_task_id']}/depart",dict(operation_id='T7.DEPART.MISSING.'+str(s['case_id']))));save()
 with oracle_connection()as c:
  q=c.cursor();q.execute('select STATUS from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:o',o=s['load_body']['operation_id']);assert q.fetchone()[0]=='LOADED'
  q.execute('select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w',w=s['warehouse_id']);s['after_load_stock']=list(q.fetchone());assert s['after_load_stock']==[s.get('expected_remaining',150),0]
 s['load_stage']='PASS';print(json.dumps(dict(stage=s['load_stage'],trip=s['transport_task_id'],warehouse_remaining=s['after_load_stock'],departure_without_document=s['departure_without_document'])))
finally:s['http']+=CALLS;save()
