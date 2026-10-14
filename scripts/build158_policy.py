import json
from pathlib import Path
base="db/migrations/2026-10-10_ni081_range_apply/";out={}
defs=[
("RRL_PICK_RANGE_APPROVAL","""PROPOSAL_ID varchar2(100)primary key references RRL_PICK_RANGE_PROPOSAL(PROPOSAL_ID),
 OPERATION_ID varchar2(100)unique not null references RRL_PICK_RANGE_OPERATION(OPERATION_ID)deferrable initially deferred,
 WARE_ID number not null,ARTICLE varchar2(40)not null,PROOF_JSON clob not null check(PROOF_JSON is json)"""),
("RRL_PICK_RANGE_STATUS","""PICK_FACE_ARTICUL_ID number primary key references RRL_PICK_FACE_ARTICUL(PICK_FACE_ARTICUL_ID),
 MODE_CODE varchar2(20)not null check(MODE_CODE in('ACTIVE','DRAINING','CLOSED')),
 APPROVAL_OPERATION_ID varchar2(100)not null references RRL_PICK_RANGE_OPERATION(OPERATION_ID)deferrable initially deferred"""),
("RRL_PICK_RANGE_ALLOW_REPL","""PICK_FACE_ARTICUL_ID number not null references RRL_PICK_FACE_ARTICUL(PICK_FACE_ARTICUL_ID),
 DRAIN_OPERATION_ID varchar2(100)not null references RRL_PICK_RANGE_OPERATION(OPERATION_ID)deferrable initially deferred,
 REPLENISH_TASK_ID number not null references RRL_PICK_WAVE_REPLENISH_TASK(PICK_WAVE_REPLENISH_TASK_ID),
 MAX_ORIGINAL_QTY number not null check(MAX_ORIGINAL_QTY>=0),
 primary key(PICK_FACE_ARTICUL_ID,DRAIN_OPERATION_ID,REPLENISH_TASK_ID)"""),
("RRL_PICK_RANGE_MEMBER","""PROPOSAL_ID varchar2(100)not null references RRL_PICK_RANGE_APPROVAL(PROPOSAL_ID),
 PICK_FACE_ARTICUL_ID number not null references RRL_PICK_FACE_ARTICUL(PICK_FACE_ARTICUL_ID),
 ROLE_CODE varchar2(10)not null check(ROLE_CODE in('OLD','NEW')),
 primary key(PROPOSAL_ID,PICK_FACE_ARTICUL_ID,ROLE_CODE)"""),
("RRL_PICK_RANGE_DRAIN_CLOSE","""OPERATION_ID varchar2(100)primary key references RRL_PICK_RANGE_OPERATION(OPERATION_ID)deferrable initially deferred,
 PICK_FACE_ARTICUL_ID number not null references RRL_PICK_FACE_ARTICUL(PICK_FACE_ARTICUL_ID),
 FROM_APPROVAL_OPERATION_ID varchar2(100)not null references RRL_PICK_RANGE_OPERATION(OPERATION_ID)""")]
