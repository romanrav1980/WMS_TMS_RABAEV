import httpx
client=httpx.Client(auth=("admin","admin123"),timeout=30)
response=client.get("http://127.0.0.1:8088/api/delivery/store-return-custody/store",params={"store_address":"STORE.QA:bea258a7dd","task_id":1})
assert response.status_code==200,(response.status_code,response.text[:400])
assert response.json()==[]
print("PASS095 bounded trip-scoped queue route/current receiver authorization")
