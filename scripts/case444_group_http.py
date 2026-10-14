from pathlib import Path
import json,httpx
ctx=json.loads(Path('tmp/context406.json').read_text(encoding='utf-8'))
base='http://127.0.0.1:8088/api/inventory/interwarehouse'
with httpx.Client(auth=('admin','admin123'),timeout=30)as client:
 r=client.get(base+'/group-plans/'+ctx['group_plan_operation_id']);assert r.status_code==200,r.text
 value=r.json();assert value['delivered']and value['accepted_members']==2 and value['loaded_members']==2 and value['onward']['members'],value
 r=client.get(base+'/trips/'+str(ctx['group_plan']['target_trip_id'])+'/incoming');assert r.status_code==200 and r.json()['incoming_ready'],r.text
 r=client.post(base+'/group-receive',json=dict(operation_id=ctx['group_receipt_operation_id'],plan_operation_id=ctx['group_plan_operation_id'],**ctx['group_receipt_metadata']));assert r.status_code==200 and r.json()==ctx['group_receipt'],r.text
 r=client.post(base+'/group-placement',json=dict(operation_id=ctx['group_put_plan']['operation_id'],receipt_operation_id=ctx['group_receipt_operation_id'],**{k:v for k,v in ctx['group_put_metadata'].items()if k not in('target_cell','group_receipt_operation_id')}))
 assert r.status_code==200 and r.json()==ctx['group_put_plan'],r.text
print('PASS444 restartedHTTP/groupdelivered2/readyincoming/currenttypedreceive+placement exactoldreplay afteractualdelivery')
