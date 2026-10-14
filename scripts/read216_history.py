import sys
from pathlib import Path
import httpx
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
r=httpx.get("http://127.0.0.1:8088/api/inventory/tare/load-recovery-candidates",params={"load_operation_id":"SMALL216.LOAD:7df96570"},auth=("admin","admin123"),timeout=15)
assert r.status_code==200,(r.status_code,r.text[:1400])
rows=r.json();assert len(rows)==1,rows
assert rows[0]["original_booking_operation_id"]=="DIRECT216.TARE.BOOK:1118"and rows[0]["recovery_operation_id"]=="TARE216.RECOVERY:7df96570"and rows[0]["recovery_book_status"]=="CANCELLED"and rows[0]["load_status"]=="UNLOADED",rows
print("PASS216 scoped API original transfer -> accepted return -> new recovery -> native cancellation history retained after unload/cleanup")

