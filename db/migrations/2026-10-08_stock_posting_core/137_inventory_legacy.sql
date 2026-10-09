create or replace FUNCTION        RRL_INV_CREATE_LINE2_SP_OLD
( 
    cell1 varchar2 ,
    shk_art varchar2 , 
    articul_part varchar2,
    count1 NUMBER 
    
)
    RETURN varchar2 accessible by(function RRL_INV_CREATE_LINE2) IS 
    price Number;
    expiury_date date ;
    next_cell varchar2(255);
    tmp_cell varchar2(255);
    articul1 varchar2(255);
    NAKLAD_ID int;
    id1 int ;
    event_id int;
    pallet_name varchar2(255);
    
BEGIN
price:=1;
NAKLAD_ID:=1796;
expiury_date :=  to_date( '01.06.2010' , 'dd.mm.yyyy' );




    begin 
        select cell into tmp_cell from rrl_cells where cell=cell1;
    exception
            when NO_DATA_FOUND THEN
            return 'NO_CELL';
    end;


    begin 
        select ACTICUL into articul1 from RABAEV.RRL_ARTICULS where BARCODE_SHT=shk_art or BARCODE_KOR =shk_art or  BARCODE_BL=shk_art ;
       
        
    exception
            when NO_DATA_FOUND THEN
            begin       
                select ACTICUL into articul1 from RABAEV.RRL_ARTICULS where ACTICUL like  concat( '%' , articul_part ) ;
            exception
                when NO_DATA_FOUND THEN
                return 'NO_ARTICUL';
                WHEN OTHERS THEN
                return 'MORE_ARTICUL';
            end;
    end;


begin



pallet_name:= Concat( Concat( Concat('P_' , articul1 ) , '_G2_') , tmp_cell);
pallet_name:=replace(pallet_name , 'Т' ,'T' );






DBMS_OUTPUT.put_line(  pallet_name );
begin
insert into RABAEV.RRL_PALLETS
(
  UID_PALLET       ,
  ARTICUL           ,
  CREATION_DATE     ,
  EXPIRY_DATE       ,
  UNIT_COUNT        ,
  PRICE             ,
  PRIHOD_NAKLAD_ID  
)values
(
    pallet_name , 
    articul1 ,
    sysdate ,
    expiury_date ,
    count1 , 
    1,
    NAKLAD_ID
);
exception
when others then null;
end;


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
          tmp_cell ,
          expiury_date , 
          expiury_date , 
          count1 , 
          1 ,
          pallet_name ,
          'KLAD_VOSTRIKOV' ,
          NAKLAD_ID 
            );
exception
when others then
return 'ERR3';

end


commit;
next_cell:=RRL_GIVE_NEXT_CELL(cell1);
 
    RETURN next_cell;
    EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 'ERR1';
     WHEN OTHERS THEN
       
       RETURN 'ERR2';
END RRL_INV_CREATE_LINE2_SP_OLD;
/

create or replace FUNCTION        RRL_INV_CREATE_LINE3_SP_OLD
( 
    cell1 varchar2 ,
    shk_art varchar2 , 
    articul_part varchar2,
    count1 NUMBER ,
    UID_DOC int
)
    RETURN varchar2 accessible by(function RRL_INV_CREATE_LINE3) IS 
    price Number;
    expiury_date date ;
    next_cell varchar2(255);
    tmp_cell varchar2(255);
    articul1 varchar2(255);
    NAKLAD_ID int;
    id1 int ;
    event_id int;
    pallet_name varchar2(255);
    
BEGIN
price:=1;
NAKLAD_ID:=UID_DOC;
expiury_date :=  to_date( '01.06.2010' , 'dd.mm.yyyy' );




    begin 
        select cell into tmp_cell from rrl_cells where cell=cell1;
    exception
            when NO_DATA_FOUND THEN
            return 'NO_CELL';
    end;


    begin 
        select ACTICUL into articul1 from RABAEV.RRL_ARTICULS where BARCODE_SHT=shk_art or BARCODE_KOR =shk_art or  BARCODE_BL=shk_art ;
       
        
    exception
            when NO_DATA_FOUND THEN
            begin       
                select ACTICUL into articul1 from RABAEV.RRL_ARTICULS where ACTICUL like  concat( '%' , articul_part ) ;
            exception
                when NO_DATA_FOUND THEN
                return 'NO_ARTICUL';
                WHEN OTHERS THEN
                return 'MORE_ARTICUL';
            end;
    end;


