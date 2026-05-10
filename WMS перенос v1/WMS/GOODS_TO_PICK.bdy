create or replace package body GOODS_TO_PICK is

function add_summary_task( ware_id1 int ) return int
is
begin
    select RRL_SUMMARY_PICK_LIST_SQ.Nextval into id1 from dual;
    insert into  RABAEV.RRL_SUMMARY_PICK_LIST 
    (ID ,CREATEDATE , CONDITION , ware_id) 
    values  
    ( id1  , systimestamp  , 0 , ware_id1 );
return id1;
end;



-- СОЗДАНИЕ СУММАРНОГО СБОРОЧНОГО ЛИСТА 
function add_pallet_2_summary_task(  PUID varchar2 , summary_task_id1 int ) return int
is
tmp1 int;
begin
   select condition into tmp1 from  RABAEV.RRL_SUMMARY_PICK_LIST 
   where id=summary_task_id1 and condition=0;
   update  RABAEV.RRL_SBORKA_PALLETS  set summary_task_id  = summary_task_id1 
   where PALLET_UID=PUID and summary_task_id  is null;
 return 1;
 exception when no_data_found then return 0;
end;

-- СОЗДАНИЕ СУММАРНОГО СБОРОЧНОГО ЛИСТА 
function add_pallet_2_summary_task2(  PUID varchar2  ) return int
is
tmp1 int;
wid1 int;
summary_task_id1 int;
begin

   select ware_id into wid1 from   RRL_SBORKA_PALLETS PAL where PAL.PALLET_UID = PUID;
   summary_task_id1:= get_opened_summary_task( wid1 );

   select condition into tmp1 from  RABAEV.RRL_SUMMARY_PICK_LIST 
   where id=summary_task_id1 and condition=0;
   update  RABAEV.RRL_SBORKA_PALLETS  set summary_task_id  = summary_task_id1 
   where PALLET_UID=PUID and summary_task_id  is null;

   select PAL.SUMMARY_TASK_ID into summary_task_id1 from RRL_SBORKA_PALLETS PAL where PAL.PALLET_UID = PUID ;
   return summary_task_id1;
   
 exception when no_data_found then return 0;
end;


 -- ПОЛУЧИТЬ ПЕРВЫЙ СОЗДАННЫЙ И НЕЗАВЕРШЕННЫЙ СУММАРНЫЙ СБОРОЧНЫЙ ЛИСТ 
function get_opened_summary_task(ware_id1 int) return int
is
begin

    begin 
        select  max(ID) into id1 from RABAEV.RRL_SUMMARY_PICK_LIST 
        where condition=0 and ware_id=ware_id1 order by CREATEDATE desc  ;
        if(id1 is null) then
               return add_summary_task( ware_id1  );
        end if;
        return id1;
    exception 
        when no_data_found then  return add_summary_task( ware_id1  );
        when others then  return add_summary_task( ware_id1  );
    end ;
    return add_summary_task( ware_id1  );
end;


-- СОЗДАТЬ ЗАДАЧИ ДЛЯ ВОДИТЕЛЕЙ   РИЧТРАКА 
/* на основании номера ССЛ (Суммарного сборочного листа) выбираем 
строки паллет, привязанных к этому ССЛ. 
Артикулы упорядочиваем в порядке сборки
 */
function create_wtasks( summary_task_id1 int ) return int is

cursor sss is
 select RS.ARTICUL , sum( RS.QUANTITY ) from RABAEV.RRL_SBORKA_PALLETS PAL , 
RABAEV.RRL_SBORKA_PALLET_ROWS RS
 where PAL.SUMMARY_TASK_ID = summary_task_id1 and
 PAL.PALLET_UID=RS.PALLET_UID group by RS.ARTICUL; -- order by порядок сборки 
  
begin
select condition into tmp from RABAEV.RRL_SUMMARY_PICK_LIST where id=summary_task_id1;
    if(tmp<>0) then
     return 0;    
    end if;
    
    for ss in sss loop
         DBMS_OUTPUT.put_line(  ss.ARTICUL );  
    
    end loop;
    
    update  RABAEV.RRL_SUMMARY_PICK_LIST  set condition=1 where id=summary_task_id1;
return 1;
end ;

-- Функции стратегии размещения товара по ячейкам. 

begin
  -- Initialization
 null;
end GOODS_TO_PICK;
/
