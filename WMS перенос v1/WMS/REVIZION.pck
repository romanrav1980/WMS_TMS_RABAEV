create or replace package REVIZION is

  -- Author  : RRABAEV
  -- Created : 15.06.2011 10:04:49
  -- Purpose : ревизии
  
function revision_cond( rev_id int ) return int ;
function clear_cell2( cell1 varchar2     ) return int;
function clear_cell( cell1 varchar2 , puid varchar2   ) return int ;
function add_row_2_revizion( cell1 varchar2 , revision_id1 int   ) return int;
function create_revizion( ware_id1 int , user_id1 varchar2 ) return int ;
function revision_cell_kor( cell1 varchar2 , revision_id1 int ,  count2 number , user_id3 varchar2 ) return varchar2 ;
function add_row_2_reviz_type_art( cell1 varchar2 , revision_id1 int   ) return int;
function  RRL_REVIZION_CELL_PALL( articul1 varchar2, CELL1 varchar2 , count_pal int , 
   revision_row_id1 int , user_id1 varchar2 ) return varchar2 ;
   
function add_row_2_reviz_type_art2( cell1 varchar2 , articul2 varchar2 , revision_id1 int   ) return int ;
function articul_name( art varchar2 ) return varchar2;
function update_revision_row( cell1 varchar2 , articul2 varchar2 ,  revision_rowid int ,  rev_id2 int   ) return int;
function CreateNaklad_2_revizion( rev_id1 int ) return int ;
function revision_cell_sht_deleted( cell1 varchar2 , revision_id1 int , count2 number , user_id3 varchar2 ) return varchar2 ;
function  RRL_REVIZION_CELL_SHT( articul1 varchar2, CELL1 varchar2 , count_sht number , revision_row_id1 int , user_id1 varchar2 ) return varchar2;
function  RRL_REVIZION_CLEAR_MINUS( revision_id1 int , user_id1 varchar2 ) return int ;

FUNCTION  RRL_INV_CREATE_LINE5 
( 
    cell1 varchar2 ,
    articul2 varchar2,
    count1 NUMBER ,
    expiury_date date ,
    fasovka_id1 int ,
    brak_perc1 number ,
    pall_weight1 number , 
    pall_n int ,
    tn_weight1 number ,
    count_kor1 number ,
    user_id2 varchar2 , 
    NAKLAD_ID int
) return varchar2;

end REVIZION;
/
create or replace package body REVIZION is

 
function revision_cond( rev_id int ) return int is
  ret int;
begin 
  select rr.condition into ret from rrl_revizion rr where id= rev_id;
  return ret;       
exception
         when no_data_found then return -1;
end;

 --- СОЗДАНИЕ РЕВИЗИИ ПО СКЛАДУ
function create_revizion( ware_id1 int , user_id1 varchar2 ) return int is
id1 int;    

  begin
      insert into RABAEV.RRL_REVIZION
      (
        WARE_ID     ,
        CREATE_DATE  ,
        CONDITION   ,
        USER_ID    
      )values (  ware_id1, sysdate  , 0 , user_id1  ) ;
      select RABAEV.RRL_REVISION_SQ.Currval into id1 from dual;

    return id1;
  end;

-- Обнуляет остатки данного артикула в данной ячейке
function clear_cell( cell1 varchar2 , puid varchar2   ) return int is  
begin

delete from rrl_remains rr where   rr.cell=cell1 and rr.uid_poleta= puid;
return  1;
exception
  when others then null;
end;

-- Обнуляет остатки данного артикула в данной ячейке
function clear_cell2( cell1 varchar2     ) return int is  
begin
delete from rrl_remains rr where   rr.cell=cell1  ;
return  1;
exception
  when others then null;
end;

-- ДОБАВЛЕНИЕ СТРОКИ ДЛЯ РЕВИЗИИ ПО СКЛАДУ 
function add_row_2_revizion( cell1 varchar2 , revision_id1 int   ) return int is
id1 int;    

cursor sss is 
       select  rm.cell , pts.articul 
       from rrl_remains rm , rrl_pallets pts where 
       rm.cell=cell1 and pts.uid_pallet=rm.uid_poleta
       group by rm.cell , pts.articul ;

