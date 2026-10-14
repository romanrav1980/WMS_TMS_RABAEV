from pathlib import Path
import json
out={}
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
for old,new in [("RRL_STOCK_SHIPPING_CORE","003_shipping.sql"),("RRL_STOCK_EFFECT_CORE","004_effect.sql")]:
 for i,item in enumerate(m["components"]):
  text=(p.parent/item).read_text(encoding="utf-8-sig")
  if ("package "+old.lower()) in text.lower() or ("package body "+old.lower()) in text.lower():
   m["components"][i]="../2026-10-10_ni062_supplier_dispatch/"+new;break
 else:raise RuntimeError("Missing manifest package "+old)
for group,names in {"components":["002_helper.sql"],"startup_scripts":["001_schema.sql"],"additional_scripts":["005_guards.sql"]}.items():
 for name in names:
  item="../2026-10-10_ni062_supplier_dispatch/"+name
  if item not in m[group]:m[group].append(item)
if "RRL_STOCK_SUP_RETURN" not in m["packages"]:m["packages"].append("RRL_STOCK_SUP_RETURN")
out[str(p)]=json.dumps(m,indent=2)+"\n"
p=Path("scripts/build108.py");s=p.read_text(encoding="utf-8-sig");at=s.index("print(json.dumps(out,ensure_ascii=True))")
s=s[:at]+'for name in ["001_schema.sql","002_helper.sql","003_shipping.sql","004_effect.sql","005_guards.sql","apply.sql","rollback.sql"]:\n out[str(f/name)]=(f/name).read_text(encoding="utf-8-sig")\n'+s[at:];out[str(p)]=s
p=Path("wiki/index.md");out["wiki/index.updated.tmp"]="- [Поставщик: прежняя СТ и фактическая погрузка](database/retailcase_ni062_supplier_dispatch_20261010.md):108 APPLIED, exact placed return1/native ST/load/P0H0/replay/departure; supplier receipt distinct.\n"+p.read_text(encoding="utf-8-sig")
for name,line in [
 ("wiki/log.md","2026-10-10:108 reused original PALL_SPLITTER ST preparation/rows and transport assignment/single physical loading. Immutable binding to original placed supplier receipt/UID; blocked source allowed only current exact LOAD_SHIPMENT/dispatch role. Actual1→0 H0/event1/outbox1/replay/departure no second stock PASS. Fixed new typed generic shipping base-UOM propagation; old fallback retained. SQL302.379/269.461/79.190/75.267ms: retain scoped100/PK, NI06.2 owner reviews repeated history plan."),
 ("wiki/requirements/retailcase_delivery_v55/execution/active/ni06_2.md","Ticket108: [возврат поставщику существующей СТ](../../../../database/retailcase_ni062_supplier_dispatch_20261010.md), actual original preparation/assignment/load1/P0H0/replay/departure; supplier receipt/SAP acknowledgement/disposal/marked remain open.")]:
 p=Path(name);out[name]=p.read_text(encoding="utf-8-sig")+"\n"+line+"\n"
out["wiki/database/retailcase_ni062_supplier_dispatch_20261010.md"]="""# NI06.2 — возврат поставщику через прежнюю СТ,108
Migration2026-10-10-108-supplier-return-existing-loading APPLIED RABAEV/orcl. Original apply17/0; guards refinement5/0; base-UOM shipping correction2/0. New private helper and existing shipping/effect packages VALID.
Owner inventory; goods transaction owner existing RRL_STOCK_POSTING_API LOAD_SHIPMENT. Metadata prep uses existing outgoing_pallet_edit fence/PALL_SPLITTER.create_return_task/add_row_2sborka_pallets and canonical replay hash, never changes P/H. SC selects unique current supplier INN and explicit decision. Immutable receipt→ST/source binding prohibits rewriting source ST identity/quantity.

Physical current source must be exact whole placed SUPPLIER receipt, unreserved, same warehouse/unit/location/current quantity/version; applicable marking fails closed in this ordinary slice. Native existing loading pins UID, current QC/vehicle/dock/measurement checks retained. Segregated blocked cell is consumable only by exact authorised actual LOAD_SHIPMENT; direct logical SHIP denied. Existing consume/journal/units/balance remains sole goods engine. Original untyped RETURNS fallback retained.

RRL_STORE_RETURN_SUP_BIND/RETURN_SUP_DISPATCH append-only, root lock closure and transaction gates. Dispatch/outbox retain original receipt/source/batch/supplier; does not assert supplier received/SAP ACK. Supplier cargo cannot enter store receipt. API typed port/warehouse-bound pending100/suppliers200; warehouse page supplier-return.html provides durable original operation retry and links workflow to existing transport workstation, no second trip editor.

## Actual author evidence
Original source RETURN.RECEIVE:f87a0fd042, INTERNAL.RETURN:6b388966d1, warehouse9104, DS-BASE-D10, EA1/H0, placed QRPSdab5c00141. Tag f877bb1524; preparation SUP.PREPARE:f877bb1524; identifier RTN.ST:02103e6d6446e4400d52be370d7dd43b2f936c9a. Native prep/replay/assignment/preview passed. Direct logical shipment denied without effect.
[Original completion](../../scripts/ni062_supplier_dispatch_finish.py) PASS: SUP.LOAD:f877bb1524 current exact physical load→P0/H0, one goods event/immutable dispatch/SAP pending; exact replay and separate SUP.DEPART:f877bb1524 no second stock. Initial new branch missed base-UOM propagation and rolled back fully; fixed before same operation retry/current preview. Actual source quantity consumed intentionally; historical097 current-stock assertion must not be rerun.

Slow SQL302.379/269.461/79.190/75.267ms, cold single calls. Decision: retain source PK/current-warehouse bounds, inspect repeated source-history execution plan at volume; owner NI06.2. No throughput claim. Independent review/marked/multi-place/supplier receipt/disposal remain open.
"""
out["задания на проведения тестов/NI06.2/108_возврат_поставщику.md"]="""# Qwen — NI06.2,108
Use dedicated RABAEV dev fixtures through existing stock core. Do not rerun committed source fixture: its1 was intentionally dispatched.
Verify source receipt SUPPLIER and placed, original SC decision/unique supplier/current warehouse; metadata preparation leaves P/H unchanged, exact retry returns same ST, changed payload conflicts.
Reuse existing assignment and single physical loading; blocked exact source is allowed only actual LOAD_SHIPMENT/dispatch role. Logical SHIP, foreign actor/source/changed quantity/UOM/HARD/required marking denied.
Assert physical load exactly one movement/P0H0/dispatch/outbox; retry no second goods event; departure no second stock. Supplier cargo store receipt must fail. Supplier external receipt is not asserted.
Inspect changed objects VALID and slow SQL; report evidence/limits independently, no full sprint acceptance from author's PASS.
"""
print(json.dumps(out,ensure_ascii=True))
