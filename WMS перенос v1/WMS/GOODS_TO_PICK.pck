CREATE OR REPLACE PACKAGE GOODS_TO_PICK is

id1 int;
tmp int;

function delete_wtasks( summary_task_id1 int ) return int ;
 function add_summary_task( ware_id1 int)  return int ;
 function add_pallet_2_summary_task(  PUID varchar2 , summary_task_id1 int ) return int;
 function add_pallet_2_summary_task2(  PUID varchar2   ) return int;
 function distance_2_pick( CELL1 varchar2 , ware_id1 int ) return number;
 function get_opened_summary_task(ware_id1 int) return int;
function create_wtasks( summary_task_id1 int ) return int;
function update_wt_row( summary_task_id1 int , 
       articul1 varchar2 , QUANTITY1 number , QUANTITY_PLANNED1 number ,
       QUANTITY_COMPLETE1 number  ) return int ;






END GOODS_TO_PICK; 
/
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

-- МЕРА БЛИЗОСТИ ПРИ ПОДБОРЕ ПАЛЛЕТЫ В ХРАНЕНИИ
-- Паллеты выбираются в порядке Срока годности и Близости к месту сборки.
-- Близость к месту сборки = Мера. =  x +z*100.
function distance_2_pick( CELL1 varchar2 , ware_id1 int ) return number is
x1 number  ;
y1 number ;
z1 number;
Y_VISOTA1 number;
begin
   select x,y,z , Y_VISOTA into x1,y1,z1 , Y_VISOTA1 from RRL_CELLS CL 
          where CELL=CELL1 and CL.WARE_ID=ware_id1;
  if(Y_VISOTA1 is null) then 
               Y_VISOTA1:=y1;
  end if;

  if z1 is null then z1:=0;
  end if; 
return x1+Y_VISOTA1*10+Z1;
 exception 
  when no_data_found then  return 100;
    when others then return 100;
end;


function update_wt_row( summary_task_id1 int , 
       articul1 varchar2 , QUANTITY1 number , QUANTITY_PLANNED1 number ,
       QUANTITY_COMPLETE1 number  ) return int 
is
cond1 int;
id1 int;
begin
    select id into id1 from RRL_SUMMARY_PICK_LIST_ROWS where ARTICUL = articul1 and SPL_ID = summary_task_id1;
    update RRL_SUMMARY_PICK_LIST_ROWS set 
           QUANTITY= QUANTITY1, QUANTITY_COMPLETE=QUANTITY_COMPLETE1 , 
           QUANTITY_PLANNED=QUANTITY_PLANNED1 , condition=cond1
    where
           ARTICUL = articul1 and SPL_ID = summary_task_id1;

  return id1;
exception
  when no_data_found then   
  begin
    insert into RABAEV.RRL_SUMMARY_PICK_LIST_ROWS 
    (ARTICUL , SPL_ID , QUANTITY , QUANTITY_COMPLETE , QUANTITY_PLANNED , CONDITION )
     values ( articul1 , summary_task_id1 , QUANTITY1 , QUANTITY_COMPLETE1 , QUANTITY_PLANNED1  ,  cond1 );
    return 1;
  end;
  when others then   
  begin
    
    delete from RABAEV.RRL_SUMMARY_PICK_LIST_ROWS where ARTICUL = articul1 and SPL_ID = summary_task_id1;  
    insert into RABAEV.RRL_SUMMARY_PICK_LIST_ROWS 
    (ARTICUL , SPL_ID , QUANTITY , QUANTITY_COMPLETE , QUANTITY_PLANNED , CONDITION )
     values ( articul1 , summary_task_id1 , QUANTITY1 , QUANTITY_COMPLETE1 , QUANTITY_PLANNED1  ,  cond1 );
    return 1;

  end;    
  
end update_wt_row;



-- СОЗДАТЬ ЗАДАЧИ ДЛЯ ВОДИТЕЛЕЙ   РИЧТРАКА 
/* на основании номера ССЛ (Суммарного сборочного листа) выбираем 
строки паллет, привязанных к этому ССЛ. 
Артикулы упорядочиваем в порядке сборки
*/
 
