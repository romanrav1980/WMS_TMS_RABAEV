declare n number;begin select count(*) into n from RRL_STOCK_OPERATION;if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_ROLLBACK');end if;end;
/
create or replace FUNCTION        RRL_INTERNAL_MOVE2(

pallet_id varchar2 , 

cell_to varchar2 ,

count1 number ,

user_id1 varchar2

)



RETURN varchar2



IS

count2 number;

tmpVar NUMBER;

art1 varchar2(50) ;

is_otbor int;

remain_in_cell_to number;

checks_passed int;

cell_from1 varchar2(50);

cell_next varchar2(50);

debug_mode int;

new_event_uid int;



prihod_cond int;

cursor rrr is select * from RRL_REMAINS where CELL = cell_to;



BEGIN

    

prihod_cond:=0;

count2:=count1;

   debug_mode:=0;

   tmpVar := 0;

   is_otbor:=0;

   remain_in_cell_to:=0;

   checks_passed:=0;

   cell_from1:='NONE';









 -- ЕСЛИ списание на НЕДОСТАЧУ

if  ( pallet_id='NO_PALLET' ) then



    begin

        for fgr in rrr  loop

        --

             SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_uid  FROM dual;



            insert into RABAEV.RRL_EVENTS ( ID_EVENT , CELL_TO , CELL_FROM , DATE_EVENT ,  COUNT_EVENT ,

             TYPE_EVENT , UID_POLETA , USER_ID ) values

            ( new_event_uid , 'INVENT'  , fgr.CELL , SYSTIMESTAMP , fgr.REMAIN , 2 , fgr.UID_POLETA , user_id1  );



        --

        end loop;

     exception

        WHEN NO_DATA_FOUND THEN

                    NULL;

         WHEN OTHERS THEN

                    NULL;

    

    end;



    cell_next:=RABAEV.RRL_GIVE_NEXT_CELL(CELL_TO);

    RETURN CONCAT('ok_' ,  cell_next );

end if;





-- ОПРЕДЕЛЯЕМ - НЕ НАХОДИТСЯ ЛИ НАКЛАДНАЯ ДАННОГО ПАЛЛЕТА В ЧЕРНОВИКЕ?

begin

    select N.CONDITION into prihod_cond from RABAEV.RRL_PALLETS  PP , RABAEV.RRL_PRIHOD_NAKLAD N   where  PP.PRIHOD_NAKLAD_ID = N.ID  and PP.UID_PALLET = pallet_id;



    if( (prihod_cond=1) or (prihod_cond=0) ) then

        return 'NAKLAD_NE_ZAKRYTA';

    end if;



   exception

        WHEN NO_DATA_FOUND THEN

                    NULL;

         WHEN OTHERS THEN

                    NULL; 

    

end;









    begin  --  СНАЧАЛА ИЩЕМ - ЕСТЬ - ЛИ ТАКОЙ ПАЛЛЕТ КУДА

    



    select cell into cell_from1 from  RABAEV.RRL_REMAINS  where UID_POLETA=pallet_id and cell<>cell_to group by cell ;

  -- select cell into cell_from1 from  RABAEV.RRL_REMAINS  where UID_POLETA=pallet_id  group by cell ;







        if(count2=0) then

            select remain into count2 from  RABAEV.RRL_REMAINS  where UID_POLETA=pallet_id and cell=cell_from1 ;

        end if;



    exception

        WHEN NO_DATA_FOUND THEN

        

        update RABAEV.RRL_REMAINS RRR set RRR.TIME_OF_LAST_UPDATE = SYSTIMESTAMP where   

        UID_POLETA=pallet_id and cell=cell_to;

         

            cell_next:=RABAEV.RRL_GIVE_NEXT_CELL(CELL_TO);

            RETURN CONCAT('ok_' ,  cell_next );

        



         WHEN OTHERS THEN

            begin

            

                    begin

                    -- ПОПРОБУЕМ ИСКЛЮЧИТЬ ОТБОР ИЗ ПОИСКА

                    select  RABAEV.RRL_REMAINS.cell into cell_from1 from  RABAEV.RRL_REMAINS , RABAEV.RRL_CELLS  where

                         ( RABAEV.RRL_REMAINS.UID_POLETA=pallet_id) and ( RRL_REMAINS.CELL = RRL_CELLS.CELL ) and ( RRL_CELLS.OTBOR=0 ) and ( RRL_CELLS.cell<>cell_to )  ;

                    exception

                

                        WHEN NO_DATA_FOUND THEN

                            return 'pallet byl otgruzen';

                        WHEN OTHERS THEN null;

                        --    return 'other pallet3';

                    end;



                         

                    if(count2=0) then

                        select remain into count2 from  RABAEV.RRL_REMAINS  where UID_POLETA=pallet_id and cell=cell_from1 ;

                    end if;

                    





                    

            exception

            

                WHEN NO_DATA_FOUND THEN

                    return 'other pallet1';

                WHEN OTHERS THEN

                    return 'other pallet2';

            end;

         

            

    end;

    



