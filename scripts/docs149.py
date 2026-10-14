from pathlib import Path
import json
out={};page="wiki/architecture/retailcase_typed_native_boundaries_20261010.md"
out[page]="""# Типы, публичные границы и компактное проведение,149

Existing concrete WarehouseTask/CASE/short/MES/reservation/LotCheck DTOs and OracleGateway|TransactionGateway now type missing public/infra signatures. Native JSON result dict explicitly returned, previous incorrect complete->None fixed. TaskActionHandler moved to owner contract and bound factory Callable specifies handler/gateway. No separate business rule.

CaseCarrierReturn DTO and QualityWeightPolicyInput moved from API to owner contracts, old imports preserve alias identity. Reservation DTOs moved from enlarged schemas.py to passive inventory/contracts.py, existing schema names retained. OperationFactUpdate similarly passive transport/contracts; only aliases in schemas. No infrastructure→API or foreign private module dependency. Master_data receipt policy now shared platform public CONFIG UOW. Frontend StoreCasesPanel uses delivery public index.

StockPosting staging hint/capture preparation extracted to same-cursor typed stock_staging_inputs; existing retry/deadline/prepare/root/stage/commit/reset logic retained. Terminal old lot-check DML tail removed because148 adapter handles all active effects or refuses; protocol and scan normalization remain.

Remaining oversized legacy transport router receives actual extraction: unchanged PATCH /api/admin/transport/operations/{op_id}/fact in transport module API/port/native adapter, application composition injects original availability cache invalidation after successful commit. Existing TransportService native path retained for other legacy callers. No duplicated posting/scheduling logic. Native error class moved to passive contracts_plan, original infrastructure alias preserved.

Quality gate PASS:499files/0cycles/79 remaining recorded legacy debt; no new/grown regressions. --tighten-baseline only decreased actual allowances, thresholds unchanged.24 architecture/tooling casesPASS, both frontend TypeScript checksPASS; pytest cache directory warning did not affect result. Seventeen targeted cutover casesPASS. No full independent business acceptance.

Actual original SAP receipt replay exact/no new journal after staging extraction. Original task829 sync twice same/native event and stock/attempt timestamps unchanged. Original ARM task33530 fact preserved: old URI/openAPI present, empty400, cancelled trip409 through new endpoint, original operation list/facts unchanged. No new stock/TT. Positive new fact and positive full API CASE remain independent cases.

No Oracle migration; current native keyed writers retained. Native rule and warehouse calendar decisions unchanged. Main factual remaining NI08.1: approved physical ranges/drain/cost routes, joint exact schedule/driver validator, canonical warehouse calendar and independent acceptance.
"""
out["wiki/index.updated.tmp"]="- [Типизированные границы native-команд](architecture/retailcase_typed_native_boundaries_20261010.md):149 concrete DTO/public ports/same-cursor staging/old ARM URI/cache retained; full quality gatePASS499files0cycles79debt.\n"+Path("wiki/index.md").read_text(encoding="utf-8-sig")
for p,line in [
("wiki/log.md","2026-10-10:149 concrete native DTOs/gateway/public result/factory types, shared passive CASE/weight/reservation/ARM DTO contracts; module/public reader construction, frontend delivery public export. Stock hints extracted samecursor; old terminal effect tail removed. Original ARM fact URI moved module/API/port/native/composition with original cache callback. Full qualityPASS499files0cycles79legacydebt; baseline tightened only/24 architecture-tooling/bothTS PASS.17 cutover boundary cases; actual SAP saved replay/task829 sync unchanged, existing33530 URI empty400/current cancelled409/facts unchanged. No Oracle/quantity writes or full independent acceptance."),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni08_1.md","Ticket149 typed native/public contracts and old ARM endpoint extraction; full structural quality gate PASS. See architecture/retailcase_typed_native_boundaries_20261010.md; remaining business acceptance not replaced by this gate.")
]:out[p]=Path(p).read_text(encoding="utf-8-sig")+"\n"+line+"\n"
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");m=json.loads(p.read_text(encoding="utf-8-sig"))
for row in m["sprints"]:
 if row.get("id")=="NI08.1":
  row.setdefault("implementedSlices",[]).append("149 typed native/public DTO contracts/extracted same-cursor staging/ARM endpoint and original cache/quality gate PASS")
  row["evidence"]=page
out[str(p)]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
out["задания на проведения тестов/NI08.1/149_модульные_контракты_native.md"]="""# Qwen —149

Read design/final source/contracts/composition. Concrete DTO aliases must retain old JSON/OpenAPI/defaults/Decimal identity. Public bind/policy facade constructs gateway; no router DB imports. Master_data uses platform CONFIG public, frontend delivery public export. Gateway bound factory/read-only/native results correctly typed; no duplicate validation.

Staging helper uses identical posting cursor/no commit/new lock; retry and original SAP receipt replay exact. Unknown result same operation/body recovery. Terminal quality no legacy DML tail. Original ARM URI/current rights/warehouse/native error/empty400 and existing cache invalidation only after success. Original141 cancelledTT403/409/history unchanged; successful current unstartedTT fact separately verify.

Full quality gate authorPASS499files0cycles79legacydebt/24structural/bothTS, thresholds not raised and baseline only tightened. Seventeen boundary cases + originalSAP/task829/33530 evidence are not independent complete sprint acceptance.
"""
print(json.dumps(out,ensure_ascii=True))