begin
  if revision_cond(revision_id1)>1 then
    return 0;
  end if;
  
  delete from RABAEV.RRL_REVISION_ROW where REVISION_ID = revision_id1  and CELL= cell1;
  
  
  for s in sss loop
    
      insert into  RABAEV.RRL_REVISION_ROW (REVISION_ID ,CELL , REV_DATE , ARTICUL1 )
       values ( revision_id1 , s.cell , sysdate , s.articul );
      select RRL_REVISION_ROW_SQ.Currval  into id1 from dual;

  end loop;


  return id1;
end;


-- ДОБАВЛЕНИЕ СТРОК ДЛЯ РЕВИЗИИ ПО СКЛАДУ 
function add_row_2_reviz_type_art( cell1 varchar2 , revision_id1 int   ) return int is
id1 int;    

cursor rema is 
select distinct pl.articul  from rrl_remains rems, rrl_pallets pl 
   where rems.uid_poleta=pl.uid_pallet and  rems.cell=cell1 ; 

begin
  if revision_cond(revision_id1)>1 then
    return 0;
  end if;
-- Получаем список артикулов в данной ячейке 
-- по данному списку артикулов создаем записи в таблице строк ревизии . 
   for rr in rema loop
       delete from RABAEV.RRL_REVISION_ROW where REVISION_ID = revision_id1  
       and CELL= cell1 and articul1=rr.articul ;
       insert into  RABAEV.RRL_REVISION_ROW (REVISION_ID ,CELL , REV_DATE , ARTICUL1 )
       values ( revision_id1 , cell1 , sysdate , rr.articul );
       
   end loop;

  return id1;
end;


-- ДОБАВЛЕНИЕ СТРОК ДЛЯ РЕВИЗИИ ПО СКЛАДУ 
function add_row_2_reviz_type_art2( cell1 varchar2 , articul2 varchar2 , revision_id1 int   ) return int is
id1 int;    

cursor rema is 
select distinct pl.articul  from rrl_remains rems, rrl_pallets pl 
   where rems.uid_poleta=pl.uid_pallet and  rems.cell=cell1 and pl.articul=articul2 ; 

begin
  if revision_cond(revision_id1)>1 then
    return 0;
  end if;
-- Получаем список артикулов в данной ячейке 
-- по данному списку артикулов создаем записи в таблице строк ревизии . 
   for rr in rema loop
       delete from RABAEV.RRL_REVISION_ROW where REVISION_ID = revision_id1  
       and CELL= cell1 and articul1=rr.articul ;
       insert into  RABAEV.RRL_REVISION_ROW (REVISION_ID ,CELL , REV_DATE , ARTICUL1 )
       values ( revision_id1 , cell1 , sysdate , rr.articul );
       
   end loop;

  return id1;
end;



-- ОБНОВЛЕНИЕ СТРОК ДЛЯ РЕВИЗИИ ПО СКЛАДУ 
function update_revision_row( cell1 varchar2 , articul2 varchar2 ,  revision_rowid int ,  rev_id2 int   ) return int is
   

revision_id1 int ;
row_ret int;
begin
  
    if(  revision_rowid > 0 ) then

          select rr.revision_id into revision_id1 from 
                 rrl_revision_row rr where id = revision_rowid;
    
          if revision_cond(revision_id1)>1 then
            return 0;
          end if;  
        -- Получаем список артикулов в данной ячейке 
        -- по данному списку артикулов создаем записи в таблице строк ревизии . 
          update    RABAEV.RRL_REVISION_ROW rr set  rr.cell=cell1 , rr.articul1=articul2 
                    where id=revision_rowid ; 
          return revision_id1;
      else

      insert into RABAEV.RRL_REVISION_ROW  ( REVISION_ID , CELL , ARTICUL1      ) values 
           (rev_id2 , cell1 , articul2 );
           select RRL_REVISION_ROW_SQ.CURRVAL into row_ret from dual;
           return  row_ret;
      
    end if;
  
  --exception
  --  when no_data_found then return -1;
  --  when others then return -2;
  
end;




function articul_name( art varchar2 ) return varchar2 is
  ret varchar2(255);
  begin
    select name into ret from rrl_articuls where acticul=art;
    return ret;
    exception
      when no_data_found then return '';
      when others then return '';
  end;