if( cell_to=cell_from1 ) then 

    return 'cell_to=cell_from1';

end if;   

    



    if(count2=0) then

        return 'count2=0';

    end if;



begin

    -- ЕСЛИ ПАЛЛЕТ ЕСТЬ, ПРОВЕРЯЕМ ЧТО ЯЧЕЙКА НАЗНАЧЕНИЯ = ЯЧЕЙКА ОТБОРА, ЛИБО 

    --  СВОБОДНА ( ОСТАТКОВ В НЕЙ НЕТ, РЕЗЕРВА НЕТ ) 

    select OTBOR into is_otbor from RABAEV.RRL_CELLS where CELL=cell_to ;

exception

         WHEN NO_DATA_FOUND THEN

           return 'no_pallet_cell_to';

         WHEN OTHERS THEN

           return 'other pallet1';

end;





if ( (is_otbor=0) and (cell_to<>'TRASH') and (cell_to<>'IN_DOCK') )  then



    begin

        select sum(REMAIN) into remain_in_cell_to from  RABAEV.RRL_REMAINS  where CELL=cell_to ;

    exception

             WHEN NO_DATA_FOUND THEN

               remain_in_cell_to:=0;

             WHEN OTHERS THEN

               remain_in_cell_to:=0;

    end;



    if remain_in_cell_to is null then

    remain_in_cell_to:=0;

    end if;



    if(remain_in_cell_to<=0)  then

        checks_passed:=1;

    else

    return 'cell_not_empty';    

    end if;



else

    checks_passed:=1;

end if;



        

    --  ЕСЛИ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ, ТО: 

    -- делаем запись таблицы RRL_EVENTS cell_to , cell_from ,date_event , count_event

    -- type_event = 2 , UID_POLETA , USER_ID



    if( checks_passed=0 ) then

     return 'fault';

    end if;

    



  SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_uid  FROM dual;



insert into RABAEV.RRL_EVENTS ( ID_EVENT , CELL_TO , CELL_FROM , DATE_EVENT ,  COUNT_EVENT ,

 TYPE_EVENT , UID_POLETA , USER_ID ) values

( new_event_uid , cell_to  , cell_from1 , SYSTIMESTAMP , count2 , 2 , pallet_id , user_id1  );



-- ОПРЕДЕЛЯЕМ ЯЧЕЙКУ, СЛЕДУЮЩУЮ ЗА ТЕКУЩЕЙ



commit;



cell_next:=RABAEV.RRL_GIVE_NEXT_CELL(CELL_TO);





   RETURN CONCAT('ok_' ,  cell_next );

      

   EXCEPTION

     WHEN NO_DATA_FOUND THEN

       return 'err1';

     WHEN OTHERS THEN

       return 'err2';

END RRL_INTERNAL_MOVE2;
/

create or replace FUNCTION        RRL_INTERNAL_MOVE3(

pallet_id varchar2 , 

cell_to varchar2 ,

count1 number ,

user_id1 varchar2

)

-- ПРОЦЕДУРА ВНУТРЕННЕГО ПЕРЕМЕЩЕНИЯ 

-- ЕСЛИ ПЕРЕМЕЩЕНИЕ ИДЕТ В ЯЧЕЙКУ ОТБОРА, ТО КОНТРОЛИРУЕТСЯ 

--  - ЯВЛЯЕТСЯ ЛИ ДАННАЯ ЯЧЕЙКА РОДНОЙ ДЛЯ ДАННОГО ТОВАРА 



RETURN varchar2



IS

count2 number;

tmpVar NUMBER;

tmpVar2 varchar(250);

art1 varchar2(50) ;

is_otbor int;

remain_in_cell_to number;

checks_passed int;

cell_from1 varchar2(50);

cell_next varchar2(150);

dummy1 varchar(500);

