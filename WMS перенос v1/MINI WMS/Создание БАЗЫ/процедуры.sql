DROP PROCEDURE RABAEV.ADD_SFERA_EAN;

CREATE OR REPLACE PROCEDURE RABAEV.ADD_SFERA_EAN (
    row_uid OUT NUMBER,
    TMC_UID IN VARCHAR2,
      EAN_SHT      VARCHAR2 ,
  EAN_BL       VARCHAR2 ,
  EAN_KOR      VARCHAR2 ,
  MANUALENTER  CHAR,
  SHT_IN_BL    INTEGER,
  BL_IN_KOR    INTEGER,
  NAME         VARCHAR2   
)
AS
BEGIN
    INSERT INTO RABAEV.SFERA_EAN (
      УИД,
      TMC_UID    , 
      EAN_SHT    ,
      EAN_BL      , 
      EAN_KOR     ,
      MANUALENTER  ,
      SHT_IN_BL   ,
      BL_IN_KOR    ,
      NAME    
  ) VALUES (
          RABAEV.SFERA_EAN_ID.NEXTVAL,
          TMC_UID     ,
          EAN_SHT    ,
          EAN_BL      , 
          EAN_KOR     ,
          MANUALENTER  ,
          SHT_IN_BL   ,
          BL_IN_KOR    ,
          NAME    
    );
    
    
    SELECT SFERA_EAN_ID.CURRVAL INTO row_uid FROM DUAL;
    
END  ADD_SFERA_EAN;
/


DROP PROCEDURE RABAEV.RRL_ACCEPT_ORDER2;

CREATE OR REPLACE PROCEDURE RABAEV.RRL_ACCEPT_ORDER2 (
 order_id int 
 )
as
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
   -- Каждую строчку накладной : Создать множество паллет, 
   -- По каждой паллете сделать проводку, поместив ее в зону "ПРИЕМКИ".
/


DROP PROCEDURE RABAEV.RRL_ACCEPT_ORDER2_2;

CREATE OR REPLACE PROCEDURE RABAEV.RRL_ACCEPT_ORDER2_2 (
 order_id int ,
 user_id1 varchar2
 )
as
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


--commit;

end;
   -- Каждую строчку накладной : Создать множество паллет, 
   -- По каждой паллете сделать проводку, поместив ее в зону "ПРИЕМКИ".
/


DROP PROCEDURE RABAEV.RRL_ACCEPT_ORDER3;

CREATE OR REPLACE PROCEDURE RABAEV.RRL_ACCEPT_ORDER3 (
 order_id int ,
 user_id1 varchar2
 )
as
tmpVar NUMBER;
event_id int ;

cursor dddd is

   SELECT UID_PALLET, ARTICUL , CREATION_DATE , EXPIRY_DATE , UNIT_COUNT , PRICE ,
    PRIHOD_NAKLAD_ID   FROM RRL_PALLETS  where PRIHOD_NAKLAD_ID=order_id;
   
   
BEGIN

update RABAEV.RRL_PRIHOD_NAKLAD  set  condition=2  where ID = order_id ;
 

-- dbms_output.put_line('n='||event_id);
    
    
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
   -- По каждой паллете сделать проводку, поместив ее в зону "ПРИЕМКИ".
/


DROP PROCEDURE RABAEV.RRL_OTKAT_ORDER2;

CREATE OR REPLACE PROCEDURE RABAEV.RRL_OTKAT_ORDER2 (
 order_id int 
 )
as

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


DROP PROCEDURE RABAEV.RRL_STORNO_ORDER3;

CREATE OR REPLACE PROCEDURE RABAEV.RRL_STORNO_ORDER3 (
 order_id int ,
 user_id1 varchar2
 )
as
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
   -- По каждой паллете сделать проводку, удалив ее из зоны "ПРИЕМКИ".
/


