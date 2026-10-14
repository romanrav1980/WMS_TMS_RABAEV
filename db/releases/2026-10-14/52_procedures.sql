set define off

CREATE OR REPLACE procedure        ADD_SFERA_EAN (
    row_uid out number,
    TMC_UID in varchar2,
    EAN_SHT varchar2,
    EAN_BL varchar2,
    EAN_KOR varchar2,
    MANUALENTER char,
    SHT_IN_BL integer,
    BL_IN_KOR integer,
    NAME varchar2
)
as
    legacy_uid_column varchar2(64) := '"' || unistr('\FFFD\FFFD\FFFD') || '"';
begin
    execute immediate
        'insert into RABAEV.SFERA_EAN (' ||
        legacy_uid_column ||
        ', TMC_UID, EAN_SHT, EAN_BL, EAN_KOR, MANUALENTER, SHT_IN_BL, BL_IN_KOR, NAME) ' ||
        'values (RABAEV.SFERA_EAN_ID.NEXTVAL, :1, :2, :3, :4, :5, :6, :7, :8)'
        using TMC_UID, EAN_SHT, EAN_BL, EAN_KOR, MANUALENTER, SHT_IN_BL, BL_IN_KOR, NAME;

    select RABAEV.SFERA_EAN_ID.CURRVAL into row_uid from dual;
end ADD_SFERA_EAN;
/


CREATE OR REPLACE procedure RRL_ACCEPT_ORDER2(order_id int) authid definer is
 state varchar2(20);
begin
 select STATE into state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if state='PREPARED' then RRL_ACCEPT_ORDER2_SP_OLD(order_id);return; end if;
 if state!='ACTIVE' then raise_application_error(-20885,'STOCK_RELEASE_NOT_ACTIVE');end if;
 raise_application_error(-20886,'SAP_SCANNED_RECEIPT_REQUIRED: use receiving.html?receipt_document_id='||to_char(order_id,'TM9')||'; reverse physical receipt with RRL_STORNO_ORDER3');
end;
/


CREATE OR REPLACE procedure RRL_ACCEPT_ORDER2_2(order_id int,user_id1 varchar2) authid definer is
 state varchar2(20);
begin
 select STATE into state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if state='PREPARED' then RRL_ACCEPT_ORDER2_2_SP_OLD(order_id,user_id1);return; end if;
 if state!='ACTIVE' then raise_application_error(-20885,'STOCK_RELEASE_NOT_ACTIVE');end if;
 raise_application_error(-20886,'SAP_SCANNED_RECEIPT_REQUIRED: use receiving.html?receipt_document_id='||to_char(order_id,'TM9')||'; reverse physical receipt with RRL_STORNO_ORDER3');
end;
/


CREATE OR REPLACE PROCEDURE        RRL_ACCEPT_ORDER2_2_SP_OLD (
 order_id int ,
 user_id1 varchar2
 )
accessible by(procedure RRL_ACCEPT_ORDER2_2) as
tmpVar NUMBER;
tmpdec NUMBER;
tmp_number_of_pallets int;
tmp_uid_pallet varChar2(50);
tmp_current_cond int;
articul_row_NORMA_UKLADKI int ;
infin int;
cursor dddd is

   SELECT RRL_PRIHOD_NAKLAD_ROWS.ARTICUL , RRL_PRIHOD_NAKLAD_ROWS.COUNT1 , RRL_PRIHOD_NAKLAD_ROWS.PRICE ,
  RRL_PRIHOD_NAKLAD_ROWS.EXPIRY_DATE , RRL_PRIHOD_NAKLAD_ROWS.ID  , RRL_ARTICULS.NORMA_UKLADKI , 
  RRL_ARTICULS.CELL  ,  ORDID , RRL_PRIHOD_NAKLAD_ROWS.KOLPAL CUSTOM_NU   FROM rabaev.RRL_PRIHOD_NAKLAD_ROWS
   left join rabaev.RRL_ARTICULS  on  RRL_PRIHOD_NAKLAD_ROWS.ARTICUL = RRL_ARTICULS.ACTICUL  where ORDID=order_id;
   
BEGIN

infin:=0;   
   DBMS_OUTPUT.put_line( 'flag 1'); 
   tmp_current_cond:=0;
   tmpVar := 0;
   tmp_number_of_pallets:=1;
   
   select condition into tmp_current_cond from  RABAEV.RRL_PRIHOD_NAKLAD  where ID = order_id  ;
   
   if  ( tmp_current_cond=2 ) or ( tmp_current_cond=1 ) then
        return;
   end if;
   
   DBMS_OUTPUT.put_line( 'flag 2'); 
   update RABAEV.RRL_PRIHOD_NAKLAD  set  condition=1  where ID = order_id  ;
   delete from RABAEV.RRL_PALLETS   where PRIHOD_NAKLAD_ID = order_id  ;



