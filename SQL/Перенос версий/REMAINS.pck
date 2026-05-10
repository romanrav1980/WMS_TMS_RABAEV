create or replace package REMAINS is

  -- Author  : RRABAEV
  -- Created : 15.09.2011 9:04:07
  -- Purpose : ОСТАТКИ
  

  -- Public function and procedure declarations
  function create_snapshot( type2 int  ) return int;
  function close_snapshot(  snap_shot_id1 int  ) return int;
  function add_row_2_snapshot(   snap_shot_id1 int ,   cell1 varchar ,   articul1 varchar2 ) return int;
  function remains_free( articul1 varchar2 ) return number ;
  function remains_in_otbor( articul1 varchar2 ) return number;
  function remains_in_otbor_all( articul1 varchar2 ) return number ;
  function remains_free_all( articul1 varchar2 ) return number ; 


function remains_partion_in_cell( pallet_uid1 varchar2 , cell3 varchar2 ) return number ; 
function remains_partion_in_otbor( pallet_uid1 varchar2 ) return number ; 
function remains_except_part_in_otb( pallet_uid1 varchar2 ) return number ;



end REMAINS;
/
create or replace package body REMAINS is


--  ТИПЫ ФОТОГРАФИЙ :  
--  1 = перед ревизией
--  2 = после ревизии
--  3 = фотография остатков , привязанная ко времени.

  -- Function and procedure implementations
  function create_snapshot( type2 int  ) return int is

    ID1 int;
  begin
  select  RRL_REMAIN_SNAPSHOT_SQ.NEXTVAL into ID1 from dual;  
  insert into RRL_REMAIN_SNAPSHOT (ID ,TYPE1 , create_time , SNAP_SHOT_TIME  ) values ( ID1 , type2 , systimestamp , systimestamp ); 
   
    return ID1;
  end;

-- Добавляется строка к снимку
function add_row_2_snapshot( 
  snap_shot_id1 int , 
  cell1 varchar , 
  articul1 varchar2 ) return int is
  tmp int;
  ware_id1 int;
  ID1 int;
  snap_time1 Date;
  cursor sss is select rm.uid_poleta , rm.remain , pts.expiry_date  from rrl_remains rm , rrl_pallets pts where 
  pts.uid_pallet = rm.uid_poleta and rm.cell=cell1 and pts.articul=articul1 ;
  
begin 

  if(cell1 is null) or (  articul1 is null )  then 
           return -1;
  end if;

  select closed , SNAP_SHOT_TIME into tmp , snap_time1  from   RRL_REMAIN_SNAPSHOT where ID=snap_shot_id1 ;  
  if(tmp=1 ) then 
           return -1;
  end if;
  
  begin
      select ID into ID1 from RRL_REMAIN_SNAPSHOT_ROWS 
             where ARTICUL=articul1 and CELL=cell1 and  snap_shot_id=snap_shot_id1;
      return ID1;
  exception when no_data_found then null;
  end;
    
  select ware_id into ware_id1 from rrl_cells where cell=cell1 ;

  for s in sss loop

      select  RRL_REMAIN_SNAPSHOT_ROWS_SQ.NEXTVAL into ID1 from dual; 
      
      insert into RRL_REMAIN_SNAPSHOT_ROWS 
      ( ID , ARTICUL  ,CELL , PALLET_UID , REMAIN , WARE_ID ,
      CONDITION  , snap_shot_id , SNAP_TIME ) 
      values 
      ( ID1 , articul1 , cell1 , s.uid_poleta , s.remain , ware_id1 , 
      0 , snap_shot_id1 , snap_time1 );
            
   
      
  end loop;


return 1;
exception
         when no_data_found then return -2;
        -- when others then return -3;
end;

-- снимок фиксируется
function close_snapshot(  snap_shot_id1 int  ) return int is
  time_shot Date;
  cell2 varchar2(255);
  articul2 varchar2(255);
  is_first int;
  ware_id1 int;
  -- Выбираем список ячеек и артикулов
  cursor cells_arts is select distinct cell,articul 
  from rrl_remain_snapshot_rows rs where rs.snap_shot_id=snap_shot_id1;
  
  cursor current_remains is select cell, rm.uid_poleta , rm.remain  
  from rrl_remains rm , rrl_pallets pts
   where rm.uid_poleta=pts.uid_pallet and
  rm.cell = cell2 and pts.articul = articul2;
  
