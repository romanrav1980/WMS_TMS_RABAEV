from pathlib import Path
import json
out={};page="wiki/database/retailcase_ni081_pickface_config_20261010.md"
out[page]="""# NI08.1 — настройка прежнего слотирования атомарна,142

RRL_PICK_FACE_ARTICUL existing SKU master links and RRL_PICK_FACE_ASSIGNMENT temporary wave ownership retained. Old PickingService.assign_pick_face_articul committed native base fields before a separate extended-attribute UPDATE. Replaced with inventory public facade, one stock_configuration_transaction/CONFIG6 exclusive fence/cursor-bound native assign_articul + original extended UPDATE; no second mapping writer or quantity effect.

Native RRL_PICK_TOPOLOGY_API existing body has no commit/autonomous clause. Existing RRL_STOCK_CONFIG_API whitelist extended with pick_topology_edit, matching original authenticated endpoint; no requirement for an unrelated extra permission. Current active RUSERS/WARE checked against locked actual face. Explicit row ID must belong to requested face/article; ambiguous natural mapping refused. Former row movement between parent face/article not silently accepted through nested endpoint. Qty/norm DTO fields use Decimal, Oracle receives exact values.

Before disabling active CASE mapping or shifting validity out of the current legacy day, existing old SKU stock/HARD, incoming warehouse tasks and remaining CASE tasks must drain. No existing task rewritten and no P/H changed. This wrapper is not complete NS59 recommendation/approval/drain lifecycle; other old topology/configuration writers are not all converted and new global guards on every topology CRUD were not introduced142.

Migration2026-10-10-142-atomic-existing-pickface-config APPLIED5/0. Checkpoint447 previous exact config source retained; current manifest replaces047 component with new142 full package source. Config/context/root packages liveVALID, default quantity compatibility OFF unchanged.

scripts/ni081_pickface_config_existing_case.py reused only135 private face508/mapping207/SKU QNATIVED9A5C53B54. Invalid extended method after changed base priority409 rolled back the entire original row, including timestamps/base fields. Valid exact priority100.0000000000000000001 stored exactly in Oracle/same207 repeat, then original configuration restored through the same API. Disabling occupied mapping rejected409 OLD_STOCK_REQUIRES_DRAIN, P20H20 unchanged; no new goods or task fixture.

SQL config fence14.832ms/base3.478ms/extended1.631ms cursor averages. Decision retain short configuration UOW, actual parent PK/current stock cell+UID keys and bounded mapping identity; no broad load or duplicate index. General architecture remains FAIL/481files/0cycles/134debt, no baseline enlargement.

Calendar gap is separately recorded: native eligibility uses trunc(sysdate), whereas Oracle server date is at−04 and UI/operator plans use explicit region. Revision140 corrected planned times only. Actual near-expiry business-day correctness needs warehouse calendar policy, not silently replacing historical facts. Owner timezone question pending; do not infer real warehouse zone from environment Europe/Moscow or a forecast UTC bucket.
"""
out["wiki/index.updated.tmp"]="- [Настройка прежнего слотирования атомарна](database/retailcase_ni081_pickface_config_20261010.md):142 native assign+extended one CONFIG fence/current WARE/Decimal/occupied drain refusal/actual rollback/P20H20 unchanged.\n"+Path("wiki/index.md").read_text(encoding="utf-8-sig")
for name,line in [
 ("wiki/log.md","2026-10-10:142 existing face-article master one CONFIG6 UOW/native assign+extended attrs/actual parent+current actorWARE/exact Decimal/old occupied mapping drain. Config whitelist pick_topology_edit/APPLIED5/0/checkpoint447/liveVALID. Actual private207 extended enum409 left full original row, exact100.0000000000000000001/sameID repeat/original restored, disable409/P20H20 unchanged. SQL14.832/3.478/1.631ms retain short keyed configuration; other topology callers/global guards still open. Gate0cycles/134debt still FAIL. Eligibility calendar SYSDate−04 vs business zone gap recorded/owner question pending; no inferred warehouse timezone."),
 ("wiki/requirements/retailcase_delivery_v55/execution/active/ni08_1.md","Ticket142 existing SKU-face configuration atomic/exact/current scope and occupied withdrawal refused. NS59 range recommendation/approval/drain still next; other legacy topology config paths remain. Calendar policy gap also recorded, warehouse owner zone awaiting clarification."),
 ("wiki/incidents/oracle_naive_timestamps_20261010.md","Follow-up142: RRL_STOCK_ELIGIBILITY body37/39/42 uses trunc(sysdate) for expiry/minimum days/remaining-percent, body52 legacy face-validity uses sysdate. Server−04 differs from operator/business region. Plan140 timezone is not a warehouse calendar declaration. Warehouse business-day policy must be explicit; ask owner, preserve actual timestamps/history and do not assume calendar coverage from UTC forecast.")
]:
 p=Path(name);out[name]=p.read_text(encoding="utf-8-sig")+"\n"+line+"\n"
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");m=json.loads(p.read_text(encoding="utf-8-sig"))
for row in m["sprints"]:
 if row.get("id")=="NI08.1":
  row.setdefault("implementedSlices",[]).append("142 atomic original SKU-face configuration/Decimal/current parentWARE/occupied withdrawal drain refusal")
  row["evidence"]=page;row["acceptanceStatus"]="author_dev_133_142_range_lifecycle_joint_timing_calendar_independent_open"
out[str(p)]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8-sig"))
assert m["components"].count("047_configuration.sql")==1
m["components"]=[("../2026-10-10_ni081_pickface_config/001_config.sql"if x=="047_configuration.sql"else x)for x in m["components"]]
out[str(p)]=json.dumps(m,indent=2)+"\n"
out["задания на проведения тестов/NI08.1/142_атомарная_настройка_слотирования.md"]="""# Qwen —142

Read design/evidence/source facade/helpers/native config whitelist. Own mapping207/face508 restored, current P20H20/wave395 still active. No new goods/whole regression run.

One original configuration fence/UOW covers legacy native base assign and extended attrs, no internal commit; current active actorWARE and locked parent/link identity; ambiguous mapping refused. Exact Decimal SKU norm values, no float conversion on write. Invalid extended check after base change leaves full old row/timestamps; same natural mapping repeat preserves original ID.

Occupied stock/HARD/incoming/remaining CASE prevents deactivation/expired future validity; old task assignments and goods untouched. Verify foreign actor/parent-ID mismatch and future date validity. Other old topology writers remain outside this slice: no claim of full global guards or NS59 recommendations.

Calendar eligibility uses old server sysdate; owner business timezone clarification pending. Do not declare near-expiry correctness covered by plan140 or UTC forecast. Architecture still fails other debt, not baseline-expanded.
"""
print(json.dumps(out,ensure_ascii=True))
