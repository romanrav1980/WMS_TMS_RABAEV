create or replace FUNCTION        RRL_CLOSE_OTHOD_NAKLAD_SP_OLD

 -- ЗАКРЫВАЕТ ОТГРУЗОЧНУЮ НАКЛАДНУЮ 

(

    naklad_num int ,

    iser_id21 varchar2 

)

 RETURN varchar2 accessible by(function RRL_CLOSE_OTHOD_NAKLAD) IS

tmpVar int;

current_cell  varchar2(50);

kolvo_otbora NUMBER  ;

new_event_id int;

EXPEDITION_CELL varchar2(50);





cursor rowss is 

select * from RABAEV.RRL_OTHOD_NAKLAD_ROWS where ID_NAKLAD = naklad_num ;



--Определяем остатки в ячейке отбора в разрезе паллет, упорядоченных по срокам годности.

cursor rests_in_cell is

 select  RABAEV.RRL_REMAINS.REMAIN , RABAEV.RRL_REMAINS.UID_POLETA ,  RRL_PALLETS.EXPIRY_DATE 

  from RABAEV.RRL_REMAINS left join RABAEV.RRL_PALLETS on 

    RRL_REMAINS.UID_POLETA = RRL_PALLETS.UID_PALLET  

    where RRL_REMAINS.CELL = current_cell and RRL_REMAINS.REMAIN>0  order by RRL_PALLETS.EXPIRY_DATE  ; 





BEGIN



EXPEDITION_CELL:= concat( 'EX_' , naklad_num );

DBMS_OUTPUT.put_line(  'Начало' );



select condition into tmpVar from RABAEV.RRL_OTHOD_NAKLAD where ID = naklad_num;



if(tmpVar>=2) then   

    DBMS_OUTPUT.put_line(  'накладная закрыта' );

    return 'closed already';

end if;



/*

При закрытии отгрузочной накладной:

Для каждой строки: 

Определяем остатки в ячейке отбора в разрезе паллет, упорядоченных по срокам годности.

    Количество отбора - количество для отгрузки в накладную.



        по всем паллетам в ячейке отбора и пока Количество_отбора  > 0

            если количество_отбора <= количество в текущей ячейке тогда

                делаем проводку из данной паллеты на накладную в количестве Количество_отбора  

                Количество_отбора  =0

            иначе

                делаем проводку из данной паллеты на накладную в количестве = Количество_товара данной паллеты в данонй ячейке отбора  

                Количество_отбора  = Количество_отбора  - Количество_товара данной паллеты в данонй ячейке отбора  

            конец если



        конец цикла    

    

если Количество_отбора > 0 

    Делаем проводку из ячейки 'excess' на отгрузочную накладную

Количество_отбора  = 0

конец если

*/





for naklad_row in rowss loop



tmpVar:=0;

kolvo_otbora:=naklad_row.COUNT1;





    DBMS_OUTPUT.put_line(  '  НОВАЯ СТРОКА НАКЛАДНОЙ!' );

   DBMS_OUTPUT.put_line(  naklad_row.ARTICUL );



    select CELL into  current_cell from  RABAEV.RRL_ARTICULS 

    where RRL_ARTICULS.ACTICUL=naklad_row.ARTICUL ;

    

    DBMS_OUTPUT.put_line(  '  ЯЧЕЙКА ОТБОРА=' );

    DBMS_OUTPUT.put_line(  current_cell );

    



    for  ddd8 in rests_in_cell loop

-- REMAIN

    

        DBMS_OUTPUT.put_line(  '  НОВАЯ СТРОКА ОСТАТКОВ ' );

        DBMS_OUTPUT.put_line(   ddd8.REMAIN );

        DBMS_OUTPUT.put_line(   ddd8.EXPIRY_DATE );

        DBMS_OUTPUT.put_line(   ddd8.UID_POLETA );

         DBMS_OUTPUT.put_line(  '  количество отбора= ' );     

         DBMS_OUTPUT.put_line(  kolvo_otbora );  

          

        

        if(kolvo_otbora>0) then