function delete_wtasks( summary_task_id1 int ) return int is
begin
  
delete from RABAEV.RRL_SUMMARY_PICK_LIST where ID = summary_task_id1;
return 0;
end;

function create_wtasks( summary_task_id1 int ) return int is
   ware_id2 int;
   articul3 varchar2(50);
   skolko_nado number;
   count2 number;
   tmp1 int ;
   
   flag_last_pal1 int;
   flag_partial1 int;
   cell_otb varchar2(50);
skolko_pologeno number;
   
-- КУРСОР СУММАРНЫЙ ЛИСТ .       
  cursor sss is
  select ARTICUL , Q , SEQ , SEQ_GROUP from (
  select ARTICUL , Q , compl.show_sq(ARTICUL , ware_id2) SEQ , 
   compl.show_sq_gr(ARTICUL , ware_id2) SEQ_GROUP
   from (
       select RS.ARTICUL , sum( RS.QUANTITY ) Q 
       from RABAEV.RRL_SBORKA_PALLETS PAL , 
       RABAEV.RRL_SBORKA_PALLET_ROWS RS , RRL_ARTICULS ART
       where PAL.SUMMARY_TASK_ID = summary_task_id1 and
       PAL.PALLET_UID=RS.PALLET_UID and RS.QUANTITY >0
       and ART.ACTICUL = RS.ARTICUL and ART.CELL='E-6-6-6-6'
        group by RS.ARTICUL
       ) )
   order by SEQ_GROUP ,SEQ 
   ; -- order by порядок сборки 


-- КУРСОР С ОСТАТКАМИ НА СКЛАДЕ ВО ВСЕХ ДОСТУПНЫХ ЯЧЕЙКАХ  
  cursor ostat is
  select RM.REMAIN , RM.CELL , RM.UID_POLETA , 
  distance_2_pick(RM.CELL , ware_id2 ) dist  , PL.EXPIRY_DATE
    from RRL_REMAINS RM , RRL_CELLS CL , RRL_PALLETS PL 
    where CL.WARE_ID=ware_id2 and RM.CELL=CL.CELL
   and CL.BLOCKED_FOR_POPOLNENIE=0 and CL.BLOCKED_FOR_REMAINS=0
   and PL.UID_PALLET=RM.UID_POLETA and PL.ARTICUL=articul3 and RM.REMAIN>0
  order by EXPIRY_DATE , dist  ; -- КУРСОР С ОСТАТКАМИ НА СКЛАДЕ ВО ВСЕХ ДОСТУПНЫХ ЯЧЕЙКАХ   



begin
  cell_otb:='';
  DBMS_OUTPUT.put_line( 'Начало create_wtasks ');
select condition , WARE_ID into tmp , ware_id2 
       from RABAEV.RRL_SUMMARY_PICK_LIST where id=summary_task_id1;

    if(tmp<>0) then
     return 0;    
    end if;