begin



pallet_name:= Concat( Concat( Concat('P_' , articul1 ) , '_G2_') , tmp_cell);
pallet_name:=replace(pallet_name , 'Т' ,'T' );






DBMS_OUTPUT.put_line(  pallet_name );
begin
insert into RABAEV.RRL_PALLETS
(
  UID_PALLET       ,
  ARTICUL           ,
  CREATION_DATE     ,
  EXPIRY_DATE       ,
  UNIT_COUNT        ,
  PRICE             ,
  PRIHOD_NAKLAD_ID  
)values
(
    pallet_name , 
    articul1 ,
    sysdate ,
    expiury_date ,
    count1 , 
    1,
    NAKLAD_ID
);
exception
when others then null;
end;


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
          tmp_cell ,
          expiury_date , 
          expiury_date , 
          count1 , 
          1 ,
          pallet_name ,
          'KLAD_VOSTRIKOV' ,
          NAKLAD_ID 
            );
exception
when others then
return 'ERR3';

end


commit;
next_cell:=RRL_GIVE_NEXT_CELL(cell1);
 
    RETURN next_cell;
    EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 'ERR1';
     WHEN OTHERS THEN
       
       RETURN 'ERR2';
END RRL_INV_CREATE_LINE3_SP_OLD;
/

create or replace FUNCTION        RRL_INV_CREATE_LINE4_SP_OLD
( 
    cell1 varchar2 ,
    shk_art varchar2 , 
    articul_part varchar2,
    count1 NUMBER ,
    UID_DOC int,
    expiury_date date 
)
    RETURN varchar2 accessible by(function RRL_INV_CREATE_LINE4) IS 
    price Number;

    next_cell varchar2(255);
    tmp_cell varchar2(255);
    articul1 varchar2(255);
    NAKLAD_ID int;
    id1 int ;
    event_id int;
    pallet_name varchar2(255);
    
BEGIN
price:=1;
NAKLAD_ID:=UID_DOC;





    begin 
        select cell into tmp_cell from rrl_cells where cell=cell1;
    exception
            when NO_DATA_FOUND THEN
            return 'NO_CELL';
    end;


    begin 
        select ACTICUL into articul1 from RABAEV.RRL_ARTICULS where BARCODE_SHT=shk_art or BARCODE_KOR =shk_art or  BARCODE_BL=shk_art ;
       
        
    exception
            when NO_DATA_FOUND THEN
            begin       
                select ACTICUL into articul1 from RABAEV.RRL_ARTICULS where ACTICUL like  concat( '%' , articul_part ) ;
            exception
                when NO_DATA_FOUND THEN
                return 'NO_ARTICUL';
                WHEN OTHERS THEN
                return 'MORE_ARTICUL';
            end;
    end;


begin



pallet_name:= Concat( Concat( Concat('P_' , articul1 ) , '_G2_') , tmp_cell);
pallet_name:=replace(pallet_name , 'Т' ,'T' );






DBMS_OUTPUT.put_line(  pallet_name );
begin
insert into RABAEV.RRL_PALLETS
(
  UID_PALLET       ,
  ARTICUL           ,
  CREATION_DATE     ,
  EXPIRY_DATE       ,
  UNIT_COUNT        ,
  PRICE             ,
  PRIHOD_NAKLAD_ID  
)values
(
    pallet_name , 
    articul1 ,
    sysdate ,
    expiury_date ,
    count1 , 
    1,
    NAKLAD_ID
);
exception
when others then null;
end;


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
          tmp_cell ,
          expiury_date , 
          expiury_date , 
          count1 , 
          1 ,
          pallet_name ,
          'KLAD_VOSTRIKOV' ,
          NAKLAD_ID 
            );
exception
when others then
return 'ERR3';

end


commit;
next_cell:=RRL_GIVE_NEXT_CELL(cell1);
 
    RETURN next_cell;
    EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 'ERR1';
     WHEN OTHERS THEN
       
       RETURN 'ERR2';
END RRL_INV_CREATE_LINE4_SP_OLD;
/