DBMS_OUTPUT.put_line( ' Hello 1 ');  
 for  articul_row in dddd loop
 
    if(infin>1000) then  return; end if;
 
    
 
 infin:=infin+1;
 DBMS_OUTPUT.put_line( articul_row.ARTICUL );
 
 tmp_number_of_pallets:=1;
 tmpVar:=articul_row.COUNT1;
 
 articul_row_NORMA_UKLADKI:=articul_row.NORMA_UKLADKI;
 
 if  ((not ( articul_row.CUSTOM_NU is null )) and ( articul_row.CUSTOM_NU >0 )) then
     articul_row_NORMA_UKLADKI:=articul_row.CUSTOM_NU ;
 end if;
 

    while tmpVar>0 loop
          begin
        
        if(infin>1000) then  return; end if;
        infin:=infin+1;
    
        if( articul_row_NORMA_UKLADKI<=0 ) then
            DBMS_OUTPUT.put_line( 'null' );
            return;
        end if;
        
    
    DBMS_OUTPUT.put_line( ' создается паллет ');  
    
             if( tmpVar<=articul_row_NORMA_UKLADKI ) then
                tmpdec:=tmpVar;
             else
                tmpdec:=articul_row_NORMA_UKLADKI;
             end if;
         
            tmp_uid_pallet := concat( concat( concat( concat (concat( 'P_' ,articul_row.ARTICUL) ,'_' ) , order_id ) , '_' ) , tmp_number_of_pallets )  ;
         
             delete from RABAEV.RRL_REMAINS where UID_POLETA=tmp_uid_pallet  ;
             delete from RABAEV.RRL_EVENTS where   UID_POLETA  =tmp_uid_pallet  ;
     
            insert into RABAEV.RRL_PALLETS ( UID_PALLET,
              ARTICUL ,
              CREATION_DATE ,
              EXPIRY_DATE ,
              UNIT_COUNT ,
              PRICE ,
              PRIHOD_NAKLAD_ID , kladovshik  ) values (
              tmp_uid_pallet ,
              articul_row.ARTICUL ,
              systimestamp  , 
              articul_row.EXPIRY_DATE , 
              tmpdec , 
              articul_row.PRICE , 
              order_id , user_id1
              );
            tmpVar:=tmpVar-tmpdec;
            tmp_number_of_pallets:=tmp_number_of_pallets+1;
            
            DBMS_OUTPUT.put_line( tmp_number_of_pallets);  
            
        end;
    end loop;

  end loop;


DBMS_OUTPUT.put_line( ' end ');  




end;
/


CREATE OR REPLACE PROCEDURE        RRL_ACCEPT_ORDER2_SP_OLD (
 order_id int 
 )
accessible by(procedure RRL_ACCEPT_ORDER2) as
tmpVar NUMBER;
tmpdec NUMBER;
tmp_number_of_pallets int;
tmp_uid_pallet varChar2(50);
tmp_current_cond int;
articul_row_NORMA_UKLADKI int ;

cursor dddd is

   SELECT RRL_PRIHOD_NAKLAD_ROWS.ARTICUL , RRL_PRIHOD_NAKLAD_ROWS.COUNT1 , RRL_PRIHOD_NAKLAD_ROWS.PRICE ,
  RRL_PRIHOD_NAKLAD_ROWS.EXPIRY_DATE , RRL_PRIHOD_NAKLAD_ROWS.ID  , RRL_ARTICULS.NORMA_UKLADKI , 
  RRL_ARTICULS.CELL  ,  ORDID , RRL_PRIHOD_NAKLAD_ROWS.KOLPAL CUSTOM_NU   FROM rabaev.RRL_PRIHOD_NAKLAD_ROWS
   left join rabaev.RRL_ARTICULS  on  RRL_PRIHOD_NAKLAD_ROWS.ARTICUL = RRL_ARTICULS.ACTICUL  where ORDID=order_id;
   
