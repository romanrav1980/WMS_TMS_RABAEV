create or replace package body RRL_STOCK_REPL_SHARED as

 function allowed(p_uid varchar2,p_cell varchar2,p_target varchar2,p_ware number,p_owner number) return number is

  n number;v_count number:=0;v_qty number;v_target varchar2(60);v_type varchar2(30);v_status varchar2(30);v_ware number;v_remaining number;v_target_owned number;v_duplicates number;

 begin

  select count(*) into n from RRL_STOCK_RESERVATION where RESERVATION_ID=p_owner and UID_PALLET=p_uid and CELL=p_cell

   and RESERVATION_KIND='HARD' and STATUS in('ACTIVE','ALLOCATED','PICKING') and BASE_QTY>0;

  if n!=1 then return 0;end if;

  for sr in(select * from RRL_STOCK_RESERVATION where UID_PALLET=p_uid and CELL=p_cell

   and RESERVATION_KIND='HARD' and STATUS in('ACTIVE','ALLOCATED','PICKING') order by RESERVATION_ID fetch first 201 rows only) loop

   v_count:=v_count+1;if v_count>200 then raise_application_error(-20881,'SHARED_REPLENISHMENT_OWNER_BOUND');end if;

   if sr.RESERVATION_ID=p_owner then continue;end if;

   if sr.SOURCE_DOC_TYPE is null or sr.SOURCE_DOC_TYPE!='PICK_WAVE' or sr.RESERVATION_DOMAIN is null or sr.RESERVATION_DOMAIN!='PICKING'

    or sr.SOURCE_LINE_ID is null or sr.BASE_QTY is null or sr.BASE_QTY<=0 then return 0;end if;

   begin

    select t.TARGET_CELL_CODE,t.TASK_TYPE,t.STATUS,w.WARE_ID,greatest(t.QTY-nvl(t.FACT_QTY,0),0) into v_target,v_type,v_status,v_ware,v_remaining

     from RRL_PICK_TASK t join RRL_PICK_WAVE w on w.PICK_WAVE_ID=sr.SOURCE_DOC_ID

     where t.PICK_TASK_ID=sr.SOURCE_LINE_ID and w.STATUS='LAUNCHED' and t.ARTICUL=sr.ARTICUL and t.CUSTOMER_ORDER_ID=sr.CUSTOMER_ORDER_ID;

   exception when no_data_found then return 0;end;

   if v_target is null or v_target!=p_target or v_type!='CASE_PICK' or v_status not in('NEW','ASSIGNED','IN_PROGRESS')

    or v_ware!=p_ware then return 0;end if;

   select count(*) into v_duplicates from RRL_STOCK_RESERVATION

    where UID_PALLET=p_uid and CELL=p_cell and SOURCE_DOC_TYPE='PICK_WAVE' and SOURCE_DOC_ID=sr.SOURCE_DOC_ID

     and SOURCE_LINE_ID=sr.SOURCE_LINE_ID and RESERVATION_KIND='HARD' and STATUS in('ACTIVE','ALLOCATED','PICKING');

   if v_duplicates!=1 then return 0;end if;

   select nvl(sum(BASE_QTY),0) into v_target_owned from RRL_STOCK_RESERVATION

    where CELL=p_target and SOURCE_DOC_TYPE='PICK_WAVE' and SOURCE_DOC_ID=sr.SOURCE_DOC_ID and SOURCE_LINE_ID=sr.SOURCE_LINE_ID

     and RESERVATION_KIND='HARD' and STATUS in('ACTIVE','ALLOCATED','PICKING');

   if sr.BASE_QTY>greatest(0,v_remaining-v_target_owned) then return 0;end if;

  end loop;

  return 1;

 end;

end;


/