begin 
    
    time_shot:= systimestamp;     
    for ca in cells_arts loop
    -- по всем артикулам, ячейкам 
       -- делаем фотографию в разрезе партий. 
         cell2:= ca.cell ;
         articul2:= ca.articul;
         is_first:=1;
         select ware_id into ware_id1 from rrl_cells where cell=cell2;
         
         for r in current_remains loop
             if( is_first=1 ) then
                 update rrl_remain_snapshot_rows set 
                 PALLET_UID=r.uid_poleta , SNAP_TIME = time_shot , 
                 REMAIN = r.remain , CONDITION=1,  WARE_ID=ware_id1
                  where  snap_shot_id=snap_shot_id1 and
                 cell=cell2 and articul=articul2;
                 is_first:=0;
             else
               
               insert into rrl_remain_snapshot_rows ( 
               PALLET_UID , SNAP_TIME , REMAIN , CONDITION , WARE_ID ,  
                snap_shot_id , cell , articul
                      ) values ( r.uid_poleta , time_shot , r.remain , 1 , ware_id1 ,
                     snap_shot_id1 , cell2  , articul2 );
               is_first:=0;
               
             end if;
         end loop;
    -- конец цикла     
    end loop;
    
         
    update RRL_REMAIN_SNAPSHOT set closed=1 , SNAP_SHOT_TIME=time_shot where ID=snap_shot_id1 ;  
    return 1;
    
end;

function remains_free( articul1 varchar2 ) return number is
  tmp number;
  begin
  --         return 0;
  tmp:=0;    
  
  select sum( rem.remain ) into tmp 
  from rrl_remains rem ,  rrl_cells cel , rrl_pallets pts 
  where rem.cell = cel.cell and
  cel.blocked_for_remains=0 
  and rem.uid_poleta=pts.uid_pallet 
  and pts.articul= articul1  and rem.remain>0 ;    
  
  return tmp;
  exception when   others then return -999;
  
end;

function remains_in_otbor( articul1 varchar2 ) return number is
  tmp number;
  cell3 varchar2(255);
  begin
  tmp:=0;
  select  cell into cell3  from rrl_articuls where acticul=articul1;
  
  select sum( rem.remain ) into tmp 
  from rrl_remains rem   , rrl_pallets pts 
  where rem.cell = cell3 
  and rem.uid_poleta=pts.uid_pallet 
  and pts.articul= articul1 and rem.remain>0 ;    
  return tmp;
  exception when   others then return -999;
end;



function remains_in_otbor_all( articul1 varchar2 ) return number is
  tmp number;
  cell3 varchar2(255);
  begin
  --         return 0;
  tmp:=0;
      
  select  cell into cell3  from rrl_articuls where acticul=articul1;
  
  select sum( rem.remain ) into tmp 
  from rrl_remains rem   , rrl_pallets pts 
  where rem.cell = cell3 
  and rem.uid_poleta=pts.uid_pallet 
  and pts.articul= articul1 ;    
  
  return tmp;
  exception when   others then return -999;
  
end;


function remains_free_all( articul1 varchar2 ) return number is
  tmp number;
  begin
  --         return 0;
  tmp:=0;    
  
  select sum( rem.remain ) into tmp 
  from rrl_remains rem ,  rrl_cells cel , rrl_pallets pts 
  where rem.cell = cel.cell and
  cel.blocked_for_remains=0 
  and rem.uid_poleta=pts.uid_pallet 
  and pts.articul= articul1  and rem.remain>0 ;    
  
  return tmp;
  exception when   others then return -999;
  
end;


