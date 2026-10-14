from pathlib import Path
import json
out={};f=Path("db/migrations/2026-10-11_ni042_scale_packet")
out[str(f/"003_ledger.sql")]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-186-shared-scale-packet'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'One pure scale packet validator reused by original store archive and forthcoming warehouse post',sysdate,user,
'db/migrations/2026-10-11_ni042_scale_packet/apply.sql','db/migrations/2026-10-11_ni042_scale_packet/rollback.sql','APPLIED',
'Fresh store source/checkpoint/paired rollback;7 statements0errors/helpers VALID; existing authenticated store capture author scenario PASS stable10KG/replay/unstable/zero/stale/capacity/version/foreign/current archive/no P/H; warehouse archiving remains next');
commit;
"""
p=f/"apply.sql";out[str(p)]=p.read_text(encoding="utf-8")+"@@003_ledger.sql\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"));m["components"]=[x.replace("../2026-10-10_ni053_scale_capture/002_capture.sql","../2026-10-11_ni042_scale_packet/002_store_contract.sql")for x in m["components"]];m["components"].insert(0,"../2026-10-11_ni042_scale_packet/001_packet.sql");m["packages"].append("RRL_SCALE_PACKET_READ");out[str(p)]=json.dumps(m,indent=2)+"\n"
out["wiki/database/retailcase_ni042_scale_packet_20261011.md"]="""# NI04.2: общий разбор устойчивого пакета весов
186 APPLIED: pure RRL_SCALE_PACKET_READ reused by original RRL_STORE_SCALE_API; no second sample/stability algorithm. Existing device/authentication/archive/replay/actual-load/current-store source rules remain in the existing store adapter.
Validator: explicit capacity/resolution, KG/matching configured GROSS or NET basis/no preset tare, recent awareUTC/zero proof,5–25 samples sorted offset0..10000ms/window>=2s/spread<=resolution/positive resolution-multiple/capacity. Final weight is last sample, never average/rounded. Original store uses GROSS/gross_weight_kg; warehouse may use explicitly configured NET/weight_kg. Invalid UTC calendar date gives explicit20886 rather than unexplained Oracle date failure.
Source/value parsing is pure, archival/effects distinct. It does not connect hardware or claim calibration validity independently of configured adapter.
Fresh native store source/checkpoint/rollback; apply7 statements0errors/USER_ERRORS empty. Existing scripts/ni053_scale_capture_case.py fully PASS on actual API/Oracle: stable10KG/original SHA/exact replay/conflict/unstable/zero/stale/capacity/version/inactive/foreign sender/current recovery/append-only; no receipt/P/H. Synthetic calibration and samples are not hardware acceptance.
Next: warehouse address/device/dedicated sender/current CASE source immutable archive, then existing CASE effect consuming exact capture once. Order deviation/last-box distinct from stability/measurement accuracy.
"""
out["wiki/database/retailcase_ni042_warehouse_scale_design_20261011.md"]="""# NI04.2: складской весовой пост
Использовать186 общий packet validator, существующие RUSERS/rights/warehouse cells/CASE line/current SKU/root single writer.
Устройство явно связано со складом и адресом поста, отдельным gateway sender, активной версией calibration/capacity/resolution и GROSS или NET режимом. TEST/HARDWARE отдельно; default device disabled. Без реального протокола аппаратное подключение не заявляется.
Пакет содержит фактические CASE task/line/version, сканы source-cell/container/product, mode-specific samples and fresh zero/calibration. Архив immutable raw/hash/first received/result outside stock transaction; одинаковый device/capture body replay, иной отказ. API audit bounds32000/nonreplayable namespace.
NET для немаркированного loose KG; sealed marked/serialized box requires exact existing unit/QR and GROSS consistency, never permits forbidden splitting. Сток-команда читает archived capture, rechecks current scope/version/config/freshness, own HARD, and consumes it once in same root transaction with movement/reservation/CASE/outbox. One unique capture use, exact operation replay remains valid after capture ages. SQL locks stay within original sorted plan; hardware waiting stays outside it.
Order15%/last-box exception is separate approved business decision; never loosens scale stability/calibration nor invents net from average.
"""
for path,line in [
 ("wiki/index.md","- [Общий пакет весов](database/retailcase_ni042_scale_packet_20261011.md):186 original store archive uses one validator/stable samples/UTC/zero/replay unchanged; [складской пост](database/retailcase_ni042_warehouse_scale_design_20261011.md) next."),
 ("wiki/log.md","2026-10-11:186 APPLIED shared pure scale packet read; original store capture author regression PASS, no quantity effects. Warehouse immutable address/post archive and once-only existing CASE effect next; hardware unknown remains explicit."),
 ("wiki/requirements/retailcase_delivery_v55/execution/active/ni04_2.md","11.10.2026:186 one native stable packet reader extracted from existing store scales, reused without duplicate algorithm. Warehouse-post design recorded; source archive/effect wiring remains next. Real hardware acceptance not claimed.")]:
 p=Path(path);out[str(p)]=p.read_text(encoding="utf-8")+"\n"+line+"\n"
roots=[p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md")]
if roots:out[str(roots[0]/"NI04.2"/"186_shared_scale_packet.md")]="""# Qwen:186
Run existing scripts/ni053_scale_capture_case.py after extraction. Confirm stable10KG/original archive/hash/replay/conflict/zero/stale/unstable/capacity/current sender/calibration/deactivation/recovery; no P/H or receipt. Pure packet reader also supports explicitly configured NET samples named weight_kg; must not average/round. Invalid UTC date/calendar and missing/zero packet evidence refused. Warehouse archive/effects not accepted by186; no physical hardware claim.
"""
print(json.dumps(out,ensure_ascii=True))
