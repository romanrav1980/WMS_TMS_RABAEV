from pathlib import Path
import json
s=Path("scripts/continue230_to_store.py").read_text(encoding="utf-8").replace("context230.json","context243.json").replace("IW230","IW243").replace("QI230","QI243").replace("Own230","Own243").replace("READY230","READY243")
s+='''\nhistory=api("GET","/api/inventory/interwarehouse/plans/"+ctx["plan"]+"/decisions")
incident=next(x for x in history["decisions"]if x["incident_kind"]=="MISSING_PALLET")
assert incident["followup_receipt_operation_id"]=="IW243.RECEIVE:"+tag,incident
queue=api("GET",f"/api/inventory/interwarehouse/warehouses/{ctx['target_ware']}?include_completed=true")
row=next(x for x in queue if x["operation_id"]==ctx["plan"])
assert row["incident_kind"]=="MISSING_PALLET"and row["incident_followup_receipt_operation_id"]=="IW243.RECEIVE:"+tag,row
print("PASS243 original later full receipt shown beside retained incident/current routed ordinary task-QC-load-depart/same3units6codes/no missing-stock deduction or investigation closure fiction")
'''
print(json.dumps({"scripts/continue243.py":s},ensure_ascii=True))
