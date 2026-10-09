create or replace FUNCTION        RRL_REVIZION_CELL_KOR
(
    CELL1 varchar2 ,
    count_kor2 varchar2 ,
    user_id1 varchar2
) return varchar2

 -- ПРОВЕДЕНИЕ ИНВЕНТАРИЗАЦИИ ДЛЯ ЯЧЕЙКИ в штуках. БЕЗ УЧЕТА СРОКОВ ГОДНОСТИ И ПАРТИЙ. 
 -- процедура выбирает в ячейке партии в порядке  сроков годности (спуска их  вниз, )     
 -- и оставляет партии с самым свежим сроком. 
 -- Если количество  превышает, указанное по учету, на величину менее 100 штук то  , 
 --     Списать с ячейки претензий с последней партией , находящейся  в ячейке отбора
 --  иначе 
 --     Породить алерт 
 --     Потребовать разбирательства специалиста по качеству, то есть списания  с указанием партии (это другая процедура) 
 --     возврат ошибки
 --конец если    
 -- возврат ок.    
 
is

articul1 varchar2(50);


cursor rema_in_p  is 
select rm.REMAIN as RM1 , RABAEV.RRL_COUNT_KOR3( pal.ARTICUL ,  rm.REMAIN , rm.UID_POLETA ) kk , 
rm.UID_POLETA 
from rrl_remains rm , rrl_pallets pal 
where rm.CELL='INVENT_P' and pal.UID_PALLET=rm.UID_POLETA
  and    pal.ARTICUL=articul1  and rm.REMAIN>0
order by    pal.EXPIRY_DATE asc;


cursor rema is select rm.REMAIN as RM1 , RABAEV.RRL_COUNT_KOR3( pal.ARTICUL ,  rm.REMAIN , rm.UID_POLETA ) kk , rm.UID_POLETA 
from rrl_remains rm , rrl_pallets pal 
where rm.CELL=CELL1 and pal.UID_PALLET=rm.UID_POLETA and  pal.ARTICUL=articul1 
  and  rm.REMAIN  >0 
order by pal.EXPIRY_DATE desc;


count_kor1 int ;
tmp varchar2(255);
to_spis number;
ostatok number;
nedostacha number;
is_otbor1 int;
last_pal_uid varchar2(50);

new_event_uid int;
ostatok2 number;

begin
ostatok2:=0;
last_pal_uid:='';
is_otbor1:=0;
nedostacha:=0;
count_kor1:= to_number( count_kor2 ) ;
ostatok:=count_kor1;
-- Проверяем, что данная ячейка является ячейкой отбора. Если не так - уходим с ошибкой.

    begin
        select ccc.OTBOR  into is_otbor1  from rrl_cells ccc where cell=cell1; 
       -- DBMS_OUTPUT.put_line('flag 1');
        select  acticul into articul1 from rrl_articuls where cell = CELL1;
    exception 
        when no_data_found then  return 'НЕТ ЯЧЕЙКИ ОТБОРА';
        when others then return 'ошибка RRL_REVIZION_CELL_KOR';
    end;



if( is_otbor1=0 ) then
    return 'НЕ ОТБОР';
end if;

for  rr in rema  loop  -- ПО Всем партиям ячейки отбора , упорядоченных по СГ ,  Проверяем- что вошло, а что нет.