function revision_cell_kor( cell1 varchar2 , revision_id1 int , count2 number , user_id3 varchar2 ) return varchar2 is
rem5  varchar2(1024);
rem4  varchar2(255);
revision_row_id2 int;
condition2 int;
begin 

      begin  -- ПРОВЕРЯЕМ СОСТОЯНИЕ РЕВИЗИИ ---  
         select rev.condition into condition2 from rrl_revizion rev where rev.id= revision_id1;
         if( condition2=2 ) then
             return 'ревизия закрыта';
         end if;
         exception 
           when no_data_found then return 'ревизии нет';
      end;  -- ПРОВЕРЯЕМ СОСТОЯНИЕ РЕВИЗИИ --- 
  
      begin  -- ПРОВЕРЯЕМ СОСТОЯНИЕ СТРОКИ ---      
           select id  into revision_row_id2 from RABAEV.RRL_REVISION_ROW where cell=cell1 and REVISION_ID = revision_id1  and rownum<=1 ;  
           exception 
             when no_data_found then revision_row_id2:=add_row_2_revizion(cell1 , revision_id1 ) ;
      end;  -- ПРОВЕРЯЕМ СОСТОЯНИЕ СТРОКИ --- 
      
      
    rem4 := RABAEV.RRL_REVIZION_CELL_KOR( CELL1  ,    count2 ,    user_id3 )  ;
    
    rem5 :=concat( concat( ' кор=' , to_char(count2) ) , concat( 'кор. время=' , to_char( sysdate )  ));
    update RABAEV.RRL_REVISION_ROW set remark1= concat (remark1 , concat(rem5, rem4) )   , 
      count_kor=count2
     where id=revision_row_id2 ;
     return rem4;
      

end;



function revision_cell_sht_deleted( cell1 varchar2 , revision_id1 int , count2 number , user_id3 varchar2 ) return varchar2 is
rem5  varchar2(1026);
rem4  varchar2(255);
revision_row_id2 int;
condition2 int;
begin 

      begin  -- ПРОВЕРЯЕМ СОСТОЯНИЕ РЕВИЗИИ ---  
         select rev.condition into condition2 from rrl_revizion rev where rev.id= revision_id1;
         if( condition2=2 ) then
             return 'ревизия закрыта';
         end if;
         exception 
           when no_data_found then return 'ревизии нет';
      end;  -- ПРОВЕРЯЕМ СОСТОЯНИЕ РЕВИЗИИ --- 
  
      begin  -- ПРОВЕРЯЕМ СОСТОЯНИЕ СТРОКИ ---      
           select id  into revision_row_id2 from RABAEV.RRL_REVISION_ROW where cell=cell1 and REVISION_ID = revision_id1  and rownum<=1 ;  
           exception 
             when no_data_found then revision_row_id2:=add_row_2_revizion(cell1 , revision_id1 ) ;
      end;  -- ПРОВЕРЯЕМ СОСТОЯНИЕ СТРОКИ --- 
      
      
    rem4 := RABAEV.RRL_REVIZION_CELL( CELL1  ,    count2 ,    user_id3 )  ;
    
    rem5 :=concat( concat( ' кор=' , to_char(count2) ) , concat( 'sht. время=' , to_char( sysdate )  ));
    update RABAEV.RRL_REVISION_ROW set remark1= concat (remark1 , concat(rem5, rem4) )   , 
      count_kor=count2
     where id=revision_row_id2 ;
     return rem4;
      

end;


-- ============================================================================================

function  RRL_REVIZION_CELL_PALL( 
   articul1 varchar2, CELL1 varchar2 , count_pal int , revision_row_id1 int , 
    user_id1 varchar2 ) return varchar2

 -- ПРОВЕДЕНИЕ ИНВЕНТАРИЗАЦИИ ДЛЯ ЯЧЕЙКИ в паллетах. БЕЗ УЧЕТА СРОКОВ ГОДНОСТИ И ПАРТИЙ. 
-- По данной ячейке выбираем количество паллет по ФЕФО.
--    Все паллеты сверх указанного количества отправляем в ячейку излишков. 
is
new_event_uid int;
tmp varchar2 (250);
count_pal_fixed int;
counter_invent_p int;
/*cursor rema_in_p  is -- Остатки в ячейке излишков.
  select sum(rm.REMAIN) as RM1 , count( DISTINCT rm.UID_POLETA ) kk , 
  rm.UID_POLETA 
  from rrl_remains rm , rrl_pallets pal 
  where rm.CELL='INVENT_P' and pal.UID_PALLET=rm.UID_POLETA
    and    pal.ARTICUL=articul1  and rm.REMAIN>0
  order by    pal.EXPIRY_DATE asc; */

