from pathlib import Path
import json
d=Path("db/migrations/2026-10-12_ni061_nested_receiving");out={}
def put(n,s):out[(d/n).as_posix()]=s
put("010_ledger.sql","""merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-314-nested-interwarehouse-receive' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'First-leg nested one-stock-leaf cargo receipt keeps physical HU identities and appends new links with existing quantity and unit kernels; old archive preserved',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
""")
files=["001_columns.sql","002_source.sql","003_receive_core.sql","004_plan_guard.sql","005_receiving.sql","006_container_guard.sql","007_link_guard.sql","008_departure_guard.sql","009_recompile.sql","010_ledger.sql"]
put("apply.sql","".join("@@"+f+"\n"for f in files))
put("rollback.sql","""declare n number;begin
 select count(*)into n from RRL_INTERWARE_PLAN where SOURCE_HU_JSON is not null;
 if n!=0 then raise_application_error(-20899,'NESTED_PLAN_HISTORY_REQUIRES_FORWARD_RECOVERY');end if;
end;
/
@@000_before_rrl_stock_interware_rec.sql
@@000_before_rrl_interware_plan_guard.sql
@@000_before_rrl_hu_container_guard.sql
@@000_before_rrl_hu_link_write_guard.sql
@@000_before_rrl_hu_departure_guard.sql
drop package RRL_IW_HU_REC_CORE;
drop package RRL_IW_HU_SOURCE;
@@009_recompile.sql
""")
put("verify.sql","select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME in('RRL_IW_HU_SOURCE','RRL_IW_HU_REC_CORE','RRL_STOCK_INTERWARE_REC');\nselect OPERATION_ID,ROOT_UID,SOURCE_PLACE_UID from RRL_INTERWARE_PLAN where SOURCE_HU_JSON is not null;\n")
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"));put("000_before_manifest.json",p.read_text(encoding="utf-8"))
m["packages"]+=["RRL_IW_HU_SOURCE","RRL_IW_HU_REC_CORE"]
m["components"]+=["../2026-10-12_ni061_nested_receiving/002_source.sql","../2026-10-12_ni061_nested_receiving/003_receive_core.sql"]
m["additional_scripts"]+=["../2026-10-12_ni061_nested_receiving/"+f for f in files[1:9]]
m["startup_scripts"].append("../2026-10-12_ni061_nested_receiving/001_columns.sql")
m["required_columns"].setdefault("RRL_INTERWARE_PLAN",[]).extend(["SOURCE_PLACE_UID","SOURCE_HU_JSON"])
out[p.as_posix()]=json.dumps(m,indent=2)+"\n"
page="wiki/database/retailcase_ni061_nested_receiving_20261012.md"
out[page]="""# Приёмка физической матрёшки между складами
314 APPLIED в dev RABAEV/orcl, первый bounded slice один STOCK leaf внутри CONTAINER-only дерева200nodes/depth legacy16; одно исходное СТ и первое межскладское плечо. Multi-hop guard сохранён: source315 onward→третий склад был отклонён INTERWARE_MULTI_HOP_EXPLICIT_LINEAGE_REQUIRED; он не снят. Для actual314 использован новый firstleg SAPfixture316.

Schema: RRL_INTERWARE_PLAN nullable SOURCE_PLACE_UID и SOURCE_HU_JSON. ROOT_UID сохраняет товарный лист для прежних stock/unit/receipt/ownership механизмов; SOURCE_PLACE_UID отдельно обозначает физическое верхнее место. SOURCE_COMPOSITION_JSON остаётся точным исходным архивом load. Immutable header guard сверяет stockleaf/frozen load/currentepochs/зарезервированные unique newlink IDs. Старые flatplans используют NULL новых полей.

RRL_IW_HU_SOURCE предоставляет bounded readonlystock/sourcecontext и guarded metadata captureCFG6/current source dispatcher; context включает контейнеры и старые closed links, versions и новые IDs. Retained HU tare-book custody пока явно блокируется: другой owner должен провести её законный межскладской переход. Новый private RRL_IW_HU_REC_CORE только восстанавливает metadata/links, quantitywriter тот же Root/REC/BALANCE/UNIT. Whole receipt required; partial nested не заявлен поддержанным.

У фактической приёмки скан верхнего HU обязателен. Stockleaf barcode вместоверхнего HU отказан. Existing receipt3 updates SAMEphysicalunits/codes and stockleaf once, затем те же контейнеры получают receivingcell/nextversion и новые links. Старые source load/history/deactivated links сохраняются. Guards разрешают изменения только в native IN_FLIGHT exactsource/container/link plan с ordered row/HU anchors; прямое metadata изменение не легализовано. SAP/regulatory aggregates не подменяют warehouse hierarchy; externalACKfalse.

Actualsource316: ARTMAS/SUPPLY/SAPbirth3/6codes, original autoPUT/pick/ST, firstlegTOP→BOX→stock/LOAD/DEPART, guardedplan/sourcecapture; actual314 UNLOAD zeroquantity + RECEIPT3 by2aggregation scans. SamephysicalTOP/BOX IDs,2newlinks/currentWAREreceiving/P3H0/3oldunits6codes. Native late rollback removesstock/newlinks/containerlocation/receipt; exactHTTPretry stable. Protected20/20. tmp/context316.json and tmp/context314_received.json. НЕ повторять factory316/nativeinitial314.

Whole-HU placement/task/custody/onward continuation ещё не установлены этим314: текущее дерево в receivingquarantine, товар не принят магазином. Source315 remainsdeparted towardcustomer and cancomplete existingSTORE path; emptytestthirdwarehouse metadata hasno stock/sourceplan. Do not pretend itwasreceived.

Nativeobjects allVALID afterDDL/recompile/currentbody install. Runtime manifest/includes SQL represented. Rollback refuses retainednestedhistory; forward recovery needed ifphysicalreceipt exists. No DBcopy/new schema/instance.

Next: existing oneHU task placement, physical-place custody release, secondleg sameHU; multiST and multiSKU/partial nested, independenthardware/realERP/gov remain.
"""
p=Path("wiki/index.md");out[p.as_posix()]="- [Межскладская приёмка матрёшки](database/retailcase_ni061_nested_receiving_20261012.md):314 actual firstleg316/sameTOP-BOX/3oldunits6codes/2newlinks/rollback-replay/P3; wholeHU placement next.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");out[p.as_posix()]=p.read_text(encoding="utf-8")+"\n- 12.10.2026 314 installed/actual nested receipt: newnullable sourceplace/contextcolumns, source capture/private container recovery, guarded oldhandlers. Source316SAPfirstleg TOP/BOX/leaf3 -> actual314 P3H0/sameids/old6codes/newlinks2/historypreserved/late rollback/replay/protected20/20. Multi-hop315blockedguard retained. Placement/custody wholeHU continuation pending, no falsecustomercredit.\n"
p=Path("wiki/runbooks/retailcase_active_work.md");out[p.as_posix()]=p.read_text(encoding="utf-8")+"\nLatest314 installed source/REC/guards/columns, actual source316firstleg nested received: tmp/context314_received P3H0 inIR314/same TOP IH316+BOX IB316/newlinks2/old3units6codes. DO NOT rerun source316 orcase314 initialchecks. Source315 departedB→customer/notreceivedC; multi-hop guard rejected source314_plan, emptyCmetadata noP. NativeallVALID/serv314 currentAPIplan. Next317 existing oneHU task insertion/callback/guard plus physical-place custody318. ContextSource315 canfinishSTOREsame312 path, no warehouse3 workaround.\n"
root=next(Path(".").glob("*/NI08.1/178_container_cell_index.md")).parent.parent
out[(root/"NI06.1/314_nested_receiving.md").as_posix()]="# Qwen314\nRead wiki/context314_received. Source316 received3 already: savedexactHTTP body repeat only, no factories/nativeinitialrerun. Freshfirstleg oneSTOCK underTOP/BOX: actualfrozenarchive/currentcontainer epochs/closedsourceLinks/newuniqueIDs/oldunitfingerprint; partial/multiST/multiSKU/crossheldtare/source acceptedbystore denied. Stockleafbarcode cannot replaceTOPscan. Latefail aftercontainer/link insert rollbackP/units/HUstate/newlinks/receipt/outbox; concurrent sameRoot commands one winner. Oldhistory untouched, quantityonlyleaf. Multi-hop guard retained315; do notdisableit. Placement/custody/secondleg stillpending317318.\n"
p=Path("scripts/build314_source.py");t=p.read_text(encoding="utf-8").replace("links.put(i,x)","links.put(i,x,true)");out[p.as_posix()]=t
print(json.dumps(out))
