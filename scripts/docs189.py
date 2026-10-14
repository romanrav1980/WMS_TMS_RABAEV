from pathlib import Path
import json,hashlib
out={};f=Path("db/migrations/2026-10-11_ni042_scale_net")
out[str(f/"checkpoint.json")]=json.dumps({"migration_id":"2026-10-11-189-case-scale-net","before_sha256":hashlib.sha256((f/"000_before_admission.sql").read_bytes()).hexdigest(),"recovery":"Fresh prior188 native admission only; existing shared CASE root; no data rewrite/no DB copy"},indent=2)
out[str(f/"002_ledger.sql")]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-189-case-scale-net'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Current unmarked KG NET scale route and original capture source validation',sysdate,user,
'db/migrations/2026-10-11_ni042_scale_net/apply.sql','db/migrations/2026-10-11_ni042_scale_net/rollback.sql','APPLIED',
'CASE1063 NET9.6/P20H10/PARTIAL remaining.4; CASE1064 outer rollback all/root concurrent two IDs one winner1064:B/loser409/saved replay/native cleanup. Quality544/0/76/24/bothTS PASS; device hardware/order tolerance separate.');
commit;
"""
out[str(f/"apply.sql")]=(f/"apply.sql").read_text(encoding="utf-8")+"@@002_ledger.sql\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"));m["components"].append("../2026-10-11_ni042_scale_net/001_admission.sql")
out[str(p)]=json.dumps(m,indent=2)+"\n"
out["wiki/database/retailcase_ni042_scale_net_20261011.md"]="""# NI04.2: точный NET-отбор на весах
189 APPLIED; transactional case190. [[retailcase_ni042_scale_use_20261011]], [[retailcase_ni042_warehouse_scale_20261011]].
POST existing CASE /tasks/{task}/lines/{line}/weigh-line accepts only operation/capture/source-cell/carrier. READ ONLY current CASE scope derives cumulative fact previous+archived exact NET; saved canonical replay precedes current read. Existing CASE_PICK_CONFIRM performs stock/H/physical journal/domain/outbox/use atomically. Extra quantity is forbidden.
Native current SKU weighted TYPE_W2/3/5/6/7 and exact KG->KG1:1 required for both scale modes; current serialized flag/card/CRPT/profiles prevent loose marked opening. Original archived product must equal command product. Current source/device/freshness/rank70 captured-use fence remains188.
Raw TSD current policy distinguishes serialized box from unmarked loose KG; archive mode/basis/time choices exclude used captures. NET selection disables manual cumulative fact and stores original route/body durably; old intents retain fallback confirm. Read-only original archive retains historical stock_posted:false, separate use_by_capture reflects actual operation use (no rewriting original packet).
Own189 QW189E9B0458977/WARE35315013/revision258/CASE1063/capture3A6F7D403DD023DC6A08D1562285D6C1016B2995B1C55799BB85D76BDEF5E150: existing stock20KG/pick-face, demand10, NET9.6 -> PARTIAL remaining.4, P20/H10 across source+carrier, exact replay/no second movement/changed409/native cleanup/original13520/20. This preserves remaining demand; no order tolerance closure claim.
First author69c19fa69a stock10/demand10 correctly chosen FULL_PICK by old planner; native cleanup. Second d34e9a6b4e/wave423 rejected missing old BOX capacity conversion for replenishment; native WAVE_CANCEL/release/count cleanup via cleanup189_failed_launch. Final directly available pick-face intentionally isolates NET scenario; no assertion of missing replenishment capacity setup.
Own190 QW190E119626D90/WARE34752098/revision259/CASE1064: prepare+execute proved USE/currentCASE9.6 in transaction; outer rollback removed USE/operation/events/CASE quantity and P/H restored20/10. Two concurrent distinct operation IDs same capture exactly one200/one409; winner CASE.WEIGHT182:1064:B. Saved retry identical journal; native cleanup. Root owns mandatory outbox same TX, but author190 does not independently assert outbox-row rollback. Current native USER_ERRORS empty.
Quality PASS544files/0cycles/76debt/24tests/bothTS. RawJS syntax PASS. Pending real hardware protocol/commissioning, order±15%/lastbox8or12 without unauthorized marked split, actual browser acceptance.
Slow SQL USE count86x0jmcyxt9c4 .506ms/7; INSERT9b4nq6cd89zg8 5.292ms/4 and PKread51mtxj734zrff2.638ms/4 retained indexed keys. New history joinbp28t2murqvqn209.991ms firstparse/dynamic sampling177.119ms: explicit decision bound51 captures before USE PK join; inventory owns statistics/plan check at pilot rather than extra speculative index. Cold samples are not throughput evidence.
"""
for path,line in [
("wiki/index.md","- [Точный NET-отбор на весах](database/retailcase_ni042_scale_net_20261011.md):189 current unmarkedKG/native root/TSD,190 rollback+concurrent one winner; remaining demand preserved."),
("wiki/log.md","2026-10-11:189 APPLIED exact NET CASE route/native current KG/marking/source;190 rollback and two-ID concurrency passed CASE1064. Quality544/0/76/24/bothTS. History209.991ms cold→bound51 before PK join; inventory pilot stats/plan owner. Order tolerance remains separate."),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni04_2.md","11.10.2026:189 exact unmarked NET9.6 route/TSD/native proof installed;190 outer rollback and concurrent capture one winner passed. Demand10 remains PARTIAL9.6/.4; ±15% and lastbox policy, real hardware/browser acceptance remain open.")]:
 p=Path(path);out[str(p)]=p.read_text(encoding="utf-8")+"\n"+line+"\n"
roots=[p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md")]
if roots:out[str(roots[0]/"NI04.2"/"189_190_scale_net_tx.md")]="""# Qwen:189/190
Run ni042_warehouse_scale_net_case.py and ni042_warehouse_scale_tx_case.py dedicated dev. Verify exact9.6KG/current unmarked policy/one capture use/remaining.4, native outer rollback including outbox, simultaneous different operation IDs one winner, replay after timeout using original payload, current CRPT/profile/warehouse/device/version refusal. Browser raw case-pick-tsd select NET TEST capture -> manual fact disabled -> saved weigh-line route, refresh retries original command. Source20/H10 conserved before native cleanup. Original13520/20 unchanged. Inspect bounded51 history before PK USE join and plan/statistics; no real hardware/legal ACK claim.
"""
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/warehouse_scales.py");t=p.read_text(encoding="utf-8")
a="""select c.RESULT_JSON,c.CAPTURE_KEY,u.STOCK_OPERATION_ID from RRL_WH_SCALE_CAPTURE c
                    left join RRL_WH_SCALE_USE u on u.CAPTURE_KEY=c.CAPTURE_KEY
                    where c.CASE_PICK_TASK_ID=:p_task and c.CASE_PICK_LINE_ID=:p_line
                    order by c.RECEIVED_AT desc,c.CAPTURE_KEY desc fetch first 51 rows only"""
b="""select c.RESULT_JSON,c.CAPTURE_KEY,u.STOCK_OPERATION_ID from(
                    select RESULT_JSON,CAPTURE_KEY,RECEIVED_AT from RRL_WH_SCALE_CAPTURE
                    where CASE_PICK_TASK_ID=:p_task and CASE_PICK_LINE_ID=:p_line
                    order by RECEIVED_AT desc,CAPTURE_KEY desc fetch first 51 rows only)c
                    left join RRL_WH_SCALE_USE u on u.CAPTURE_KEY=c.CAPTURE_KEY
                    order by c.RECEIVED_AT desc,c.CAPTURE_KEY desc"""
assert a in t;out[str(p)]=t.replace(a,b)
print(json.dumps(out,ensure_ascii=True))
