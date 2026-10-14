import json
from pathlib import Path
out={}
base="db/migrations/2026-10-10_ni081_range_proposal/"
schema=[]
definitions=[
("RRL_PICK_RANGE_OPERATION","""OPERATION_ID varchar2(100) primary key,ACTION_CODE varchar2(30)not null,WARE_ID number not null,
 ARTICLE varchar2(40)not null,ACTOR varchar2(100)not null,REQUEST_HASH varchar2(64)not null,
 REQUEST_JSON clob not null check(REQUEST_JSON is json),RESULT_JSON clob not null check(RESULT_JSON is json),
 CREATED_AT timestamp with time zone default systimestamp not null"""),
("RRL_PICK_RANGE_PROPOSAL","""PROPOSAL_ID varchar2(100)primary key references RRL_PICK_RANGE_OPERATION(OPERATION_ID),
 WARE_ID number not null,ARTICLE varchar2(40)not null,SOURCE_SIGNATURE varchar2(64)not null,
 SOURCE_JSON clob not null check(SOURCE_JSON is json)"""),
("RRL_PICK_RANGE_CANCEL","""PROPOSAL_ID varchar2(100)primary key references RRL_PICK_RANGE_PROPOSAL(PROPOSAL_ID),
 CANCEL_OPERATION_ID varchar2(100)unique not null references RRL_PICK_RANGE_OPERATION(OPERATION_ID),
 REASON varchar2(2000)not null""")]
for name,cols in definitions:
 ddl="create table "+name+"("+cols+")"
 schema.append("begin execute immediate q'~"+ddl+"~';exception when others then if sqlcode!=-955 then raise;end if;end;\n/")