/*

        по всем паллетам в ячейке отбора и пока Количество_отбора  > 0

        

            если количество_отбора <= количество в текущей ячейке тогда

                делаем проводку из данной паллеты на накладную в количестве Количество_отбора  

                Количество_отбора  =0

            иначе

                делаем проводку из данной паллеты на накладную в количестве = Количество_товара данной паллеты в данонй ячейке отбора  

                Количество_отбора  = Количество_отбора  - Количество_товара данной паллеты в данонй ячейке отбора  

            конец если



        конец цикла  

*/          

            if(kolvo_otbora <= ddd8.REMAIN )  then

                -- UID_POLETA

                

                

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

                      ) values ( new_event_id ,

                      current_cell,

                      EXPEDITION_CELL,

                      SYSTIMESTAMP , 

                      kolvo_otbora ,

                      2,

                      ddd8.UID_POLETA ,

                      iser_id21 ,

                      naklad_num

                      ) ;

                    kolvo_otbora:=0;

                else

                  SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_id FROM dual;

                -- делаем проводку из данной паллеты на накладную в количестве = Количество_товара данной паллеты в данонй ячейке отбора  

                -- Количество_отбора  = Количество_отбора  - Количество_товара данной паллеты в данонй ячейке отбора  

                    insert into RABAEV.RRL_EVENTS ( ID_EVENT , 

                          CELL_FROM      ,

                          CELL_TO  ,

                          DATE_EVENT  ,

                          COUNT_EVENT ,

                          TYPE_EVENT ,

                          UID_POLETA ,

                          USER_ID    ,

                          OTHOD_NAKL_ID       

                      ) values ( new_event_id,

                      current_cell, 

                      EXPEDITION_CELL,

                      SYSTIMESTAMP , 

                      ddd8.REMAIN ,

                      2,

                      ddd8.UID_POLETA ,

                      iser_id21 ,

                      naklad_num

                      ) ;

                      

                    kolvo_otbora:=kolvo_otbora-ddd8.REMAIN;

                

                

            end if;      



   

        end if;

    end loop;





         DBMS_OUTPUT.put_line(  '  почти конец ' );   

         DBMS_OUTPUT.put_line(  '  количество отбора= ' );     

         DBMS_OUTPUT.put_line(  kolvo_otbora );  



--если Количество_отбора > 0 

--    Делаем проводку из ячейки 'excess' на отгрузочную накладную

--Количество_отбора  = 0

--конец если

if(kolvo_otbora >0 )  then

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

                      ) values ( new_event_id ,

                      'EXCESS',

                      EXPEDITION_CELL,

                      SYSTIMESTAMP , 

                      kolvo_otbora ,

                      2,

                     concat( 'EXCESS_' , naklad_row.ARTICUL ) ,

                      iser_id21 ,

                      naklad_num

                      ) ;

kolvo_otbora:=0;

end if;



   DBMS_OUTPUT.put_line(  '  почти конец ' );   



end loop;



update  RABAEV.RRL_OTHOD_NAKLAD set condition = 2  where ID = naklad_num;

   DBMS_OUTPUT.put_line(  '  СОВСЕМ конец ' );   





commit;



   RETURN 'ok';

END RRL_CLOSE_OTHOD_NAKLAD_SP_OLD;
/

create or replace FUNCTION        RRL_CLOSE_OTHOD_PALLET_SP_OLD

 -- ЗАКРЫВАЕТ ОТГРУЗОЧНУЮ НАКЛАДНУЮ 

(

    PALLET_ID1 varchar2 ,

    iser_id21 varchar2 

)



 RETURN varchar2 accessible by(function RRL_CLOSE_OTHOD_PALLET) IS

tmpVar int;

current_cell  varchar2(50);

kolvo_otbora NUMBER  ;

new_event_id int;

EXPEDITION_CELL varchar2(50);

PALLET_ROW_ID1 int;



cursor rowss is 

