from pathlib import Path
import json
out={};d='db/migrations/2026-10-12_ni061_group_placement'
p=Path('db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json');m=json.loads(p.read_text(encoding='utf-8'));value='../'+d.split('/')[-1]+'/apply.sql'
if value not in m['additional_scripts']:m['additional_scripts'].append(value)
out[p.as_posix()]=json.dumps(m,indent=2)+'\n'
page='wiki/database/retailcase_ni061_group_placement_20261012.md'
out[page]='''# Групповая приёмка размещается существующим заданием HU
417 APPLIED/VALID, owner remains RRL_STOCK_HU_TASK/RRL_STOCK_HU_CMD. New RRL_IW_GROUP_PUT only validates grouped receipt and records immutable links; it does not write quantity. Root single-writer ACTIVE/compatOFF preserved.

Actual419: context406 original received TOP/twoSKU3EA each/sixoldunits/ninecodes planned as existing MANUAL/PUTAWAY/WAREHOUSE_HU task1HU. Native group bridge validates exact received leaves, originalavailable unit keys, no hard reserves, warehouse/actor/current cell/stock versions and no other active placement. Native common HU target policy retained: non-system ordinary buffer, explicit warehouse height unit M/3m/100kg and current manual measurements7kg/1x1x1.5m. Missing measurements/height-unit and invalid system-target layout were correctly refused before task creation; fixture configuration was corrected.

Completion uses existing HU_TASK_COMPLETE, preserving one physical task and two commodity stockmove facts3EA each. Native perleaf PUTAWAY location mode is admitted only through compiled exact group receipt matrix. Receipt→plan→task→placement facts guarded by current transaction context/exact resolved domain/actual perlot commodity move rows. Full late rollback restored task PLANNED and receiving stock; actual completion/replay delivered3each to target buffer, no newkeys/codes, P20/H20 unchanged.

423–425 typed group placement API, bounded group worklist/detail and current contentversion; target comes from immutable interwarehouse plan. Current warehouse access precedes command and cached result. Dedicated raw interwarehouse-groups UI: source proof/plan, whole unload/receive, perSKU profiles and barcode fields, scanner draft, saved operation intent/retry, existing task link. No hardware/browser/independent acceptance claimed. Current API restart required to load latest Python.

Remaining: group custody and onward ST/load/store source lineage; departure promises must include groups before group flow is operationally closed. Partial/aggregate-only grouping and high-leaf batching remain open. Never rerun source404405 or initial receipt/P3 in receiving after placement. Context406 retains all completed stages and target bufferP3each.
'''
for filename,entry in [('wiki/index.md','- [Размещение многотоварного места](database/retailcase_ni061_group_placement_20261012.md):417–425 originaltask1HU/2commoditymoves3EA/old6keys9codes/nativeproof/rollback-replay/typedAPI/rawUI; custody/onward next.\n'),('wiki/log.md','\n- 12.10.2026 417–427: actualgroup existingHU task1HU/two commodity3EA/native groupreceipt→task→placement matrix/exactkeys/whole rollback/replay/P20H20. Core common target measurements/height policy retained; own target configuredM/3m/100kg. Added typedAPI/current-scoped group worklist/detail/rawUI/durable scan and operation intents. NativeVALID; group custody/onward/departure gate remain.\n'),('wiki/requirements/retailcase_delivery_v55/execution/active/ni06_1.md','\n417–425: groupreceiving placed using originalHU task1HU/commodity2x3EA/exactoriginalkeys/nativegroup linkage/late rollback/replay. TypedAPI/rawUI/durableintent/scandraft. Custody/onward/departure group promise and customer source lineage remain.\n')]:
 p=Path(filename);old=p.read_text(encoding='utf-8');out[filename]=entry+old if filename=='wiki/index.md'else old+entry
p=Path('wiki/requirements/retailcase_delivery_v55/implementation_plan.json');m=json.loads(p.read_text(encoding='utf-8'))
for x in m['increments']:
 if x['id']=='NI06.1':
  x.setdefault('implementedSlices',[]).append('417–425 existingwholeHU task1HU/commodity2x3EA/exact groupreceipt/key proof/rollback-replay/typedAPI/rawUI intents')
  x['remainingScope']=['group custody/onward and departure promise/customer source integration','partial/aggregate-only grouped receiving','aggregation invalidation/repacking lifecycle','independent acceptance/hardware/current real ERP and government ACK']
out[p.as_posix()]=json.dumps(m,ensure_ascii=False,indent=2)+'\n'
p=Path('wiki/runbooks/retailcase_active_work.md');t=p.read_text(encoding='utf-8').replace('Current native409/app411','Current native417/app425')
t=t.replace('Whole-HU placement/custody/onward next.','Whole-HU placement419 done/targetP3each; group custody/onward/departure gate next.')
out[p.as_posix()]=t
root=next(Path('.').glob('*/NI08.1/178_container_cell_index.md')).parent.parent
out[(root/'NI06.1/427_group_placement.md').as_posix()]='# Qwen417–425\nRetainedctx406 task1HU/DONE withtwo exact3EA commoditymove facts/nativegroupreceipt-plan-task-placement. Old6keys9codes/P20H20; fulltrialrollback restoredreceiving/taskPLANNED. Current targetM/3m/100kg/7kg manualdimensions1x1x1.5; missingheightunit/measurement refusals notbypassed. Verify typedAPI/currentWARE/rawUI savedop/draft/profilematrix independently afterserverrestart. Do notrerun factory/source412 receiving assertions after419 placement. Groupcustody/onward remains.\n'
print(json.dumps(out))
