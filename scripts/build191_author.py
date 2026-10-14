from pathlib import Path
import json
t=Path("scripts/ni042_warehouse_scale_net_case.py").read_text(encoding="utf-8").replace("189","191")
a='  q.execute("select STATUS from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=:p_line",p_line=line);assert q.fetchone()==("PARTIAL",)'
assert a in t
t=t.replace(a,a+'''
  preview_url=base+f"/tasks/{case}/lines/{line}/order-weight-preview"
  response=api.get(preview_url);assert response.status_code==200,(response.status_code,response.text)
  preview=response.json();assert preview["requested_quantity"]=="10"and preview["picked_quantity"]=="9.6"and preview["tolerance_pct"]=="15"and preview["within_tolerance"]and not preview["allows_close"]
  policy_url="http://127.0.0.1:8088/api/finished-goods/skus/"+article+"/receiving-policy"
  response=api.get(policy_url);assert response.status_code==200,(response.status_code,response.text)
  old=response.json();assert old["order_weight_tolerance_pct"]=="15"
  config={"expected_version":old["version"],"marking_required":False,"serialized_weight_boxes":False,"profiles":[],"order_weight_tolerance_pct":"2.00"}
  response=api.put(policy_url,json=config);assert response.status_code==200,(response.status_code,response.text);updated=response.json()
  assert updated["order_weight_tolerance_pct"]=="2.00"
  stale=api.put(policy_url,json=config);assert stale.status_code==409,(stale.status_code,stale.text)
  invalid=api.put(policy_url,json={**config,"expected_version":updated["version"],"order_weight_tolerance_pct":"100.01"});assert invalid.status_code==422
  preview=api.get(preview_url).json();assert not preview["within_tolerance"]and preview["lower_quantity"]=="9.8"
  legacy={k:v for k,v in config.items()if k!="order_weight_tolerance_pct"};legacy["expected_version"]=updated["version"]
  response=api.put(policy_url,json=legacy);assert response.status_code==200,(response.status_code,response.text)
  saved=response.json();assert saved["order_weight_tolerance_pct"]=="2"
  response=api.put(policy_url,json={**legacy,"expected_version":saved["version"],"order_weight_tolerance_pct":"15"});assert response.status_code==200
  preview=api.get(preview_url).json();assert preview["within_tolerance"]and preview["lower_quantity"]=="8.5"and preview["upper_quantity"]=="11.5"
  print("PASS191 SKU default15/exact2/current original order10 picked9.6/preview within15 outside2/optimistic stale409/>100422/old client preserves configured2/no automatic close",flush=True)
''')
print(json.dumps({"scripts/ni042_order_weight_policy_case.py":t},ensure_ascii=True))
