create or replace package RRL_STOCK_REPL_ADMISSION authid definer as
 function reason(p_uid varchar2,p_target varchar2,p_ware number,p_article varchar2) return varchar2;
 function mode_for(p_task number) return varchar2;
 function policy_signature(p_task number) return varchar2;
 procedure assert_target(p_uid varchar2,p_target varchar2,p_ware number,p_article varchar2);
end;
/

create or replace package body RRL_STOCK_REPL_ADMISSION as
 function lot_key(p_uid varchar2) return varchar2 is v RRL_PALLETS%rowtype;v_supplier varchar2(100);v_key varchar2(500);
 begin
  select * into v from RRL_PALLETS where UID_PALLET=p_uid;
  select max(SUPPLIER_BATCH) into v_supplier from RRL_SAP_PALLET_RECEIPT where UID_PALLET=nvl(v.STOCK_ORIGIN_UID,v.UID_PALLET);
  v_key:=case when v.PROD_BATCH_ID is not null then 'MES:'||to_char(v.PROD_BATCH_ID,'TM9')
   when v_supplier is not null then 'SAP:'||v_supplier
   when v.PRIHOD_NAKLAD_ID is not null then 'DOC:'||to_char(v.PRIHOD_NAKLAD_ID,'TM9')
   else 'UID:'||nvl(v.STOCK_ORIGIN_UID,v.UID_PALLET) end;
  return v_key||':EXP:'||nvl(to_char(v.EXPIRY_DATE,'YYYYMMDDHH24MISS'),'NULL')
   ||':MADE:'||nvl(to_char(v.PRODUCED_DATE,'YYYYMMDDHH24MISS'),'NULL');
 end;
 function reason(p_uid varchar2,p_target varchar2,p_ware number,p_article varchar2) return varchar2 is
  v_mix number;v_pick number;v_count number;v_key varchar2(1000);
 begin
  select count(*),max(OTBOR) into v_count,v_pick from RRL_CELLS where CELL=p_target and WARE_ID=p_ware;
  if v_count!=1 then return 'REPLENISHMENT_TARGET_MISSING_OR_AMBIGUOUS';end if;
  select nvl(max(ALLOW_PICK_BATCH_MIX),0) into v_mix from RRL_RECEIPT_SKU_RULE where WARE_ID=p_ware and ARTICUL=p_article;
  v_key:=lot_key(p_uid);v_count:=0;
  for t in(select p.UID_PALLET,p.ARTICUL from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA where r.CELL=p_target and r.REMAIN>0) loop
   v_count:=v_count+1;if v_count>200 then raise_application_error(-20881,'REPLENISHMENT_TARGET_LOTS_BOUND');end if;
   if t.ARTICUL!=p_article then return 'REPLENISHMENT_TARGET_OTHER_SKU';end if;
   if not(v_mix=1 and v_pick=1) and lot_key(t.UID_PALLET)!=v_key then return 'REPLENISHMENT_TARGET_BATCH_MIX_FORBIDDEN';end if;
  end loop;
  return null;
 end;
 function mode_for(p_task number) return varchar2 is t RRL_PICK_WAVE_REPLENISH_TASK%rowtype;
  v_kind varchar2(40);v_abc varchar2(100);v_occupied number;v_short number;
 begin
  select * into t from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_REPLENISH_TASK_ID=p_task;
  select WAVE_KIND into v_kind from RRL_PICK_WAVE where PICK_WAVE_ID=t.PICK_WAVE_ID;
  select count(*) into v_short from RRL_CASE_PICK_SHORT where REPLENISH_TASK_ID=p_task and RECOVERY_STATE='WAIT_REPLENISHMENT';
  -- Minimax and urgent shortage retain their explicit quantity contracts.
  if v_kind='REPLENISHMENT' or v_short>0 then return nvl(t.REPLENISHMENT_QTY_MODE,'FULL_PALLET');end if;
  select upper(trim(ABC_GROUP)) into v_abc from RRL_ARTICULS where ACTICUL=t.ARTICUL;
  select count(*) into v_occupied from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA
   where r.CELL=t.TARGET_CELL_CODE and r.REMAIN>0 and p.ARTICUL=t.ARTICUL;
  if v_abc='B' and v_occupied>0 and nvl(t.REPLENISHMENT_QTY_MODE,'FULL_PALLET')!='FULL_PALLET' then return 'FILL_TO_VOLUME';end if;
  return 'FULL_PALLET';
 end;
 function policy_signature(p_task number) return varchar2 is v json_object_t:=json_object_t();v_abc varchar2(100);v_mix number;v_ware number;v_article varchar2(160);
 begin
  select w.WARE_ID,t.ARTICUL,a.ABC_GROUP into v_ware,v_article,v_abc from RRL_PICK_WAVE_REPLENISH_TASK t
   join RRL_PICK_WAVE w on w.PICK_WAVE_ID=t.PICK_WAVE_ID join RRL_ARTICULS a on a.ACTICUL=t.ARTICUL where t.PICK_WAVE_REPLENISH_TASK_ID=p_task;
  select nvl(max(ALLOW_PICK_BATCH_MIX),0) into v_mix from RRL_RECEIPT_SKU_RULE where WARE_ID=v_ware and ARTICUL=v_article;
  v.put('mode',mode_for(p_task));v.put('abc',v_abc);v.put('mix',v_mix);
  return rawtohex(sys.dbms_crypto.hash(v.to_clob,sys.dbms_crypto.hash_sh256));
 end;
 procedure assert_target(p_uid varchar2,p_target varchar2,p_ware number,p_article varchar2) is v_reason varchar2(200);
 begin
  v_reason:=reason(p_uid,p_target,p_ware,p_article);
  if v_reason is not null then raise_application_error(-20887,v_reason);end if;
 end;
end;
/
