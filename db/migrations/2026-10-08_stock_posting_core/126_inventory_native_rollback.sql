create or replace FUNCTION        RRL_ADD_INV_LINE
(

    CELL5         varchar2 , 
    articul5      varchar2 ,
    COUNT15        number ,
    date_of_expire5  date ,
    PRICE5  number ,
    inventory_id  int , 
    iser_id5 varchar2

)
 RETURN varchar2 IS
tmpVar varchar2(150);
tmp_uid_pallet varchar2(150);
new_event_id int ;

BEGIN

   tmpVar := '';
   -- СОЗДАЕМ НОВЫЙ ПАЛЛЕТ С АРТИКУЛОМ И СРОКОМ ГОДНОСТИ
   
  tmp_uid_pallet := concat( concat( concat( concat (concat( 'P_' ,articul5) ,'_G' ) , inventory_id ) , '_' ) , CELL5 )  ;
   
 /*
  begin 
  
    select UID_PALLET into tmpVar from RABAEV.RRL_PALLETS  where  UID_PALLET = tmp_uid_pallet ;


  exception
  
  WHEN NO_DATA_FOUND THEN
      */
        insert into RABAEV.RRL_PALLETS
          (
              UID_PALLET        ,
              ARTICUL           ,
              CREATION_DATE     ,
              EXPIRY_DATE       ,
              UNIT_COUNT        ,
              PRICE             ,
              PRIHOD_NAKLAD_ID  )  values 
          (
              tmp_uid_pallet , 
              articul5,
              SYSTIMESTAMP ,
              date_of_expire5 ,
              COUNT15 ,
              PRICE5 , 
              -1* inventory_id
          )  ;
  
  --end;




   -- ЗАПИСЫВАЕМ ЕГО КОЛИЧЕСТВо В ЯЧЕЙКУ
   
    SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_id FROM dual;

                    insert into RABAEV.RRL_EVENTS ( ID_EVENT , 
                          CELL_FROM      ,
                          CELL_TO  ,
                          DATE_EVENT  ,
                          COUNT_EVENT ,
                          TYPE_EVENT ,
                          UID_POLETA ,
                          USER_ID    ,
                          OTHOD_NAKL_ID       
                      ) values ( 
                      new_event_id ,
                      'INVENT',
                      cell5,
                      SYSTIMESTAMP , 
                      COUNT15 ,
                      1,
                      tmp_uid_pallet ,
                      iser_id5 ,
                      ( -1* inventory_id )
                      ) ;
    
   
   -- ***************************************************
   
   
   RETURN tmpVar;
  
       
END RRL_ADD_INV_LINE;
/
