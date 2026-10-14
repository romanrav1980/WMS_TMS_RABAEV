from pathlib import Path
import json
f={};root="db/migrations/2026-10-14_ni022_stock_floor_type/"
p=Path(root+"001_schema.sql");s=p.read_text(encoding="utf-8")
s=s.replace(" constraint RRL_PAL_FLOOR_WARE_FK foreign key(DECLARED_WARE_ID)references RRL_WARES(ID),\n","")
f[str(p)]=s
p=Path("wiki/database/nicora_ni022_stock_floor_type_20261014.md")
f[str(p)]=p.read_text(encoding="utf-8")+"\n1203: first CREATE rejected before any object change because legacy RRL_WARES.ID has no PK/UK. New table did not exist. Retained FK to pallet/type/Root; warehouse is checked by native scope count/current actor and stored as declared history, no new global WARES constraint/index. This is explicit legacy schema limitation, not an assumed FK.\n"
print(json.dumps(f))