BEGIN
    
   tmp_current_cond:=0;
   tmpVar := 0;
   tmp_number_of_pallets:=1;
   
   select condition into tmp_current_cond from  RABAEV.RRL_PRIHOD_NAKLAD  where ID = order_id  ;
   
   if  ( tmp_current_cond=2 ) or ( tmp_current_cond=1 ) then
        return;
   end if;
   
   update RABAEV.RRL_PRIHOD_NAKLAD  set  condition=1  where ID = order_id  ;
   delete from RABAEV.RRL_PALLETS   where PRIHOD_NAKLAD_ID = order_id  ;



DBMS_OUTPUT.put_line( ' Hello 1 ');  
 for  articul_row in dddd loop
 
 DBMS_OUTPUT.put_line( articul_row.ARTICUL );
 
 tmp_number_of_pallets:=1;
 tmpVar:=articul_row.COUNT1;
 
 articul_row_NORMA_UKLADKI:=articul_row.NORMA_UKLADKI;
 
 if  ((not ( articul_row.CUSTOM_NU is null )) and ( articul_row.CUSTOM_NU >0 )) then
     articul_row_NORMA_UKLADKI:=articul_row.CUSTOM_NU ;
 end if;
 
 
    while tmpVar>0 loop
        begin
     
    

        
    
    DBMS_OUTPUT.put_line( ' создается паллет ');  
    
             if( tmpVar<=articul_row_NORMA_UKLADKI ) then
                tmpdec:=tmpVar;
             else
                tmpdec:=articul_row_NORMA_UKLADKI;
             end if;
         
            tmp_uid_pallet := concat( concat( concat( concat (concat( 'P_' ,articul_row.ARTICUL) ,'_' ) , order_id ) , '_' ) , tmp_number_of_pallets )  ;
        
             delete from RABAEV.RRL_REMAINS where UID_POLETA=tmp_uid_pallet  ;
             delete from RABAEV.RRL_EVENTS where   UID_POLETA  =tmp_uid_pallet  ;
     
            insert into RABAEV.RRL_PALLETS ( UID_PALLET,
              ARTICUL ,
              CREATION_DATE ,
              EXPIRY_DATE ,
              UNIT_COUNT ,
              PRICE ,
              PRIHOD_NAKLAD_ID   ) values (
              tmp_uid_pallet ,
              articul_row.ARTICUL ,
              articul_row.EXPIRY_DATE , 
              articul_row.EXPIRY_DATE , 
              tmpdec , 
              articul_row.PRICE , 
              order_id 
              );
            tmpVar:=tmpVar-tmpdec;
            tmp_number_of_pallets:=tmp_number_of_pallets+1;
            
            DBMS_OUTPUT.put_line( tmp_number_of_pallets);  
            
        end;
    end loop;

  end loop;


DBMS_OUTPUT.put_line( ' end ');  


commit;

end;
/


CREATE OR REPLACE procedure RRL_ACCEPT_ORDER3(order_id int,user_id1 varchar2) authid definer is
 state varchar2(20);
begin
 select STATE into state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if state='PREPARED' then RRL_ACCEPT_ORDER3_SP_OLD(order_id,user_id1);return; end if;
 if state!='ACTIVE' then raise_application_error(-20885,'STOCK_RELEASE_NOT_ACTIVE');end if;
 raise_application_error(-20886,'SAP_SCANNED_RECEIPT_REQUIRED: use receiving.html?receipt_document_id='||to_char(order_id,'TM9')||'; reverse physical receipt with RRL_STORNO_ORDER3');
end;
/


CREATE OR REPLACE PROCEDURE        RRL_ACCEPT_ORDER3_SP_OLD (
 order_id int ,
 user_id1 varchar2
 )
accessible by(procedure RRL_ACCEPT_ORDER3) as
tmpVar NUMBER;
event_id int ;

cursor dddd is

   SELECT UID_PALLET, ARTICUL , CREATION_DATE , EXPIRY_DATE , UNIT_COUNT , PRICE ,
    PRIHOD_NAKLAD_ID   FROM RRL_PALLETS  where PRIHOD_NAKLAD_ID=order_id;
   
   
BEGIN

update RABAEV.RRL_PRIHOD_NAKLAD  set  condition=2  where ID = order_id ;
 


    
    
     for  pallet_row in dddd loop
     
        select RRL_EVENT_ID_SQ.NEXTVAL into event_id from dual;
        event_id:=event_id+1;


         insert into RABAEV.RRL_EVENTS
            (  ID_EVENT ,  
            CELL_FROM , 
            CELL_TO    ,    
            DATE_EVENT  ,  
            DATE_OF_ORDER,   
            COUNT_EVENT   , 
            TYPE_EVENT  ,  
            UID_POLETA    ,
            USER_ID  ,  
            PRIHOD_NAKL_ID ) values (
          event_id ,
          'IN_ACCEPT',
          'IN_DOCK',
          pallet_row.CREATION_DATE , 
          pallet_row.CREATION_DATE , 
          pallet_row.UNIT_COUNT , 
          1 ,
          pallet_row.UID_PALLET ,
          user_id1 ,
          pallet_row.PRIHOD_NAKLAD_ID 
            );


      end loop;

