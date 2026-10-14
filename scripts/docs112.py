from pathlib import Path
import json
out={}
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
for group,name in [("startup_scripts","001_schema.sql"),("additional_scripts","002_guards.sql")]:
 item="../2026-10-10_ni071_expenses/"+name
 if item not in m[group]:m[group].append(item)
out[str(p)]=json.dumps(m,indent=2)+"\n"
p=Path("wiki/index.md");out["wiki/index.updated.tmp"]="- [Допрасход: логист и финансовый контроль](database/nicora_ni071_expenses_20261010.md):112 APPLIED, original TT10.01GEL/independent phases, vehicle4.00 only/no goods, included-rate work denied.\n"+p.read_text(encoding="utf-8-sig")
for name,line in [
 ("wiki/log.md","2026-10-10:112 explicit extra expense catalog/immutable object-date-currency-amount report/logistic basis and independent finance approval, existing TT/vehicle, no goods. Actual trip10.01GEL approved WEIGHT pending allocation, vehicle4.00 NONE-only, included-rate article and same phase actor finance denied, replay preserved tag80b1fc8567. Slow94.579/53.908/52.864ms retain object/date index and bounded100/200; finance owner plans growing source history. Raw extra expense UI durable intents. Allocation next113."),
 ("wiki/requirements/nikora_delivery_v55/execution/active/ni07_1.md","Ticket112: [дополнительные расходы](../../../../database/nicora_ni071_expenses_20261010.md), current warehouse expense report/explicit extra article/logist+independent finance, actual TT10.01 WEIGHT pending allocation, vehicle4.00 only/NONE, no P. Actual goods allocation and correction/monthly norms next.")]:
 p=Path(name);out[name]=p.read_text(encoding="utf-8-sig")+"\n"+line+"\n"
out["wiki/database/nicora_ni071_expenses_20261010.md"]="""# NI07.1 — дополнительные расходы и два решения,112
2026-10-10-112-extra-expense-dual-approval APPLIED10/0 RABAEV/orcl; article/expense/decision guards VALID. Catalog version/scope/included flag, immutable expense copies article version/name and exact Decimal cents/currency/date/document/source existing TT or vehicle/warehouse/reporting actor.
Current bound edit_bill_tt report; calc_tt_price LOGIST selects TT base quantity or goods weight; VEHICLE alwaysNONE. Different current bound create_tt_price FINANCE confirms same basis or rejects. Expense row FORUPDATE first, unique expense+phase/ophash; exact original intent retry. Initial PK concurrent race retries same request once after rollback, no quantity effect.
Rate-included article blocked, WAREHOUSE_PICKING cannot register as extra code. No automatic duplicate-recognition of arbitrary differently named work; explicit catalog and financial review enforce classification. Current catalog optimistic versions preserve expense snapshots; full catalog-history audit/late correcting charges separate.
Approved TT monetary expense is visible pending allocation; vehicle approval is vehicle only and must never allocate goods. Existing billing/TT/vehicle retained; no carrier PRICE overwrite/new invoice. Raw logistics-expenses.html has catalog/report/two-phase controls/durable intents.

[Author case](../../scripts/ni071_expense_case.py) PASS tag80b1fc8567: non-admin warehouse2378876 trip33514/report10.01GEL/replay/conflict, included-rate article denied, LOGIST WEIGHT then same actor FINANCE403, independent admin APPROVED_PENDING_ALLOCATION/replay. Original vehicle4.00GEL WEIGHT409 thenNONE/independent finance APPROVED_VEHICLE_ONLY. Goods events unchanged; actor retired. Earlier lowercase dev code was validation422 before any article/fact.
Slow94.579/53.908/52.864ms: retain existing source PK/new object+date index, warehouse100/catalog200. Finance owner checks repeated source-history plans. Independent acceptance/actual invoice attachment/allocation/late corrections/monthly rates remain open.
"""
out["задания на проведения тестов/NI07.1/112_допрасходы.md"]="""# Qwen — NI07.1,112
Own existing TT/vehicle, article/explicit scope/version/included flag, exact cents/date/currency/document. Report no goods effect, current warehouse permissions and original intent retry/conflict.
Included common work and WAREHOUSE_PICKING extra code denied. LOGIST chooses trip WEIGHT or BASE_QUANTITY, vehicleNONE only. Other current bound FINANCE confirms same basis/rejects; same actor/missing prior stage/current warehouse denied. Repeated phase/operation safe.
Vehicle expense never allocates goods; TT approval currently pending allocation. Both have immutable decisions/source and no goods events. Unknown technical answer retains original intent, no guessed confirmation.
Review actual SQL/indexes/source limits/VALID. Late correction, complete catalog audit and allocation are later explicit evidence, not inferred here.
"""
print(json.dumps(out,ensure_ascii=True))