-- Остатки указанной партии в отборе 
function remains_partion_in_otbor( pallet_uid1 varchar2 ) return number is
  tmp number;
  articul1 varchar2(255);
  cell3 varchar2(255);
  begin
  tmp:=0.0;
  if( pallet_uid1 is null ) then
  return 0.0;
  end if;
  
  select pts.articul into articul1 from rrl_pallets pts where pts.uid_pallet=pallet_uid1 ;
  
  select  cell into cell3  from rrl_articuls where acticul=articul1;
  
  select sum( rem.remain ) into tmp 
  from rrl_remains rem  
  where rem.cell = cell3 
  and rem.uid_poleta=pallet_uid1
  and rem.remain>0 ;    
  return tmp;
  
  exception 
    when no_data_found then return 0.0;
    when   others then return -999;
end;


-- Остатки кроме указанной партии в отборе 
function remains_except_part_in_otb( pallet_uid1 varchar2 ) return number is
  tmp number;
  articul1 varchar2(255);
  cell3 varchar2(255);
  begin
  tmp:=0;
  if( pallet_uid1 is null ) then
  return 0;
  end if;
  
  select pts.articul into articul1 from rrl_pallets pts where pts.uid_pallet=pallet_uid1 ;
  
  select  cell into cell3  from rrl_articuls where acticul=articul1;
  
  -------------------------------------------
  
  select sum( rem.remain ) into tmp 
  from rrl_remains rem ,  rrl_pallets pts 
  where rem.cell = cell3 
  and rem.uid_poleta=pts.uid_pallet 
  and   rem.uid_poleta<>pallet_uid1 and pts.uid_pallet <>pallet_uid1 
  and pts.articul= articul1  and rem.remain>0 ;
       
  -------------------------------------------  
  return tmp;
  
  exception when   others then return -999;
end;

-- Остатки указанной партии в указанной ячейке 
function remains_partion_in_cell( pallet_uid1 varchar2 , cell3 varchar2 ) return number is
  tmp number;
  articul1 varchar2(255);
  begin
  if( pallet_uid1 is null ) then
      return 0;
  end if;
  
  tmp:=0;
  
  select sum( rem.remain ) into tmp 
  from rrl_remains rem  
  where rem.cell = cell3 
  and rem.uid_poleta=pallet_uid1
  and rem.remain>0 ;    
  return tmp;
  
  exception when   others then return -999;
end;


function close_othod_pall_row( PALLET_ROW_ID1 int, prih_pall_uid varchar2 , kolvo_otbora number ,   ) return int is
    current_cell varchar2(50);
    ARTICUL1 varchar2(50);
begin

    select rs.articul into ARTICUL1 
       from rrl_sborka_pallet_rows rs where id= PALLET_ROW_ID1;

 select CELL into  current_cell from  RABAEV.RRL_ARTICULS  where RRL_ARTICULS.ACTICUL= ARTICUL1 ; 
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
                      naklad_row2.PRIHOD_PALLET_UID ,
                      iser_id21 ,
                      PALLET_ROW_ID1
                      ) ;
    DBMS_OUTPUT.put_line( concat( concat( naklad_row2.ARTICUL , ' списание для определенной партии ' ) ,naklad_row2.PRIHOD_PALLET_UID ) );
  

end;


-- ФУНКЦИИ РАБОТЫ С ЗАКРЫТИЕМ ПАЛЛЕТ
FUNCTION CLOSE_OTHOD_PALLET(  PALLET_ID1 varchar2 ,  iser_id21 varchar2  ) RETURN varchar2 IS

      rm_in_otbor number;
      tmpVar int;
      current_cell  varchar2(50);
      kolvo_otbora NUMBER  ;
      new_event_id int;
      EXPEDITION_CELL varchar2(50);
      PALLET_ROW_ID1 int;

-- Курсор со строками паллета, для которых не выбрана партия .
cursor rowss is 
select * from RABAEV.RRL_SBORKA_PALLET_ROWS where PALLET_UID = PALLET_ID1 and QUANTITY>0 and PRIHOD_PALLET_UID is null ;

-- Курсор со строками паллета, для которых  выбрана партия .
cursor rowss2 is 
select * from RABAEV.RRL_SBORKA_PALLET_ROWS where PALLET_UID = PALLET_ID1 and QUANTITY>0 and not( PRIHOD_PALLET_UID is null );

cursor rowss3 is 
select * from RABAEV.RRL_SBORKA_PALLET_ROWS where PALLET_UID = PALLET_ID1 and QUANTITY>0 ;

