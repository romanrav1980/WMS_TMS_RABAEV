from pathlib import Path
import json
p=Path("api/wms_api_server/app/modules/finance/infrastructure/shipping_register.py");s=p.read_text(encoding="utf-8")
start=s.index('        cur.execute("""with candidate_ids')
body=s[start:]
body="\n".join(line[4:] if line.startswith("    ") else line for line in body.splitlines())+"\n"
prefix=s[:start]+'        return read_snapshot(cur,ware,day,after,limit)\n\ndef read_snapshot(cur: Any,ware: int,day: date,after: int,limit: int) -> dict:\n'
print(json.dumps({str(p):prefix+body},ensure_ascii=True))