select * from RABAEV.RRL_SBORKA_PALLET_ROWS where PALLET_UID = PALLET_ID1 and QUANTITY>0 ;



--Определяем остатки в ячейке отбора в разрезе паллет, упорядоченных по срокам годности.

cursor rests_in_cell is

 select  RABAEV.RRL_REMAINS.REMAIN , RABAEV.RRL_REMAINS.UID_POLETA ,  RRL_PALLETS.EXPIRY_DATE 

  from RABAEV.RRL_REMAINS , RABAEV.RRL_PALLETS  

     

    where RRL_REMAINS.UID_POLETA = RRL_PALLETS.UID_PALLET and

     RRL_REMAINS.CELL = current_cell and RRL_REMAINS.REMAIN>0  

     order by RRL_PALLETS.EXPIRY_DATE  ; 





BEGIN



 

DBMS_OUTPUT.put_line(  'Начало' );



select condition into tmpVar from RABAEV.RRL_SBORKA_PALLETs where PALLET_UID = PALLET_ID1;



if(tmpVar>=2) then   

    DBMS_OUTPUT.put_line(  'накладная закрыта' );

    return 'closed already';

end if;



/*

При закрытии отгрузочной паллеты:

Для каждой строки: 

Определяем остатки в ячейке отбора в разрезе паллет, упорядоченных по срокам годности.

    Количество отбора - количество для отгрузки в накладную.



        по всем паллетам в ячейке отбора и пока Количество_отбора  > 0

            если количество_отбора <= количество в текущей ячейке тогда

                делаем проводку из данной паллеты на строку паллета в количестве Количество_отбора  

                Количество_отбора  =0

            иначе

                делаем проводку из данной паллеты на накладную в количестве = Количество_товара данной паллеты в данонй ячейке отбора  

                Количество_отбора  = Количество_отбора  - Количество_товара данной паллеты в данонй ячейке отбора  

            конец если



        конец цикла    

    

если Количество_отбора > 0 

    Делаем проводку из ячейки 'excess' на отгрузочную накладную

Количество_отбора  = 0

конец если

*/





for naklad_row in rowss loop





PALLET_ROW_ID1:= naklad_row.ID;



tmpVar:=0;

kolvo_otbora:=naklad_row.QUANTITY;









   DBMS_OUTPUT.put_line(  '  НОВАЯ СТРОКА ПАЛЛЕТЫ ОТГРУЗКИ!' );

   DBMS_OUTPUT.put_line(  naklad_row.ARTICUL );



    select CELL into  current_cell from  RABAEV.RRL_ARTICULS  where RRL_ARTICULS.ACTICUL=naklad_row.ARTICUL ;

    

    DBMS_OUTPUT.put_line(  '  ЯЧЕЙКА ОТБОРА=' );

    DBMS_OUTPUT.put_line(  current_cell );

    



    for  ddd8 in rests_in_cell loop

-- REMAIN

    

        update RABAEV.RRL_SBORKA_PALLET_ROWS set PRIHOD_PALLET_UID = ddd8.UID_POLETA where ID = naklad_row.ID ; 

        update RABAEV.RRL_SBORKA_PALLET_ROWS set EXPIRY_DATE = ddd8.EXPIRY_DATE where ID = naklad_row.ID ; 

        

    

        DBMS_OUTPUT.put_line(  '  НОВАЯ СТРОКА ОСТАТКОВ ' );

        DBMS_OUTPUT.put_line(  ddd8.REMAIN );

        DBMS_OUTPUT.put_line(  ddd8.EXPIRY_DATE );

        DBMS_OUTPUT.put_line(  ddd8.UID_POLETA );

        DBMS_OUTPUT.put_line(  '  количество отбора1= ' );     

        DBMS_OUTPUT.put_line(  kolvo_otbora );  

          

        

        if(kolvo_otbora>0) then

