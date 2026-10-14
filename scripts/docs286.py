from pathlib import Path
import json
out={}
page="wiki/database/nicora_ni081_trip_origin_read_20261011.md"
out[page]="""# Настроенная база в текущей оценке рейса
286 NI08.1. Existing road-leg reader derives origin from current native sourceV4 in the same read snapshot when depot_address is empty. One configured warehouse uses existing address; missing/multiple origins remain WAREHOUSE_DEPOT_UNKNOWN with null driving totals. Explicit dispatcher override remains labelled DISPATCHER_EXPLICIT_ADDRESS, never verified hub. Existing React road panel allows empty field and shows actual used address. No route/quantity write or new solver.
 
Author actual33564 own9807 positive configuration under outer rollback was read as CONFIGURED_WAREHOUSE_REFERENCE; configuration restored. ActualHTTP default request200 UNKNOWN onunsetrealhub. Domain configured directedH→A12km/17.01min=>18; A→H23km/31min, nocentroid substitution. SQLdecision retain original boundedROAD_LEGS_PK281 leading(p m)NL/PK andoriginversionunique. Needownerrealbase/coordinates/windows/driverlaw; no operationaladmission/independentQwen claim.
"""
for path,line in [
("wiki/index.md",f"- [База в текущей оценке рейса]({page.removeprefix('wiki/')}):286 configuredcurrentorigin/same snapshot, missingbase UNKNOWN/null, currentHTTP passed."),
("wiki/log.md","2026-10-11:286 originalroadlegs derivesconfiguredsourceV4 warehouseorigin whenfieldempty, samecursor; absent/multipleoriginUNKNOWN/null notzero. ExistingReactpanel updated/no newpult. Positiveown33564/9807 underrollback, actualHTTP default200UNKNOWN; domaindirectional12/23km18/31min. ExistingboundedNL/cachePK retained. No operationalacceptance/realhub guess."),
("wiki/runbooks/nicora_active_work.md","Latest286 appcurrentroadlegs emptydepot ->nativeV4 configuredwarehouseorigin/same snapshot, missingbaseUNKNOWN/null. Rootserv286 freshstarted; authoractualHTTP200/ownpositiveorigin outerrollback. Architecture6240cycles76/TypeScript+encodingpassed. 285actualversion1 null9807 unchanged. Next sharedstorewindows/driver-gate, externalowneranswers pending."),
("wiki/requirements/nikora_delivery_v55/execution/active/ni08_1.md","11.10.2026:286 Прежняя оценка дорожных плеч берёт текущую базу склада из sourceV4; пустая/неоднозначная база даёт UNKNOWN/null. Native ownpositive rollback, directional configuredcosts и HTTPdefault проверены. Полный допуск/окна/нормы/independent остаются.")
]:out[path]=Path(path).read_text(encoding="utf-8")+"\n"+line+"\n"
out["wiki/index.md"]=out["wiki/index.md"].replace("current native285/app285/","current native285/app286/")
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");j=json.loads(p.read_text(encoding="utf-8"));next(x for x in j["increments"]if x["id"]=="NI08.1").setdefault("implementedSlices",[]).append("286 currenttrip roadleg read configuredwarehouseorigin same snapshot/unknownmissing/explicitoverridehonest/currentHTTP")
out[p.as_posix()]=json.dumps(j,indent=2)+"\n"
root=next(p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md"))
out[(root/"NI08.1"/"286_trip_origin.md").as_posix()]="# Qwen286\nEmptydepot selects single current sourceV4 configuredwarehouseorigin; missing/multiWARE returns UNKNOWN/null, neverzero/centroidrealhub. Explicitoverride honest. Samecursor origin/currentSource/matrix/currentWARE; configurebase mutationstales native approvals. Positiveown33564 underouterrollback, directionalcosts12/23km18/31min and HTTPdefault200UNKNOWN authorpassed. Realhub/driverlaw/windows/currentcoverage external notpassed.\n"
print(json.dumps(out,ensure_ascii=True))