commit;

end;
/


CREATE OR REPLACE procedure RRL_OTKAT_ORDER2(order_id int) authid definer is
 state varchar2(20);
begin
 select STATE into state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if state='PREPARED' then RRL_OTKAT_ORDER2_SP_OLD(order_id);return; end if;
 if state!='ACTIVE' then raise_application_error(-20885,'STOCK_RELEASE_NOT_ACTIVE');end if;
 raise_application_error(-20886,'SAP_SCANNED_RECEIPT_REQUIRED: use receiving.html?receipt_document_id='||to_char(order_id,'TM9')||'; reverse physical receipt with RRL_STORNO_ORDER3');
end;
/


CREATE OR REPLACE PROCEDURE        RRL_OTKAT_ORDER2_SP_OLD (
 order_id int 
 )
accessible by(procedure RRL_OTKAT_ORDER2) as

tmp_current_cond int;
tmp_v varchar2(50);
cursor dddd is

   SELECT   UID_PALLET  from RABAEV.RRL_PALLETS   where PRIHOD_NAKLAD_ID = order_id ;
   
BEGIN
    
   tmp_current_cond:=0;

   
   select condition into tmp_current_cond from  RABAEV.RRL_PRIHOD_NAKLAD  where ID = order_id  ;
   
   if  ( tmp_current_cond=2 )  then
        return;
   end if;
   
   update RABAEV.RRL_PRIHOD_NAKLAD  set  condition=0  where ID = order_id  ;
   
   if  ( tmp_current_cond=1 or tmp_current_cond=0 )  then
     delete from RABAEV.RRL_PALLETS   where PRIHOD_NAKLAD_ID = order_id  ;
   end if;


 for  articul_row in dddd loop
            tmp_v := articul_row.UID_PALLET ;
             delete from RABAEV.RRL_REMAINS where UID_POLETA= tmp_v ;
             delete from RABAEV.RRL_EVENTS where   UID_POLETA=tmp_v  ;
  end loop;



commit;

end;
/


CREATE OR REPLACE procedure RRL_STORNO_ORDER3(
 order_id int,user_id1 varchar2,p_operation_id varchar2 default null,p_reason varchar2 default 'Reverse incoming document')
authid definer as
 state varchar2(20);operation varchar2(100);j json_object_t:=json_object_t();s json_object_t:=json_object_t();m json_object_t:=json_object_t();result clob;
begin
 select STATE into state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if state='PREPARED' then RRL_STORNO_ORDER3_SP_OLD(order_id,user_id1);return;end if;
 operation:=nvl(p_operation_id,'RECEIPT.REVERSE:'||to_char(order_id,'TM9'));
 j.put('contract_version',2);j.put('operation_id',operation);j.put('command_type','RECEIPT_REVERSE');j.put('actor',user_id1);
 s.put('receipt_document_id',order_id);j.put('source',s);j.put('lines',json_array_t());j.put('units',json_array_t());
 m.put('reason',p_reason);j.put('metadata',m);
 RRL_STOCK_NATIVE_API.post(j.to_clob,user_id1,result);
end;
/


CREATE OR REPLACE PROCEDURE        RRL_STORNO_ORDER3_SP_OLD (
 order_id int ,
 user_id1 varchar2
 ) accessible by(procedure RRL_STORNO_ORDER3) as
tmpVar NUMBER;
event_id int ;

cursor dddd is

   SELECT UID_PALLET, ARTICUL , CREATION_DATE , EXPIRY_DATE , UNIT_COUNT , PRICE ,
    PRIHOD_NAKLAD_ID   FROM RRL_PALLETS  where PRIHOD_NAKLAD_ID=order_id;
   
   
BEGIN

if( RRL_PRIHOD_MAY_STORNO(order_id )=0 ) then 
    return;
end if;

