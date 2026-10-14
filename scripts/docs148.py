from pathlib import Path
import json
out={};page="wiki/database/retailcase_cutover_adapters_20261010.md"
out[page]="""# Активное ядро обязательно для всех адаптеров,148

Shared inventory require_active_release exact current release read raises StockPostingError STOCK_RELEASE_NOT_ACTIVE, installed API handler503. Ten adapters CASE/short/terminal quality/reservation/document release/wave/MES no longer return None/False in PREPARED to select old effect. Native commands/source permissions/transactions unchanged; compatibility OFF unchanged.

Removed native-first legacy tails from CasePickService confirm/approve; MesService apply/calculate/release/confirm/cancel; StockReservationService create/promote/release/consume/cancel; PickingService physical full-pallet confirmation and reservation source builder. Original native branch return shapes retained. Existing CASE metadata shortcuts PREPARED removed, now ordinary serialized metadata path. Private old direct balance and MES reservation builders permanently refuse, cannot reactivate by PREPARED. Native-first MES/reservation/picking imports now inventory public contracts. No schema migration/history deleted.

Thirteen meaningful boundary cases PASS: three inactive shared states and ten adapter no opt-out paths. Actual current direct-native CASE history has no requested_confirmation API snapshot; attempted author positive replay therefore had no matching fixture. Corrected case to verify facade cannot relabel original native operation with another API body:409 OPERATION_CONTENT_CONFLICT and unchanged event snapshot on NATIVE.CASE:a6bcf2cbe3:1030. Positive API CASE confirmation/replay still independent functional case, not claimed. Existing original SAP receipt native replay exact/journal unchanged. No fresh goods or changes to retained135 P20H20.

Architecture488files/0cycles/118debt remaining, FAIL; down from133, no baseline expansion. File-size remnants and typed/public boundaries next. Original public endpoints retained, rollback should be forward native behavior rather than restored PREPARED executor.

SQL immutable operation lookup bounded PK retained; native completed proof review147 applies. All business document PREPARED statuses preserved, read-only reconciliation diagnostic not an effect bypass. Full sprint/independent acceptance still open.
"""
out["wiki/index.updated.tmp"]="- [Общий запрет старых проводок PREPARED](database/retailcase_cutover_adapters_20261010.md):148 ten adapters ACTIVE-only/native-first legacy tails removed/13 casesPASS/debt118/stock unchanged.\n"+Path("wiki/index.md").read_text(encoding="utf-8-sig")
for p,line in [
("wiki/log.md","2026-10-10:148 shared ACTIVE-only release boundary in ten adapters/no PREPARED None-False legacy opt-out; obsolete CASE/MES/reservation/picking native-first tails removed; serialized CASE metadata all states; old direct helpers closed/public imports.13 boundary casesPASS. No original API CASE requested_confirmation fixture: positive not claimed; actual direct-native1030 conflict409/event unchanged. Original SAP replay exact/no journal. Architecture488files0cycles118debtFAIL, no allowance growth; independent full API case next."),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni08_1.md","Ticket148 all ten stock adapters ACTIVE-only and legacy native-first tails removed; see database/retailcase_cutover_adapters_20261010.md. Positive full API CASE acceptance remains explicit pending.")
]:out[p]=Path(p).read_text(encoding="utf-8-sig")+"\n"+line+"\n"
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");m=json.loads(p.read_text(encoding="utf-8-sig"))
for row in m["sprints"]:
 if row.get("id")=="NI08.1":row.setdefault("implementedSlices",[]).append("148 all stock adapters ACTIVE-only/native-first legacy physical branches removed")
out[str(p)]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
out["задания на проведения тестов/NI08.1/148_общая_граница_нового_ядра.md"]="""# Qwen —148

Read ACTIVE boundary and ten adapters/native-first old service paths. InactivePREPARED/CUTOVER/missing release503, no fallback writes/None opt-out. Metadata CASE still serialized; old direct balance/MES reservation builder always refuses. Source recording and document statuses PREPARED retained.

Check current successful CASE API confirmation and same operation replay on owned source/session, no duplicate physical/reserve/event. Existing direct-native history lacks requested_confirmation API snapshot: cannot relabel this operation as new API body, conflict409 expected. Do not call negative conflict a successful replay. Preserve retained135 P20H20 for current workload/range demonstrations unless explicitly advancing this functional scenario and updating current fixture docs. Native-first MES/reservations/full-pallet response shapes/rights/aware proofs/exactDecimal unchanged. Author13 boundary cases and actual native conflict/original SAP replay only; no independent acceptance.
"""
print(json.dumps(out,ensure_ascii=True))