-- Остатки в указанной ячейке.
rows_cnt int;
cursor rema is select  rm.REMAIN   , rm.UID_POLETA 
  from rrl_remains rm , rrl_pallets pal 
  where rm.CELL=CELL1 and pal.UID_PALLET=rm.UID_POLETA and  pal.ARTICUL=articul1 
    and  rm.REMAIN  >0 
  order by pal.EXPIRY_DATE desc;

cursor rema_invent_p  is select  rm.REMAIN   , rm.UID_POLETA 
  from rrl_remains rm , rrl_pallets pal 
  where rm.CELL='INVENT_P' and pal.UID_PALLET=rm.UID_POLETA and  pal.ARTICUL=articul1 
    and  rm.REMAIN  >0 
  order by pal.EXPIRY_DATE desc;

begin
count_pal_fixed:=0;
rows_cnt:=0;

-- ПО ВСЕМ ОСТАТКАМ 
for rrow in rema loop
  rows_cnt:=rows_cnt+1;
    count_pal_fixed:=count_pal_fixed+1;
    if(count_pal_fixed>count_pal) then -- Лишние паллеты
        tmp := RABAEV.RRL_INTERNAL_MOVE2(
            rrow.UID_POLETA ,  'INVENT_P' ,
            rrow.remain , user_id1 );
     end if;
end loop;

if( count_pal_fixed>count_pal  ) then
tmp:= concat( 'Недостача ' , concat( to_char( count_pal_fixed-count_pal ) , ' паллет'));
end if;

if( count_pal_fixed < count_pal  ) then
tmp:= concat( 'Излишек ' , concat( to_char(count_pal- count_pal_fixed ) , ' паллет'));
counter_invent_p:=0;
      for rrow2 in rema_invent_p loop -- излишек возвращаем из ячейки излишков.
          counter_invent_p:=counter_invent_p+1;    
          if(  counter_invent_p<=count_pal-count_pal_fixed ) then
          
           SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_uid  FROM dual;
           
           insert into rrl_events ( ID_EVENT  ,  cell_from ,cell_to , date_event ,count_event,
           type_event,uid_poleta,user_id ) 
           values (new_event_uid, 'INVENT_P' , CELL1 , systimestamp , 
           rrow2.remain ,2 ,rrow2.uid_poleta, user_id1 );
          
          end if;
      end loop;
end if;

if( count_pal_fixed = count_pal  ) then
 tmp:= 'ok';
end if;
 
update RRL_REVISION_ROW set REMARK1 = tmp , NUM_OF_PALL=count_pal  where id=revision_row_id1;
commit;
return tmp;

exception 
       when no_data_found then  return 'neok';
       when others then raise;


END;


-- По указанной ревизии вычищает ячейки от отрицательных остатков.
function  RRL_REVIZION_CLEAR_MINUS( revision_id1 int , user_id1 varchar2 ) return int is
 new_event_uid int;
 cell4 varchar2(255);
 tmp varchar2(255);
 articul5 varchar2(255);
 
 cursor cells1  is select distinct rr.cell , rr.articul1 from rrl_revision_row rr 
 where rr.revision_id=revision_id1 ;

 cursor min_rem is select rem1.cell , rem1.uid_poleta , rem1.remain 
        from rrl_remains rem1 , rrl_pallets pts where pts.uid_pallet=rem1.uid_poleta and
        pts.articul = articul5 and  rem1.cell=cell4 and rem1.remain<0;

begin

    for cell3 in cells1 loop
    cell4:=cell3.cell;    
    articul5:=cell3.articul1;
        for rrow in min_rem loop   
           SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_uid  FROM dual;           
           insert into rrl_events ( ID_EVENT  ,  cell_from ,cell_to , date_event ,count_event,
           type_event,uid_poleta,user_id ) 
           values (new_event_uid , CELL4 , 'INVENT_P'  , systimestamp , 
           rrow.remain ,2 ,rrow.uid_poleta, user_id1 );
        end loop;
        
    end loop;
    commit;
return 1;
end;

function  RRL_REVIZION_CELL_SHT( 
   articul1 varchar2, CELL1 varchar2 , count_sht number , revision_row_id1 int , 
    user_id1 varchar2 ) return varchar2

 -- ПРОВЕДЕНИЕ ИНВЕНТАРИЗАЦИИ ДЛЯ ЯЧЕЙКИ в штуках. БЕЗ УЧЕТА СРОКОВ ГОДНОСТИ И ПАРТИЙ. 
