exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.transport_composition import build_transport_loading
from app.delivery_composition import build_delivery_receipt
from app.modules.delivery.infrastructure.order_delivery import OrderDelivery
from app.oracle_gateway import OracleGateway
p=Path('tmp/context671.json');saved=json.loads(p.read_text(encoding='utf-8'));tag=saved['first']['tag'];loading=build_transport_loading();receiver=build_delivery_receipt()
def save():p.write_text(json.dumps(saved,indent=2),encoding='utf-8')
if 'group_second_depart'not in saved:saved['group_second_depart']=loading.depart('GROUP712.DEPART:'+tag,saved['group_plan']['target_trip_id'],'admin');save()
address=saved['group_onward']['members'][0]['final_address']
if 'group_store_receipt'not in saved:
 preview=receiver.preview(saved['group_second_load_operation_id'],address,'admin');saved['group_store_preview']=preview;save()
 assert preview['marked_unit_control']['physical_unit_count']==6
 meta=dict(scan_place=preview['root_scan_identifier'],expected_composition_signature=preview['composition_signature'],before_cameras=True,observations=[],case_note='',scale_capture_key='',photo_ids=[],weight_act_confirmed=False,scans=[dict(code,disposition='ACCEPTED')for ctx in(saved['first'],saved['second'])for unit in ctx['units']for code in unit['codes']])
 op='GROUP712.STORE:'+tag
 saved.update(group_store_receipt=receiver.confirm(op,saved['group_second_load_operation_id'],address,meta,'admin'),group_store_operation_id=op,group_store_metadata=meta);save()
assert receiver.confirm(saved['group_store_operation_id'],saved['group_second_load_operation_id'],address,saved['group_store_metadata'],'admin')==saved['group_store_receipt']
for ctx in(saved['first'],saved['second']):
 snapshot=OrderDelivery(OracleGateway()).get(ctx['order']);saved['group_order_'+ctx['article']]=snapshot;save()
 print(json.dumps(dict(order=ctx['order'],quantities=snapshot['quantities']),ensure_ascii=True))
print('GROUP712 actualgroup depart/STORE6oldunits9codes/replay; inspect originalorder projection')
