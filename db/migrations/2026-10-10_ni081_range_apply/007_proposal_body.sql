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
  v_saved boolean:=false;n number;reason varchar2(2000);identity varchar2(100);sig varchar2(64);result clob;
 begin
  current_actor(p_actor,p_ware);
  if p_operation is null or lengthb(p_operation)>100 or p_article is null or lengthb(p_article)>40
   or p_action not in('SAVE_DRAFT','CANCEL_DRAFT','APPROVE','CLOSE_DRAIN')or p_action is null then
   raise_application_error(-20881,'PICK_RANGE_OPERATION_INPUT_REQUIRED');end if;
  digest:=lower(rawtohex(sys.dbms_crypto.hash(p_request,sys.dbms_crypto.hash_sh256)));
  current_actor(p_actor,p_ware);
  begin
   select *into old from RRL_PICK_RANGE_OPERATION where OPERATION_ID=p_operation;
   if old.REQUEST_HASH!=digest or old.ACTOR!=p_actor or old.ACTION_CODE!=p_action or old.WARE_ID!=p_ware or old.ARTICLE!=p_article then
    raise_application_error(-20886,'PICK_RANGE_OPERATION_CONTENT_CONFLICT');end if;
   p_result:=old.RESULT_JSON;return;
  exception when no_data_found then null;end;
  if p_action in('SAVE_DRAFT','APPROVE')and p_source is null then
   j.put('status','SOURCE_RECOMPUTATION_REQUIRED');p_result:=j.to_clob;return;
  end if;
  reason:=b.get_string('reason');
  if reason is null or length(reason)<8 then raise_application_error(-20881,'PICK_RANGE_REASON_REQUIRED');end if;
  select count(*)into n from RRL_ARTICULS where ACTICUL=p_article;
  if n!=1 then raise_application_error(-20886,'PICK_RANGE_ARTICLE_NOT_CURRENT');end if;
  if p_action in('APPROVE','CLOSE_DRAIN')then
   RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
   savepoint RRL_RANGE157;v_saved:=true;g_tx:=dbms_transaction.local_transaction_id(true);
   RRL_PICK_RANGE_APPLY_CORE.apply_change(p_operation,p_actor,p_action,p_ware,p_article,p_request,p_source,result);
   j:=json_object_t.parse(result);j.put('operation_id',p_operation);result:=j.to_clob;
   insert into RRL_PICK_RANGE_OPERATION(OPERATION_ID,ACTION_CODE,WARE_ID,ARTICLE,ACTOR,REQUEST_HASH,REQUEST_JSON,RESULT_JSON)
    values(p_operation,p_action,p_ware,p_article,p_actor,digest,p_request,result);
   p_result:=result;g_tx:=null;return;
  end if;
  if p_action='SAVE_DRAFT'then
   s:=json_object_t.parse(p_source);sig:=s.get_string('source_signature');
   if sig is null or not regexp_like(sig,'^[0-9a-f]{64}$')or b.get_string('expected_source_signature')is null or sig!=b.get_string('expected_source_signature')
    or s.get_number('warehouse_id')is null or s.get_string('article')is null
    or s.get_number('warehouse_id')!=p_ware or s.get_string('article')!=p_article then
    raise_application_error(-20886,'PICK_RANGE_SOURCE_PROOF_CONFLICT');end if;
   j:=s.get_object('range_recommendation');
   if j.get_string('status')is null or j.get_string('status')!='NOMINAL_RECOMMENDATION'
    or j.get_boolean('applied')is null or j.get_boolean('applied')then
    raise_application_error(-20886,'PICK_RANGE_COMPLETE_RECOMMENDATION_REQUIRED');end if;
   j:=json_object_t();identity:=p_operation;
   j.put('status','DRAFT');j.put('proposal_id',identity);j.put('source_signature',sig);
  else
   identity:=b.get_string('proposal_id');
   select *into proposal from RRL_PICK_RANGE_PROPOSAL where PROPOSAL_ID=identity for update;
   if proposal.WARE_ID!=p_ware or proposal.ARTICLE!=p_article then
    raise_application_error(-20882,'PICK_RANGE_PROPOSAL_SCOPE_CONFLICT');end if;
   select (select count(*)from RRL_PICK_RANGE_CANCEL where PROPOSAL_ID=identity)
    +(select count(*)from RRL_PICK_RANGE_APPROVAL where PROPOSAL_ID=identity)into n from dual;
   if n>0 then raise_application_error(-20886,'PICK_RANGE_PROPOSAL_NOT_CURRENT_DRAFT');end if;
   j.put('status','CANCELLED');j.put('proposal_id',identity);
  end if;
  j.put('operation_id',p_operation);j.put('stock_changed',false);j.put('range_applied',false);
  result:=j.to_clob;
  current_actor(p_actor,p_ware);
  savepoint RRL_RANGE157;v_saved:=true;g_tx:=dbms_transaction.local_transaction_id(true);
  begin
  insert into RRL_PICK_RANGE_OPERATION(OPERATION_ID,ACTION_CODE,WARE_ID,ARTICLE,ACTOR,REQUEST_HASH,REQUEST_JSON,RESULT_JSON)
   values(p_operation,p_action,p_ware,p_article,p_actor,digest,p_request,result);
  exception when dup_val_on_index then
   select *into old from RRL_PICK_RANGE_OPERATION where OPERATION_ID=p_operation;
   if old.REQUEST_HASH!=digest or old.ACTOR!=p_actor or old.ACTION_CODE!=p_action or old.WARE_ID!=p_ware or old.ARTICLE!=p_article then
    raise_application_error(-20886,'PICK_RANGE_OPERATION_CONTENT_CONFLICT');end if;
   p_result:=old.RESULT_JSON;g_tx:=null;return;
  end;
  if p_action='SAVE_DRAFT'then
   insert into RRL_PICK_RANGE_PROPOSAL(PROPOSAL_ID,WARE_ID,ARTICLE,SOURCE_SIGNATURE,SOURCE_JSON)
    values(identity,p_ware,p_article,sig,p_source);
  else
   insert into RRL_PICK_RANGE_CANCEL(PROPOSAL_ID,CANCEL_OPERATION_ID,REASON)values(identity,p_operation,reason);
  end if;
  p_result:=result;g_tx:=null;
 exception when others then
  if v_saved then rollback to RRL_RANGE157;end if;g_tx:=null;
  raise;
 end;
end;
/
