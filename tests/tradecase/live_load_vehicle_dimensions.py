"""Reproduce and verify the configured vehicle dimension guard on the owned T08 fixture only."""
import json,os,re,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import live_topup_physical_660 as qa
qa.s.update(json.loads(qa.STATE.read_text(encoding='utf-8')))
s=qa.s
FILE=qa.OUT/'vehicle-dimensions.json'
r=json.loads(FILE.read_text(encoding='utf-8'))if FILE.exists()else dict(results={})
def save():FILE.write_text(json.dumps(r,indent=2,default=str),encoding='utf-8')
def call(key,method,path,body=None,status=200):
 if key not in r['results']:r['results'][key]=dict(method=method,path=path,body=body,status=status);save()
 v=r['results'][key]
 if 'result'not in v:v['result']=qa.expect(v['status'],qa.http(v['method'],v['path'],v['body']));save()
 return v['result']
def body(key):
 ship=s['shipments'][key]
 if 'qc.'+key not in r['results']:
  quality=qa.expect(200,qa.http('GET','/api/outgoing-quality/'+ship['shipment_identifier']))
  n=next(k for k,p in s['pallets'].items()if p['pallet']==ship['pallet'])
  scans=[dict(system_code='CRPT',profile_code='TOBACCO',code=s['fixture']['gtin']+s['fixture']['tag'][:2]+n+str(i).zfill(3))for i in range(1,201)]
  call('qc.'+key,'POST','/api/outgoing-quality/'+ship['shipment_identifier']+'/scan',dict(operation_id=qa.tag()+'.geometry.qc.'+key,expected_composition_signature=quality['composition_signature'],error_count=0,scans=scans))
 p=qa.expect(200,qa.http('GET','/api/transport/loading/single-preview?shipment_identifier='+ship['shipment_identifier']))
 original=s['load_bodies'][key]
 return dict(original,expected_version=p['expected_version'],expected_composition_signature=p['composition_signature'],measurements=dict(original['measurements'],content_version=p['expected_version']))
def main():
 assert s['phase']=='UNLOADED' and s['fixture']['warehouse_id']==223214750
 os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=re.search(r'PASS=(\S+?)[`,)\s]',Path('AGENTS.md').read_text(encoding='utf-8'))[1]
 first,second=sorted(s['shipments'])[:2]
 url='/api/transport/loading/confirm-single'
 try:
  if 'before'not in r:r['before']=qa.stock();save()
  if 'too_high'not in r['results']:
   bad=body(first);bad['operation_id']=qa.tag()+'.geometry.toohigh'
   profile=qa.expect(200,qa.http('GET',f"/api/admin/transport/vehicles/{s['vehicle']}/profile"))
   assert profile['profile']['cargo_height_mm']==2000,profile
   call('too_high','POST',url,bad,409)
   assert 'LOAD_PLACE_EXCEEDS_VEHICLE_DIMENSIONS'in json.dumps(r['results']['too_high']['result'])
   assert tuple(qa.stock())==(6600,6600,33)
  if 'profile_corrected'not in r['results']:
   p=qa.expect(200,qa.http('GET',f"/api/admin/transport/vehicles/{s['vehicle']}/profile"))
   b=dict(s['steps']['profile']['body'],operation_id=qa.tag()+'.geometry.profile2600',expected_version=p['version'],expected_source_hash=p['base_hash'],cargo_height_mm=2600,outer_height_mm=3500,reason='Correct owned synthetic fixture; 2.5m pallet cannot fit original 2m body',evidence_reference='QA_CORRECTION_NOT_ORIGINAL_66M3_PHYSICAL_ACCEPTANCE')
   call('profile_corrected','POST','/api/admin/transport/vehicle-profiles',b)
  if 'fits'not in r['results']:
   fits=body(first);fits['operation_id']=qa.tag()+'.geometry.fits'
   call('fits','POST',url,fits)
  fits=r['results']['fits']['body'];result=r['results']['fits']['result']
  assert qa.expect(200,qa.http('POST',url,fits))==result
  call('changed','POST',url,dict(fits,measurements=dict(fits['measurements'],height_m='1.5')),409)
  if 'volume'not in r['results']:
   full=body(second);full['operation_id']=qa.tag()+'.geometry.volume'
   full['measurements']=dict(full['measurements'],width_m='2.5',depth_m='13.2',height_m='2.6')
   call('volume','POST',url,full,409)
   assert 'LOAD_BOUNDING_VOLUME_EXCEEDS_VEHICLE'in json.dumps(r['results']['volume']['result'])
   assert tuple(qa.stock())==(6400,6400,32)
  unload=dict(operation_id=qa.tag()+'.geometry.unload',load_operation_id=fits['operation_id'],expected_version=fits['expected_version'],**{k:fits[k]for k in ['scan_container','scan_cell','scan_vehicle','scan_dock']},reason='Return synthetic geometry acceptance pallet')
  u=call('unload','POST','/api/transport/loading/unload',unload)
  assert qa.expect(200,qa.http('POST','/api/transport/loading/unload',unload))==u
  r['after']=qa.stock();assert tuple(r['after'])==(6600,6600,33)
  r['status']='PASS';save();print(json.dumps(dict(status=r['status'],after=r['after'])))
 finally:r.setdefault('http',[]).extend(qa.CALLS);save()
if __name__=='__main__':main()
