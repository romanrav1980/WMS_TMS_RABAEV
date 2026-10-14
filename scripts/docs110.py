from pathlib import Path
import json
out={}
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
for package,name in [("RRL_STOCK_EFFECT_CORE","003_effect.sql"),("RRL_STOCK_POSTING_API","004_root.sql")]:
 for i,item in enumerate(m["components"]):
  if ("package "+package.lower()) in (p.parent/item).read_text(encoding="utf-8-sig").lower():
   m["components"][i]="../2026-10-10_ni062_disposal/"+name;break
 else:raise RuntimeError("Missing component "+package)
for group,name in [("components","002_command.sql"),("startup_scripts","001_schema.sql"),("additional_scripts","005_guards.sql")]:
 item="../2026-10-10_ni062_disposal/"+name
 if item not in m[group]:m[group].append(item)
if "RRL_STOCK_RETURN_DISPOSE" not in m["packages"]:m["packages"].append("RRL_STOCK_RETURN_DISPOSE")
out[str(p)]=json.dumps(m,indent=2)+"\n"
p=Path("wiki/index.md");out["wiki/index.updated.tmp"]="- [Списание возвратного брака](database/retailcase_ni062_disposal_20261010.md):110 APPLIED, separate act/independent Root/exact blocked1/P0H0/event1/loss original store/outbox1/replay.\n"+p.read_text(encoding="utf-8-sig")
for name,line in [
 ("wiki/log.md","2026-10-10:110 ordinary DISPOSAL return consumes exact whole blocked source via existing effect core under explicit Root/current version/scans/independent SC decision. Original store is cost/loss destination; immutable act/fact and SAP pending atomic. Fresh approved SAP source1 from STORE.RECEIPT:04633c677f/current driver/receipt DISPOSAL.RECEIVE:b10092cbf0 then report/denials/dispose/replay/second409 actual PASS taga2c9f83b4f; P0H0/event1/fact1/outbox1. SQL27.200/16.126/1.028ms retain source unique/warehouse bounded100; NI06.2 owner checks grown source history plan. Marked and actual destruction evidence separate."),
 ("wiki/requirements/retailcase_delivery_v55/execution/active/ni06_2.md","Ticket110: [утилизация возвратного брака](../../../../database/retailcase_ni062_disposal_20261010.md), ordinary whole blocked source1, independent explicit core/P0H0/event1/SAP pending/loss original store/replay. Marked lifecycle and partial/multi-place remain open.")]:
 p=Path(name);out[name]=p.read_text(encoding="utf-8-sig")+"\n"+line+"\n"
out["wiki/database/retailcase_ni062_disposal_20261010.md"]="""# NI06.2 — утилизация возвратного брака,110
2026-10-10-110-return-disposal-original-loss-store APPLIED17/0 RABAEV/orcl. New private RRL_STOCK_RETURN_DISPOSE, existing Root/effect and guards VALID. Checkpoint426Root/427Effect; goods facts forward correction only.

Warehouse-bound warehouse_return_dispatch reporter stores immutable disposal receipt/document archive reference/hash/reason. Different active warehouse-bound SC actor store_return_approve conducts entire approved DISPOSAL return with source pallet/cell scan/current stock version. Exact whole source/noHARD/sameWARE blockedcell/noHU/currentBASE policy. Current marked profile denies ordinary command; no silent omitted units.
Existing Root sorted resource closure/recheck/operation replay and native effect consume→unit/balance/journal sole writer. Explicit disposal context permits blocked source; unrelated shipments cannot use it. Immutable disposal fact and STORE_RETURN_DISPOSED SAP pending event same transaction. Loss attribution is original accepted store STORE_ADDR through original return approval, not executing warehouse. No external SAP acknowledgement implied.

API typed port/raw warehouse return-disposal.html has immutable saved operation retry and current source version; report does not affect P. Unknown technical failure remains503/unconfirmed; confirmed business refusals allow corrected new intent.

## Actual author evidence
[Source](../../scripts/ni062_disposal_source_case.py): original accepted STORE.RECEIPT:04633c677f had remaining return allowance1. Ordinary approved DISPOSAL1, assumed SAP file, same existing trip/bound driver/return receiving in blocked cell; DISPOSAL.RECEIVE:b10092cbf0. Own source warehouse387548 initially had no return-zone/default receiving config; additive own cells/QDGb10092cbf0/QDDb10092cbf0/QDSb10092cbf0 configured. Source vehicle own max20kg/4places. Earlier missing BARCODE column/join policy attempts before approval had no goods effect.

[Disposal case](../../scripts/ni062_disposal_case.py) PASS taga2c9f83b4f: non-admin bound report/replay; same reporter403, stale version/foreigncell409; independent Root dispose1→P0H0, one event/fact/outbox; original loss STORE.QA:04633c677f; exact replay, second operation409. Fixture observer/driver retired. Synthetic destruction document means dev evidence only, not real destruction/SAP ACK.

Slow27.200/16.126/1.028ms: retain source unique indexes/current warehouse100; NI06.2 owner checks repeated growing source-history plan. Independent acceptance/actual archive proof/marked regulatory writeoff/partial disputes remain separate.
"""
out["задания на проведения тестов/NI06.2/110_утилизация_возврата.md"]="""# Qwen — NI06.2,110
Own actual approved DISPOSAL receipt, do not rerun committed source1. Separate warehouse report no stock; exact replay/conflict.
Independent SC required; same actor/foreign warehouse/receipt SUPPLIER or REUSE/foreign scan/stale version/HARD/nested HU/marked policy denied.
Whole current blocked quantity consumed once through Root/effect; P0H0/event1/fact1/SAP pending1; original accepted store preserved as loss attribution. Replay no effects, different second operation denied.
Verify source recheck under current locks, failed command rollback and live changed objects VALID. Synthetic documentary/hardware/SAP ACK limits explicit. Slow SQL decision and independent evidence, no full sprint claim.
"""
print(json.dumps(out,ensure_ascii=True))
