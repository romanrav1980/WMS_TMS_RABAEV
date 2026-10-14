from pathlib import Path
import json
p=Path('wiki/requirements/nikora_delivery_v55/implementation_plan.json');b=json.loads(p.read_text(encoding='utf-8-sig'))
for i in b['increments']:
 if i['id']=='NI05.1':
  i['historicalPendingSlices']=i.pop('pendingSlices',[])
  i['remainingDeliveryWork']='Native QC policy/exemption/audit/label guard and store/warehouse selectors implemented. C0029 real store profile/replay/56 windows passed. Independent marking/weight/equipment acceptance remains separate.'
 if i['id']=='NI08.1':
  i['changeRequired']='Native store/fleet/weekly route installed and verified; C0033 final metadata UI delivered K0038. Remaining code: C0034 night Gantt/mobile/overlay.'
  i['remainingDeliveryWork']='C0034 existing Gantt 00-24, midnight clipping, responsive card/overlay and removal of duplicated route panel; then common quality gate. External road/legal/provider acceptance separate.'
b['currentWork']['claudeQueue']=['C0034 night Gantt/mobile/overlay and one route panel']
p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=Path('wiki/database/nicora_store_access_dimensions_20261014.md');s=p.read_text(encoding='utf-8');s=s.replace('Prepared 14.10.2026, not applied by delegated agent.','Installed by root 14.10.2026 in RABAEV/orcl; native scenarios and focused independent source review passed.');s=s.replace('Native acceptance waits for root apply; scripts/store_access_native_case.py prepared with isolated retained TEST metadata and no stock changes.','scripts/store_access_native_case.py passed on isolated retained TEST metadata, without changing stock. Full physical/pilot acceptance is separate.');p.write_text(s,encoding='utf-8')
p=Path('wiki/database/nicora_vehicle_outer_dimensions_20261014.md');s=p.read_text(encoding='utf-8');s=s.replace('Prepared 14.10.2026, **not applied**.','Installed by root 14.10.2026 in RABAEV/orcl; native version/replay/bounds cases passed.');s=s.replace('Native compilation/acceptance awaits root application.','Native compilation and targeted fixture passed; see applied result below.');p.write_text(s,encoding='utf-8')
