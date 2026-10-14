from pathlib import Path
import json
out={}
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"));repl={"../2026-10-10_ni062_return_receiving/002_command.sql":"../2026-10-10_ni062_reuse_boxes/003_receiving.sql","../2026-10-10_ni062_return_putaway/002_helper.sql":"../2026-10-10_ni062_reuse_boxes/004_putaway.sql","../2026-10-09_ni032_replenishment_admission/002_policy.sql":"../2026-10-10_ni062_reuse_boxes/006_repl_policy.sql"}
m["components"]=[repl.get(x,x) for x in m["components"]]
for group,names in {"components":["002_reuse.sql"],"startup_scripts":["001_schema.sql"],"additional_scripts":["005_guards.sql"]}.items():
 for name in names:
  item="../2026-10-10_ni062_reuse_boxes/"+name
  if item not in m[group]:m[group].append(item)
out[str(p)]=json.dumps(m,indent=2)+"\n"
p=Path("scripts/build107.py");s=p.read_text(encoding="utf-8-sig");at=s.index("print(json.dumps(out,ensure_ascii=True))");s=s[:at]+'''for name in ["002_reuse.sql","003_receiving.sql","005_guards.sql","006_repl_policy.sql","apply.sql","refine.sql"]:
 out[str(f/name)]=(f/name).read_text(encoding="utf-8-sig")
'''+s[at:];out[str(p)]=s
p=Path("wiki/index.md");out["wiki/index.updated.tmp"]="- [Исправная коробка возвращена в отбор](database/retailcase_ni062_reuse_boxes_20261010.md):107 APPLIED, own SAP source BOX24→actual store→approved return→blocked receipt/proof1x24→existing task/picking24/eligible/replay.\n- [Oracle native JSON в SAP обмене](incidents/oracle_native_json_sap_20261010.md): actual ARTMAS/supply/receipt bridge fixed, native dict/list and text supported, reserved raw bind removed.\n"+p.read_text(encoding="utf-8-sig")
p=Path("wiki/log.md");out[str(p)]=p.read_text(encoding="utf-8-sig")+"\n2026-10-10:107 ordinary complete-good-box REUSE fulfilled through original SAP batch/BOX exact UOM/source expiry and existing warehouse task to configured picking cell/shared batch mixing/temperature/planned occupancy. Fresh source ARTMAS+SAP receipt24/store accepted24 then approved return1x24/driver/blocked birth/putaway/eligible/replay actual PASS. Fixed preexisting native JSON list/dict double decode and reserved raw SQL bind in supply import; same source continued. SQL36.482/32.593/30.188ms retain PK/scoped queue/bounded200 planned lots.\n"
p=Path("wiki/requirements/retailcase_delivery_v55/execution/active/ni06_2.md");out[str(p)]=p.read_text(encoding="utf-8-sig")+"\nTicket107: [исправные полные коробки в отбор](../../../../database/retailcase_ni062_reuse_boxes_20261010.md), actual verified source BOX24/approval/SAP/driver/blocked receipt/proof/current picking cell/task24/eligible/replay; marked/multi-place and final supplier/disposal transfer remain open.\n"
out["wiki/database/retailcase_ni062_reuse_boxes_20261010.md"]="""# NI06.2 — исправный возврат полной коробки в отбор,107
2026-10-10-107-return-full-good-box-reuse APPLIED RABAEV/orcl,17 statements/0 errors plus refinement12/0. REC/PUT/reuse helper/replenishment policy/guards VALID. Existing typed return receipt permits REUSE; optional separate blocked REUSE receiving zone; immutable RRL_RETURN_REUSE_PROOF source.

Приёмка REUSE требует approved COMPLETE_GOOD_BOX, фактическое подтверждение комплектности/исправности, ШК именно BOX, целое число коробок и exact current BOX→BASE quantity equal approved quantity. Original SAP verified supplier batch/expiry retained; legacy unverified batch не допускается в reusable stock. Current minimum shelf life checked before birth and placement. Required marking still refuses this ordinary slice, never omitted.

Товар сначала рождается в отдельной недоступной для отбора/пополнения зоне. Existing MANUAL/PUTAWAY task/Root transfer preserves UID/source/batch/quantity; target is current configured SKU PICK_CELL (fallback legacy article cell) in same warehouse, usable OTBOR. Shared RRL_STOCK_REPL_ADMISSION.lot_key/assert_target preserves original mixing policy. Different SKU forbidden, other batches only when explicit ALLOW_PICK_BATCH_MIX; current and planned target occupants considered. Temp/min shelf/mass tested against current rules. Positive height/published slots still require later exact physical proofs; alternate picking address needs existing slotting configuration, not arbitrary scan override.

API existing receive adds optional full_box_count/complete_good_boxes, defaults excluded for earlier replay. New warehouse reuse-zone config uses original version/config fence. Existing warehouse ARM adds controls/BOX confirmation; placement queue shows current picking target.

## Actual author evidence
No eligible SAP-origin BOX source existed after earlier dev cleanup. [Fresh source fixture](../../scripts/ni062_reuse_source_case.py)/[original continuation](../../scripts/ni062_reuse_source_continue.py) used assumed ARTMAS10 and warehouse supply XML through existing import, ordinary BOX24, actual SAP receipt and existing putaway, existing whole picking/ST/nested load/departure/store acceptance24. Source tag cdbf4c0962, article REUSE.QA:cdbf4c0962, original SSCC300000034517022819, warehouse13583852. Actual source traces retained; hardware/SAP external ACK not claimed.

[Return case](../../scripts/ni062_reuse_boxes_case.py) PASS, tag e6c16d0bbd: approval24, assumed SAP return, current dedicated driver pickup, wrong box_count2 refused, actual blocked P24/H0 + immutable proof1x24/batch, existing putaway to QIPcdbf4c0962, physical P24/H0 and eligibility reason null, exact receive/task replay and one placement. Returned own stock24 retained for subsequent functional work, driver retired/binding inactive.

Actual flow uncovered existing SAP JSON native-list decoding and reserved :raw bind bugs; fixed existing integration rather than new importer, continued original source. [[../incidents/oracle_native_json_sap_20261010]].

Slow proof SQL36.482/32.593/30.188ms. Retain PK and bounded warehouse queues100/planned occupants200, existing target/source-cell indexes. NI06.2 owner checks real occupied-cell plan at growing volume. Independent acceptance/mixed batch/marked/multi-place/final supplier transfer and disposal remain open.
"""
out["wiki/incidents/oracle_native_json_sap_20261010.md"]="""# Oracle native JSON в существующем SAP обмене
10.10.2026, выявлено при NI06.2 REUSE. ARTMAS импорт создал новый own article, WarehouseSupplyOrder then500 before any inventory. Direct original service traceback: UNITS_JSON already list, json.loads(list) TypeError. After decoding fix source then ORA-01745 for reserved bind :raw. No partial source/order persisted on rejected transactions.

Shared platform read_oracle_json accepts native dict/list/scalar, JSON text and LOB; applied to current supply message replay/aggregation/UOM, article apply/replay and receipt staged domain. Existing source binding renamed xml_raw, aggregation code_raw/agg_level. No transport/XML mapping replaced.

Same original source cdbf4c0962 continued: ARTMAS source APPLIED, supply order5b3e036751484ec0b1eb0a746187f4d4, actual SAP receipt BOX24 and warehouse task, physical shipment/store receipt24. Original helper replay supports native JSON result. This is assumed gateway technical source, no real SAP ACK.
"""
out["задания на проведения тестов/NI06.2/107_исправная_коробка_в_отбор.md"]="""# Qwen — NI06.2,107
Create own approved ordinary full good BOX return from actually received original SAP batch. Actual barcode BOX/current conversion/full_box_count and receivedBASE exact; wrong EA barcode/count/incomplete/batch/expiry/staleSKU rules denied with no birth/proof/outbox.
Dedicated driver actual pickup, warehouse blocked receipt/proof1xBOX, existing MANUAL PUTAWAY to current allowed picking cell, current/temp/shelf/mass/current+planned occupancy. Wrong SKU never mixed; other batch allowed only explicit ALLOW_PICK_BATCH_MIX.
Immutable original source SSCC/batch/date/UOM, typed return header/source approval/SAP return (no purchase), receive and task exact replay. After placement usable stock/one SAP outbox; SAP pending/export not actual ACK.
Occupied-cell concurrent plans must not bypass policy/capacity. Published slots/height explicitly denied until exact proof; no silent overwrite target by scan.
Do not rerun source/author one-time cases (source approval now consumed); use retained own stock for later read/case. Native JSON/text/LOB source/UOM/replay supported, reserved bind absent. Longest SQL decision required.
"""
print(json.dumps(out,ensure_ascii=True))
