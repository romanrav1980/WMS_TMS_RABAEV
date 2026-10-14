from pathlib import Path
import json
out={}
p=Path("db/migrations/2026-10-10_ni061_onward/001_schema.sql");s=p.read_text(encoding="utf-8")
if "add(FINAL_ADDRESS_SOURCE" not in s:s+="""
begin execute immediate q'[alter table RRL_INTERWARE_ONWARD_BIND add(FINAL_ADDRESS_SOURCE varchar2(30) default 'FROZEN_LOAD' not null check(FINAL_ADDRESS_SOURCE in('FROZEN_LOAD','CURRENT_GUARDED_LEGACY')))]';exception when others then if sqlcode!=-1430 then raise;end if;end;
/
"""
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_onward.py");s=p.read_text(encoding="utf-8")
s=s.replace("reference: str,actor: str) ->","reference: str,actor: str,accept_legacy_address: bool=False) ->",1)
s=s.replace("[receipt_id,reason,reference,actor]","[receipt_id,reason,reference,actor,accept_legacy_address]",1)
old='''                if not address:
                    raise StoreReturnReceiveError("INTERWARE_ONWARD_FINAL_ADDRESS_REQUIRED","Frozen original delivery address required")'''
new='''                address_source="FROZEN_LOAD"
                if not address:
                    if not accept_legacy_address:
                        raise StoreReturnReceiveError("INTERWARE_ONWARD_FINAL_ADDRESS_REQUIRED","Historical load has no frozen address; explicit guarded legacy-address decision required")
                    cur.execute("select ADDR from RRL_SBORKA_PALLETS where ID=:st for update wait 5",st=source_st)
                    address=cur.fetchone()[0]
                    if not address:
                        raise StoreReturnReceiveError("INTERWARE_ONWARD_FINAL_ADDRESS_REQUIRED","Original legacy ST has no delivery address")
                    address_source="CURRENT_GUARDED_LEGACY"'''
assert old in s;s=s.replace(old,new,1)
s=s.replace('"status":"PREPARED","stock_changed":False','"final_address":address,"final_address_source":address_source,"legacy_address_confirmed":address_source=="CURRENT_GUARDED_LEGACY","status":"PREPARED","stock_changed":False',1)
s=s.replace("SOURCE_CELL,FINAL_ADDRESS,ORIGINAL_FULFILLMENT_JSON","SOURCE_CELL,FINAL_ADDRESS,FINAL_ADDRESS_SOURCE,ORIGINAL_FULFILLMENT_JSON",1)
s=s.replace(":version,:cell,:address,:ownership",":version,:cell,:address,:address_source,:ownership",1)
s=s.replace("cell=dock,address=address,ownership=","cell=dock,address=address,address_source=address_source,ownership=",1)
out[str(p)]=s
for rel in ["api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py","api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py"]:
 p=Path(rel);s=p.read_text(encoding="utf-8")
 s=s.replace("reason: str, reference: str, actor: str) ->","reason: str, reference: str, actor: str, accept_legacy_address: bool=False) ->",1)
 s=s.replace(".prepare(operation_id,receipt_id,reason,reference,actor)",".prepare(operation_id,receipt_id,reason,reference,actor,accept_legacy_address)")
 out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py");s=p.read_text(encoding="utf-8")
s=s.replace("class OnwardPlan(PlacementPlan):","class OnwardPlan(PlacementPlan):\n    accept_legacy_address: bool = Field(default=False,strict=True)",1)
s=s.replace("body.reason,body.decision_reference,user.username)","body.reason,body.decision_reference,user.username,body.accept_legacy_address)",1)
out[str(p)]=s
p=Path("db/migrations/2026-10-10_ni061_onward/004_guards.sql");s=p.read_text(encoding="utf-8")
s=s.replace("member.DESTINATION_ADDR=:new.FINAL_ADDRESS","((:new.FINAL_ADDRESS_SOURCE='FROZEN_LOAD'and member.DESTINATION_ADDR=:new.FINAL_ADDRESS)or(:new.FINAL_ADDRESS_SOURCE='CURRENT_GUARDED_LEGACY'and member.DESTINATION_ADDR is null and json_value(:new.RESULT_JSON,'$.legacy_address_confirmed')='true'and exists(select 1 from RRL_SBORKA_PALLETS original where original.ID=p.SOURCE_ST_ID and original.ADDR=:new.FINAL_ADDRESS)))",1)
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