out[base+"001_schema.sql"]="\n".join(schema)+"\n"
out[base+"002_api.sql"]="""create or replace package RRL_PICK_RANGE_PROPOSAL_API authid definer as
 function write_allowed return number;
 procedure execute_command(p_operation varchar2,p_actor varchar2,p_action varchar2,p_ware number,p_article varchar2,
  p_request clob,p_source clob,p_result out clob);
end;
/
create or replace package body RRL_PICK_RANGE_PROPOSAL_API as
 g_tx varchar2(100);
 function write_allowed return number is begin
  if g_tx is not null and g_tx=dbms_transaction.local_transaction_id(false)then return 1;end if;return 0;end;
 procedure current_actor(p_actor varchar2,p_ware number)is n number;begin
  select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0
   and(WARE_ID=p_ware or upper(trim(USER_GROUP))='GLOBAL_ADMIN')and RRL_HAS_WRIGHT(ID,'pick_topology_edit')=1;
  if n!=1 then raise_application_error(-20882,'PICK_RANGE_CURRENT_WARE_ACTOR_REQUIRED');end if;
 end;
 procedure execute_command(p_operation varchar2,p_actor varchar2,p_action varchar2,p_ware number,p_article varchar2,
  p_request clob,p_source clob,p_result out clob)is
  b json_object_t:=json_object_t.parse(p_request);s json_object_t;j json_object_t:=json_object_t();
  digest varchar2(64);old RRL_PICK_RANGE_OPERATION%rowtype;proposal RRL_PICK_RANGE_PROPOSAL%rowtype;
  v_entered boolean:=false;v_saved boolean:=false;n number;reason varchar2(2000);identity varchar2(100);sig varchar2(64);result clob;
 begin
  current_actor(p_actor,p_ware);
  if p_operation is null or lengthb(p_operation)>100 or p_article is null or lengthb(p_article)>40
   or p_action not in('SAVE_DRAFT','CANCEL_DRAFT')or p_action is null then
   raise_application_error(-20881,'PICK_RANGE_OPERATION_INPUT_REQUIRED');end if;
  digest:=lower(rawtohex(sys.dbms_crypto.hash(p_request,sys.dbms_crypto.hash_sh256)));
  RRL_STOCK_CONFIG_API.begin_change(p_actor,'pick_topology_edit');v_entered:=true;
  current_actor(p_actor,p_ware);
  begin
   select *into old from RRL_PICK_RANGE_OPERATION where OPERATION_ID=p_operation;
   if old.REQUEST_HASH!=digest or old.ACTOR!=p_actor or old.ACTION_CODE!=p_action or old.WARE_ID!=p_ware or old.ARTICLE!=p_article then
    raise_application_error(-20886,'PICK_RANGE_OPERATION_CONTENT_CONFLICT');end if;
   p_result:=old.RESULT_JSON;RRL_STOCK_CONFIG_API.end_change;return;
  exception when no_data_found then null;end;
  if p_action='SAVE_DRAFT'and p_source is null then
   j.put('status','SOURCE_RECOMPUTATION_REQUIRED');p_result:=j.to_clob;RRL_STOCK_CONFIG_API.end_change;return;
  end if;
  reason:=b.get_string('reason');
  if reason is null or length(reason)<8 then raise_application_error(-20881,'PICK_RANGE_REASON_REQUIRED');end if;
  select count(*)into n from RRL_ARTICULS where ACTICUL=p_article;
  if n!=1 then raise_application_error(-20886,'PICK_RANGE_ARTICLE_NOT_CURRENT');end if;
  if p_action='SAVE_DRAFT'then
   s:=json_object_t.parse(p_source);sig:=s.get_string('source_signature');
   if sig is null or length(sig)!=64 or sig!=b.get_string('expected_source_signature')
    or s.get_number('warehouse_id')!=p_ware or s.get_string('article')!=p_article then
    raise_application_error(-20886,'PICK_RANGE_SOURCE_PROOF_CONFLICT');end if;
   j:=s.get_object('range_recommendation');
   if j.get_string('status')!='NOMINAL_RECOMMENDATION'or j.get_boolean('applied')then
    raise_application_error(-20886,'PICK_RANGE_COMPLETE_RECOMMENDATION_REQUIRED');end if;
   j:=json_object_t();identity:=p_operation;
   j.put('status','DRAFT');j.put('proposal_id',identity);j.put('source_signature',sig);
  else
   identity:=b.get_string('proposal_id');
   select *into proposal from RRL_PICK_RANGE_PROPOSAL where PROPOSAL_ID=identity for update;
   if proposal.WARE_ID!=p_ware or proposal.ARTICLE!=p_article then
    raise_application_error(-20882,'PICK_RANGE_PROPOSAL_SCOPE_CONFLICT');end if;
   select count(*)into n from RRL_PICK_RANGE_CANCEL where PROPOSAL_ID=identity;
   if n>0 then raise_application_error(-20886,'PICK_RANGE_PROPOSAL_ALREADY_CANCELLED');end if;
   j.put('status','CANCELLED');j.put('proposal_id',identity);
  end if;
  j.put('operation_id',p_operation);j.put('stock_changed',false);j.put('range_applied',false);
  result:=j.to_clob;
  savepoint RRL_RANGE157;v_saved:=true;g_tx:=dbms_transaction.local_transaction_id(true);
  insert into RRL_PICK_RANGE_OPERATION(OPERATION_ID,ACTION_CODE,WARE_ID,ARTICLE,ACTOR,REQUEST_HASH,REQUEST_JSON,RESULT_JSON)
   values(p_operation,p_action,p_ware,p_article,p_actor,digest,p_request,result);
  if p_action='SAVE_DRAFT'then
   insert into RRL_PICK_RANGE_PROPOSAL(PROPOSAL_ID,WARE_ID,ARTICLE,SOURCE_SIGNATURE,SOURCE_JSON)
    values(identity,p_ware,p_article,sig,p_source);
  else
   insert into RRL_PICK_RANGE_CANCEL(PROPOSAL_ID,CANCEL_OPERATION_ID,REASON)values(identity,p_operation,reason);
  end if;
  p_result:=result;g_tx:=null;RRL_STOCK_CONFIG_API.end_change;
 exception when others then
  if v_saved then rollback to RRL_RANGE157;end if;g_tx:=null;
  if v_entered then RRL_STOCK_CONFIG_API.end_change;end if;raise;
 end;
end;
/
"""
guards=[]
for name,_ in definitions:
 trg=name.replace("RRL_PICK_RANGE_","RRL_PR_")+"_G"
 guards.append("create or replace trigger "+trg+" before insert or update or delete on "+name+" for each row\nbegin\n if updating or deleting or RRL_PICK_RANGE_PROPOSAL_API.write_allowed!=1 then raise_application_error(-20863,'PICK_RANGE_IMMUTABLE_API_ONLY');end if;\nend;\n/")
out[base+"003_guards.sql"]="\n".join(guards)+"\n"
out[base+"apply.sql"]="@@001_schema.sql\n@@002_api.sql\n@@003_guards.sql\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
m["packages"].append("RRL_PICK_RANGE_PROPOSAL_API");m["components"].append("../2026-10-10_ni081_range_proposal/002_api.sql")
m["startup_scripts"].append("../2026-10-10_ni081_range_proposal/001_schema.sql")
m["additional_scripts"].append("../2026-10-10_ni081_range_proposal/003_guards.sql")
out[str(p)]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
print(json.dumps(out))
