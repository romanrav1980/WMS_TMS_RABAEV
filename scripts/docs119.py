from pathlib import Path
import json,re
out={}
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
mapping={"../2026-10-10_ni062_disposal/004_root.sql":"../2026-10-10_ni061_receiving/005_root.sql","../2026-10-10_ni062_return_receiving/004_location_acl.sql":"../2026-10-10_ni061_receiving/004_location_acl.sql"}
m["components"]=[mapping.get(x,x) for x in m["components"] if x!="../2026-10-10_ni052_single_load/005_shipping_core.sql"]
for name in ["002_command.sql","003_balance_acl.sql"]:
 item="../2026-10-10_ni061_receiving/"+name
 if item not in m["components"]:m["components"].append(item)
for group,name in [("startup_scripts","001_schema.sql"),("additional_scripts","006_guards.sql")]:
 item="../2026-10-10_ni061_receiving/"+name
 if item not in m[group]:m[group].append(item)
if "RRL_STOCK_INTERWARE_REC" not in m["packages"]:m["packages"].append("RRL_STOCK_INTERWARE_REC")
out[str(p)]=json.dumps(m,indent=2)+"\n"
out["wiki/index.updated.tmp"]="- [Физическая приёмка межскладского груза](database/retailcase_ni061_receiving_20261010.md):119 APPLIED, original unload0/native target receipt3H0/event1/SAP pending1/replay/source0; onward existing task/leg next.\n"+Path("wiki/index.md").read_text(encoding="utf-8-sig")
for name,line in [
 ("wiki/log.md","2026-10-10:119 native INTERWARE_UNLOAD/RECEIVE/current target interwarehouse_receive/immutable sources and blocked receiving buffer. APPLIED17/0 + helperfix2/0, checkpoints430Root/431Balance/432Location. Original118 physical unload349bc1ff57 no goods, same operation receipt3H0/event1/SAPpending1/source0/replay/conflict/second/early/scans/foreign passed. ORA40573 rolled back before successful retry; JSON payload CLOB assigned beforeSQL. UI physical scans/durable retry/current actual stages. Manifest fixes stale duplicate shipping definition after108 and includes current balance ACL; generated-only runtime bundle. SQL48.671/50.372/25.058ms retain plan/source unique/bounded queue/source indexes, inventory/transport owner growing lineage."),
 ("wiki/requirements/retailcase_delivery_v55/execution/active/ni06_1.md","Ticket119: [выгрузка и приёмка](../../../../database/retailcase_ni061_receiving_20261010.md), original118 cargo/sourceST preserved/current target receiver/separate unload0/receipt3H0/native stock/outbox1; existing placement/onward final customer ownership next."),
 ("wiki/requirements/retailcase_delivery_v55/execution/active/ni07_2.md","Ticket119 prerequisite: daily interwarehouse unload/receipt and current unload/receipt backlog added to same-snapshot day board. Pending placement/onward leg are separate; external SAP pending is not final acknowledgment.")]:
 p=Path(name);out[name]=p.read_text(encoding="utf-8-sig")+"\n"+line+"\n"