dummy2 varchar(500);



articul1 varchar2(250);

cell_otbora_for_pallet varchar2(50);

ware_id_to int;

debug_mode int;

new_event_uid int;

SPIS_IF_HRAN_NO_EMPTY1 varchar(100);

data_spisania Date ;

alternative_puid varchar2(400);

alternative_cell varchar2(400);

alternative_date date;

rret varchar2(500);

helv varchar2(500);



user_group1 varchar2(500);

weight_limit_warning1 int;

WEIGHT_LIMIT_STOP1 int;

weight_of_cell_to number;

PRIEMPALLET_WEIGHT1 number;

prihod_cond int;

cursor rrr is select * from RRL_REMAINS where CELL = cell_to;

cursor rrr2 is select * from  RABAEV.RRL_REMAINS  where CELL=cell_to ;



BEGIN

    



begin

    select rusers.USER_GROUP into user_group1 from rusers where rusers.ID=user_group1 ;

exception 

        when no_data_found then null;

        when others then null;

end;







    begin -- ФИКСИРУЕМ ВРЕМЯ ПОСЛЕДНЕГО ДОСТУПА К ЯЧЕЙКЕ        

        update rrl_cells set LAST_TIME_OF_UPDATE= SYSTIMESTAMP where CELL=cell_to;

    exception        

        when no_data_found then null;

        when others then null;

    end;





select ware_id into ware_id_to from RABAEV.rrl_cells CC where CC.cell =  cell_to;

articul1:=null;



DBMS_OUTPUT.put_line( 'Начало' );



if( pallet_id<>'NO_PALLET' ) then



    begin

        select PA.ARTICUL into articul1 from  RABAEV.RRL_PALLETS  PA where PA.UID_PALLET=pallet_id;

    exception

    when no_data_found then 

        helv:= Concat( 'отсутствует паллет ' , concat( pallet_id , concat( ' ячейка=' , cell_to) ) ) ; 

        insert into rrl_error_log ( error , datet  ,user_id ) values ( helv , systimestamp , user_id1 ) ;

        DBMS_OUTPUT.put_line( 'ошибка 0 типа' );

        return 'Pallet Udalen. I2';

    when others then 

        DBMS_OUTPUT.put_line( 'ошибка 1 типа' );

    end;



end if;



DBMS_OUTPUT.put_line( articul1 );



DBMS_OUTPUT.put_line( 'Флаг1' );





   prihod_cond:=0;

   count2:=count1;

   debug_mode:=0;

   tmpVar := 0;

   is_otbor:=0;

   remain_in_cell_to:=0;

   checks_passed:=0;

   cell_from1:='NONE';

   weight_limit_warning1:=0; -- Настройка - предупреждать - ли в случае превышения веса

   PRIEMPALLET_WEIGHT1 := 0; -- Вес перемещаемого товара

   WEIGHT_LIMIT_STOP1 := 0;







 -- ЕСЛИ списание на НЕДОСТАЧУ

if  ( pallet_id='NO_PALLET' ) then



    begin

        for fgr in rrr  loop

        --

             SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_uid  FROM dual;



            insert into RABAEV.RRL_EVENTS ( ID_EVENT , CELL_TO , CELL_FROM , DATE_EVENT ,  COUNT_EVENT ,

             TYPE_EVENT , UID_POLETA , USER_ID ) values

            ( new_event_uid , 'INVENT'  , fgr.CELL , SYSTIMESTAMP , fgr.REMAIN , 2 , fgr.UID_POLETA , user_id1  );



        --

        end loop;

     exception

        WHEN NO_DATA_FOUND THEN

                    NULL;

         WHEN OTHERS THEN

                    NULL;

    

    end;



    cell_next:=RABAEV.RRL_GIVE_NEXT_CELL(CELL_TO);

    RETURN CONCAT('ok_' ,  cell_next );

end if;





-- ОПРЕДЕЛЯЕМ - НЕ НАХОДИТСЯ ЛИ НАКЛАДНАЯ ДАННОГО ПАЛЛЕТА В ЧЕРНОВИКЕ?

begin

    select N.CONDITION into prihod_cond from RABAEV.RRL_PALLETS  PP , RABAEV.RRL_PRIHOD_NAKLAD N   where  PP.PRIHOD_NAKLAD_ID = N.ID  and PP.UID_PALLET = pallet_id;



    if( (prihod_cond=1) or (prihod_cond=0) ) then

        return 'NAKLAD_NE_ZAKRYTA';

    end if;



   exception

        WHEN NO_DATA_FOUND THEN

                    NULL;

         WHEN OTHERS THEN

                    NULL; 

    

