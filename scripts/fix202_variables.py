from pathlib import Path
import re,json
p=Path("db/migrations/2026-10-11_ni042_small_final_weight/002_api.sql");s=p.read_text(encoding="utf-8")
s=re.sub(r"(?<!')\b(id|code|volume|weight|width_mm|height_mm|max_clients|active|required)\b(?!')",lambda m:"v_"+m[0],s)
print(json.dumps({str(p):s,"db/migrations/2026-10-11_ni042_small_final_weight/006_recompile.sql":"@@002_recompile_api.sql\nalter package RRL_STOCK_PALLET_QC_CMD compile body;\nalter package RRL_STOCK_TARE_CMD compile body;\nalter package RRL_STOCK_TARE_RESOLVE compile body;\nalter package RRL_STOCK_TARE_BOOK_CMD compile body;\n","db/migrations/2026-10-11_ni042_small_final_weight/002_recompile_api.sql":s[:s.index("create context ")]},ensure_ascii=True))
