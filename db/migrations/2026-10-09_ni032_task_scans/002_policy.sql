create or replace package RRL_STOCK_TASK_SCAN authid definer as
 function profile_signature(p_article varchar2) return varchar2;
 procedure assert_draft(p_request clob,p_task number,p_uid varchar2,p_cell varchar2,p_actor varchar2);
end;
/
create or replace package body RRL_STOCK_TASK_SCAN as
 function profile_signature(p_article varchar2) return varchar2 is
  j json_object_t:=json_object_t();a json_array_t:=json_array_t();x json_object_t;n number;v number;
 begin
  select nvl(max(MARKING_REQUIRED),0),nvl(max(POLICY_VERSION),0) into n,v from RRL_SKU_RECEIPT_POLICY where ARTICUL=p_article;
  j.put('marked',n);j.put('policy',v);
  for r in(select SYSTEM_CODE,PROFILE_CODE,PROFILE_VERSION,SCAN_MODE from RRL_SKU_RECEIPT_PROFILE where ARTICUL=p_article order by SYSTEM_CODE,PROFILE_CODE fetch first 51 rows only) loop
   if a.get_size=50 then raise_application_error(-20881,'TASK_MARK_PROFILE_BOUND');end if;
   x:=json_object_t();x.put('system',r.SYSTEM_CODE);x.put('profile',r.PROFILE_CODE);x.put('version',r.PROFILE_VERSION);x.put('scan_mode',r.SCAN_MODE);a.append(x);
  end loop;
  j.put('profiles',a);
  return rawtohex(sys.dbms_crypto.hash(j.to_clob,sys.dbms_crypto.hash_sh256));
 end;
 procedure assert_draft(p_request clob,p_task number,p_uid varchar2,p_cell varchar2,p_actor varchar2) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t;draft RRL_TASK_SCAN_DRAFT%rowtype;
  v_version number;v_article varchar2(160);a clob;b clob;v_draft_id varchar2(100);
 begin
  m:=d.get_object('metadata');m.on_error(0);
  if not m.has('scan_draft_id') or m.get('scan_draft_id').is_null then return;end if;
  v_draft_id:=m.get_string('scan_draft_id');
  select * into draft from RRL_TASK_SCAN_DRAFT where DRAFT_ID=v_draft_id;
  if draft.TASK_ID!=p_task or draft.ACTOR!=p_actor or draft.SOURCE_UID!=p_uid or draft.SOURCE_CELL!=p_cell then
   raise_application_error(-20886,'TASK_SCAN_DRAFT_IDENTITY_CONFLICT');end if;
  select s.STOCK_VERSION,p.ARTICUL into v_version,v_article from RRL_REMAINS s join RRL_PALLETS p on p.UID_PALLET=s.UID_POLETA
   where s.UID_POLETA=p_uid and s.CELL=p_cell;
  if v_version!=draft.STOCK_VERSION or profile_signature(v_article)!=draft.PROFILE_SIGNATURE then
   raise_application_error(-20886,'TASK_SCAN_DRAFT_STALE: reload profile and scan current composition');end if;
  a:=json_array_t.parse(draft.UNIT_KEYS_JSON).to_clob;b:=m.get_array('unit_keys').to_clob;
  if dbms_lob.compare(a,b)!=0 then raise_application_error(-20884,'TASK_SCAN_DRAFT_SELECTION_CHANGED');end if;
 exception when no_data_found then raise_application_error(-20886,'TASK_SCAN_DRAFT_OR_STOCK_NOT_FOUND');
 end;
end;
/