end;









    begin  --  СНАЧАЛА ИЩЕМ - ЕСТЬ - ЛИ ТАКОЙ ПАЛЛЕТ КУДА

    



        select cell into cell_from1 from  RABAEV.RRL_REMAINS  where UID_POLETA=pallet_id and cell<>cell_to group by cell ;

        -- select cell into cell_from1 from  RABAEV.RRL_REMAINS  where UID_POLETA=pallet_id  group by cell ;







        if(count2=0) then

            select remain into count2 from  RABAEV.RRL_REMAINS  where UID_POLETA=pallet_id and cell=cell_from1 ;

        end if;



    exception

        WHEN NO_DATA_FOUND THEN

        

        update RABAEV.RRL_REMAINS RRR set RRR.TIME_OF_LAST_UPDATE = SYSTIMESTAMP where   

        UID_POLETA=pallet_id and cell=cell_to;

         

            cell_next:=RABAEV.RRL_GIVE_NEXT_CELL(CELL_TO);

            RETURN CONCAT('ok_' ,  cell_next );

        



         WHEN OTHERS THEN

            begin

            

                    begin

                    -- ПОПРОБУЕМ ИСКЛЮЧИТЬ ОТБОР ИЗ ПОИСКА

                    

                    select  RABAEV.RRL_REMAINS.cell into cell_from1 from  RABAEV.RRL_REMAINS , RABAEV.RRL_CELLS  where

                         ( RABAEV.RRL_REMAINS.UID_POLETA=pallet_id) and ( RRL_REMAINS.CELL = RRL_CELLS.CELL ) and ( RRL_CELLS.OTBOR=0 ) and ( RRL_CELLS.cell<>cell_to )  ;

                         

                    exception

                

                        WHEN NO_DATA_FOUND THEN

                        

                            dummy1:=ADD_HISTORY_NOTE (  user_id1,  cell_to     ,  '',  'net stolko tovara',  pallet_id ,  count1  ) ;

                            return 'net stolko tovara';

                            

                        WHEN OTHERS THEN

                           null ; -- return 'other pallet3';

                    end;



                         

                    if(count2=0) then

                        select remain into count2 from  RABAEV.RRL_REMAINS  where UID_POLETA=pallet_id and cell=cell_from1 ;

                    end if;

                    





                    

            exception

            

                WHEN NO_DATA_FOUND THEN

                    dummy1:=ADD_HISTORY_NOTE (  user_id1,  cell_to     ,  '',  'other pallet1',  pallet_id ,  count1  ) ;

                    return 'other pallet1';

                WHEN OTHERS THEN

                    dummy1:=ADD_HISTORY_NOTE (  user_id1,  cell_to     ,  '',  'other pallet2',  pallet_id ,  count1  ) ;

                    return 'other pallet2';

            end;

         

            

    end;

    



if( cell_to=cell_from1 ) then 

    return 'cell_to=cell_from1';

end if;   

    



    if(count2=0) then

        return 'count2=0';

    end if;











begin

    -- ЕСЛИ ПАЛЛЕТ ЕСТЬ, ПРОВЕРЯЕМ ЧТО ЯЧЕЙКА НАЗНАЧЕНИЯ = ЯЧЕЙКА ОТБОРА, ЛИБО 

    --  СВОБОДНА ( ОСТАТКОВ В НЕЙ НЕТ, РЕЗЕРВА НЕТ ) 

    select OTBOR  into is_otbor from RABAEV.RRL_CELLS where CELL=cell_to ;

exception

         WHEN NO_DATA_FOUND THEN

         

           return 'no_pallet_cell_to';

         WHEN OTHERS THEN

           return 'other pallet1';

end;





if ( (is_otbor=0) and (cell_to<>'TRASH') and (cell_to<>'IN_DOCK') )  then



PRIEMPALLET_WEIGHT1 := RRL_PRIEMPALLET_WEIGHT( pallet_id , count1 );

-- Если перемещение идет не в ячейку отбора, проверяем параметры веса ячейки.  если вес не допустим -

