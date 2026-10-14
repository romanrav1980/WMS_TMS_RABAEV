from pathlib import Path
import json
out={}
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
for group,name in [("startup_scripts","001_schema.sql"),("additional_scripts","002_guards.sql")]:
 item="../2026-10-10_ni071_correction/"+name
 if item not in m[group]:m[group].append(item)
out[str(p)]=json.dumps(m,indent=2)+"\n"
p=Path("wiki/index.md");out["wiki/index.updated.tmp"]="- [Поздняя коррекция расходов](database/nicora_ni071_correction_20261010.md):114 APPLIED, linked signed credit/dual phases/current original total recheck/stale second denied/net0/history/no goods.\n"+p.read_text(encoding="utf-8-sig")
for name,line in [
 ("wiki/log.md","2026-10-10:114 existing expense/dual approval/allocation extended with signed magnitude/original source/expected confirmed total; original-before-child locks/final current total recheck prevents competing credits from reducing cost belowzero. Actual synthetic large source reversed through linked credit, two pending credits stale second final denied then rejected, exact signed allocation/replay/net0/history/no goods PASS47517f0309. SQL64.108/97.240/37.890ms retain correction index/expense PK/phase uniques; finance owner growth plan. UI shows signed correction and original IDs; original goods unchanged."),
 ("wiki/requirements/nikora_delivery_v55/execution/active/ni07_1.md","Ticket114: [поздняя финансовая коррекция](../../../../database/nicora_ni071_correction_20261010.md), original immutable source/signed debit or credit/dual phases/current confirmed total/original basis/signed allocation; actual stale competing credit denied/net0/history preserved. Monthly shared rates, complete source bases/crosswarehouse remain.")]:
 p=Path(name);out[name]=p.read_text(encoding="utf-8-sig")+"\n"+line+"\n"
out["wiki/database/nicora_ni071_correction_20261010.md"]="""# NI07.1 — поздняя финансовая корректировка,114
2026-10-10-114-linked-expense-corrections APPLIED RABAEV/orcl schema2/0 then apply7/0; existing expense/decision guards VALID. Positive absolute AMOUNT retained; ADJUSTMENT_SIGN±1/CORRECTION_OF_OP/EXPECTED_CONFIRMED_TOTAL and root index added. Previous ordinary positive snapshots/hash shape unchanged.

Correction references original root only, approved original same warehouse/article/version/name/object/currency and original agreed basis. Original-before-child lock order in report/phase decisions; current confirmed total=original amount + approved signed corrections. Expected total checked at report and independently again at final FINANCE approval, total cannot belowzero or exceed configured1e18 bound. Original history/allocations never rewritten. Two phases/right/current warehouse/different controller retained. Source article may now be inactive; correction preserves original frozen article identity.
Exact signed cents persisted as magnitude+sign; allocation keeps original source/basis and magnitude, signed results/invoice/warehouse register display correction. Vehicle corrections remain vehicle only. Report/decision/operation repeats preserve saved results; original ordinary canonical requests unchanged. Raw UI chooses original approved root and freezes current confirmed total/object/currency, user enters signed difference.

[Author case](../../scripts/ni071_correction_case.py) PASS47517f0309: original synthetic EX.PRECISION:f57025b124 amount12345678901234567.89, linked negative credit/dual signatures/original WEIGHT basis, exact signed allocation/replay. Two pending credits initially saw same original total; after first approval second final409/stale and explicit finance rejection. Confirmed root net0; further−0.01 denied. Original amount/allocation and goods events retained. This neutralizes software monetary boundary fixture through visible history, no real payment. Actor retired.
SQL64.108/97.240/37.890ms: retain root correction index/expense PK/phase uniques, finance owner checks repeated growing lineage plan. Admin TypeScript/encoding PASS; live warehouse queue HTTP200/signed figures/exact root0. Independent concurrency acceptance/multi-leaf signed cent allocation/monthly shared rates remain open.
"""
out["задания на проведения тестов/NI07.1/114_коррекция_расхода.md"]="""# Qwen — NI07.1,114
Own original confirmed expense, signed adjustment new document/source expected total. No edits/deletes to original. Exact same object/article/currency/warehouse/original basis; correction chains not allowed.
Two phases/different finance actor/root-before-child locks. Two pending credits same total: afterfirst confirm second final must refuse stale, no negative remaining total/partial writes. Reject stale request explicitly. Debit/credit/vehicle cases, no goods effects.
Signed allocation preserves total and exact original physical source; replay immutable, invoice shows original and correcting lines. Old positive requests canonical replay unchanged.
Synthetic precision root f57025b124 was neutralized by original credit47517f0309, do not rerun as fresh. Check actual SQL/source keys/VALID and limits; no actual payment asserted.
"""
print(json.dumps(out,ensure_ascii=True))
