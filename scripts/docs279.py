from pathlib import Path
import json
out={}
out["wiki/database/retailcase_ni081_road_duration_20261011.md"]="""# Происхождение длительности прежней дорожной матрицы
279 NI08.1. Existing routing OsrmProvider/ValhallaProvider now build_cost_matrix returns bothdistance andproviderduration. Legacy DistanceMatrixService uses realreturnedprofile time instead of distance/50; Haversine has no roadtime and explicitly uses SPEED_50_ESTIMATE. Additive DURATION_BASIS default SPEED_50_ESTIMATE labels all oldcache rows honestly; ROAD_PROFILE_ESTIMATE onlynew decoded providerresponses. These are planning profiles, not observed traffic/driverlaw/truckadmission.

OSRM official table contract: https://project-osrm.org/docs/v5.24.0/api/#table-service — seconds/metres, nullunreachable, fallback_speed estimation. Decoder rejects nonOk/null/nonfinite/negative/shape/fallback_speed_cells, preservesdirectional asymmetry,ceil minutes to0.01 (no shorter rounding). Valhalla requires actualnumeric distance/time instead of previous null->0. Bound200points beforeprovider request. Existing auto fallback remainsHaversine, storedbasisexplicitestimated; explicit providerfailure raises. No livepublicprovider configured.

Puredecoder in transport/domain/road_matrix, existingproviders remainadapters. MERGE rowconstruction extracted through transport/public into infrastructure/distance_matrix_rows; rebuild shrunk andarchitecture baseline tightened, no extra debt/cycle. Sameexistingdistancecache PK, no newmatrixregistry. ExistingVRP currentlyconsumesdistance; full duration-window admission notclaimed, nextwire boundedroadlegs.

AuthormockOSRM10km601s→10.02min,12km1201s→20.02min; null/NoTable/fallbackspeed refusal. ExistingOracle MERGE onown temporary QA279 pairrecords records ROAD_PROFILE_ESTIMATE, wholeouterrollback noresidue. ColumnNOTNULL/defaultverified. BothlocalOSRM/Valhalla unavailable; no realroute claim. SQLMERGE20.989ms/2/464buffers cold; decisionownertransport/Oracle keepexistingpairPK/targetedMERGE, no speculative index/cache/timeoutincrease. Independentprovider/realroad/capacity case remainsQwen. Nativeqtywriter unchanged.

Migration2026-10-11_ni081_road_duration/001_schema.sql mirrored in currentmanifest startup; safe rollback removesonlyclassificationcolumn nothistoricaldistance orquantity. Existingcached speedtimes remainestimates until explicitrebuild; noautomaticbulkcache refresh.
"""
for path,line in [
("wiki/index.md","- [Время дорожной матрицы](database/retailcase_ni081_road_duration_20261011.md):279 providerduration вместо50км/ч, nullнеzero, явный ROAD_PROFILE/SPEED basis; localroadproviders unavailable."),
("wiki/log.md","2026-10-11:279 existingOSRM/Valhalla buildcost distance+duration; oldDistanceMatrix rebuildusesproviderdurations, Haversine SPEED50 explicitly. AdditivebasisdefaultoldrowsSPEED50; strict boundeddecoder/null-fallback-nozero/ceil0.01/directional times. Mockcontract+actualownpair OracleMERGE outerrollback/noresidue/columnverified/providerslocalunavailable. MERGE20.989ms2/464buffers retainpairPK; rowconstruction extractedexistingrebuild shrank/baseline tightened/613cycles0debt76. OfficialOSRMdocs source, no realroad/traffic/legalclaim."),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni08_1.md","11.10.2026:279 Прежняя дорожная матрица сохраняет время из OSRM/Valhalla и явное происхождение. Старые записи/расчёт50кмч помечены SPEED_50_ESTIMATE, неизвестный маршрут не даёт нулевое время. Реальные localproviders недоступны; авторский mock+Oracle rollback не заменяет realrouting. Подключение к общему допуску/окнам остаётся."),
("wiki/runbooks/retailcase_active_work.md","Latest279 app613/nativebasiscolumn on RRL_ADDR_DISTANCE_MATRIX NOTNULL/default SPEED_50_ESTIMATE; providersreturn roadprofileduration whenavailable, localOSRM/Valhalla bothfalse. No matrixbulkrefresh orrealroadclaim. OwnQA279 temporarypairs fullyrollback; noST/stock. ExistingVRPdistance stillused; nextwire readonlytriproadleg provenance/unknowns/currentorder.")
]:out[path]=Path(path).read_text(encoding="utf-8")+"\n"+line+"\n"
out["wiki/index.md"]=out["wiki/index.md"].replace("current native276/app278/","current native279/app279/")
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");j=json.loads(p.read_text(encoding="utf-8"));j["startup_scripts"].append("../2026-10-11_ni081_road_duration/001_schema.sql");out[str(p)]=json.dumps(j,indent=2)+"\n"
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");j=json.loads(p.read_text(encoding="utf-8"))
next(x for x in j["increments"]if x["id"]=="NI08.1").setdefault("implementedSlices",[]).append("279 existingroadmatrix providerdurations/basisclassification/strict unknownroute nozero/boundeddecoder andoldwriterreuse")
out[str(p)]=json.dumps(j,indent=2)+"\n"
root=next(p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md"))
out[str(root/"NI08.1"/"279_road_duration.md")]="# Qwen279\nOSRM seconds/metres both annotations;601s=>10.02min, directionalreturn1201s=>20.02. Null/error/fallbackspeed/nonfinite/ragged nozero route. Valhalla actualtime/never null->0. Explicitprovider failure raises; autoHaversine basisSPEED50. Oldcachedsource=osrm stillSPEED50 until explicitrebuild, notrealprofiletime. ExistingOraclecache pairPK/MERGE basis/rollback/noqty. Provider n<=200; independentrealprovider/traffic andduration-window solver binding pending. Author mocks+Oracle temporarypairrollback only; localprovidersfalse.\n"
out["db/migrations/2026-10-11_ni081_road_duration/002_ledger.sql"]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-279-road-duration-basis'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Existing routing matrix duration provenance',sysdate,user,
'db/migrations/2026-10-11_ni081_road_duration/001_schema.sql','db/migrations/2026-10-11_ni081_road_duration/rollback.sql','APPLIED',
'Oldrows SPEED50 default; newOSRM/Valhalla actualprofiledurations; null/fallback refused, no qty. Mockdecoder+ownOracleMERGE20.989ms2/464buf rollback; localproviders unavailable, no realroad/legalclaim.');
commit;
"""
print(json.dumps(out,ensure_ascii=True))