-- тогда предупреждение или отказ (в зависимости от настроек склада ячейки, куда перемещается товар)                 

    -- Находим ограничения по весу для данной ячейки.

    begin

    

        select weight_limit_warning , cells.LIMIT_WEIGHT , WEIGHT_LIMIT_STOP into weight_limit_warning1 , weight_of_cell_to , WEIGHT_LIMIT_STOP1 from rrl_wares ww , rrl_cells cells 

            where cells.CELL = cell_to and cells.WARE_ID= ww.ID ;

            -- ЕСЛИ ВКЛЮЧЕНА НАСТРОЙКА СРАВНЕНИЯ ВЕСА И ПРЕДУПРЕЖДЕНИЯ О ВЕСЕ.

            if (  weight_limit_warning1 = 1 ) then  -- СРАВНИВАЕМ ВЕС ПАЛЛЕТА С ЛИМИТАМИ ПО ДАННОЙ ЯЧЕЙКЕ 

               if(weight_of_cell_to > PRIEMPALLET_WEIGHT1 )then

                 dummy1:=ADD_HISTORY_NOTE (  user_id1,  cell_to     ,  '',  'weight_limit_warning',  pallet_id ,  count1  ) ;

               end if;

            end if;



            if (  WEIGHT_LIMIT_STOP1 = 1 ) then  

               if(weight_of_cell_to > PRIEMPALLET_WEIGHT1 )then

                return 'LIMIT_VESA';

               end if;

            end if;



            

        exception

        WHEN NO_DATA_FOUND THEN null;

        WHEN OTHERS THEN null;

        

    end; 







-- ЕСЛИ перемещение идет не в назначенную ячейку - сообщение об ошибке  карщика.      









    begin

        select sum(REMAIN) into remain_in_cell_to from  RABAEV.RRL_REMAINS  where CELL=cell_to ;

    exception

             WHEN NO_DATA_FOUND THEN

               remain_in_cell_to:=0;

             WHEN OTHERS THEN

               remain_in_cell_to:=0;

    end;



    if remain_in_cell_to is null then

    remain_in_cell_to:=0;

    end if;



    if(remain_in_cell_to<=0)  then

        checks_passed:=1;

    else

        -- ЕСЛИ ДЛЯ ДАННОЙ ЯЧЕЙКИ  УЖЕ ЕСТЬ ОСТАТОК ЧЕГО -ТО 

     -- если для данного склкда указана опция - списывать паллеты на недостачу, то списываем все в соотв. ячейку.

        select SPIS_IF_HRAN_NO_EMPTY into SPIS_IF_HRAN_NO_EMPTY1  from rrl_wares where rrl_wares.id = ware_id_to;

        

        if( (not ( SPIS_IF_HRAN_NO_EMPTY1 is null ) ) or (SPIS_IF_HRAN_NO_EMPTY1 <>'')  ) then

        

           

                checks_passed:=1;

                

                 for fgr2 in rrr2  loop

                    

                     tmpVar2:=RABAEV.RRL_INTERNAL_MOVE2(

                     fgr2.UID_POLETA  , 

                     SPIS_IF_HRAN_NO_EMPTY1  ,

                     fgr2.REMAIN ,

                     user_id1 

                        );



                end loop;

                

           

        

        end if;

        

        

        if(checks_passed=0) then

            dummy1:=ADD_HISTORY_NOTE (  user_id1,  cell_to     ,  '',  'cell_not_empty',  pallet_id ,  count1  ) ;

            return 'cell_not_empty';

        end if;

        

    end if;



else



