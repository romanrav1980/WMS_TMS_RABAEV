from pathlib import Path
import json
p="scripts/case1086_two_top_wait.py";s=Path(p).read_text(encoding="utf-8")
old='"reason":"Retained standalone CASE packed into existing empty outer"}'
assert old in s
s=s.replace(old,'"retained_tare_booking_operation_id":"TARE987.BOOK:"+tag+":1131",'+old,1)
s=s.replace(',"HU1086.ATTACH",body)',',"HU1086.ATTACH.RETAINED",body)',1)
print(json.dumps({p:s},ensure_ascii=True))
