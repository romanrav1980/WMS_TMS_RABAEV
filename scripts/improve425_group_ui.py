from pathlib import Path
import json
out={}
p=Path('api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_group_read.py');t=p.read_text(encoding='utf-8')
needle='            state=q.fetchone()\n'
add='''            state=q.fetchone()
            q.execute("""select p.HU_CONTENT_VERSION,p.HU_CURRENT_CELL from RRL_PALLETS p
                join RRL_IW_GROUP_PLAN g on g.ROOT_UID=p.UID_PALLET
                join RRL_CELLS c on c.CELL=p.HU_CURRENT_CELL and c.WARE_ID=g.TARGET_WARE_ID
                where g.OPERATION_ID=:plan_id""",plan_id=plan)
            current=q.fetchone()
'''
assert needle in t;t=t.replace(needle,add,1)
t=t.replace('                        grouped_receipt_available=True,stock_changed=False)','                        current_content_version=current[0]if current else None,current_cell=current[1]if current else None,\n                        grouped_receipt_available=True,stock_changed=False)',1)
out[p.as_posix()]=t
p=Path('api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py');t=p.read_text(encoding='utf-8')
t=t.replace('{"code":exc.code,"message":str(exc),"outcome_confirmed":True})from exc','{"code":exc.code,"message":str(exc),"operation_id":body.operation_id,"outcome_confirmed":True})from exc')
out[p.as_posix()]=t
p=Path('wiki-raw/wms_admin_ui_reference/interwarehouse-groups.js');t=p.read_text(encoding='utf-8')
t=t.replace('e.confirmed=r.status<500&&d.detail?.outcome_confirmed===true&&d.detail?.operation_id===body?.operation_id;','e.confirmed=r.status===422||(r.status<500&&d.detail?.outcome_confirmed===true&&d.detail?.operation_id===body?.operation_id);')
t=t.replace(' taskLink(result.placement_task_id);restoreScans();',''' el("ggVersion").value=result.current_content_version??"";
 if(result.receive_cell)el("ggFrom").value=result.receive_cell;
 el("ggTo").placeholder=result.plan.outbound_dock;
 taskLink(result.placement_task_id);restoreScans();''',1)
t=t.replace(' detail=null;el("ggLots").replaceChildren();',' detail=null;el("ggProfile").replaceChildren();el("ggLots").replaceChildren();',1)
out[p.as_posix()]=t
print(json.dumps(out))
