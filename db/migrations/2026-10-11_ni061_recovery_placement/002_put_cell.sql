create or replace package RRL_STOCK_IW_PUT_CELL authid definer
 accessible by(package RRL_STOCK_INTERWARE_PUT,package RRL_STOCK_IW_RECOVERY_PUT)as
 procedure assert_target(p_ware number,p_uid varchar2,p_from varchar2,p_target varchar2,p_gross number,p_task_id number);
end;
/
create or replace package body RRL_STOCK_IW_PUT_CELL as
 procedure assert_target(p_ware number,p_uid varchar2,p_from varchar2,p_target varchar2,p_gross number,p_task_id number)is
 v_capacity number;v_height number;v_weight number;v_unknown number;n number;
 begin
 select LIMIT_WEIGHT,LIMIT_HEIGHT into v_capacity,v_height from RRL_CELLS where CELL=p_target and WARE_ID=p_ware and nvl(BLOCKED_FOR_ACCEPT,0)=0 and nvl(BLOCKED_FOR_REMAINS,0)=0 and nvl(BLOCKED_FOR_POPOLNENIE,0)=0;
 if p_target=p_from then raise_application_error(-20886,'INTERWARE_SEPARATE_OUTBOUND_BUFFER_REQUIRED');end if;
 if nvl(v_height,0)>0 then raise_application_error(-20886,'INTERWARE_TARGET_HEIGHT_PROOF_REQUIRED');end if;
 select count(*)into n from RRL_TOPOLOGY_CELL_SLOT sl join RRL_TOPOLOGY_CELL tc on tc.TOPOLOGY_CELL_ID=sl.TOPOLOGY_CELL_ID join RRL_WAREHOUSE_TOPOLOGY t on t.TOPOLOGY_ID=tc.TOPOLOGY_ID where tc.LEGACY_CELL_CODE=p_target and tc.WARE_ID=p_ware and tc.ACTIVE=1 and sl.ACTIVE=1 and t.STATUS='PUBLISHED';
 if n!=0 then raise_application_error(-20886,'INTERWARE_TARGET_SLOT_FLOW_REQUIRED');end if;
 if nvl(v_capacity,0)>0 then
  select nvl(sum(pp.WEIGHT_BRUTTO),0),nvl(sum(case when pp.WEIGHT_BRUTTO is null then 1 else 0 end),0)into v_weight,v_unknown from(
   select r.UID_POLETA UID_PALLET from RRL_REMAINS r where r.CELL=p_target and r.REMAIN>0 and r.UID_POLETA!=p_uid
   union select wt.UID_PALLET from RRL_WAREHOUSE_TASK wt where wt.TO_CELL=p_target and wt.STATUS not in('DONE','CANCELLED')and wt.UID_PALLET!=p_uid and(p_task_id is null or wt.TASK_ID!=p_task_id)
  )occupants join RRL_PALLETS pp on pp.UID_PALLET=occupants.UID_PALLET;
  if p_gross is null or v_unknown>0 or v_weight+p_gross>v_capacity then raise_application_error(-20886,'INTERWARE_TARGET_WEIGHT_CAPACITY_EXCEEDED');end if;
 end if;
 exception when no_data_found then raise_application_error(-20886,'INTERWARE_AVAILABLE_TARGET_CELL_REQUIRED');end;
end;
/
