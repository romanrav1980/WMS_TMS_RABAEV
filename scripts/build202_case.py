from pathlib import Path
import json
s=Path("scripts/ni042_direct_receiving_case.py").read_text(encoding="utf-8").replace("199","202")
s=s.replace('zip(customers,(12,8))','zip(customers,(6,))')
s=s.replace('assert q.fetchone()[0]==20\n  finally','assert q.fetchone()[0]==6\n  finally')
s=s.replace('assert sorted(r[4]for r in rows)==[8,12]','assert sorted(r[4]for r in rows)==[6]')
s=s.replace('assert q.fetchone()==(0,0)\n  q.execute("select sum(PICKED_QTY)','assert q.fetchone()==(14,0)\n  q.execute("select sum(PICKED_QTY)')
s=s.replace('assert q.fetchone()[0]==20\n  print("PASS202','assert q.fetchone()[0]==6\n  print("PASS202')
anchor=' for customer,quantity in zip'
i=s.index(anchor)
s=s[:i]+''' customer_id=700000000+int(tag,16)
 meta("declare x RRL_CUSTOMER%rowtype;begin select *into x from RRL_CUSTOMER where CUSTOMER_ID=:p_template;x.CUSTOMER_ID:=:p_id;x.CUSTOMER_CODE:=:p_code;insert into RRL_CUSTOMER values x;end;",p_template=customers[0],p_id=customer_id,p_code="QSC202"+tag)
 customers=(customer_id,)
 type_body={"pallet_type_code":"SMALL202."+tag,"pallet_type_name":"Own202 final weighing small box","load_unit_class":"CONTAINER","default_volume_m3":"0.001","default_weight_kg":"0.1","final_weight_required":True,"expected_version":0}
 created_type=call("POST","/api/case-pick/pallet-types",type_body);small_type=created_type["pallet_type_id"]
 types=call("GET","/api/case-pick/pallet-types");current_type=next(x for x in types if x["pallet_type_id"]==small_type)
 assert current_type["final_weight_required"]==1 and current_type["type_version"]==1
 # Old client omission preserves the new safety requirement.
 old_client={**type_body,"pallet_type_id":small_type,"expected_version":1};old_client.pop("final_weight_required")
 call("POST","/api/case-pick/pallet-types",old_client)
 conflict=api.post(base+"/api/case-pick/pallet-types",json={**type_body,"pallet_type_id":small_type,"expected_version":1});assert conflict.status_code==409
 try:q.execute("update RRL_PALLET_TYPE set FINAL_WEIGHT_REQUIRED=0 where PALLET_TYPE_ID=:p_id",p_id=small_type);raise AssertionError("Final weight bypassed by raw write")
 except oracledb.DatabaseError as exc:c.rollback();assert exc.args[0].code==20863
 meta("insert into RRL_CUSTOMER_PALLET_TYPE_RULE(CUSTOMER_PALLET_TYPE_RULE_ID,CUSTOMER_ID,PALLET_TYPE_ID,IS_DEFAULT,ACTIVE,CREATED_BY)select nvl(max(CUSTOMER_PALLET_TYPE_RULE_ID),0)+1,:p_customer,:p_type,1,1,'admin'from RRL_CUSTOMER_PALLET_TYPE_RULE",p_customer=customer_id,p_type=small_type)
''' +s[i:]
# Verify CASE uses the original customer carrier-type rule.
s=s.replace('   assert cell==receive;case_types.add(case_type)','   assert cell==receive and case_type==small_type;case_types.add(case_type)')
idx=s.index('  print("PASS202 actual SAP')
end=s.index('\n',idx)
s=s[:idx]+'''  q.execute("select CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:p_case",p_case=case);version=int(q.fetchone()[0])
  call("POST",f"/api/case-pick/tasks/{case}/close-pallet",{"operation_id":"SMALL202.CLOSE:"+tag,"expected_content_version":version,"reason":"Complete current six-unit small box"})
  sid=seq("RRL_SBORKA_PALLETS_SQ");ff=seq("RRL_CUSTOMER_ORDER_FULF_SQ");identifier="SMALL202.ST:"+tag
  meta("insert into RRL_SBORKA_PALLETS(ID,PALLET_UID,ST_NUMBER,WARE_ID,CONDITION,ADDR)values(:p_id,:p_uid,:p_uid,:p_ware,0,'Own202 current small-box shipment')",p_id=sid,p_uid=identifier,p_ware=ware)
  meta("insert into RRL_SBORKA_PALLET_ROWS(ID,PALLET_UID,ARTICUL,EI,QUANTITY)values(RRL_SBORKA_PALLET_ROWS_SQ.nextval,:p_uid,:p_article,'EA',6)",p_uid=identifier,p_article=article)
  meta("insert into RRL_CUSTOMER_ORDER_FULFILLMENT(FULFILLMENT_ID,CUSTOMER_ORDER_ID,LEGACY_SBORKA_PALLET_ID,PALLET_UID,STATUS,FACT_QTY)values(:p_id,:p_order,:p_ship,:p_uid,'PLANNED',0)",p_id=ff,p_order=orders[0],p_ship=sid,p_uid=identifier)
  from app.modules.inventory.infrastructure.case_shipment_binding import bind_case_shipment
  bind_case_shipment(OracleGateway(),int(case),identifier,carrier,version,"admin")
  from app.modules.master_data.infrastructure.quality_weight_policy import QualityWeightPolicy
  from app.modules.master_data.contracts_quality_weight import WeightPolicyInput
  QualityWeightPolicy(OracleGateway()).set(ware,article,WeightPolicyInput(expected_version=0,base_uom="EA",base_weight_kg="0.05",box_weight_kg="0.05"),"admin")
  from app.modules.inventory.infrastructure.outgoing_quality import OutgoingQuality
  quality=OutgoingQuality(OracleGateway());before=quality.status(identifier)
  assert before["control_mode"]=="WEIGHT"and before["required"]and not before["ready"],before
  check={"operation_id":"SMALL202.QC:"+tag,"quality_kind":"WEIGHT","gross_weight":"0.400","wood_weight":"0.100","expected_composition_signature":before["composition_signature"]}
  verified=quality.check(identifier,check,"admin");assert verified["verified"]==1 and verified["ready"],verified
  assert quality.check(identifier,check,"admin")==verified
  after=quality.status(identifier);assert after["ready"]and after["control_mode"]=="WEIGHT"
  q.execute("select TRIAL_WEIGHT,WOOD_WEIGHT from RRL_SBORKA_PALLETS where ID=:p_id",p_id=sid);gross,tare_weight=q.fetchone()
  assert Decimal(str(gross))==Decimal("0.400")and Decimal(str(tare_weight))==Decimal("0.100")
  print("PASS202 own small type/exact Decimal/version conflict/old-client preserves finalflag/direct write20863/warehouse NONE still child WEIGHT/physicalCASE6/net.300/gross.400/tare.100 counted once/current QC/replay/original source14 unaffected",article,small_type,identifier,flush=True)'''+s[end:]
# zero owned test tare assets after books are released.
anchor='  if wave is not None:\n   q.execute("select STATUS from RRL_PICK_WAVE'
before='''  for case_type in case_types:
   available=call("GET",f"/api/inventory/tare/warehouses/{ware}/availability");current=next(x for x in available if x["pallet_type_id"]==case_type)
   call("POST","/api/inventory/tare/count",{"operation_id":"SMALL202.TARE.ZERO:"+str(ware),"owner_ware_id":ware,"pallet_type_id":case_type,"condition":"GOOD","observed_quantity":"0","expected_version":current["balance_version"]or 0,"reason":"Retire own empty software box","decision_reference":"SMALL202.END:"+tag})
'''
assert anchor in s;s=s.replace(anchor,before+anchor)
print(json.dumps({"scripts/ni042_small_final_weight_case.py":s},ensure_ascii=True))
