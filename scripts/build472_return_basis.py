import json
from pathlib import Path
d=Path("db/migrations/2026-10-12_ni062_return_basis");out={}
schema="""declare n number;begin
 select count(*)into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_STORE_RETURN_APPROVAL'and COLUMN_NAME='RETURN_BASIS';
 if n=0 then execute immediate q'[alter table RRL_STORE_RETURN_APPROVAL add(RETURN_BASIS varchar2(10)default 'ACCEPTED'not null check(RETURN_BASIS in('ACCEPTED','REFUSED','DAMAGED')))]';end if;
end;
/
"""
out[str(d/"001_schema.sql")]=schema
def read(name,kind):
 return Path("tmp/return471_"+name.lower()+"_"+kind.replace(" ","_").lower()+".sql").read_text(encoding="utf-8")
spec=read("RRL_STORE_RETURN_UNIT_CORE","PACKAGE")
spec=spec.replace(" function accepted_units", " function disposition_units(p_receipt varchar2,p_uid varchar2,p_uom varchar2,p_basis varchar2)return clob;\n function select_disposition_units(p_receipt varchar2,p_uid varchar2,p_uom varchar2,p_qty number,p_keys clob,p_basis varchar2)return clob;\n function accepted_units",1)
out[str(d/"002_units_spec.sql")]=spec
body=read("RRL_STORE_RETURN_UNIT_CORE","PACKAGE BODY")
start=body.index(" function accepted_units(");end=body.index(" procedure persist(",start)
section=body[start:end]
general=section.replace("function accepted_units(p_receipt varchar2,p_uid varchar2,p_uom varchar2)","function disposition_units(p_receipt varchar2,p_uid varchar2,p_uom varchar2,p_basis varchar2)")
general=general.replace(" begin\n  select json_value(COMPOSITION_JSON"," begin\n  if p_basis is null or p_basis not in('ACCEPTED','REFUSED','DAMAGED')then raise_application_error(-20886,'STORE_RETURN_BASIS_REQUIRED');end if;\n  select json_value(COMPOSITION_JSON",1)
general=general.replace("if fact_count=0 and not json_object_t.parse(proof)","if fact_count=0 and p_basis!='ACCEPTED'then return to_clob('[]');end if;\n  if fact_count=0 and not json_object_t.parse(proof)")
general=general.replace("UNIT_DISPOSITION='ACCEPTED'","UNIT_DISPOSITION=p_basis").replace("where fact_count=0 and state_text='ACCEPTED'","where fact_count=0 and state_text='ACCEPTED'and p_basis='ACCEPTED'")
general=general.replace("function select_units(p_receipt varchar2,p_uid varchar2,p_uom varchar2,p_qty number,p_keys clob)","function select_disposition_units(p_receipt varchar2,p_uid varchar2,p_uom varchar2,p_qty number,p_keys clob,p_basis varchar2)")
general=general.replace("wire clob:=accepted_units(p_receipt,p_uid,p_uom)","wire clob:=disposition_units(p_receipt,p_uid,p_uom,p_basis)").replace("STORE_RETURN_ACCEPTED_SELECTED_UNIT_QUANTITY_REQUIRED","STORE_RETURN_DISPOSITION_SELECTED_UNIT_QUANTITY_REQUIRED")
wrappers=""" function accepted_units(p_receipt varchar2,p_uid varchar2,p_uom varchar2)return clob is
 begin return disposition_units(p_receipt,p_uid,p_uom,'ACCEPTED');end;
 function select_units(p_receipt varchar2,p_uid varchar2,p_uom varchar2,p_qty number,p_keys clob)return clob is
 begin return select_disposition_units(p_receipt,p_uid,p_uom,p_qty,p_keys,'ACCEPTED');end;
"""
body=body[:start]+general+wrappers+body[end:]
out[str(d/"003_units_body.sql")]=body
cmd=read("RRL_STOCK_STORE_RETURN_CMD","PACKAGE BODY")
cmd=cmd.replace("v_qty number;v_used number;","v_qty number;v_used number;v_basis varchar2(10):=nvl(m.get_string('return_basis'),'ACCEPTED');v_limit number;")
cmd=cmd.replace("if v_destination='REUSE' and", "if v_basis not in('ACCEPTED','REFUSED','DAMAGED')then raise_application_error(-20886,'STORE_RETURN_BASIS_REQUIRED');end if;\n if v_basis!='ACCEPTED'and v_destination='REUSE'then raise_application_error(-20886,'STORE_RETURN_EXCEPTION_REUSE_INSPECTION_REQUIRED');end if;\n if v_destination='REUSE' and",1)
old="where RECEIPT_OPERATION_ID=v_receipt and LINE_NO=v_line;"
assert cmd.count(old)==1;cmd=cmd.replace(old,"where RECEIPT_OPERATION_ID=v_receipt and LINE_NO=v_line and RETURN_BASIS=v_basis;")
cmd=cmd.replace("if v_qty+v_used>original.ACCEPTED_BASE_QTY then", "case v_basis when 'ACCEPTED'then v_limit:=original.ACCEPTED_BASE_QTY;when 'REFUSED'then v_limit:=original.REFUSED_BASE_QTY;when 'DAMAGED'then v_limit:=original.DAMAGED_BASE_QTY;end case;\n if v_qty+v_used>v_limit then")
cmd=cmd.replace("STORE_RETURN_ACCEPTED_QUANTITY_EXCEEDED","STORE_RETURN_SOURCE_DISPOSITION_QUANTITY_EXCEEDED")
cmd=cmd.replace("RRL_STORE_RETURN_UNIT_CORE.select_units(v_receipt,original.LOT_UID,original.BASE_UOM,v_qty,m.get_array('unit_keys').to_clob)","RRL_STORE_RETURN_UNIT_CORE.select_disposition_units(v_receipt,original.LOT_UID,original.BASE_UOM,v_qty,m.get_array('unit_keys').to_clob,v_basis)")
cmd=cmd.replace("p_domain.put('receipt_operation_id',v_receipt);","if v_basis!='ACCEPTED'then p_domain.put('return_basis',v_basis);end if;\n p_domain.put('receipt_operation_id',v_receipt);")
cmd=cmd.replace("v_good number;","v_good number;v_basis varchar2(10);")
cmd=cmd.replace("v_lot:=v.get_string('lot_uid');","v_basis:=nvl(v.get_string('return_basis'),'ACCEPTED');\n v_lot:=v.get_string('lot_uid');")
cmd=cmd.replace("COMPLETE_GOOD_BOX,APPROVED_BY)","COMPLETE_GOOD_BOX,APPROVED_BY,RETURN_BASIS)")
cmd=cmd.replace("v_reference,v_good,p_actor);","v_reference,v_good,p_actor,v_basis);")
cmd=cmd.replace("j.put('operation_id',op);","if v_basis!='ACCEPTED'then j.put('return_basis',v_basis);j.put('customer_accepted_quantity_changed',false);end if;\n j.put('operation_id',op);")
out[str(d/"004_command.sql")]=cmd
guard=read("RRL_STORE_RETURN_APPROVAL_GUARD","TRIGGER")
guard=guard.replace("v_line number;","v_line number;v_basis varchar2(10);")
guard=guard.replace("into v_kind,v_state,v_receipt,v_line"," ,nvl(json_value(RESOLVED_PLAN_JSON,'$.domain.return_basis'),'ACCEPTED')into v_kind,v_state,v_receipt,v_line,v_basis")
guard=guard.replace("or v_line!=:new.LINE_NO then","or v_line!=:new.LINE_NO or v_basis!=:new.RETURN_BASIS then")
out[str(d/"005_guard.sql")]=guard
for name,kind in [("RRL_STOCK_STORE_RETURN_CMD","PACKAGE BODY"),("RRL_STORE_RETURN_UNIT_CORE","PACKAGE"),("RRL_STORE_RETURN_UNIT_CORE","PACKAGE BODY"),("RRL_STORE_RETURN_APPROVAL_GUARD","TRIGGER")]:
 out[str(d/("000_before_"+name.lower()+"_"+kind.replace(" ","_").lower()+".sql"))]=read(name,kind)
out[str(d/"apply.sql")]="@@001_schema.sql\n@@002_units_spec.sql\n@@003_units_body.sql\n@@004_command.sql\n@@005_guard.sql\n@@006_ledger.sql\nalter package RRL_STOCK_POSTING_API compile body;\n/\n"
out[str(d/"006_ledger.sql")]="merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-472-store-return-disposition-basis' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Existing store return owner: separate accepted/refused/damaged caps and exact physical unit disposition',sysdate,user,'apply.sql','rollback.sql','APPLIED');\n/\n"
out[str(d/"rollback.sql")]="-- Do not revert after non-ACCEPTED approvals are committed: dependent physical flows require preserved source basis.\n-- Forward repair preferred; original native sources saved as000_before*.sql.\n"
print(json.dumps(out))
