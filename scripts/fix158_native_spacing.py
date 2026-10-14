import json
from pathlib import Path
p=Path("db/migrations/2026-10-10_ni081_range_apply/006_core.sql");s=p.read_text(encoding="utf-8").replace("v_faceand","v_face and").replace("v_celland","v_cell and")
print(json.dumps({str(p):s}))
