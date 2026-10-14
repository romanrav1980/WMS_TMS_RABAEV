from pathlib import Path
import json
out={}
p=Path('api/wms_api_server/app/services/transport_service.py');s=p.read_text(encoding='utf-8-sig')
s=s.replace('where = "WHERE BLOCKED = 0" if active_only else ""', 'where = "WHERE NVL(BLOCKED,0)=0 AND NVL(DELETED,0)=0" if active_only else ""')
s=s.replace('PALLETS, GIDROBORT, BLOCKED\n                  FROM RABAEV.RRL_TR_VEHICLE', 'PALLETS, GIDROBORT, BLOCKED, MAX_WEIGHT_KG, DELETED\n                  FROM RABAEV.RRL_TR_VEHICLE')
s=s.replace('max_pallets=int(v.get("PALLETS") or 20),','max_pallets=int(v.get("PALLETS") or 0),').replace('max_tons=float(v.get("MAX_TONS") or v.get("MAX_VEHICLE_TONS") or 20),','max_tons=float(v.get("MAX_WEIGHT_KG") or 0)/1000,')
s=s.replace('            for v in raw_vehicles\n        ]', '            for v in raw_vehicles if float(v.get("PALLETS")or0)>0 and float(v.get("MAX_WEIGHT_KG")or0)>0\n        ]',1).replace('or0','or 0')
s=s.replace('detail="Нет активных ТС"', 'detail="Нет действующих ТС с заданной паллетной и весовой вместимостью"')
out[str(p)]=s
p=Path('db/migrations/2026-10-10_ni081_transport_plan/002_rules.sql');s=p.read_text(encoding='utf-8-sig')
needle=" procedure assert_actor(p_actor varchar2,p_ware number)is n number;begin"
s=s.replace(needle,needle+"""
  select count(*)into n from RRL_WARES where ID=p_ware;
  if n!=1 then raise_application_error(-20886,'PLAN_CURRENT_WARE_REQUIRED');end if;""")
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
