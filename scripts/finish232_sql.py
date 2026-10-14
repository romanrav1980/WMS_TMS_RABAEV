from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni053_final_custody");out={}
p=f/"002_command.sql";s=p.read_text(encoding="utf-8").replace("EXTRA_BASE_QTY!=0","REPORTED_EXTRA_BASE_QTY!=0")
s=s.replace("or l.ROOT_UID is null","or(l.ROOT_UID is null and l.ROOT_CASE_TASK_ID is null)")
s=s.replace("p_domain.put('uid',l.ROOT_UID)","p_domain.put('uid',nvl(l.ROOT_UID,'CASE:'||RRL_STOCK_PLAN_HELPER.decimal_text(l.ROOT_CASE_TASK_ID)))")
s=s.replace("plan clob;fresh json_object_t;j","plan clob;fresh json_object_t;op varchar2(100):=d.get_string('operation_id');j")
s=s.replace("where OPERATION_ID=d.get_string('operation_id')","where OPERATION_ID=op");out[str(p)]=s
p=f/"007_load_guard.sql";s=(f/"000_before_rrl_tt_hu_load_fact_guard.sql").read_text(encoding="utf-8")
start=s.index(" elsif kind_name='INTERWARE_CUSTODY_RELEASE' then");end=s.index(" elsif :new.CUSTODY_RELEASED_AT",start)
branch=s[start:end]
branch=branch.replace("kind_name='INTERWARE_CUSTODY_RELEASE'","kind_name in('STORE_RECEIPT','STORE_CUSTODY_RELEASE')")
a=branch.index("  declare n number;begin")
branch=branch[:a]+"""  declare n number;begin
   select count(*)into n from RRL_STORE_LOAD_CUSTODY f join RRL_STORE_RECEIPT_FACT r on r.OPERATION_ID=f.RECEIPT_OPERATION_ID
    where f.OPERATION_ID=op and f.LOAD_OPERATION_ID=:old.LOAD_OPERATION_ID and r.LOAD_OPERATION_ID=:old.LOAD_OPERATION_ID
     and r.RECEIPT_STATE='ACCEPTED'and f.RELEASED_AT=:new.CUSTODY_RELEASED_AT and r.RECEIVED_AT=:new.CUSTODY_RELEASED_AT;
   if n!=1 then raise_application_error(-20863,'STORE_ACTUAL_FULL_CUSTODY_PROOF_REQUIRED');end if;
  end;
"""
s=s[:end]+branch+s[end:];out[str(p)]=s
out[str(f/"009_recompile.sql")]="alter package RRL_STOCK_STORE_CUSTODY_CMD compile body;\nalter package RRL_STOCK_STORE_RECEIPT_CMD compile body;\nalter package RRL_STOCK_POSTING_API compile body;\n"
out[str(f/"rollback.sql")]="declare n number;begin select count(*)into n from RRL_STORE_LOAD_CUSTODY;if n>0 then raise_application_error(-20863,'STORE_CUSTODY_FORWARD_REPAIR_REQUIRED');end if;end;\n/\n@@000_before_rrl_stock_store_receipt_cmd.sql\n@@000_before_rrl_stock_store_return_tr_cmd.sql\n@@000_before_rrl_stock_store_return_cust_cmd.sql\n@@000_before_rrl_stock_posting_api.sql\n@@000_before_rrl_tt_hu_load_fact_guard.sql\ndrop trigger RRL_STORE_LOAD_CUSTODY_GUARD;\ndrop table RRL_STORE_LOAD_CUSTODY;\ndrop package RRL_STOCK_STORE_CUSTODY_CMD;\n"
print(json.dumps(out,ensure_ascii=True))
