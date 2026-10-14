from pathlib import Path
import json
out={}
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"));repl={"../2026-10-10_ni063_warehouse_tare_loss/004_command.sql":"../2026-10-10_ni063_holder_loss/002_command.sql","../2026-10-10_ni063_booked_handover/003_tare_command.sql":"../2026-10-10_ni063_holder_loss/004_tare_command.sql","../2026-10-10_ni063_warehouse_tare_loss/007_resolution_command.sql":"../2026-10-10_ni063_holder_loss/005_resolution_command.sql"}
m["components"]=[repl.get(x,x) for x in m["components"]]
for group,names in {"startup_scripts":["001_schema.sql"],"additional_scripts":["003_debt.sql"]}.items():
 for name in names:
  item="../2026-10-10_ni063_holder_loss/"+name
  if item not in m[group]:m[group].append(item)
out[str(p)]=json.dumps(m,indent=2)+"\n"
p=Path("scripts/ni063_holder_loss_case.py");s=p.read_text(encoding="utf-8-sig").replace(' call(admin,f"/api/admin/rights/groups/{group}/rights",{"right_name":"tare_loss_report","description":"Own vehicle loss observer"})',' for right in ["tare_loss_report","tare_offer"]:\n  call(admin,f"/api/admin/rights/groups/{group}/rights",{"right_name":right,"description":"Own vehicle loss observer"})',1);out[str(p)]=s
p=Path("wiki/index.md");out["wiki/index.updated.tmp"]="- [Недостача тары магазина и автомобиля](database/nicora_ni063_holder_loss_20261010.md):106 APPLIED, original debt1→0/deadline retained; pending vehicle claim blocks transfer then reject restores1; driver UI.\n"+p.read_text(encoding="utf-8-sig")
p=Path("wiki/log.md");out[str(p)]=p.read_text(encoding="utf-8-sig")+"\n2026-10-10:106 current store/vehicle loss observation via same claims/decision Root, original debt association and all-holder pending availability. Store damaged1 independent loss0/debt0/deadline retained; vehicle claim blocks authorized offer and reject preserves1. React driver form/strict typecheck passed. Slow loss/debt SQL377.890/238.772ms cold single calls: retain source claim index+bounded queries; NI06.3 owner inspect plan/incremental projection if repeated latency grows.\n"
p=Path("wiki/requirements/nikora_delivery_v55/execution/active/ni06_3.md");out[str(p)]=p.read_text(encoding="utf-8-sig")+"\nTicket106: [недостача магазина/автомобиля](../../../../database/nicora_ni063_holder_loss_20261010.md), current participant/vehicle scan/original store loan cap, pending quantity unavailable in every holder; independent writeoff/reject and driver UI.\n"
out["wiki/database/nicora_ni063_holder_loss_20261010.md"]="""# NI06.3 — недостача у магазина и автомобиля,106
2026-10-10-106-store-vehicle-tare-loss APPLIED RABAEV/orcl,16 statements/0 errors; LOSS/CMD/RESOLVE/debt VALID. Added source claim/transport source FK fields to existing105 immutable claim, no historical rows rewritten.

REPORT STORE requires current bound receiver and exact original RRL_TARE_STORE_DEBT claim key/owner/type/condition/store. Multiple pending claims cannot exceed that debt or current free physical balance. Vehicle requires current dedicated driver/actual trip vehicle ID and scan. Independent DECIDE retains original custody/source, closes entire claim once, consumes exact same-condition physical balance. STORE writeoff reduces original loan, not a fabricated receipt; original due/policy retained.

All-source OFFER/ACCEPT and DAMAGE/WRITE_OFF now call shared usable quantity check; pending loss cannot be transferred or separately written off. Previous warehouse request canonical metadata excludes new null optional fields, old replay preserved.

[Author](../../scripts/ni063_holder_loss_case.py): original own100 DAMAGED store1→REPORT, other writeoff refused, same observer403, independent loss physical0/debt0/policy1/same due/replay; source historical100 remains, its old current-state verifier must not be rerun. Vehicle report1 succeeded; author first lacked tare_offer and stopped before testing actual denial. [Original continuation](../../scripts/ni063_holder_loss_continue.py) grants explicit role, proves blocked offer409, rejects claim independently/vehicle1/replay/events0. Dedicated original actors retired/binding inactive.

React existing driver TarePanel includes TareLossForm, current balance/version and original debt selector; independent decisions use existing loss register showing actual holder. TypeScript noEmit PASS; independent browser acceptance open.

Slow SQL1udsdar3bn0fj377.890ms and8fkdyyswa5w46238.772ms cold single calls. Added source FK index; retain bounded200 claims/debt and balance PK, no timeout inflation. Owner NI06.3 checks repeated plans/pushdown/incremental projection on growth. No capacity claim.

Remaining: damaged return inspection/current custody disposal, physical repack/cancellation and independent full-sprint review.
"""
out["задания на проведения тестов/NI06.3/106_недостача_магазина_машины.md"]="""# Qwen — NI06.3,106
Собственные store/vehicle ordinary tare balances. STORE bound observer source original claim ID/condition/current version, report qty≤debt minus pending and physical free. VEH current dedicated driver/same trip vehicle scan. Foreign store/source/qty/scan denied.
Pending amount blocks OFFER/ACCEPT/DAMAGE/WRITE_OFF at every holder; reserve inclusion never doubles physicalqty.
Another controller WRITE_OFF/REJECT exactly once; source loan/deadline retained, no goods event. Concurrent reports sourcecap and one decision perclaim. Old105 canonical report replay unchanged (new optional null fields excluded).
Driver UI reads current source/version, resets on actor/trip/owner/type change, original intent retry; no final financial decision by observer.
Longest SQL actual evidence/decision. Do not rerun100 current verifier or one-time106 author (debt intentionally settled).
"""
print(json.dumps(out,ensure_ascii=True))
