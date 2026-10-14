from pathlib import Path
import json
page="wiki/database/retailcase_ni081_range_capacity_20261010.md";out={}
out[page]="""# NI08.1 / NS59 — действующий диапазон и препятствия вывода,145

Same READ ONLY snapshot as143 extends existing scenario with original published cells and RRL_STOCK_REPL_CAPACITY.remaining_base_quantity. Native current capacity includes occupied volume/all article norms and existing assigned arrivals; no duplicated Python volume budget. Distinct cell counted once, duplicated active face refused as ambiguous, limit100; unknown norm/missing capacity is refusal/null, not certified zero.

Shows original face/cell/route IDs and volume/weight limits, known remaining BASE volume budget and additional quantity outside known volume. Withdrawal blockers: any physical stock/HARD, active incoming or outgoing warehouse task including ERROR, unfinished CASE lines. No assignment or active configuration changed. Volume check never asserts physical admission: weight/geometry/product compatibility/route-cost comparison/approval explicit pending. No invented pallet height or travel rate.

Author script ni081_range_capacity_existing_case.py actual original135 face508/cellQGd9a5c53b54 current P20H20/native volume0, stock and unfinished CASE blockers, no withdrawal/admission/apply; stock remains20/20. Dedicated raw scenario page shows per-cell reasons and no apply button, node syntax PASS. Initial generator quote error and actual CASE field PLANNED_QTY corrected before running case. No Oracle DDL or new fixture.

SQL face reader58.914ms/1, native capacity13.775ms/1, another associated cursor36.805ms/1. Decision retain max100 faces and canonical bounded budget. Before large range production scenario, batch face/stock/task observations and expose timing, owner inventory; no second capacity rule. Current native nested budget loops bounded200/source, full100face load not claimed.

Architecture488files/0cycles/134 remaining violations, FAIL; no allowance expansion or independent acceptance. Full NS59 approval/drain/routing-cost remains open.
"""
out["wiki/index.updated.tmp"]="- [Ёмкость действующего диапазона](database/retailcase_ni081_range_capacity_20261010.md):145 original face/cell/native volume budget/withdrawal blockers; actual508 volume0/P20H20/no apply.\n"+Path("wiki/index.md").read_text(encoding="utf-8-sig")
for p,line in [
("wiki/log.md","2026-10-10:145 original published face/cell/route/native volume capacity added to143 same READ ONLY snapshot, shared cell once/unknown null/stock-HARD/active source-target tasks/unfinished CASE withdrawal blockers. Existing508 actual volume0/P20H20/no withdrawal or apply. SQL native13.775/face58.914ms bounded100 kept; large-range batch ownerinventory backlog. Architecture488files0cycles134debtFAIL no baseline growth; full NS59 open."),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni08_1.md","Ticket145 existing range/canonical volume capacity/withdrawal blockers read model delivered; see database/retailcase_ni081_range_capacity_20261010.md. Approval/drain/route-cost still next.")
]:out[p]=Path(p).read_text(encoding="utf-8-sig")+"\n"+line+"\n"
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");m=json.loads(p.read_text(encoding="utf-8-sig"))
for row in m["sprints"]:
 if row.get("id")=="NI08.1":
  row.setdefault("implementedSlices",[]).append("145 original range/native remaining volume budget/current withdrawal blockers")
  row["evidence"]=page
out[str(p)]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
out["задания на проведения тестов/NI08.1/145_емкость_действующего_диапазона.md"]="""# Qwen —145

Read143/145 design/source/live canonical RRL_STOCK_REPL_CAPACITY, source same READ ONLY transaction. Existing135 face508/cell and P20H20; no fresh stock. Native remaining volume0, current stock/HARD and unfinished CASE withdrawal refusal. Duplicate shared cell no doublecapacity, missing budget/null not zero. Active source OR target warehouse tasks including ERROR block withdrawal. No physical admission/route-cost certification/range apply.

Check max100 face calls bounded200 native observations perface; batch proposal must reuse native rule. Exact Decimal text and source signature include range. Same snapshot and current warehouse actor retained. UI shows reasons/no apply. Authorcase only, no independent acceptance.
"""
print(json.dumps(out,ensure_ascii=True))
