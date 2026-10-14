from pathlib import Path
import json
out={};f=Path("db/migrations/2026-10-11_ni042_case_sscc")
out[str(f/"007_context.sql")]="create context RRL_CASE_SSCC_CTX using RRL_CASE_SSCC_API;\n"
out[str(f/"008_ledger.sql")]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-203-case-logistic-sscc'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Original CASE SSCC issuance and attached-label admission',sysdate,user,
'db/migrations/2026-10-11_ni042_case_sscc/apply.sql','db/migrations/2026-10-11_ni042_case_sscc/rollback.sql','APPLIED',
'Own QPB20356E93BB1 type8 CASE6: 18digit SSCC 090000000000000025 synthetic test prefix; native metadata rollback/original CP history/replay/conflict/print GS1 SVG ZPL/confirm/direct history guard; existing CASE6 QC/source14/native cleanup. Small final-required containers label before pick. No government ACK or GS1 ownership claim.');
commit;
"""
out[str(f/"apply.sql")]=(f/"apply.sql").read_text(encoding="utf-8")+"@@008_ledger.sql\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");original=p.read_text(encoding="utf-8");m=json.loads(original)
out[str(f/"000_before_manifest.json")]=original
matches=[x for x in m["components"]if "create or replace package RRL_STOCK_CASE_PICK_CMD "in(p.parent/x).read_text(encoding="utf-8")];assert len(matches)==1,matches
at=m["components"].index(matches[0]);m["components"][at:at+1]=["../2026-10-11_ni042_case_sscc/002_allocator.sql","../2026-10-11_ni042_case_sscc/006_recompile.sql","../2026-10-11_ni042_case_sscc/005_case.sql"]
m["packages"].extend(["RRL_SSCC_ALLOCATOR","RRL_CASE_SSCC_API"]);m["startup_scripts"].append("../2026-10-11_ni042_case_sscc/001_schema.sql")
m["additional_scripts"].extend(["../2026-10-11_ni042_case_sscc/007_context.sql","../2026-10-11_ni042_case_sscc/004_guard.sql"])
m["required_columns"]["RRL_CASE_SSCC_LABEL"]=["OPERATION_ID","CASE_PICK_TASK_ID","SSCC","ORIGINAL_CARRIER","WARE_ID","REQUESTED_VERSION","REQUEST_JSON","RESULT_JSON","CONFIRMED_AT","CONFIRMED_BY"]
out[str(p)]=json.dumps(m,indent=2)+"\n"
out["wiki/database/nicora_ni042_case_sscc_20261011.md"]="""# NI04.2: стандартный SSCC пустой коробки
203 APPLIED; [[nicora_ni042_case_sscc_design_20261011]]. Existing incoming and CASE labels share RRL_RECEIPT_SSCC_SQ and the native allocator/current actor WARE/receipt or CASE permission. Assigned GS1 prefix6..12digits/extension/range/checksum/collisions checked; old arbitrary internal carrier identifiers remain supported. No stock writer added.
CASE empty NEW/ASSIGNED/current scanned carrier/version/not packed/no legacy shipment only; business CONFIG X+ROWmetadata anchor serializes against native posting. Issue archives original CP/actor/source/request/result, changes current carrier/version in same TX; replay preserves result and current access required. Attached SSCC confirmation is explicit scan, separate from issuing/printing. New CONTAINER FINAL_WEIGHT_REQUIRED cannot be picked without confirmed label; checks before compile and under actual locks. Original history immutable; issued carrier cannot be replaced by raw writes.
Own QPB20356E93BB1/type8/CASE6: native outer rollback restores original CP/no archive; actual 090000000000000025 checksum, exact repeat/body409, GS1 SVG and ZPL, wrong scan409, unlabelled/unconfirmed admission20887, label DELETE20863; correct AI00 confirm/repeat. Existing direct SAP20/source14/CASE6/current gross.400 tare.100 net.300 QC/replay/native return/count cleanup; original135 P20H20 preserved. Prefix900000 is isolated synthetic software data, no registration or government aggregation ACK claim.
TSD separate case-sscc-label.js: issue/reprint/attached scan, durable actor/API-keyed original intent, identical retry after unknown result; current CASE refreshed after identity/version change. Existing UI raw carrier entry keeps legacy identifiers. New typed API ports/public wiring architecture554/0cycles/76debt.
Longest relevant cold queries: collision5v24v8vrmc0yq12.068ms1; label INSERT8hdu6h8dthd9612.179ms2; confirm6q6b5xuu1yj8s4.228ms1. Keep current unique SSCC/CASE/OP keys and rownum1 collision stop; inventory owner check index/plan and batching before production volume, no throughput claim from one fixture. Rejected DELETE20.012ms is guard/error compilation, no operational delete path.
204/205 final addressed GROSS/TARE source archive and once-only QC still pending; whole NS40 not accepted.
"""
for path,line in[
("wiki/index.md","- [SSCC малой коробки](database/nicora_ni042_case_sscc_20261011.md):203 shared allocator/immutable original CP/GS1 print/scan confirmation/native admission/currentCASE6; addressed final scales next."),
("wiki/log.md","2026-10-11:203 CASE logistic SSCC applied/current native root+allocator/API/immutable guards. Own QPB20356E93BB1/090000000000000025 software prefix/currentCASE6/native rollback/replay/refusals/print/attached scan/QC+source14/cleanup. TSD durable identical retry; architecture554/0/76. Collision12.068ms1/insert12.179ms2 retain keys/bounds, inventory plan owner. No real GS1 assignment/hardware/government ACK.204/205 next."),
("wiki/requirements/nikora_delivery_v55/execution/active/ni04_2.md","11.10.2026:203 NS40 standard BOX SSCC before pick, shared receiving allocator/current prefix/current emptyCASE/native guard/immutable CP history/GS1 print/scan confirmed/TSD durable retry. Actual own6/directSAP20/source14/weight QC passed.204 addressed final scale+205 once QC remain; NS40 not closed.")]:
 p=Path(path);out[path]=p.read_text(encoding="utf-8")+"\n"+line+"\n"
roots=[p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md")]
if roots:out[str(roots[0]/"NI04.2"/"203_case_sscc.md")]="""# Qwen: 203 CASE SSCC
Run scripts/ni042_case_sscc_case.py dedicated dev. Native metadata outer rollback restores CP and no label archive; same request/actor/op returns same label after current scope, changedbody rejects. Parallel issue same CASE cannot create second SSCC; foreignWARE/native/root invalid/current assignee denied. Shared actual receiving counter/checksum/prefix/range/collision. GS1 SVG/ZPL contain AI00+18digits but no plan quantity. Wrong attached scan/unconfirmed first pick refuse without P/H effects; confirm then original CASE6 path/currentQC/source14/native cleanup. Archive delete/update and current carrier rewrite denied. Browser TSD durable originalbody/unknown-response identical retry/reprint/current version refresh/scan confirmation, no new OP after uncertainty. Synthetic prefix not legal GS1 or government ACK. Current keys/index/bounded collision SQL.
"""
print(json.dumps(out,ensure_ascii=True))