-- По данной ячейке выбираем количество штук по ФЕФО.
--    Все штуки сверх указанного количества отправляем в ячейку излишков. 
is
new_event_uid int;
tmp varchar2 (250);
counter_invent_p number;
to_spis number;

-- Остатки в указанной ячейке.

cursor rema is select  rm.REMAIN   , rm.UID_POLETA 
  from rrl_remains rm , rrl_pallets pal 
  where rm.CELL=CELL1 and pal.UID_PALLET=rm.UID_POLETA and  pal.ARTICUL=articul1 
    and  rm.REMAIN  >0 
  order by pal.EXPIRY_DATE desc;

cursor rema_invent_p  is select  rm.REMAIN   , rm.UID_POLETA 
  from rrl_remains rm , rrl_pallets pal 
  where rm.CELL='INVENT_P' and pal.UID_PALLET=rm.UID_POLETA and  pal.ARTICUL=articul1 
    and  rm.REMAIN  >0 
  order by pal.EXPIRY_DATE desc;

count_sht_rem number;
how_many_return number;

begin


count_sht_rem:= 0;
to_spis:=0;

-- ПО ВСЕМ ОСТАТКАМ 
for rrow in rema loop
--   если остаток текущего паллета  больше оставшегося количества инвентаризации, то 
--        списываем с текущего паллета, ячейки количество= остаток паллета- оставшееся
--        оставшееся := 0
     count_sht_rem:=count_sht_rem+rrow.remain;
    if( count_sht_rem>count_sht ) then
        if( count_sht_rem-count_sht>rrow.remain ) then
                   tmp := RABAEV.RRL_INTERNAL_MOVE2(
                      rrow.UID_POLETA ,  'INVENT_P' ,
                      rrow.remain , user_id1 );
            else
                   tmp := RABAEV.RRL_INTERNAL_MOVE2(
                      rrow.UID_POLETA ,  'INVENT_P' ,
                      count_sht_rem-count_sht , user_id1 );
        end if;
    end if;
   
              
end loop;


if( count_sht_rem=count_sht  ) then
    tmp:= 'ok';
end if;


if( count_sht_rem-count_sht>0  ) then
tmp:= concat( 'Недостача ' , concat( to_char( count_sht_rem-count_sht ) , ' шт'));
end if;

if( count_sht_rem-count_sht<0  ) then
tmp:= concat( 'Излишек ' , concat( to_char( -count_sht_rem+count_sht ) , ' шт'));
counter_invent_p:=0;
how_many_return:=-count_sht_rem+count_sht;

      for rrow2 in rema_invent_p loop -- излишек возвращаем из ячейки излишков.
          counter_invent_p:=counter_invent_p+rrow2.remain;
          if( how_many_return>0 ) then        
              if( rrow2.remain>how_many_return ) then
                  to_spis:=how_many_return;
                  how_many_return:=0;
              else
                  to_spis:=rrow2.remain;
                  how_many_return:=how_many_return-rrow2.remain;
              end if;

           SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_uid  FROM dual;           
           insert into rrl_events ( ID_EVENT  ,  cell_from ,cell_to , date_event ,count_event,
           type_event,uid_poleta,user_id ) 
           values (new_event_uid, 'INVENT_P' , CELL1 , systimestamp , 
           rrow2.remain ,2 ,rrow2.uid_poleta, user_id1 );

          end if;
      end loop;
      
end if;


 
update RRL_REVISION_ROW set REMARK1 = tmp , count1=count_sht  where id=revision_row_id1;
commit;
return tmp;

exception 
       when no_data_found then  return 'neok';
       when others then raise;


END;



function CreateNaklad_2_revizion( rev_id1 int ) return int is
         rev_naklad_id1 int;
         ret int;
         ware_id3 int;
