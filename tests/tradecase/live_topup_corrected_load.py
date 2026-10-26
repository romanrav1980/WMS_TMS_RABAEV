"""Repeat the owned 660 BOX physical cycle after the documented synthetic vehicle correction."""
import json,os,re,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import live_topup_physical_660 as qa
FILE=qa.OUT/'topup-physical-660-corrected.json'
r=json.loads(FILE.read_text(encoding='utf-8'))if FILE.exists()else dict(phase='PLANNED',steps={})
def save():FILE.write_text(json.dumps(r,indent=2,default=str),encoding='utf-8')
def step(key,path,body):
 if key not in r['steps']:r['steps'][key]=dict(path=path,body=body);save()
 v=r['steps'][key]
 if 'result'not in v:v['result']=qa.expect(200,qa.http('POST',v['path'],v['body']));save()
 return v['result']
def main():
 qa.s.update(json.loads(qa.STATE.read_text(encoding='utf-8')));s=qa.s
 assert s['fixture']['warehouse_id']==223214750 and s['phase']=='UNLOADED'
 assert r['phase']!='CLOSED','Never reopen a closed fixture'
 os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=re.search(r'PASS=(\S+?)[`,)\s]',Path('AGENTS.md').read_text(encoding='utf-8'))[1]
 prefix=qa.tag()+'.corrected'
 try:
  if r['phase']in('PLANNED','LOADING'):
   profile=qa.expect(200,qa.http('GET',f"/api/admin/transport/vehicles/{s['vehicle']}/profile"))
   assert profile['profile']['cargo_height_mm']==2600 and profile['state']=='READY'
   r['profile']=profile;r['phase']='LOADING';save()
   for key,ship in sorted(s['shipments'].items()):
    if 'qc.'+key not in r['steps']:
     quality=qa.expect(200,qa.http('GET','/api/outgoing-quality/'+ship['shipment_identifier']))
     n=next(k for k,p in s['pallets'].items()if p['pallet']==ship['pallet'])
     scans=[dict(system_code='CRPT',profile_code='TOBACCO',code=s['fixture']['gtin']+s['fixture']['tag'][:2]+n+str(i).zfill(3))for i in range(1,201)]
     step('qc.'+key,'/api/outgoing-quality/'+ship['shipment_identifier']+'/scan',dict(operation_id=prefix+'.qc.'+key,expected_composition_signature=quality['composition_signature'],error_count=0,scans=scans))
    if 'load.'+key not in r['steps']:
     p=qa.expect(200,qa.http('GET','/api/transport/loading/single-preview?shipment_identifier='+ship['shipment_identifier']))
     old=s['load_bodies'][key]
     body=dict(old,operation_id=prefix+'.load.'+key,expected_version=p['expected_version'],expected_composition_signature=p['composition_signature'],measurements=dict(old['measurements'],content_version=p['expected_version']))
    else:body=r['steps']['load.'+key]['body']
    result=step('load.'+key,'/api/transport/loading/confirm-single',body)
    if 'load_replay'not in r:
     assert qa.expect(200,qa.http('POST','/api/transport/loading/confirm-single',body))==result
     r['load_replay']=key;save()
   r['after_load']=qa.stock();assert tuple(r['after_load'][:2])==(0,0)
   r['facts']=qa.db("select count(*),sum(GROSS_WEIGHT_KG),sum(BOUNDING_VOLUME_M3) from RRL_TT_HU_LOAD_FACT where TT_ID=:t and STATUS='LOADED'",t=s['transport']['transport_task_id'])
   assert r['facts']==[(33,6600,79.2)],r['facts']
   r['load_posted']=qa.db('select -sum(BASE_QTY) from RRL_EVENTS where OPERATION_ID like :o',o=prefix+'.load.%')[0][0];assert r['load_posted']==6600
   r['phase']='LOADED';save()
  if r['phase']in('LOADED','UNLOADING'):
   r['phase']='UNLOADING';save()
   for key in sorted(s['shipments']):
    loaded=r['steps']['load.'+key]['body']
    body=dict(operation_id=prefix+'.unload.'+key,load_operation_id=loaded['operation_id'],expected_version=loaded['expected_version'],**{k:loaded[k]for k in ['scan_container','scan_cell','scan_vehicle','scan_dock']},reason='Return owned synthetic 660 BOX test load')
    u=step('unload.'+key,'/api/transport/loading/unload',body)
    if 'unload_replay'not in r:
     assert qa.expect(200,qa.http('POST','/api/transport/loading/unload',body))==u
     r['unload_replay']=key;save()
   r['after_unload']=qa.stock();assert tuple(r['after_unload'])==(6600,6600,33)
   r['unload_posted']=qa.db('select sum(BASE_QTY) from RRL_EVENTS where OPERATION_ID like :o',o=prefix+'.unload.%')[0][0];assert r['unload_posted']==6600
   r['phase']='UNLOADED';r['status']='PASS';save()
  print(json.dumps({k:r.get(k)for k in ['phase','status','after_load','after_unload','facts']}))
 finally:r.setdefault('http',[]).extend(qa.CALLS);save()
if __name__=='__main__':main()
