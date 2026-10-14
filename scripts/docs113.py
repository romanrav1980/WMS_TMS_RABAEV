from pathlib import Path
import json
out={}
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
for group,names in {"startup_scripts":["001_schema.sql","003_weight_source.sql"],"additional_scripts":["002_guards.sql"]}.items():
 for name in names:
  item="../2026-10-10_ni071_allocation/"+name
  if item not in m[group]:m[group].append(item)
item="../2026-10-10_ni071_expenses/003_document_key.sql"
if item not in m["additional_scripts"]:m["additional_scripts"].append(item)
out[str(p)]=json.dumps(m,indent=2)+"\n"
p=Path("wiki/index.md");out["wiki/index.updated.tmp"]="- [Распределение расхода на фактический товар](database/nicora_ni071_allocation_20261010.md):113 APPLIED, original approved10.01/exact source weights/cents/replay/vehicle denial, Decimal boundary exact; existing invoice extra lines.\n"+p.read_text(encoding="utf-8-sig")
for name,line in [
 ("wiki/log.md","2026-10-10:113 actual original112 trip expense10.01GEL allocated exact cents/WEIGHT on frozen departed STOCK source; missing stock weight resolved only single-leaf measured BOX net of known frozen tare. Vehicle/current source/full departure/units constraints fail closed. Actual/replay/conflict/second denied PASS5ed6f17714. Financial Oracle NUMBER reads changed to explicit NLS decimal text/Decimal; synthetic12345678901234567.89 report/dual approval/allocation/sum/replay exactPASSf57025b124, duplicate source document differentOP denied. Slow178.031/63.177/43.554ms retain source PK/batched box proofs200loads/10000leaves; finance owner monitors grown history. UI allocation and existing invoice extra expense feature. No goods event."),
 ("wiki/requirements/nikora_delivery_v55/execution/active/ni07_1.md","Ticket113: [распределение](../../../../database/nicora_ni071_allocation_20261010.md), actual approved trip10.01/WEIGHT/source/cents/replay; vehicle refused, exact large Decimal dev case. Existing invoice shows extras/current allocation status. CASE/multi-warehouse source resolver/corrections/monthly rates remain open.")]:
 p=Path(name);out[name]=p.read_text(encoding="utf-8-sig")+"\n"+line+"\n"
out["wiki/database/nicora_ni071_allocation_20261010.md"]="""# NI07.1 — распределение дополнительного расхода,113
2026-10-10-113-trip-expense-exact-allocation APPLIED7/0 + exact weight source1/0; duplicate112 document business key1/0. Immutable RRL_LOGISTICS_EXP_ALLOCATION/ALLOC_LINE and guards VALID RABAEV/orcl. Finance owns transaction, no P/H/quantity effects.
Current warehouse calc_tt_price, original expense row first lock/approved independent FINANCE/same selected basis, TRIP only. Source all original actual load manifests bound200/all sameWARE/DEPARTED; exact STOCK leaf qty/UOM frozen. CASE without exact stock provider fails closed. Duplicate source leaf rejected/max10000. BASE_QUANTITY requires one same base unit; WEIGHT requires positive exact goods weights, container tare excluded.

If frozen STOCK lacks weight, only original measured BOX proof with exactly one STOCK descendant and known container tare can resolve net goods weight. Persist MEASURED_BOX_NET/source BOX UID or FROZEN_STOCK/NONE identity, not guessed proportional weight. Box proofs fetched one indexed trip batch/max10000, hierarchy cycle/duplicate/bound checks.
Allocate exact cents by largest fractional remainder/deterministic source-key; original expense currency/amount/basis/decision frozen and same-TX Oracle sum check. Unique expense→allocation and op/hash replay. Vehicle costs cannot allocate goods. Source document key ware/article/object/currency/reference prevents new operation repeating same documentary line; include line in reference when document has multiple articles/lines.

Financial NUMBER retrieval uses explicit NLS dot decimal text→Decimal for rate/expense/proof/sum; no float money round trip. New raw allocation button/queue and finance BillingExtraExpenses component inside existing invoice detail show confirmed/pending/rejected/allocated extras through original TT.PAY_ORDER_ID. Carrier invoice PRICE stays distinct.

## Actual author evidence
Original112 EX.REPORT:80b1fc8567/10.01GEL/trip33514. Frozen STOCK weight null, first attempt properly denied and left no allocation. Added exact measured BOX single-leaf net derivation, original FULL.HU.SHIP:22c5dc5ec4/BOX gross2 minus frozen BOX tare1→goods1. [Original completion](../../scripts/ni071_allocation_existing_case.py) PASS tag5ed6f17714: whole10.01 assigned exact source/replay/conflict/second denied/vehicle no allocation/no goods.
Initial author sum assertion compared native driver float10.01 to Decimal and failed after business commit; SQL decimal-text assertion corrected, original saved operation inspected rather than repeated fresh allocation.
[Precision case](../../scripts/ni071_expense_precision_case.py) PASS tagf57025b124: synthetic dev-only amount12345678901234567.89 exact report/independent decisions/source allocation/Oracle sum/replay; duplicate same document new ID409. Own actor retired. No actual payment/invoice created.
SQL178.031/63.177/43.554ms: retain source PK/unique expense/document, batched proofs and scoped200/10000. Finance owner checks growing source histories. Admin TypeScript PASS. Independent review/multiple goods cent case/CASE representation/multiware/cost corrections/monthly rates remain open; synthetic amount not real liability.
"""
out["задания на проведения тестов/NI07.1/113_распределение_расхода.md"]="""# Qwen — NI07.1,113
Own approved TRIP expense/logist basis/independent finance, exact departed source manifests; no stock effects. Vehicle/unknown approval/mixed warehouse/nondeparted/CASE missing provider/source duplicates deny.
WEIGHT exact positive source, missing STOCK weight only measured BOX with single source and known tare; stored derivation source. Multi-leaf without individualweights refuses. BASE_QUANTITY mixed UOM refuses.
Largest-remainder cents deterministic, sum equals exact originalcurrency amount; immutable sources/decision/reference, retry/conflict/second newOP same expense denied. Source documentary key prevents repeated line undernewOP.
Verify financial reads preserve decimal strings/Decimal including large synthetic dev amount; do not reuse committed 112/113 sources as fresh allocation. Existing invoice extra feature respects pending/rejected/allocated, vehicle expense excluded.
Review SQL/bounds/VALID/independent evidence. No real invoice payment or external signed-document acceptance inferred.
"""
print(json.dumps(out,ensure_ascii=True))