out[base+"001_schema.sql"]="\n".join("begin execute immediate q'~create table "+name+"("+cols+")~';exception when others then if sqlcode!=-955 then raise;end if;end;\n/"for name,cols in defs)+"\n"
out[base+"002_policy.sql"]="""create or replace package RRL_PICK_RANGE_POLICY authid definer as
 function target_write_allowed(p_cell varchar2,p_article varchar2,p_repl number,p_quantity number)return number;
 function new_target_allowed(p_cell varchar2,p_article varchar2,p_exclude_repl number default null)return number;
end;
/
create or replace package body RRL_PICK_RANGE_POLICY as
 function target_write_allowed(p_cell varchar2,p_article varchar2,p_repl number,p_quantity number)return number is
  n number;identity number;mode varchar2(20);operation varchar2(100);
 begin
  select count(*),max(s.PICK_FACE_ARTICUL_ID),max(s.MODE_CODE),max(s.APPROVAL_OPERATION_ID)
   into n,identity,mode,operation from RRL_PICK_RANGE_STATUS s
   join RRL_PICK_FACE_ARTICUL a on a.PICK_FACE_ARTICUL_ID=s.PICK_FACE_ARTICUL_ID
   join RRL_PICK_FACE f on f.PICK_FACE_ID=a.PICK_FACE_ID
   where f.CELL_CODE=p_cell and a.ARTICUL=p_article and s.MODE_CODE in('DRAINING','CLOSED');
  if n=0 then return 1;end if;
  if n!=1 or mode!='DRAINING'or p_repl is null or p_quantity is null then return 0;end if;
  select count(*)into n from RRL_PICK_RANGE_ALLOW_REPL where PICK_FACE_ARTICUL_ID=identity
   and DRAIN_OPERATION_ID=operation and REPLENISH_TASK_ID=p_repl and MAX_ORIGINAL_QTY>=p_quantity;
  return case when n=1 then 1 else 0 end;
 end;
 function new_target_allowed(p_cell varchar2,p_article varchar2,p_exclude_repl number default null)return number is
  q number;c varchar2(100);a varchar2(40);
 begin
  if p_exclude_repl is not null then
   begin
    select QTY,TARGET_CELL_CODE,ARTICUL into q,c,a from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_REPLENISH_TASK_ID=p_exclude_repl;
    if c!=p_cell or a!=p_article then return 0;end if;
   exception when no_data_found then return 0;end;
  end if;
  return target_write_allowed(p_cell,p_article,p_exclude_repl,q);
 end;
end;
/
"""
guards=[]
for name,_ in defs:
 trg=name.replace("RRL_PICK_RANGE_","RRL_RA_")+"_G"
 mutable=name=="RRL_PICK_RANGE_STATUS"
 condition="deleting or RRL_PICK_RANGE_PROPOSAL_API.write_allowed!=1"if mutable else"updating or deleting or RRL_PICK_RANGE_PROPOSAL_API.write_allowed!=1"
 guards.append("create or replace trigger "+trg+" before insert or update or delete on "+name+" for each row\nbegin\n if "+condition+"then raise_application_error(-20863,'PICK_RANGE_NATIVE_APPLY_ONLY');end if;\nend;\n/")
guards.append("""create or replace trigger RRL_REPL_RANGE_TARGET_G before insert or update on RRL_PICK_WAVE_REPLENISH_TASK for each row
begin
 if inserting or nvl(:new.TARGET_CELL_CODE,chr(0))!=nvl(:old.TARGET_CELL_CODE,chr(0))
  or nvl(:new.ARTICUL,chr(0))!=nvl(:old.ARTICUL,chr(0))or nvl(:new.QTY,0)>nvl(:old.QTY,0)then
  if RRL_PICK_RANGE_POLICY.target_write_allowed(:new.TARGET_CELL_CODE,:new.ARTICUL,:new.PICK_WAVE_REPLENISH_TASK_ID,:new.QTY)!=1 then
   raise_application_error(-20886,'PICK_RANGE_FUTURE_REPLENISHMENT_BLOCKED');end if;
 end if;
end;
/
""")
out[base+"003_guards.sql"]="\n".join(guards)+"\n"
cap=Path(base+"000_before_capacity.sql").read_text(encoding="utf-8")
needle=" begin\n  select count(*),max(MAX_VOLUME)"
# Live captured text can preserve CRLF as universal newlines in read_text.
if needle not in cap:raise ValueError("Native capacity anchor missing")
cap=cap.replace(needle," begin\n  if RRL_PICK_RANGE_POLICY.new_target_allowed(p_cell,p_article,p_exclude_repl)!=1 then return 0;end if;\n  select count(*),max(MAX_VOLUME)",1)
out[base+"004_capacity_contract.sql"]=cap
out[base+"004_capacity_body.sql"]="create or replace "+cap.split("create or replace ",2)[2]
top=Path(base+"000_before_topology.sql").read_text(encoding="utf-8")
needle="           and pfa.CASE_PICK_ENABLED = 1"
if top.count(needle)!=1:raise ValueError("Native topology selector anchor missing")
top=top.replace(needle,needle+"\n           and RRL_PICK_RANGE_POLICY.new_target_allowed(pf.CELL_CODE,pfa.ARTICUL)=1",1)
out[base+"005_topology_contract.sql"]=top
out[base+"005_topology_body.sql"]="create or replace "+top.split("create or replace ",2)[2]
out[base+"apply_policy.sql"]="@@001_schema.sql\n@@002_policy.sql\n@@004_capacity_body.sql\n@@005_topology_body.sql\n@@003_guards.sql\n"
print(json.dumps(out))