update RABAEV.RRL_SUMMARY_PICK_LIST set condition =1 where id=summary_task_id1; 
delete from RABAEV.RRL_WT where parent_id = summary_task_id1 and type1='WR1';

    for ss in sss loop -- По всем строкам ссумарного сборочного листа (ССЛ)
        -- DBMS_OUTPUT.put_line(  ss.ARTICUL ); 
         articul3:= ss.ARTICUL ; 
         cell_otb:='';
         begin
                    select CELL into cell_otb from rrl_articuls where acticul= articul3;
         exception
           when no_data_found then cell_otb:='NO';
         end;
         skolko_nado := ss.q;
         skolko_pologeno:=0;
         -- для каждой строки Артикул, количество подбираем 
         -- необходимое количество товара на паллетах в Хранении
         --    Берем его как максимально подходящий по срокам, наиболее близко-стоящий
         for ost1 in ostat loop

              flag_last_pal1 :=0;
              flag_partial1  :=0;
   
         if(skolko_nado>0) then
                  count2 :=  min2 ( ost1.Remain , skolko_nado );
                  -- если ost1.Remain > skolko_nado ставим метку последнего неполного паллета 
                  if  ost1.Remain > skolko_nado then 
                       flag_partial1:=1;
                  end if;
                  
                  skolko_nado:= skolko_nado - count2 ;
                  DBMS_OUTPUT.put_line( 
                   concat( concat( concat( concat( ' ARTICUL=' , ss.ARTICUL )  ,
                   concat( ' CELL =' , ost1.CELL ) ) , concat(  ' dist=' , to_char(ost1.dist) ) ) ,
                   concat (concat( ' UID_POLETA =' , ost1.UID_POLETA ) ,
                   concat( ' EXPIRY_DATE =' , to_char( ost1.EXPIRY_DATE ) ) )   
                   ) ) ;
                   -- ДОБАВЛЯЕМ ДАННЫЙ ПАЛЛЕТ НА СПУСК ВНИЗ. 
                  
                  -- если  skolko_nado=0 ставим метку последнего паллета
                  if(skolko_nado=0) then
                  flag_last_pal1 :=1;
                  end if;
                  
                  insert into RABAEV.RRL_WT
                  (  
                  ORDER1 , 
                  articul ,
                    TYPE1 , --{ WR – Задача ричтраку на пополнение WR1 – Задача ричтраку на пополнение зоны динамического подбора }
                    PUID  , FROM1 , TO1   , COUNT1 ,   
                    --PLAN_START_TIME ,PLAN_END_TIME , FACT_START_TIME ,FACT_END_TIME ,
                    WORKER  , -- РИЧТРАК 
                    CONDTION   ,  -- Состояние. 0-не назначена 1-назначена 2-начата 3-закончена.
                    PARENT_ID , -- Ссылка на создателя.  summary_task_id
                    flag_partial ,
                    flag_last_pal
                  ) values ( 
                  ss.seq ,
                  articul3 ,
                  'WR1' ,  ost1.UID_POLETA  , ost1.cell , cell_otb , count2 , 
                  --null , null ,null , null 
                  null , 0 , summary_task_id1 , flag_partial1 , flag_last_pal1 );
                  skolko_pologeno := skolko_pologeno +count2;
                    

                  
                  
                  
                  
                  -- КОНЕЦ СОЗДАНИЯ WTASK.
         end if;
         end loop;
         
         -- НЕ ХВАТАЕТ 
         if( skolko_nado>0 ) then
          DBMS_OUTPUT.put_line( concat( concat( 'для артикула ' , ss.articul ) , concat( ' не хватает ' ,  skolko_nado ) ) );
         
          insert into RABAEV.RRL_WT
                  (  
                  ORDER1 , 
                  articul ,
                    TYPE1 , --{ WR – Задача ричтраку на пополнение WR1 – Задача ричтраку на пополнение зоны динамического подбора }
                    PUID  , FROM1 , TO1   , COUNT1 ,   
                    
                    WORKER  , -- РИЧТРАК 
                    CONDTION   ,  -- Состояние. 0-не назначена 1-назначена 2-начата 3-закончена.
                    PARENT_ID , -- Ссылка на создателя.  summary_task_id
                    flag_last_pal
                  ) values ( 
                  ss.seq ,
                  articul3 ,
                  'WR1' ,  'NULL'  , 'INVENT' , cell_otb , skolko_nado ,  
                  null , 0 , summary_task_id1 , 1 );
         
         end if;
         -- НЕ ХВАТАЕТ 
         
         
         tmp1:=update_wt_row( summary_task_id1  , 
                        ss.articul  , ss.q ,  skolko_pologeno ,
                        0  );
         
    end loop;
--    Закрываем ССЛ (condition=1)
     DBMS_OUTPUT.put_line( 'Конец create_wtasks ');
    update  RABAEV.RRL_SUMMARY_PICK_LIST  set condition=2 where id=summary_task_id1;
return 1;
end ;

-- Функции стратегии размещения товара по ячейкам. 

begin
  -- Initialization
 null;
end GOODS_TO_PICK;
/