DBMS_OUTPUT.put_line( concat( concat('ячейка, Паллет = ' ,  rr.UID_POLETA) , concat( ' кол-во=' , rr.kk ) ) );

    if(rr.kk=0 ) then
    DBMS_OUTPUT.put_line( concat('нулевое кол-во коробок для ' ,  rr.UID_POLETA) );
        return concat('нулевое к-во коробок для ' ,  rr.UID_POLETA);
    end if;

    if(ostatok>=rr.kk) then
    -- все ок.  
      null;
    else 
        last_pal_uid := rr.UID_POLETA ;
        if(rr.kk<=ostatok) then -- если ostatok<0 , то списывается вся партия . 
            to_spis:=rr.RM1;
            DBMS_OUTPUT.put_line( concat( 'FL1 to_spis=' , to_spis ) );

        else -- Если остаток спиания меньше остатка в ячейке, то  данная партия в количестве [rr.REMAIN-ostatok] списывается в недостачу. 
            to_spis:= (rr.kk-ostatok)*floor(  ( rr.rm1/rr.kk )  );  -- rr.rm1 - (rr.rm1*ostatok)/rr.kk ; -- ;
            DBMS_OUTPUT.put_line( concat( concat( 'FL2 rr.kk=' , to_char(rr.kk) )  , concat( ' rr.rm1/rr.kk=' , to_char(rr.rm1/rr.kk) ) ) );
            DBMS_OUTPUT.put_line( concat( 'FL3 ostatok=' , ostatok ) );

        end if; -- ВЛОЖЕННОСТЬ В КОРОБКУ = обязательно целое число!!!! 

        nedostacha:= nedostacha + to_spis;
        DBMS_OUTPUT.put_line( concat( concat('списываем в недостачу ' , rr.UID_POLETA )   , concat( ' кол=' , to_char(to_spis) ) ) );
        tmp := RABAEV.RRL_INTERNAL_MOVE2(
        rr.UID_POLETA , 
        'INVENT_P' ,
        to_spis ,
        user_id1 );


    end if;

    if (( last_pal_uid is null ) or ( last_pal_uid='' )) then
        last_pal_uid := rr.UID_POLETA ;
    end if;

  ostatok:=ostatok- rr.kk;
if(ostatok<0) then
    ostatok:=0;
end if;

end loop; -- ПО Всем партиям ячейки отбора , упорядоченных по СГ ,  Проверяем- что вошло, а что нет.


-- если ostatok > 0  , то в ячейке не хватает  партий, их надо найти или спросить.
-- Если количество  превышает, указанное по учету, на величину менее 100 штук то  , 
 --     Пока остаток не скомпенсирован, по всем партиям ячейки INVENT_P 
 --     Списать с ячейки излишков в ячейку, количество = min ( остаток , остаток в ячейке  )

 -- если ostatok < 0 , то в ячейке зафиксирована недостача в количестве ostatok. она списана уже на  INVENT_P возвращаем ок.
 -- иначе 
 -- Если после этого оказалось, что не хватает товара для восполнения излишка, берем последнюю партию в ячейке отбора. 
 -- 