/*

        по всем паллетам в ячейке отбора и пока Количество_отбора  > 0

        

            если количество_отбора <= количество в текущей ячейке тогда

                делаем проводку из данной паллеты на накладную в количестве Количество_отбора  

                Количество_отбора  =0

            иначе

                делаем проводку из данной паллеты на накладную в количестве = Количество_товара данной паллеты в данонй ячейке отбора  

                Количество_отбора  = Количество_отбора  - Количество_товара данной паллеты в данонй ячейке отбора  

            конец если



        конец цикла  

*/          DBMS_OUTPUT.put_line(  CONCAT( 'REMAIN = ' , ddd8.REMAIN )  );

            if(kolvo_otbora <= ddd8.REMAIN )  then

               

                

                

                 SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_id FROM dual;

                

                

                    insert into RABAEV.RRL_EVENTS ( ID_EVENT , 

                          CELL_FROM      ,

                          CELL_TO  ,

                          DATE_EVENT  ,

                          COUNT_EVENT ,

                          TYPE_EVENT ,

                          UID_POLETA ,

                          USER_ID    ,

                          PALLET_ROW_ID       

                      ) values ( new_event_id ,

                      current_cell,

                      EXPEDITION_CELL,

                      SYSTIMESTAMP , 

                      kolvo_otbora ,

                      3,

                      ddd8.UID_POLETA ,

                      iser_id21 ,

                      PALLET_ROW_ID1

                      ) ;

                    kolvo_otbora:=0;

                else

                  SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_id FROM dual;

                -- делаем проводку из данной паллеты на накладную в количестве = Количество_товара данной паллеты в данонй ячейке отбора  

                -- Количество_отбора  = Количество_отбора  - Количество_товара данной паллеты в данонй ячейке отбора  

                    insert into RABAEV.RRL_EVENTS ( ID_EVENT , 

                          CELL_FROM      ,

                          CELL_TO  ,

                          DATE_EVENT  ,

                          COUNT_EVENT ,

                          TYPE_EVENT ,

                          UID_POLETA ,

                          USER_ID    ,

                          PALLET_ROW_ID       

                      ) values ( new_event_id,

                      current_cell, 

                      EXPEDITION_CELL,

                      SYSTIMESTAMP , 

                      ddd8.REMAIN ,

                      3,

                      ddd8.UID_POLETA ,

                      iser_id21 ,

                      PALLET_ROW_ID1

                      ) ;

                      

                    kolvo_otbora:=kolvo_otbora-ddd8.REMAIN;

                

                

            end if;      



   

        end if;

    end loop;





         DBMS_OUTPUT.put_line(  '  почти конец ' );   

         DBMS_OUTPUT.put_line(  '  количество отбора2= ' );     

         DBMS_OUTPUT.put_line(  kolvo_otbora );  



--если Количество_отбора > 0 

--    Делаем проводку из ячейки 'excess' на отгрузочную накладную

--Количество_отбора  = 0

--конец если

if(kolvo_otbora >0 )  then

                     SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_id FROM dual;

                      insert into RABAEV.RRL_EVENTS ( ID_EVENT , 

                          CELL_FROM      ,

                          CELL_TO  ,

                          DATE_EVENT  ,

                          COUNT_EVENT ,

                          TYPE_EVENT ,

                          UID_POLETA ,

                          USER_ID    ,

                          PALLET_ROW_ID       

                      ) values ( new_event_id ,

                      current_cell,

                      'MINUS',

                      SYSTIMESTAMP , 

                      kolvo_otbora ,

                      3,

                      'MINUS'   ,

                      iser_id21 ,

                      PALLET_ROW_ID1

                      ) ;

kolvo_otbora:=0;

end if;



   DBMS_OUTPUT.put_line(  '  почти конец ' );   



end loop;



update   RABAEV.RRL_SBORKA_PALLETs  set condition = 2  where   PALLET_UID = PALLET_ID1;









   DBMS_OUTPUT.put_line(  '  СОВСЕМ конец ' );   

   RETURN 'ok';



exception 

when no_data_found then  return 'neok';

when others then raise;





END RRL_CLOSE_OTHOD_PALLET_SP_OLD;
/
