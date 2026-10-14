from pathlib import Path
import json
out={};f=Path("db/migrations/2026-10-11_ni042_warehouse_scale")
out[str(f/"004_ledger.sql")]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-187-warehouse-scale-archive'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Addressed warehouse scale immutable archive, dedicated current warehouse sender, existing CASE/version source, shared stability reader',sysdate,user,
'db/migrations/2026-10-11_ni042_warehouse_scale/apply.sql','db/migrations/2026-10-11_ni042_warehouse_scale/rollback.sql','APPLIED',
'Own CASE1060 actual API TEST device stable gross10.1/raw SHA/current warehouse/scans/version/exact replay/conflict/unstable/admin-sender403/read permission/append-only/no stock; current independent source scope; quality544/0/76/24/bothTS PASS; once-only stock consumption next');
commit;
"""
p=f/"apply.sql";out[str(p)]=p.read_text(encoding="utf-8")+"@@004_ledger.sql\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"));m["components"].append("../2026-10-11_ni042_warehouse_scale/002_archive.sql");m["packages"].append("RRL_WH_SCALE_API");m["additional_scripts"].extend(["../2026-10-11_ni042_warehouse_scale/001_schema.sql","../2026-10-11_ni042_warehouse_scale/003_guards.sql"]);out[str(p)]=json.dumps(m,indent=2)+"\n"
out["wiki/database/retailcase_ni042_warehouse_scale_20261011.md"]="""# NI04.2: складской архив весового поста
187 APPLIED. [[retailcase_ni042_warehouse_scale_design_20261011]], [[retailcase_ni042_scale_packet_20261011]].
Additive RRL_WH_SCALE_DEVICE/CAPTURE metadata; no second stock balance. Device tied WARE/post cell/dedicated nonGLOBAL sender current RUSERS warehouse, version/active(default0)/TEST or HARDWARE/GROSS or NET/capacity/resolution/calibration. Device writes only CONFIG X/warehouse_settings_edit/current actor+old/new warehouse; deactivation rather than deletion.
Native RRL_WH_SCALE_API archives canonical raw/SHA/source task+line/content version/source-cell/carrier/product/current weighted SKU. Serialized box requires GROSS+original GS1 label; loose weight requires NET/product barcode and no applicable marks. Shared186 stable samples/freshUTC/zero/no preset/version/valid calibration. Device row serializes same capture identity; body conflict rejected. Replay retains original even if task changes, but current device sender warehouse and original WARE/post remain required.
Capture has no P/H/effect/outbox stock. Append-only context guard bound to package/TX/capture key. Reader/current CASE permission READ ONLY, bounded50 history; raw device packet namespace audit bound32000/nonreplayable.
API /api/inventory/warehouse-scales devicesPUT warehouse_settings_edit, capturePOST dedicated warehouse_scale_ingest, readGET case_pick_execute/current task warehouse. TEST explicitly reported; no hardware calibration/driver acceptance inferred.
scripts/ni042_warehouse_scale_archive_case.py: own QW187B1C3F64096/wave420 CASE1060/deviceWH.SCALE187:b1c3f64096/current senderQS187b1c3f64096. Actual stable10.1GROSS archived key25CA7B09B84A207DDC2CF755164271926F2E8670D1A071EB9FB9EC6BADAFB0EB, original/test/source/version/replay; changed body409/unstable409/admin pretending sender403/sender reading without CASE right403/direct-delete20863. P/H before/after archive unchanged. Subsequent old weighted CASE/replay/native cleanup passed, sender retired; history retained.
During native scope hardening, PowerShell quote escaping emitted backslash and unsupported SQL UPDATING predicate. Corrected exact SQL source and scalar old-ware variable; USER_ERRORS empty before API exposure/cases. Initial schema apply12 statements0errors; config/archive guarded as above. Quality PASS544 files/0 cycles/76 existing debt/24 tests/bothTS.
SQL capture d65x22b77pknn32.277ms/5 and initialinsert6mkpdqnrvnbx730.338ms/1; history0pwdgfdczu0rf13.486ms/1. Decision: retain device/capture PK and task/line/time index/max50, no extra index from cold sample; inventory owner bounded batching/plan check before industrial scale. No load certificate.
Next: same root CASE movement consumes capture once under planned unique/row locks, exact saved operation replay after expiry. Order15%/last-box exception distinct from device stability; no marked splitting allowed here.
"""
for path,line in [
 ("wiki/index.md","- [Складской архив весового поста](database/retailcase_ni042_warehouse_scale_20261011.md):187 addressed device/current dedicated sender/CASE version/stable10.1/immutable replay/no P-H; native consumption next."),
 ("wiki/log.md","2026-10-11:187 APPLIED warehouse scale archive API/current warehouse/config guards/shared186 sample rules. Own TEST stable10.1/source/replay/refusals/no P-H passed, quality544/0/76/24/bothTS. Capture32.277ms/5 cold bounded PK/history retained. Once-only stock use next."),
 ("wiki/requirements/retailcase_delivery_v55/execution/active/ni04_2.md","11.10.2026:187 addressed warehouse scale/dedicated current sender/immutable current CASE source archive API passed; TEST clearly separate, no stock on capture. Same-root consumption/tolerance/lastbox next.")]:
 p=Path(path);out[str(p)]=p.read_text(encoding="utf-8")+"\n"+line+"\n"
roots=[p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md")]
if roots:out[str(roots[0]/"NI04.2"/"187_warehouse_scale_archive.md")]="""# Qwen:187
Run scripts/ni042_warehouse_scale_archive_case.py. Confirm warehouse/post/current CASE/source scans/content version/dedicated sender/stable gross10.1/TEST reported/raw+SHA/exact replay/409conflict/unstable/admin sender403/reader rights/direct delete denied. Archive alone leavesP/H unchanged; native stock cleanup. Configure foreign warehouse/old device warehouse reassignment refused to nonGLOBAL; replay original WARE/post scope required. NET loose must be unmarked weighted SKU; serialized box onlyGROSS. Packet32000 limit/nonreplayable audit. Root consuming capture/real hardware/tolerance are not accepted by187.
"""
print(json.dumps(out,ensure_ascii=True))