out["wiki/database/retailcase_ni061_receiving_20261010.md"]="""# NI06.1 — выгрузка и приёмка второго склада,119
2026-10-10-119-native-interwarehouse-unload-receipt APPLIED17/0 + JSON payload helperfix2/0. All helper/Root/balance/location/guardsVALID RABAEV/orcl; checkpoints430Root431Balance432Location.
Existing RRL_STOCK_POSTING_API extended private RRL_STOCK_INTERWARE_REC; original sole RRL_STOCK_BALANCE_CORE. New append-only RRL_INTERWARE_UNLOAD/RECEIPT source plan and event references, unique plan/custody receipt. Original pallet identity/SKU/batch/expiry/first-leg load/originalST retained, no vendor purchase/no second customer fulfillment.
UNLOAD current bound target receiver/interwarehouse_receive scans exact original vehicle/pallet/targetdock; immutable custody fact with no goods effect. RECEIVE requires existing unload, exact original SKU/full BASE qty/barcode/pallet/blocked receiving cell (accept allowed/remains+replenishment blocked), current ordinary marking policy/no existing positive balance. Metadata/root plans sorted source/stock closure/uniqueness, under native policy fence before recheck. Native apply_delta+write_leg+typed receipt+SAP INTERWAREHOUSE_RECEIVED pending same short TX. Existing journal/outbox unchanged. Placement/onward delivery separate next120; nested/marked/partial exception deny until explicit unit/tree flow.
Author scripts/ni061_receiving_case.py followed by ni061_receiving_finish.py PASS349bc1ff57 on original118: early receipt409/wrong vehicle409/unload0/replay/second409/qty2 denial/current foreignWARE403. Initial receive ORA40573 j.to_clob used in SQLVALUES rolled entire goods receipt back; helper now assigns CLOB beforeSQL. Retry identical OP → target9104/QIR349bc1ff57 P3H0/event1/SAP1/source0/history/originalST. Replay unchanged/conflict/second denied; current queue original stages. Own actor retired. Do not rerun fresh fixture on committed plan.
Raw interwarehouse UI now physical unload/receipt scans, source quantity/BASE/vehicle/current stage queue and per-user durable intent; unknown technical result503 stays retryable.
SQL48.671/50.372/25.058ms retain plan/source unique and sourcePK/bounded100 queue, inventory/transport owner checks growing lineage. Manifest removes stale shipping redefinition that followed current108 and explicitly retains new current balance ACL. Source bundle generated only, never applied wholesale.
Full NI06.1 remains open: placement/onward ownership/packing/temperature/marked/nested, discrepancy handling and external acceptance.
"""
out["задания на проведения тестов/NI06.1/119_межскладская_приемка.md"]="""# Qwen — NI06.1,119
Existing ordinary departed118 plan, original single pallet/custody. Target-scoped interwarehouse_receive, active role; scans vehicle/pallet/inbounddock. UNLOAD immutable/root/no goods. Early/second unload/current foreign receiver deny.
RECEIVE exact source full qty/BASE/current barcode, original UID/batch/expiry, blocked receiving buffer accept allowed. No unload/wrong qty/foreign SKU/current marking required/current stock already restored/second receive deny. Native stock delta+event+receipt+SAP message same TX, no fake supplier order or repeated customer fulfillment.
Original source0/target3H0/event1/SAP1/replay, unknown result durable retry. Original119349bc1ff57 already accepted; use continuation not fresh creation. Check task/onward separate, source unchanged, Root locks/current recheck. SQL explicit decision/source/manifest/liveVALID and independent acceptance recorded separately.
"""
p=Path("api/wms_api_server/app/modules/finance/infrastructure/reconciliation_sources.py");s=p.read_text(encoding="utf-8")
if '"interwarehouse_receipts"' not in s:
 s=s.replace("DAILY=[",'DAILY=[\n ("interwarehouse_unloads","select count(*)from RRL_INTERWARE_UNLOAD where WARE_ID=:ware and CREATED_AT>=:day_from and CREATED_AT<:day_to"),\n ("interwarehouse_receipts","select count(*)from RRL_INTERWARE_RECEIPT where WARE_ID=:ware and CREATED_AT>=:day_from and CREATED_AT<:day_to"),')
 s=s.replace("BACKLOG=[",'BACKLOG=[\n ("interwarehouse_unload_pending","select count(*)from RRL_INTERWARE_PLAN p where p.TARGET_WARE_ID=:ware and not exists(select 1 from RRL_INTERWARE_UNLOAD u where u.PLAN_OPERATION_ID=p.OPERATION_ID)"),\n ("interwarehouse_receipt_pending","select count(*)from RRL_INTERWARE_UNLOAD u where u.WARE_ID=:ware and not exists(select 1 from RRL_INTERWARE_RECEIPT r where r.PLAN_OPERATION_ID=u.PLAN_OPERATION_ID)"),')
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
