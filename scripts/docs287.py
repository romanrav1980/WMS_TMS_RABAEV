from pathlib import Path
import json
out={}
page="wiki/database/retailcase_ni081_delivery_windows_20261011.md"
out[page]="""# Окна доставки прежних СТ
287 NI08.1. Native TIME sourceV5 includes existing pallet ZONE_TIME_PLAN_IN/OUT and bounded destination_rules (unique activeRRL_ADDR count, UNLOAD_NORM_MIN, TW_STRICT, coordinates). Current changedwindow/norm invalidates time/route old approvals without rewriting history or physicalfacts. Route source intentionally excludes ARM operations, preventing own regenerate from invalidating its route input; do not restore operations there.
 
Read-only delivery_window_preview uses one transaction/snapshot: current native route source+road pair provenance, original bounded operations query. DRIVE plan start in explicit selectedwallregion, intersection of allmemberwindows for eachorderedaddress, fresh directedprofile leg, wait untilopen, unload norm, lateness from servicefinish vsclose, thenreturn profile. Missingwindow/norm/policy/addressuniqueness/road/previousclock -> UNKNOWN/null, not invented0. Hard/soft latewindow flaggedseparately. This is EARLIEST_DRIVE_WAIT_UNLOAD_WITHOUT_DRIVER_BREAKS, no legal/physical admission. Stopregionnotverified, driverbreaks/additionalstages notincluded.
 
GET /api/transport/preflight/trips/{id}/delivery-windows requires transport_dispatch_edit/currentWARE and explicitUTC/Moscow/Tbilisi region. Existing TransportRouteInput hosts separate TransportDeliveryWindows table witharrival/window/servicefinish/wait/late/reasons; actor/API/trip/zone generation fence. No stock/route/newplanwrite.
 
Author domain20.02min arrival08:20:01.2/open09wait/servicefinish09:30/return10:10:00.6; close09:15→late15, missingwindowUNKNOWN. Actualown33564 currentsourceV5 metadatawindow perturbation outerrollback changeshash andrestores exactly/P20H20. ActualHTTP200 missingrealbase/windows→INSUFFICIENT_EVIDENCE/null. Architecture6270cycles76/TS passed, NativeallVALID. IndependentQwen/browser/fullvalidrealroute notpassed.
 
SQL287 scoped destination source4.093ms5exec/115totalbuffers, directedroad2.65ms10exec/59totalbuffers. Decision transport/Oracle: retain bounded200 destinations/members and existing address/matrixPK joins; no broadindex/cache. Realhub/country/driverlaw/SAP+gov/hardware remain externalacceptance.
"""
for path,line in [
("wiki/index.md",f"- [Окна доставки прежних СТ]({page.removeprefix('wiki/')}):287 sourceV5 existingwindows/norms/earliestcurrentroute/table, missingdataUNKNOWN; no admissionclaim."),
("wiki/index.md","- [Проект окон доставки](database/retailcase_ni081_delivery_windows_design_20261011.md):287 originalwindow boundaries/current source invalidation."),
("wiki/log.md","2026-10-11:287 nativeTIMEsourceV5 addsoriginalSTwindows+boundeduniquedestinationrules/norms/coords; routeoperationexclusionretained. Same-snapshot readonly deliveryestimate DRIVE+directedroad+windowintersection/wait/unload/return; hard-softlate/missingUNKNOWN. ExistingReactroutepanel table/explicitregion/generationfence. Actualown33564windowhashmutation outerrollback/P20H20 and HTTPmissingrealdataUNKNOWN; domainfit/late/missing authorpassed. SQL4.093ms5/115buf +2.65ms10/59buf keepexistingbounds/PK. NativeVALID/architecture627/TS pass. No driverbreak/legal/physical/independentclaim."),
("wiki/runbooks/retailcase_active_work.md","Latest287 Native TIME sourceV5 includes originalZONE_TIME_PLAN_IN/OUT/destinationrulescount/norm/strict/coords; RouteSource intentionally removesoperations toavoidself-invalidation. App287 currentwindowpreview/table/explicitregion/samecursorroad+originalops. serv286 reloaded currentHTTP200unknown. Own33564windowtemporarymutationrollbackexactrestore/P20H20. SQLbounded4.093/2.65ms keepexistingPK/bounds. Next shared driver-rest/warehouse timing admission, actualcountry/basegov config pending. Oldcases280version3/285version4 historical, don'trerunexpectoldversion."),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni08_1.md","11.10.2026:287 SourceV5 включает исходные окна доставки СТ/норматив разгрузки/строгость/координаты. Есть текущая оценка прибытия/ожидания/разгрузки/возврата и таблица диспетчера, поздние окна отмечены; пропуски UNKNOWN. Authorownrollback/hash/HTTP/domainpassed. Режим водителя, реальная база/окна и независимый допуск остаются.")
]:out[path]=out.get(path,Path(path).read_text(encoding="utf-8"))+"\n"+line+"\n"
out["wiki/index.md"]=out["wiki/index.md"].replace("current native285/app286/","current native287/app287/")
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");j=json.loads(p.read_text(encoding="utf-8"));next(x for x in j["increments"]if x["id"]=="NI08.1").setdefault("implementedSlices",[]).append("287 sourceV5 originalSTdeliverywindows/destinationnorms/strict/coords; same-snapshot earliestroad-wait-unload-return table, hard-softlate/missingUNKNOWN")
out[p.as_posix()]=json.dumps(j,indent=2)+"\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");j=json.loads(p.read_text(encoding="utf-8"));j["additional_scripts"].append("../2026-10-11_ni081_delivery_windows/001_body.sql");out[p.as_posix()]=json.dumps(j,indent=2)+"\n"
root=next(p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md"))
out[(root/"NI08.1"/"287_delivery_windows.md").as_posix()]="# Qwen287\nNativecurrentSourceV5 originalallmemberwindows/addressnormpolicy/coordinate provenance. Hashchangeswindow/norm preservehistory. RouteSource removesoperationsintentionally. Samecursor originalops/read source/road; windowsintersect, directedtime/wait/unload/late+return, missingfieldsUNKNOWN/null. DRIVERbreaks/returnsprocessing/stopzonesnotverified -> no admission. Domainfit09:30/return10:10:00.6, late15, missingUNKNOWN authorpassed; ownwindowmutationouterrollback restoreshash/P20H20 and actualHTTPunknownpassed. Browser/realallvalidroute/independentacceptance pending.\n"
out["db/migrations/2026-10-11_ni081_delivery_windows/002_ledger.sql"]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-287-delivery-windows-source-v5'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Existing ST delivery windows and destination norms sourceV5',sysdate,user,'db/migrations/2026-10-11_ni081_delivery_windows/001_body.sql','db/migrations/2026-10-11_ni081_delivery_windows/rollback.sql','APPLIED','Bound200 originalwindows/addressunique-norm-strict-geo; currenthash changes/ownrollbackrestore. Earliestreadonly estimate/HTTPunknown no driver/physicalclaim; SQL4.093ms/2.65ms boundedkeys retained.');
commit;
"""
print(json.dumps(out,ensure_ascii=True))