cursor rowss4 is 
select * from RABAEV.RRL_SBORKA_PALLET_ROWS where PALLET_UID = PALLET_ID1 and QUANTITY>0 ;



--Определяем остатки в ячейке отбора в разрезе паллет, упорядоченных по срокам годности.
cursor rests_in_cell is
 select  RABAEV.RRL_REMAINS.REMAIN , RABAEV.RRL_REMAINS.UID_POLETA ,  RRL_PALLETS.EXPIRY_DATE 
  from RABAEV.RRL_REMAINS , RABAEV.RRL_PALLETS  
    where RRL_REMAINS.UID_POLETA = RRL_PALLETS.UID_PALLET and
     RRL_REMAINS.CELL = current_cell and RRL_REMAINS.REMAIN>0  
     order by RRL_PALLETS.EXPIRY_DATE  ; 
BEGIN


for naklad_row2 in rowss3 loop -- Для каждой строки паллеты фиксируем остаток в отборе до проведения паллета
 begin 
 update RABAEV.RRL_SBORKA_PALLET_ROWS set REMAINS_PICK_BEFORE = REMAINS.remains_in_otbor_all( naklad_row2.articul )  , 
 close_date=systimestamp 
    where  ID = naklad_row2.ID; 
    exception 
        when no_data_found then null; 
 end;
end loop; 

-- Паллеты во втором статусе 2 раза не проводим
  DBMS_OUTPUT.put_line(  'Начало' );
  select condition into tmpVar from RABAEV.RRL_SBORKA_PALLETs where PALLET_UID = PALLET_ID1; -- 
  if(tmpVar>=2) then   
      DBMS_OUTPUT.put_line(  'накладная закрыта' );
      return 'closed already';
  end if;
-- Паллеты во втором статусе 2 раза не проводим

-- Проводим строки паллет с подобранными партиями
for naklad_row2 in rowss2 loop
    PALLET_ROW_ID1:= naklad_row2.ID;
    kolvo_otbora:=naklad_row2.QUANTITY;
    select CELL into  current_cell from  RABAEV.RRL_ARTICULS  where RRL_ARTICULS.ACTICUL=naklad_row2.ARTICUL ; 
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
                      naklad_row2.PRIHOD_PALLET_UID ,
                      iser_id21 ,
                      PALLET_ROW_ID1
                      ) ;
    DBMS_OUTPUT.put_line( concat( concat( naklad_row2.ARTICUL , ' списание для определенной партии ' ) ,naklad_row2.PRIHOD_PALLET_UID ) );
end loop;
-- Проводим строки паллет с подобранными партиями


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

   DBMS_OUTPUT.put_line(  concat( 'НОВАЯ СТРОКА ПАЛЛЕТЫ ОТГРУЗКИ!' , naklad_row.ARTICUL ) );
   select CELL into  current_cell from  RABAEV.RRL_ARTICULS  where RRL_ARTICULS.ACTICUL=naklad_row.ARTICUL ; 
   DBMS_OUTPUT.put_line( concat( 'ЯЧЕЙКА ОТБОРА=' , current_cell ) );

 

    for  ddd8 in rests_in_cell loop  -- ЦИКЛ ПО ОСТАТКАМ В ЯЧЕЙКЕ ОТБОРА 
    
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
*/          
            DBMS_OUTPUT.put_line(  CONCAT( 'REMAIN = ' , to_char( ddd8.REMAIN ) ) );
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

commit;

for naklad_row2 in rowss4 loop
 begin 
 update RABAEV.RRL_SBORKA_PALLET_ROWS set  REMAINS_PICK_AFTER  = REMAINS.remains_in_otbor_all( naklad_row2.articul ) , close_date=systimestamp
    where  ID = naklad_row2.ID; 
    exception 
        when no_data_found then null; 
 end;
-- 

end loop; 


   DBMS_OUTPUT.put_line(  '  СОВСЕМ конец ' );   
   RETURN 'ok';

exception 
when no_data_found then  return 'neok';
when others then raise;


END CLOSE_OTHOD_PALLET;



















begin
  -- Initialization
  null;
end REMAINS;
/