update RABAEV.RRL_PRIHOD_NAKLAD  set  condition=3  where ID = order_id ;
    
    
     for  pallet_row in dddd loop
     
        select RRL_EVENT_ID_SQ.NEXTVAL into event_id from dual;
        event_id:=event_id+1;


         insert into RABAEV.RRL_EVENTS
            (  ID_EVENT ,  
            CELL_FROM , 
            CELL_TO    ,    
            DATE_EVENT  ,  
            DATE_OF_ORDER,   
            COUNT_EVENT   , 
            TYPE_EVENT  ,  
            UID_POLETA    ,
            USER_ID  ,  
            PRIHOD_NAKL_ID ) values (
          event_id ,
          'IN_ACCEPT',
          'IN_DOCK',
          pallet_row.CREATION_DATE , 
          pallet_row.CREATION_DATE , 
          ( (-1)*(pallet_row.UNIT_COUNT ) ) , 
          1 ,
          pallet_row.UID_PALLET ,
          user_id1 ,
          pallet_row.PRIHOD_NAKLAD_ID 
            );


      end loop;

commit;

end;
/


CREATE OR REPLACE procedure RRL_TARE_ASSERT_WRITE(p_table varchar2,p_key varchar2,p_kind varchar2) authid definer is
 op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');v_kind varchar2(80);v_state varchar2(20);
begin
 if op is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'TARE_ROOT_TRANSACTION_REQUIRED');end if;
 select COMMAND_TYPE,STATE into v_kind,v_state from RRL_STOCK_OPERATION where OPERATION_ID=op;
 if v_state!='IN_FLIGHT' or(v_kind!=p_kind and not(p_kind='COUNT_OR_ACCEPT' and v_kind in('TARE_COUNT','TARE_ACCEPT','TARE_DAMAGE','TARE_WRITE_OFF','TARE_BOOK','TARE_BOOK_CANCEL','TARE_LOSS_REPORT','TARE_LOSS_DECIDE')))then raise_application_error(-20863,'TARE_ROOT_COMMAND_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW',p_table,p_key));
end;
/


CREATE OR REPLACE PROCEDURE        RRL_TR_VEHICLE_DEL(p_id NUMBER) AS
BEGIN
    UPDATE RABAEV.RRL_TR_VEHICLE SET DELETED = 1 WHERE ID = p_id;
    IF SQL%ROWCOUNT = 0 THEN
        RAISE_APPLICATION_ERROR(-20099, 'Vehicle not found: ' || p_id);
    END IF;
END;
/


CREATE OR REPLACE PROCEDURE        RRL_TR_VEHICLE_UPDATE(
    p_id             NUMBER,
    p_num_plat       VARCHAR2,
    p_transtype_id   VARCHAR2,
    p_max_weight_kg  NUMBER,
    p_max_pallets    NUMBER,
    p_sobstvennyy    NUMBER,
    p_doverennost_ot VARCHAR2
) AS
BEGIN
    UPDATE RABAEV.RRL_TR_VEHICLE
       SET NUM            = p_num_plat,
           TR_TYPE        = p_transtype_id,
           MAX_WEIGHT_KG  = p_max_weight_kg,
           PALLETS        = p_max_pallets,
           SOBSTVENNYY    = p_sobstvennyy,
           DOVERENNOST_OT = p_doverennost_ot
     WHERE ID = p_id AND NVL(DELETED, 0) = 0;
    IF SQL%ROWCOUNT = 0 THEN
        RAISE_APPLICATION_ERROR(-20098, 'Vehicle not found: ' || p_id);
    END IF;
END;
/


CREATE OR REPLACE PROCEDURE        RRL_TR_VODITEL_DEL(p_id NUMBER) AS
BEGIN
    UPDATE RABAEV.RRL_TR_VODITEL SET DELETED = 1 WHERE ID = p_id;
    IF SQL%ROWCOUNT = 0 THEN
        RAISE_APPLICATION_ERROR(-20096, 'Driver not found: ' || p_id);
    END IF;
END;
/


CREATE OR REPLACE PROCEDURE        RRL_TR_VODITEL_UPDATE(
    p_id             NUMBER,
    p_name           VARCHAR2,
    p_phone          VARCHAR2,
    p_license_number VARCHAR2,
    p_company        VARCHAR2
) AS
BEGIN
    UPDATE RABAEV.RRL_TR_VODITEL
       SET F              = p_name,
           TEL            = p_phone,
           LICENSE_NUMBER = p_license_number,
           COMPANY        = p_company
     WHERE ID = p_id AND NVL(DELETED, 0) = 0;
    IF SQL%ROWCOUNT = 0 THEN
        RAISE_APPLICATION_ERROR(-20095, 'Driver not found: ' || p_id);
    END IF;
END;
/

