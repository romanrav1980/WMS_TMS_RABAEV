create or replace FUNCTION        RRL_UPDATE_SBORKA_PALLET_ROWS2(

PALLET_UID_to varchar2 ,
row_id_from int 


)
 RETURN INT 
 IS
 
PALLET_UID_from varchar2(255);
tmpVar int;
articul_temp varchar(255);
row_id_upd int;
count1 number;
count2 number;
tt varchar(200);

BEGIN
 declare release_state varchar2(20);op varchar2(100);kind varchar2(80);request clob;d json_object_t;src json_object_t;
  source_row RRL_SBORKA_PALLET_ROWS%rowtype;target_row RRL_SBORKA_PALLET_ROWS%rowtype;target_id number;source_id number;n number;actor_value varchar2(50);
 begin
  select STATE into release_state from RRL_STOCK_RELEASE where RELEASE_ID=1;
  if release_state='ACTIVE'then
   op:=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');
   if op is null then raise_application_error(-20863,'ST_ROW_MOVE_EXPLICIT_ROOT_REQUIRED');end if;
   select COMMAND_TYPE,CANONICAL_REQUEST into kind,request from RRL_STOCK_OPERATION where OPERATION_ID=op and STATE='IN_FLIGHT';
   d:=json_object_t.parse(request);src:=d.get_object('source');
   if kind!='ST_PREPARED_ROW_MOVE'or src.get_number('row_id')!=row_id_from then raise_application_error(-20863,'ST_ROW_MOVE_ROOT_SCOPE_REQUIRED');end if;
   select ID into target_id from RRL_SBORKA_PALLETS where PALLET_UID=PALLET_UID_to;
   if target_id!=src.get_number('target_shipment_id')then raise_application_error(-20863,'ST_ROW_MOVE_TARGET_SCOPE_REQUIRED');end if;
   select *into source_row from RRL_SBORKA_PALLET_ROWS where ID=row_id_from;
   select ID into source_id from RRL_SBORKA_PALLETS where PALLET_UID=source_row.PALLET_UID;
   RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_SBORKA_PALLETS',RRL_STOCK_PLAN_HELPER.decimal_text(source_id)));
   RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_SBORKA_PALLETS',RRL_STOCK_PLAN_HELPER.decimal_text(target_id)));
   RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_SBORKA_PALLET_ROWS',RRL_STOCK_PLAN_HELPER.decimal_text(row_id_from)));
   select count(*)into n from RRL_SBORKA_PALLET_ROWS where PALLET_UID=PALLET_UID_to and ARTICUL=source_row.ARTICUL;
   if n=0 then
    update RRL_SBORKA_PALLET_ROWS set PALLET_UID=PALLET_UID_to,SELECTED=1 where ID=row_id_from;
    tmpVar:=row_id_from;
   elsif n=1 then
    select *into target_row from RRL_SBORKA_PALLET_ROWS where PALLET_UID=PALLET_UID_to and ARTICUL=source_row.ARTICUL;
    RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_SBORKA_PALLET_ROWS',RRL_STOCK_PLAN_HELPER.decimal_text(target_row.ID)));
    update RRL_SBORKA_PALLET_ROWS set QUANTITY=QUANTITY+source_row.QUANTITY,ORDER_WEIGHT=ORDER_WEIGHT+source_row.ORDER_WEIGHT,
     PACK_COUNT=PACK_COUNT+source_row.PACK_COUNT,ORIGINAL_QUANTITY=nvl(ORIGINAL_QUANTITY,0)+nvl(source_row.ORIGINAL_QUANTITY,0),
     ORIGINAL_ORDER_WEIGHT=nvl(ORIGINAL_ORDER_WEIGHT,0)+nvl(source_row.ORIGINAL_ORDER_WEIGHT,0),SELECTED=1
     where ID=target_row.ID;
    delete from RRL_SBORKA_PALLET_ROWS where ID=row_id_from;tmpVar:=target_row.ID;
   else raise_application_error(-20887,'ST_ROW_MOVE_AMBIGUOUS_TARGET');end if;
   actor_value:=d.get_string('actor');
   update RRL_SBORKA_PALLETS set PROOVED_BY_SCAN=0,PROOVED=0,KLADOVSHIK=actor_value where ID in(source_id,target_id);
   return tmpVar;
  elsif release_state!='PREPARED'then raise_application_error(-20885,'STOCK_RELEASE_NOT_ACTIVE');end if;
 end;
   tmpVar := 0;
 
select PR.ARTICUL  ,  PR.QUANTITY   , PR.PALLET_UID  into articul_temp , count2 , PALLET_UID_from from RRL_SBORKA_PALLET_ROWS PR where PR.ID = row_id_from ;

    if( PALLET_UID_from= PALLET_UID_to ) then 
        return row_id_from;
    end if;
    

    begin
        --   СМОТРИМ В ПРЕДЫДУЩЕМ ПАЛЛЕТЕ . 
        select PR.ID , PR.QUANTITY into row_id_upd , count1  from RRL_SBORKA_PALLET_ROWS PR where PR.PALLET_UID = PALLET_UID_to and PR.ARTICUL = articul_temp  ;
        --update RRL_SBORKA_PALLET_ROWS PR  set   PR. , selected=1 where ID = row_id_from ;    
--       tt:= RRL_UPDATE_PALLET_ROW2( row_id_upd  ,    count1+count2 , 'MOVE' ); 
        tt:= RRL_UPDATE_PALLET_ROW2( articul_temp   ,  PALLET_UID_to  ,    count1+count2 , 'MOVE' ); 
        
        if( PALLET_UID_from <> PALLET_UID_to ) then 
            
            delete  from RRL_SBORKA_PALLET_ROWS   where  ID = row_id_from;
            
        end if;
        
    exception
        when no_data_found then
        -- Если в паллете, куда переностися строка нет таких артикулов.   
            update RRL_SBORKA_PALLET_ROWS  set  PALLET_UID = PALLET_UID_to , selected=1 where ID = row_id_from ;
        when others then RAISE;
          
    end;

   
   RETURN tmpVar;
    
END RRL_UPDATE_SBORKA_PALLET_ROWS2;
/