if( ostatok > 0  ) then 

    DBMS_OUTPUT.put_line ( concat( 'излишки есть кол=' , to_char(ostatok) ) );
    ostatok2:=ostatok;
    -- НОВОЕ 
    -- зафиксирован излишек, данный излишек нужно переслать из INVENT_P в текущую ячейку. 

    for  rr in rema_in_p  loop

        if ( ostatok2>0 ) then 


          if (( last_pal_uid is null ) or ( last_pal_uid='' )) then
                last_pal_uid := rr.UID_POLETA ;
          end if;

          if(rr.kk<=ostatok2) then 
          DBMS_OUTPUT.put_line ( 'flag 1 ');
            to_spis:=rr.RM1;
          else 
          DBMS_OUTPUT.put_line ( concat( concat( 'flag 2   ostatok2=' , to_char(ostatok2) ) , concat( '    rr.kk= ' , to_char(rr.kk) ) ));
             to_spis:= (ostatok2)*floor(  ( rr.rm1/rr.kk )  );  
          end if;

            DBMS_OUTPUT.put_line ( concat( concat( 'INVENT_P => ' , concat( cell1 , ' кол=' )  )   ,to_number(  to_spis )  ));
            DBMS_OUTPUT.put_line ( concat( ' паллет =' , rr.UID_POLETA  ));

            SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_uid  FROM dual;
            insert into RABAEV.RRL_EVENTS ( ID_EVENT , CELL_TO , CELL_FROM , DATE_EVENT ,  COUNT_EVENT ,
                TYPE_EVENT , UID_POLETA , USER_ID ) values
                ( new_event_uid ,  cell1  , 'INVENT_P' , SYSTIMESTAMP , to_spis , 2 , rr.UID_POLETA , user_id1  );

            ostatok2:=ostatok2-rr.kk;

        end if;

    end loop;  


    -- Вываливаемся с ошибкой, либо 
    -- если по складу действует настройка пополнения излишков из недостач, то ищем паллет, попавший в недостачу не позднее 2 дней от текущей даты
    -- иначе весь излишек проводим   
    -- если он есть, то делаем проводку из него на ячейку 

    if ostatok2>0 then  -- ЕСЛИ КОЛИЧЕСТВА В ЯЧЕЙКЕ INVENT_P не достаточно 


        -- 
        if (( last_pal_uid is null ) or ( last_pal_uid='' )) then
            begin 
                    select UID_POLETA  into last_pal_uid from(  
                    select  rm.UID_POLETA 
                    from rrl_remains rm , rrl_pallets pal 
                    where rm.CELL='INVENT_P' and pal.UID_PALLET=rm.UID_POLETA
                      and  rm.REMAIN  >0 and pal.ARTICUL=articul1 
                    order by sign( rm.REMAIN)  asc ,  pal.EXPIRY_DATE desc ) where rownum=1  ; 
            exception 
                    when no_data_found then  null ;
                    when others then null;
            end;
        end if;


        if (( last_pal_uid is null ) or ( last_pal_uid='' )) then
            begin 
                    select UID_POLETA  into last_pal_uid from(  
                    select  rm.UID_POLETA 
                    from rrl_remains rm , rrl_pallets pal 
                    where rm.CELL=cell1 and pal.UID_PALLET=rm.UID_POLETA
                      and  rm.REMAIN  >0 and pal.ARTICUL=articul1 
                    order by  pal.EXPIRY_DATE desc ) where rownum=1  ; 
            exception 
                    when no_data_found then  null ;
                    when others then null;
            end;
        end if;



      if (( last_pal_uid is null ) or ( last_pal_uid='' )) then
            begin 
                    select UID_PALLET into last_pal_uid from(  
                    select pal.UID_PALLET from rrl_pallets pal where pal.ARTICUL=articul1 order by Expiry_date desc ) 
                    where rownum=1 ; 
            exception 
                    when no_data_found then  return 'ИЗЛИШКИ НЕ РАСП';
            end;
      end if;


        to_spis:=round(  ostatok* 10000/RABAEV.RRL_COUNT_KOR3 ( articul1  ,10000 , last_pal_uid ),0 ) ; 
        DBMS_OUTPUT.put_line ( concat( concat( 'Недостача покрыта не вся!!! Партия= ' , last_pal_uid  ) , concat( ' списываем=' , to_char(to_spis) )  ) );
        SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_uid  FROM dual;
        insert into RABAEV.RRL_EVENTS ( ID_EVENT , CELL_TO , CELL_FROM , DATE_EVENT ,  COUNT_EVENT ,
             TYPE_EVENT , UID_POLETA , USER_ID ) values
             ( new_event_uid ,  cell1  , 'INVENT_P' , SYSTIMESTAMP , to_spis , 2 , last_pal_uid , user_id1  );

    end if;  -- ЕСЛИ КОЛИЧЕСТВА В ЯЧЕЙКЕ INVENT_P не достаточно 


    return  concat ( 'ИЗЛИШКИ ' ,  concat( to_char(ostatok) , ' кор' ) );
else 

if(ostatok <> 0) then
    return  concat( 'СПИСАНО ' , to_char(ostatok) ) ;
end if;
--return 'СОВПАЛО';
DBMS_OUTPUT.put_line('излишков нет');
 -- Порождаем сообщение о недостаче. 
    return concat( 'НЕДОСТАЧА ' , concat( to_char(nedostacha) , ' шт' )  ) ;
end if;


return 'ok';

exception 
when no_data_found then  return 'neok';
when others then raise;


END RRL_REVIZION_CELL_KOR;
/
