import httpx
client=httpx.Client(auth=("admin","admin123"),timeout=25)
base="http://127.0.0.1:8088/api/delivery/store-receipts"
tag="bea258a7dd";case="STORE.RECEIPT:"+tag
def get(path):
 response=client.get(base+path);assert response.status_code==200,(response.status_code,response.text[:1000]);return response.json()
listed=get("/cases?store_address=STORE.QA:"+tag+"&limit=1")
assert len(listed["items"])==1 and listed["items"][0]["case_id"]==case
detail=get("/cases/"+case)
assert detail["lines"][0]["accepted_base_qty"]=="2" and detail["lines"][0]["missing_base_qty"]=="1"
assert detail["lines"][0]["reported_extra_base_qty"]=="1" and len(detail["obligations"])==2
assert all(row["status"]=="OPEN" and row["base_qty"]=="1" for row in detail["obligations"])
assert not detail["return_approved"] and not detail["warehouse_stock_restored"]
assert get("/cases?store_address=STORE.QA:"+tag+"&after="+case)["items"]==[]
print("PASS086 logistics real HTTP dossier/exact decimal strings/bounded cursor/original source/open obligations/no fake return authority")