DBMS_OUTPUT.put_line( 'спуск в отбор' );



    if cell_to<>'MEZONIN' then

        begin

            -- НЕ ДАЕМ СТАВИТЬ ТОВАР В ЛЕВЫЙ ОТБОР

                select AR.CELL , PP.EXPIRY_DATE  into  cell_otbora_for_pallet , data_spisania

                from RABAEV.RRL_PALLETS  PP , RABAEV.RRL_ARTICULS AR   

                where   PP.UID_PALLET = pallet_id and AR.ACTICUL=PP.ARTICUL ;

                

                if( cell_otbora_for_pallet<>cell_to ) then

                    DBMS_OUTPUT.put_line( concat( cell_otbora_for_pallet , concat( '#' , cell_to ) ) );

                    dummy1:=ADD_HISTORY_NOTE (  user_id1,  cell_to     ,  '',  'OTBOR_DRUGOGO_ARTICULA',  pallet_id ,  count1  ) ;

                    return 'OTBOR_DRUGOGO_ARTICULA';

                end if;

                

                

                -- Проверяем нарушение принципа FEFO 

                -- ИЩЕМ ПАЛЛЕТ ЭТОГО ТОВАРА В ХРАНЕНИИ ХУДШИМ СРОКОМ 

                -- data_spisania 

                DBMS_OUTPUT.put_line( concat('Флаг2' , articul1 ) );

                if not ( articul1  is null ) then

                DBMS_OUTPUT.put_line( 'ffff4' );

                    if  (1=1) then 

                    

                        alternative_puid :='';

                        alternative_cell :='';

                        alternative_date:=null;

                        begin

                        DBMS_OUTPUT.put_line( 'Флаг3' );

                            select UID_PALLET , CELL , EXPIRY_DATE  into alternative_puid , alternative_cell , alternative_date  from  (

                            select  PA.UID_PALLET , REMA.CELL , PA.EXPIRY_DATE  from RABAEV.RRL_REMAINS REMA , RABAEV.RRL_PALLETS  PA , RRL_CELLS CE  where 

                            REMA.UID_POLETA= PA.UID_PALLET and REMA.CELL=CE.CELL and PA.ARTICUL=articul1  and PA.EXPIRY_DATE<data_spisania  and CE.BLOCKED_FOR_REMAINS<>1 and CE.OTBOR<>1 order by PA.EXPIRY_DATE 

                            ) where rownum<=1  ; 

                            DBMS_OUTPUT.put_line( 'Флаг4' );

                            dummy2:=to_char( data_spisania, 'DD-MM-YYYY'  );

                            dummy1:= concat(concat(to_char( alternative_date, 'DD-MM-YYYY' ) , ' # ') , dummy2 ) ;

                            

                          --  rret :=concat( concat( concat( concat( Concat('SMOTRI SROK:' ,   alternative_cell) , ' ' ) , alternative_puid ) , ' srok=') , to_char( alternative_date, 'DD-MM-YYYY' ) ); 

                            rret := concat(concat( concat(Concat('SMOTRI SROK:' ,   alternative_cell) , ' [') , dummy1 ) ,  ']' )  ; 

                           dummy1:=ADD_HISTORY_NOTE (  user_id1,  cell_to     ,  '',  rret ,  pallet_id ,  count1  ) ;

                           DBMS_OUTPUT.put_line( 'Флаг5' );

                         return rret;

                      

                      exception

                            WHEN NO_DATA_FOUND THEN  null;

                            WHEN OTHERS THEN  null; 

                        end;

                    end if;

                end if;

             

        exception

                 WHEN NO_DATA_FOUND THEN

                     return 'no_articul';

                 WHEN OTHERS THEN

                  null;

        end;



    end if;



    checks_passed:=1;

end if;



        

    --  ЕСЛИ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ, ТО: 

    -- делаем запись таблицы RRL_EVENTS cell_to , cell_from ,date_event , count_event

    -- type_event = 2 , UID_POLETA , USER_ID



    if( checks_passed=0 ) then

     return 'fault';

    end if;

    



  SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_uid  FROM dual;



insert into RABAEV.RRL_EVENTS ( ID_EVENT , CELL_TO , CELL_FROM , DATE_EVENT ,  COUNT_EVENT ,

 TYPE_EVENT , UID_POLETA , USER_ID ) values

( new_event_uid , cell_to  , cell_from1 , SYSTIMESTAMP , count2 , 2 , pallet_id , user_id1  );



-- ОПРЕДЕЛЯЕМ ЯЧЕЙКУ, СЛЕДУЮЩУЮ ЗА ТЕКУЩЕЙ



commit;



cell_next:=RABAEV.RRL_GIVE_NEXT_CELL(CELL_TO);





   RETURN CONCAT('ok_' ,  cell_next );

      

   EXCEPTION

     WHEN NO_DATA_FOUND THEN

          dummy1:=ADD_HISTORY_NOTE (  user_id1,  cell_to     ,  '', concat( 'RRL_INTERNAL_MOVE3:err1 ' , cell_to ) ,  pallet_id ,  count1  ) ;

                 

       return 'err1';

     WHEN OTHERS THEN

     dummy1:=ADD_HISTORY_NOTE (  user_id1,  cell_to     ,  '',  'RRL_INTERNAL_MOVE3:err2' ,  pallet_id ,  count1  ) ;

       return 'err2';

END RRL_INTERNAL_MOVE3;
/
