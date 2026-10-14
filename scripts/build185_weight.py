from pathlib import Path
import json,hashlib
f=Path("db/migrations/2026-10-11_ni051_physical_box_mass");s=(f/"000_before_weight.sql").read_text(encoding="utf-8")
helper=""" procedure physical_mass(p_uid varchar2,p_quantity number,p_mass out number,p_lightest out number)is
  n number;bad number;qty number;
 begin
  if p_uid is null then raise_application_error(-20887,'QUALITY_WEIGHT_PHYSICAL_UID_REQUIRED');end if;
  select count(*),nvl(sum(BASE_QTY),0),nvl(sum(GROSS_WEIGHT_KG),0),min(GROSS_WEIGHT_KG),
   nvl(sum(case when BASE_QTY is null or BASE_QTY<=0 or BASE_UOM is null or BASE_UOM!='KG'
    or GROSS_WEIGHT_KG is null or GROSS_WEIGHT_KG<BASE_QTY or MEASUREMENT_REFERENCE is null or WEIGHT_LABEL_SCAN is null then 1 else 0 end),0)
   into n,qty,p_mass,p_lightest,bad from(select BASE_QTY,BASE_UOM,GROSS_WEIGHT_KG,MEASUREMENT_REFERENCE,WEIGHT_LABEL_SCAN
    from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_uid and STOCK_STATUS!='ISSUED'and rownum<=10001);
  if n>10000 then raise_application_error(-20881,'QUALITY_WEIGHT_PHYSICAL_UNIT_BOUND_10000');end if;
  if n=0 or bad>0 or qty!=p_quantity then raise_application_error(-20887,'QUALITY_WEIGHT_ACTUAL_BOX_MASS_COMPOSITION_REQUIRED');end if;
 end;
"""
needle="create or replace package body RRL_STOCK_QC_WEIGHT as\n";assert s.count(needle)==1;s=s.replace(needle,needle+helper)
s=s.replace("v_policy_uom varchar2(20);v_qty number;v_count number:=0;","v_policy_uom varchar2(20);v_qty number;v_count number:=0;v_physical_mass number;v_lightest number;")
a="   begin\n    select QC_BASE_WEIGHT_KG"
assert s.count(a)==1
s=s.replace(a,"""   if RRL_WEIGHT_BOX_CAPACITY.enabled(v_article)=1 then
    if l.get_string('base_uom')is null or l.get_string('base_uom')!='KG'then raise_application_error(-20887,'QUALITY_WEIGHT_PHYSICAL_KG_REQUIRED');end if;
    physical_mass(l.get_string('uid'),v_qty,v_physical_mass,v_lightest);
    p_expected:=p_expected+v_physical_mass;v_count:=v_count+1;
    p_tolerance:=case when p_tolerance is null then v_lightest/2 else least(p_tolerance,v_lightest/2)end;
    continue;
   end if;
"""+a)
out={str(f/"001_weight_contract.sql"):s,str(f/"001_weight_body.sql"):s[s.index("create or replace package body"):],
str(f/"apply.sql"):"-- MIGRATION_ID:2026-10-11-185-actual-box-quality-mass\n@@001_weight_body.sql\n@@../2026-10-08_stock_posting_core/014b_recompile.sql\n",
str(f/"rollback.sql"):"@@000_before_weight.sql\n@@../2026-10-08_stock_posting_core/014b_recompile.sql\n",
str(f/"verify.sql"):"select object_name,object_type,status from user_objects where object_name='RRL_STOCK_QC_WEIGHT';\nselect name,line,text from user_errors where name='RRL_STOCK_QC_WEIGHT';\n"}
out[str(f/"checkpoint.json")]=json.dumps({"migration_id":"2026-10-11-185-actual-box-quality-mass","sha256":{p:hashlib.sha256(v.encode()).hexdigest()for p,v in out.items()},"before_sha256":hashlib.sha256((f/"000_before_weight.sql").read_bytes()).hexdigest(),"recovery":"fresh native weight calculator and paired rollback; no DB copy"},indent=2)
print(json.dumps(out,ensure_ascii=True))
