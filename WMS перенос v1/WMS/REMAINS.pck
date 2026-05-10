create or replace package REMAINS is

  -- Author  : RRABAEV
  -- Created : 15.09.2011 9:04:07
  -- Purpose : ОСТАТКИ
  

  -- Public function and procedure declarations
  function create_snapshot( type2 int  ) return int;
  function close_snapshot(  snap_shot_id1 int  ) return int;
  function add_row_2_snapshot(   snap_shot_id1 int ,   cell1 varchar ,   articul1 varchar2 ) return int;
  

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
  insert into RRL_REMAIN_SNAPSHOT (ID ,TYPE1 , create_time  ) values ( ID1 , type2 , systimestamp  ); 
   
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
begin 

if(cell1 is null) or (  articul1 is null )  then 
         return -1;
end if;


  select closed into tmp  from   RRL_REMAIN_SNAPSHOT where ID=snap_shot_id1 ;  
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

  select  RRL_REMAIN_SNAPSHOT_ROWS_SQ.NEXTVAL into ID1 from dual; 
  insert into RRL_REMAIN_SNAPSHOT_ROWS ( ID , ARTICUL  ,CELL ,WARE_ID ,CONDITION  , snap_shot_id) values 
         ( ID1 , articul1 , cell1 ,  ware_id1 , 0 , snap_shot_id1 );


exception
         when no_data_found then return -2;
         when others then return -3;
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



begin
  -- Initialization
  null;
end REMAINS;
/
