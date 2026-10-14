from pathlib import Path
import json
out={};page="wiki/database/retailcase_task_sync_readonly_20261010.md"
out[page]="""# Повтор синхронизации читает проведение,147

WarehouseTaskDomainSyncService now ACTIVE-only native committed proof reader. Removed PREPARED escape and exclusively-used old domain mutation/replenishment/MES retry executor; obsolete task_stock_move.py and task_reservation.py plus call-free inventory public wrappers removed. Original sync list/detail/retry/dispatch interfaces retained, no history deletion. Native root atomically owns stock/reserve/domain/SYNCED.

Inactive release503; ACTIVE without matching APPLIED operation/task quantity/pallet/source-target and SYNCED fact409 TASK_POSTING_REQUIRED. Existing HU unpack/relocation/completion proof variants retained. Retry cannot create legacy event/reservation/MES/wave effect or fake repair. Compatibility trigger configuration unchanged/defaultoff. Business document status PREPARED elsewhere is not release bypass.

Seven bounded cases PASS: task completion inactive3, sync inactive3, active missing proof refuses without writes/transaction. Actual ni032_sync_readonly_existing_case.py original120 task829 retry twice same HTTP proof, complete event1 qty3, all stock/sync attempts/timestamps unchanged. No new fixture.

Proof SQL mean21.036ms/2, other12.758ms/1. Decision keep original task/operation keyed lookup/exists and current proof variants, no history scan expansion or new index. Not load benchmark. Independent Qwen acceptance remains open.
"""
out["wiki/index.updated.tmp"]="- [Синхронизация задания читает проводку](database/retailcase_task_sync_readonly_20261010.md):147 PREPARED effect executor removed/ACTIVE proof only/original829 retry unchanged/7 boundary casesPASS.\n"+Path("wiki/index.md").read_text(encoding="utf-8-sig")
for p,line in [
("wiki/log.md","2026-10-10:147 removed PREPARED domain-sync stock/reservation/MES/wave executor and exclusively-used obsolete modules/public wrappers. ACTIVE native proof reader preserves HU variants; inactive503/missing proof409/no writes.7 bounded casesPASS; actual completed829 two retry replies exact/event1 qty3/all stock/sync attempts/timestamps unchanged. SQL21.036/12.758ms keyedproof kept; no new migration/history or independent acceptance."),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni08_1.md","Ticket147 eliminates old sync effect executor; retry reads native committed proof only. See database/retailcase_task_sync_readonly_20261010.md.")
]:out[p]=Path(p).read_text(encoding="utf-8-sig")+"\n"+line+"\n"
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");m=json.loads(p.read_text(encoding="utf-8-sig"))
for row in m["sprints"]:
 if row.get("id")=="NI08.1":row.setdefault("implementedSlices",[]).append("147 single-writer native proof-only warehouse task sync retry")
out[str(p)]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
out["задания на проведения тестов/NI08.1/147_повтор_синхронизации_без_эффекта.md"]="""# Qwen —147
Existing ordinary task829 and existing HU completion/unpack/same-cell relocation proof variants. Retry must return original native SYNCED proof without new P/H/event/reservation/MES/wave/syncattempt timestamp. PREPARED/CUTOVER/missing release503; active missing real native posting409. No fake history repair or compatibility toggle. Native source/request/result task/quantity/pallet/cell matches required. Author7 boundary cases and actual829 twicePASS; independently exercise HU variants if owned original fixture exists.
"""
print(json.dumps(out,ensure_ascii=True))
