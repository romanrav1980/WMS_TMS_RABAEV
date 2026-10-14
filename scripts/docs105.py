from pathlib import Path
import json
out={}
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"));repl={"../2026-10-10_ni063_tare_assembly/006_root.sql":"../2026-10-10_ni063_warehouse_tare_loss/005_root.sql","../2026-10-10_ni063_tare_assembly/002_planning.sql":"../2026-10-10_ni063_warehouse_tare_loss/002_planning.sql","../2026-10-10_ni063_tare_assembly/005_resolution_command.sql":"../2026-10-10_ni063_warehouse_tare_loss/007_resolution_command.sql"}
m["components"]=[repl.get(x,x) for x in m["components"]]
for group,names in {"components":["004_command.sql"],"startup_scripts":["001_schema.sql","003_availability.sql"],"additional_scripts":["006_guards.sql"]}.items():
 for name in names:
  item="../2026-10-10_ni063_warehouse_tare_loss/"+name
  if item not in m[group]:m[group].append(item)
out[str(p)]=json.dumps(m,indent=2)+"\n"
p=Path("wiki-raw/wms_admin_ui_reference/tare-loss.js");s=p.read_text(encoding="utf-8-sig").replace('pending={path,body};localStorage.setItem(key(),JSON.stringify(pending));','const intent={path,body};localStorage.setItem(key(),JSON.stringify(intent));pending=intent;');out[str(p)]=s
p=Path("wiki/index.md");out["wiki/index.updated.tmp"]="- [Складская недостача тары](database/retailcase_ni063_warehouse_tare_loss_20261010.md):105 APPLIED; claim physical3/free2, independent writeoff2/free2, reject releases suspicion; goods unchanged.\n"+p.read_text(encoding="utf-8-sig")
p=Path("wiki/log.md");out[str(p)]=p.read_text(encoding="utf-8-sig")+"\n2026-10-10:105 Root warehouse tare loss report/independent decide implemented, current pending claim excluded from usable tare in shared planning/view. Actual non-admin3/free2/COUNT+DAMAGE refusal/sameactor403/independent writeoff2 and reject release/replay/event0. Dedicated UI and manifest, observed SQL58.532ms/43.623/39.215 bounded+PK retained.\n"
p=Path("wiki/requirements/retailcase_delivery_v55/execution/active/ni06_3.md");out[str(p)]=p.read_text(encoding="utf-8-sig")+"\nTicket105: [складская недостача](../../../../database/retailcase_ni063_warehouse_tare_loss_20261010.md), pending claim blocks usable warehouse quantity; separate independent full writeoff/reject with original immutable history. Store/vehicle loss claims and moving damage lineage remain open.\n"
out["wiki/database/retailcase_ni063_warehouse_tare_loss_20261010.md"]="""# NI06.3 — складская недостача тары,105
2026-10-10-105-warehouse-tare-loss APPLIED RABAEV/orcl,26 statements/0 errors plus bounded resolve correction2/0. LOSS/Root/planning/views/guards VALID. New RRL_TARE_LOSS_CLAIM and RRL_TARE_LOSS_DECISION immutable, full decision unique per original claim.

REPORT requires tare_loss_report, current warehouse binding, exact current balance version, positive integer quantity no larger than currently free. It leaves physicalqty unchanged and immediately excludes suspect quantity from availability. Shared held_quantity includes active BOOK plus unresolved loss; BOOK/COUNT/OFFER/ACCEPT/DAMAGE and warehouse damaged WRITE_OFF cannot consume a claimed unit. Pending claim remains part of history, not erased.

DECIDE requires tare_writeoff and another active actor. WRITE_OFF closes full claim and reduces original same-condition warehouse physical balance once. REJECT closes full claim and releases suspect quantity without physical correction. Partial decisions/outside store/vehicle loss claims are outside this slice. One short Root transaction: claim/decision, balance version, journal fact table, mandatory outbox; no goods P/H/events.

[Dedicated UI](../../wiki-raw/wms_admin_ui_reference/tare-loss.html) reads own warehouse catalog/current balance/claims, stores exact operation intent before sending and retains unknown result. API loss-report/loss-decide/warehouses/{ware}/loss-cases; view supports GOOD and DAMAGED source histories, usable planning currently GOOD.

[Author](../../scripts/ni063_loss_case.py) first stopped before REPORT because new zero-line types were absent from Python stock contract; fixed type registry, then [original continuation](../../scripts/ni063_loss_continue.py) PASS, without second fixture count: non-admin REPORT physical3/free2, count0/damage3 refused, same actor403, independent loss physical2/free2/replay, second claim REJECT free restored. Goods events0; own count0 cleanup and user retired. Long SQL58.532/43.623/39.215ms: retain balance/time index, claim unique decision PK and bounds200, NI06.3 owner reviews plan on real growth.

Full NI06.3 remains open: store/vehicle loss and claims, moving damaged custody, repack/packing, independent acceptance.
"""
out["задания на проведения тестов/NI06.3/105_складская_недостача_тары.md"]="""# Qwen — NI06.3,105
Новый собственный warehouse tare count3; bound non-admin REPORT1→physical3/free2. BOOK/OFFER/COUNT/DAMAGE and DAMAGED writeoff cannot spend pending-loss amount.
Same observer DECIDE forbidden even if granted tare_writeoff. Another active controller WRITE_OFF once→physical2/free2, exact replay/no goods event; another operation same claim rejected.
Second claim REJECT releases availability without physical correction. Concurrent REPORT totals cannot exceed free; concurrent decisions have one winner/unique original claim and original outbox only. Failed/stale version leaves no claim/qty/outbox.
Direct mutation/history deletion denied. Exact source and immutable decisions retained. Unknown HTTP result original intent repeat. Maximum queue200, longest actual SQL decision required. No repeat one-time author-case.
"""
# Keep reproducible emitter's latest source files, not a second divergent template.
p=Path("scripts/build105.py");s=p.read_text(encoding="utf-8-sig");at=s.index('print(json.dumps(out,ensure_ascii=True))');s=s[:at]+'''out[str(f/"007_resolution_command.sql")]=Path("db/migrations/2026-10-10_ni063_warehouse_tare_loss/007_resolution_command.sql").read_text(encoding="utf-8-sig")
out[str(f/"apply.sql")]=out[str(f/"apply.sql")].replace("@@006_guards.sql","@@006_guards.sql\\n@@007_resolution_command.sql")
'''+s[at:];out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