begin

  select r.rev_naklad_id , ware_id into rev_naklad_id1 , ware_id3 from rrl_revizion r where id= rev_id1;
  if( not rev_naklad_id1 is null ) and (  rev_naklad_id1 >0 ) then
      return rev_naklad_id1;
  end if;

  ret:=ADD_RRL_PRIH_NAKLAD2( NAKLAD_NUMBER => concat( 'INV_' , to_char(rev_id1) ) , 
                         DATE_OF_NAKLAD => sysdate ,DATE_OF_ACCEPT => sysdate,
                         POSTAVSHIK_NAME => 'INV', 
                         SM_NAKLAD_NUMBER => concat( 'INV_' , to_char(rev_id1) ) ,
                         ZAKAZ_NUMBER1 => concat( 'INV_' , to_char(rev_id1) ) ,
                         ware_id1 => ware_id3 );
               
  if( ret>0 ) then
      update RABAEV.RRL_PRIHOD_NAKLAD set condition=2 where id=ret;
      update  rrl_revizion set rev_naklad_id=ret where id= rev_id1;
  end if;
            
  return ret;
exception
  when no_data_found then return -1;
  when others then return -2;
end;

-- ============================================================================================


FUNCTION  RRL_INV_CREATE_LINE5 
( 
    cell1 varchar2 ,
    articul2 varchar2,
    count1 NUMBER ,
    expiury_date date ,
    fasovka_id1 int ,
    brak_perc1 number ,
    pall_weight1 number , 
    pall_n int ,
    tn_weight1 number ,
    count_kor1 number ,
    user_id2 varchar2 , 
    NAKLAD_ID int
)
    RETURN varchar2 IS 
    price Number;
    ret2 varchar2(255);
    event_id int;
    pallet_name varchar2(255);


BEGIN
-- =================================================
pallet_name:= CONCAT( Concat( Concat( Concat('P_' , articul2 ) , '_G3_') , cell1) , concat( '_' ,to_char(pall_n) ) ) ;
pallet_name:=replace(pallet_name , 'Т' ,'T' );
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
            articul2 ,
            sysdate ,
            expiury_date ,
            count1 , 
            1,
            NAKLAD_ID
        );
        exception
          when others then return 'EXISTS';
end;
-- ОСТАТКИ

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
          CELL1 ,
          expiury_date , 
          expiury_date , 
          count1 , 
          1 ,
          pallet_name ,
          user_id2 ,
          NAKLAD_ID 
            );
    
    ret2:=RABAEV.RRL_PRIHODPALLET_CHANGE(PALLET_UID1 => pallet_name ,art => articul2 ,
        UNIT_COUNT1 => count1 ,DEFECT_PERC1 => brak_perc1 ,COUNT_KOR1 => count_kor1 ,
        WEIGHT_BRUTTO1 => pall_weight1 , WEIGHT_TN1 => tn_weight1 ,MOD_ID1 => fasovka_id1 );

return pallet_name;
-- =================================================
END ;


-- РАБОТА со снимками
-- создание открывающего снимка по ревизии.
function rev_create_snap_shot_before( rev_id int ) return int is
    snap_id1 int;
    tmp int;
    cursor sss is select rs.cell , rs.articul1  
     from rrl_revision_row rs where rs.revision_id = rev_id ;
begin
 
  select rv.SNAPSHOT_BEFORE into snap_id1 
         from rrl_revizion rv where id= rev_id;
  if( snap_id1 is null ) then
      snap_id1 := REMAINS.create_snapshot(type2 => 1);
      update rrl_revizion set SNAPSHOT_BEFORE=snap_id1 where  id= rev_id;
      for s in sss loop
          tmp:=REMAINS.add_row_2_snapshot(snap_shot_id1 => snap_id1 ,cell1 => s.cell ,articul1 => s.articul1);
      end loop;
      
      return snap_id1;
  else
      return snap_id1;
  end if;
return snap_id1;
end;
-- создание закрывающего снимка по ревизии.


function rev_create_snap_shot_after( rev_id int ) return int is
    snap_id1 int;
    tmp int;
    cursor sss is select rs.cell , rs.articul1  
     from rrl_revision_row rs where rs.revision_id = rev_id ;
begin
 
  select rv.SNAPSHOT_AFTER into snap_id1 
         from rrl_revizion rv where id= rev_id;
  if( snap_id1 is null ) then
      snap_id1 := REMAINS.create_snapshot(type2 => 2);
      update rrl_revizion set SNAPSHOT_AFTER=snap_id1 where  id= rev_id;
      for s in sss loop
          tmp:=REMAINS.add_row_2_snapshot(snap_shot_id1 => snap_id1 ,cell1 => s.cell ,articul1 => s.articul1);
      end loop;
      
      return snap_id1;
  else
      return snap_id1;
  end if;
return snap_id1;
end;







begin
null;
end REVIZION;
/
