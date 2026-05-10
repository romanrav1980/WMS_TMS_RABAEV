create or replace package compl is

  -- Author  : RRABAEV
  -- Created : 29.05.2011 15:39:59
  -- Purpose : Комплектация и сборка товара, деление на паллеты
  
  -- Public function and procedure declarations
  function update_seq( articul1 varchar2 , ware_id1 int , SQ1 int, SQGROUP int ) return int;
  function show_sq( articul1  varchar2 , ware_id1 int ) return int ;
  function show_sq_gr( articul1 varchar2 , ware_id1  int ) return int ;
  function divide_st_bypal(  stn varchar2 , ware_id11  int , user_id11 varchar2 ) return int ;
  function create_order_from_spallets( st_numb varchar2 , user_id1 varchar2 ) return int ;
  function path( articul1 varchar2 ,  sborka_pallet_uid  varchar2 ) return varchar2 ;
  function truncate_order_by_remains(  ware_id6 int )  return int ;
  function orders_start_plan(  ord_id1 int )  return int ;
  function orders_create_vycherk(  ord_id1 int )  return int ;
  function orders_check(  ware_id6 int )  return int ;
  function divide_order_bypal2( ord_id1 int ,  user_id11 varchar2 ) return int;
  function RRL_COUNT_KOR3(  row_id int) return int ;
  function RRL_COUNT_KOR4(  row_id int) return varchar2;
  function CHANGE_PALLET_ROW_QUANTITY( row_id1 int , q number , Partion varchar2 ) return int;
  function filter_show_weight_brutto( weight1 number ,  articul1 varchar2  ) return varchar2;
  function order_cond1( order_id1 int) return int ;

  function print_perc_defect( PALLET_ID1 varchar2 ) return varchar2 ;
  function print_brutto_defect( PALLET_ID1 varchar2 , weight1 number ) return varchar2; 
  function print_kolbasa_sobr( ei varchar2 , cnt number , cnt_kor number ) return varchar2 ;
  function print_ufa_sobr( ei varchar2 , cnt number , cnt_kor number ) return varchar2 ;
  function can_edit_sb_pallet( pallet_uid1 varchar2 ) return int;
  function order_rows_count( order_id1 int   ) return int;
  function order_vycherk_count( order_id1 int   ) return int ;
  function reset_2_first_status( order_id1 int   ) return int ;
 
  function debug_truncate_rem(articul1 varchar2 , ware_id6 int) return number ;
  function debug_truncate_reserv(articul1 varchar2 , ware_id6 int) return number;
  function debug_truncate_orders(articul1 varchar2 , ware_id6 int) return number; 
  FUNCTION RRL_GIVE_PALLET_UID( ST_NUMBER1 varchar2 , USER_ID1 varchar2 ,  
  PALLET_NUMBER1 int ) return varchar2 ;
  FUNCTION RRL_SBORKA_PAL_REMOVE_EMPTY( ST_NUMBER1 varchar2 , USER_ID1 varchar2  ) return int ;
  FUNCTION RRL_COPY_PALLET_ROW3(   row_id2 int ,  count1  number ,   PALLET_UID_NEW    VARCHAR2  ) RETURN int ;

  function pallet_compl_date( pall_uid varchar2 ) return Date ;
  FUNCTION RRL_vlozennost ( ART varchar2  ) return number;
  function perdiction_count_pall( st_number1 varchar2 ) return number ;
  function update_seq2( articul1 varchar2 , cell1 varchar2 , SQ1 int, SQGROUP int ) return int ;


function time_shift_end( time1 date ) return Date ;
function time_shift_start( time1 date ) return Date ;
  
  
end compl;
/
create or replace package body compl is


  -- Function and procedure implementations
function update_seq( articul1 varchar2 , ware_id1 int , SQ1 int, SQGROUP int ) return int is
     d1 int;
  begin
        select     SQ.SEQ into d1
         from RABAEV.RRL_COMPL_SEQ SQ where SQ.ARTICUL=articul1 and SQ.WARE_ID= ware_id1 ; 
         update RABAEV.RRL_COMPL_SEQ  set SEQ=SQ1 , SEQ_GROUP = SQGROUP 
         where articul= articul1 and ware_id= ware_id1;
        return 1;
    EXCEPTION
      WHEN no_data_found then 
        insert into RABAEV.RRL_COMPL_SEQ  ( articul , WARE_ID , SEQ ,SEQ_GROUP )values
               (articul1 , ware_id1 , SQ1 ,SQGROUP );
               return 1;
  end;


function update_seq2( articul1 varchar2 , cell1 varchar2 , SQ1 int, SQGROUP int ) return int is
     d1 int;
     ware_id1 int ;
  begin
  
  begin
  select ware_id into ware_id1 from rrl_cells where cell=cell1 ;
    exception
      when no_data_found then return -1 ;
  end; 
  
        select     SQ.SEQ into d1
         from RABAEV.RRL_COMPL_SEQ SQ where SQ.ARTICUL=articul1 and SQ.WARE_ID= ware_id1 ; 
         update RABAEV.RRL_COMPL_SEQ  set SEQ=SQ1 , SEQ_GROUP = SQGROUP 
         where articul= articul1 and ware_id= ware_id1;
        return 1;
    EXCEPTION
      WHEN no_data_found then 
        insert into RABAEV.RRL_COMPL_SEQ  ( articul , WARE_ID , SEQ ,SEQ_GROUP )values
               (articul1 , ware_id1 , SQ1 ,SQGROUP );
               return 1;
  end;



-- Порядок сборки для артикула
function show_sq( articul1 varchar2 , ware_id1  int ) return int is
  ret1 int;
begin

    select SQ.SEQ into ret1 from RRL_COMPL_SEQ SQ where articul=articul1 and ware_id=ware_id1;
    return ret1;
    exception
           
      when no_data_found then
      begin
           select max( SQ.SEQ ) into ret1 
           from RRL_COMPL_SEQ SQ 
           where articul=articul1  ;

       return ret1;
      end;
    when others then 
      begin
        delete from  RRL_COMPL_SEQ SQ where articul=articul1 and ware_id=ware_id1 and rownum>1 ;
        
         select SQ.SEQ into ret1 from RRL_COMPL_SEQ SQ where articul=articul1 and ware_id=ware_id1;
         return ret1;
      end;
end;


-- ГРУППА СБОРКИ ДЛЯ АРТИКУЛА
function show_sq_gr( articul1 varchar2 , ware_id1  int ) return int is
  ret1 int;
begin

    select SQ.SEQ_GROUP into ret1 from RRL_COMPL_SEQ SQ where articul=articul1 and ware_id=ware_id1;
    return ret1;
    exception
      when no_data_found then return 101;
    when others then 
      begin
        delete from  RRL_COMPL_SEQ SQ where articul=articul1 and ware_id=ware_id1 and rownum>1 ;
        commit;
         select SQ.SEQ_GROUP into ret1 from RRL_COMPL_SEQ SQ where articul=articul1 and ware_id=ware_id1;
         return ret1;
      end;
end;

-- Ячейка отбора для данного артикула в данной заявке.
function path( articul1 varchar2 ,  sborka_pallet_uid  varchar2 ) return varchar2 is
  ret1 varchar2(50);
begin

select cell into ret1  from RRL_ARTICULS where acticul = articul1;
return ret1;
exception 
when no_data_found then return 'NO_ART';
when others then  return  'ERR8';
end;

-- ДЕЛЕНИЕ СТ НА ПАЛЛЕТЫ.
-- деление ст на паллеты.
-- настройки склада - Максимум 

-- берем максимальное ограничение на паллеты из настроек склада.
-- подпроцедура сделать разбиение на основе поданных настроек.
-- Берем строки заказа из таблицы RABAEV.RRL_ORDER_ROWS  (RRL_ORDERS - шапка)
-- По всем строкам  

-- если предыдущий паллет завершен, начинаем новый паллет
-- конец если
--  у= мин ( количество коробок данного артикула , необходимое для завершения паллета , заказ на данный артикул )

-- если у=0, завершаем паллет, повторяем 
--       у= мин ( количество коробок данного артикула , необходимое для завершения паллета , заказ на данный артикул )
-- конец если 
-- Конец по всем строкам
-- фиксируем версию разбиения
-- конец процедуры.
         








-- подпроцедура сделать разбиение на основе поданных настроек( МаксимумV , МаксимумМ , номер заказа ). Возврат число
function sub_divide_pall( ord_id int , vers1 int , MAXV1 number , MAXM1 number , COMPL_GR int , ware_id2 int ) return int is 
--  Берем строки заказа из таблицы RABAEV.RRL_ORDER_ROWS  (RRL_ORDERS - шапка) 
    cursor ORDER_ROWS is 
       select RS.ARTICUL , RS.ORDER_WEIGHT , RS.QUANTITY ,
        RS.TARESIZE , RS.TAREWEIGHT , RS.ORIGINAL_QUANTITY , 
        RS.Original_Order_Weight , RS.MOD_ID , RS.EI , RS.SORTFIELD    
       from RABAEV.RRL_ORDER_ROWS RS where RS.ORDER_ID = ord_id and
       show_sq_gr( RS.ARTICUL , ware_id2 ) = COMPL_GR 
       ;
       pall_numb1 int;
       new_pall_bool int;
       K number;
       y number;
       MAXV2 number;
       MAXM2 number;
       NU number;
       sht_in_kor1 number;
       count_kor1 number;
       
begin
  pall_numb1:=0;
  K:=0;
  y:=0;
  MAXV2:=0;
  MAXM2:=0;
  new_pall_bool:=1;--  Начинаем 1-й паллет;
--    Берем строки заказа из таблицы RABAEV.RRL_ORDER_ROWS  (RRL_ORDERS - шапка) 
for r in order_rows loop--  По всем строкам  

begin
  if( r.Mod_Id=0 ) then
       select A.NORMA_UKLADKI , A.COUNT_SHT_IN_KOR into NU , sht_in_kor1  from RRL_ARTICULS A where acticul = r.articul;
  else
       select M.Sht_In_Kor into  sht_in_kor1 from RRL_ARTICUL_MODS M where M.ID = r.Mod_Id;
  end if;
  exception when no_data_found then raise;
end;

    if(sht_in_kor1=0) then 
          sht_in_kor1:=1;
    end if;

    K:= r.quantity;
    y:=1;
    while K>0 and y>0 loop
      
--        у = мин ( количество коробок данного артикула необходимое для завершения паллета, заказ на данный артикул )
      if  r.taresize >0 and r.tareweight>0 then
            count_kor1:= min2( ( MAXV1 - MAXV2 ) / r.taresize ,  ( MAXM1 - MAXM2 )/r.tareweight  ) ;
      else
           if( r.taresize<=0 and r.tareweight>0 ) then
               count_kor1:=( MAXM1 - MAXM2 )/r.tareweight ;
           end if;
           
           if( r.taresize>0 and r.tareweight<=0 ) then
               count_kor1:= ( MAXV1 - MAXV2 ) / r.taresize ;
           end if;
           if( r.taresize <=0 and r.tareweight<=0 ) then
               begin
	                  select A.NORMA_UKLADKI/sht_in_kor1 into count_kor1  from RRL_ARTICULS A where acticul = r.articul;
               exception when no_data_found then y:=0;
               end;
           end if;
      end if;
      -- ОКРУГЛЯЕМ У до коробки вверх 
      --count_kor1:=round( y/ sht_in_kor1 , 0 );
      y:= count_kor1 * sht_in_kor1 ; 
      -- у = мин ( количество коробок данного артикула необходимое для завершения паллета, заказ на данный артикул )  
      K:=K-y;
      if y=0 then
          pall_numb1:= pall_numb1+1;
--        завершаем паллет(версия, номер паллета);
--        Начинаем новый паллет ; 
      else
          -- Добавляем строку в паллет с У штук.
          insert into  RABAEV.TMP_PALLET_ROWS 
          (   VERS , ORDER_ID , ARTICUL  ,
              EI       , ORDER_WEIGHT , QUANTITY     ,
              SORTFIELD    , PACK_COUNT   ,TARESIZE     ,
              TAREWEIGHT , PALL_NUMB ) values 
          ( vers1 , ord_id , r.articul , r.ei , count_kor1*r.tareweight , y ,  r.sortfield, count_kor1 ,
           r.taresize , r.tareweight , pall_numb1 );
          
      end if;
      
    end loop;

--    К = количество товара в заказе
--    у=1;
--      Пока к>0 и у>0 цикл
--        у = мин ( количество коробок данного артикула необходимое для завершения паллета, заказ на данный артикул )

--        К=К-у;
--            если у=0, 
--                 завершаем паллет(версия, номер паллета);
--                 Начинаем новый паллет;
--            Иначе 
--            у коробок из заказа переносим в текущий паллет.
--                  если к=0 тогда
--                  конец если;
--            конец если;
--      конец цикла;

end loop;--  Конец по всем строкам

--фиксируем версию разбиения
--возвращаем количество паллет.
 

  return 0;
end;



function divide_st_bypal( stn varchar2 , ware_id11  int , user_id11 varchar2 ) return int is
  ord_id1 int;
  ware_id2 int;
  tmp int;
  vers1 int;
  cursor sqs is 
    select distinct show_sq_gr( RS.ARTICUL , ware_id2 ) GR  from RRL_ORDER_ROWS RS 
           where RS.ORDER_ID= ord_id1 ;

  ret1 int;
  MAXV1 NUMBER;
  MAXM1 NUMBER;
begin

  vers1:=1;
 

--ord_id1 := create_order_from_spallets(stn , user_id1);
  select ORDD.ID , ORDD.Ware_Id  into ord_id1 , ware_id2 
   from RRL_ORDERS ORDD where ORDD.ORD_NUMBER = stn ; 

-- ПО ВСЕМ ГРУППАМ КОМПЛЕКТАЦИИ ДЛЯ ДАННОГО СТ
  for s in sqs loop
     begin
       select GR.MAXV , GR.MAXM into MAXV1 , MAXM1  from RABAEV.RRL_COMPL_SEQ_GR GR where ID = s.gr  ;
     exception
       when no_data_found then  
         MAXV1:=20000 ; 
         MAXM1:=950;
     end; 
    tmp:= sub_divide_pall( ord_id1 , vers1 , MAXV1  , MAXM1  , s.gr , ware_id2  ) ;


  end loop;


commit ;
  return 0;
  exception 
    when no_data_found then return -1;
  
end; 


-- СОЗДАНИЕ ЗАКАЗА ИЗ СТ 
function create_order_from_spallets( st_numb varchar2 , user_id1 varchar2 ) return int is
  ret1 int;
  CREATE_DATE1  DATE  ;
  WARE_ID1      INTEGER ;
  ADDR1         VARCHAR2(255 BYTE);
  STATE1        VARCHAR2(50 BYTE);
  ORDDATE1      DATE;
  ord_id int;

 cursor sss is 
      select EI, max( TARESIZE ) TARESIZE, max( TAREWEIGHT ) TAREWEIGHT, 
      sum( ORIGINAL_ORDER_WEIGHT ) ORIGINAL_ORDER_WEIGHT, sum( ORIGINAL_QUANTITY ) ORIGINAL_QUANTITY,
      sum( PACK_COUNT ) PACK_COUNT, sum( QUANTITY  ) QUANTITY, sum(ORDER_WEIGHT) ORDER_WEIGHT,
      ARTICUL , SORTFIELD , PAL.WARE_ID , SHORTNAME
      from  RRL_SBORKA_PALLET_ROWS RR , RRL_SBORKA_PALLETS PAL
     where  RR.PALLET_UID = PAL.Pallet_Uid and PAL.ST_NUMBER = st_numb 
group by EI,        PACK_COUNT , QUANTITY , ORDER_WEIGHT ,
      ARTICUL , SORTFIELD , PAL.WARE_ID , SHORTNAME
order by SORTFIELD;

begin
  
  select RRL_ORDERS_SQ.NEXTVAL into  ord_id from dual;
  delete from RABAEV.RRL_ORDERS where ORD_NUMBER= st_numb; -- Строки удалятся каскадно.
  -- Создаем шапку
  
  select PAL.CREATE_DATE , PAL.WARE_ID , PAL.ADDR , PAL.State , PAL.CREATE_DATE  into
   CREATE_DATE1 , WARE_ID1 ,ADDR1 ,STATE1  , ORDDATE1 
   from RRL_SBORKA_PALLETS PAL where  PAl.St_Number=st_numb and rownum=1;
   
   
  insert into  RABAEV.RRL_ORDERS (ID, CREATE_DATE ,WARE_ID ,ADDR ,
  STATE ,ORDDATE , USER_ID , ORD_NUMBER) 
  values( ord_id , CREATE_DATE1,WARE_ID1 ,ADDR1 ,
  STATE1  , ORDDATE1, user_id1 , st_numb );
  
  
  for s in sss  loop
  
  
  insert into  RRL_ORDER_ROWS 
  (
    ORDER_ID                ,
    ARTICUL                 ,
    SHORTNAME               ,
    EI                      ,
    ORDER_WEIGHT            ,
    QUANTITY                ,
    SORTFIELD               ,
    WARE_ID                 ,
    PACK_COUNT              ,
    ORIGINAL_QUANTITY       ,
    ORIGINAL_ORDER_WEIGHT   ,
    CONDITION   ,
    TARESIZE  ,
    TAREWEIGHT
  ) values (
   ord_id,
    s.ARTICUL                 ,
    s.SHORTNAME               ,
    s.EI                      ,
    s.ORDER_WEIGHT            ,
    s.QUANTITY                ,
    s.SORTFIELD               ,
    s.WARE_ID                 ,
    s.PACK_COUNT              ,
    s.ORIGINAL_QUANTITY       ,
    s.ORIGINAL_ORDER_WEIGHT   ,
    0  ,
    s.TARESIZE  ,
    s.TAREWEIGHT
  );
  end loop;  
  -- Создаем строки - копируем из  RRL_SBORKA_PALLET_ROWS в   RABAEV.RRL_ORDER_ROWS  
  return ord_id;
end;


function order_cond1( order_id1 int) return int is
ret int;
  begin
    
  select COND into ret from rrl_orders where id=order_id1;
  return ret;
  exception
    when no_data_found then return 10;
end;

-- *****************************************************************************************
-- Функция обрезает заказ по доступному остатку ********************************************
-- и создает записи в таблице резерва. *****************************************************
-- *****************************************************************************************

function debug_truncate_rem(articul1 varchar2 , ware_id6 int) return number is
ret1 number;
  begin
    
      select  sum( rm.remain ) into ret1
      from rrl_remains rm , rrl_cells cl , rrl_pallets plts
      where rm.cell = cl.cell and ( cl.otbor=1 or cl.blocked_for_remains=0 )
      and plts.uid_pallet=rm.uid_poleta and cl.ware_id=ware_id6 and rm.remain > 0 and plts.articul=articul1
      group by plts.articul;

      return ret1;
  exception
  when no_data_found then return 0;
  end;

function debug_truncate_reserv(articul1 varchar2 , ware_id6 int) return number is
ret1 number;
  begin
      select sum( rs2.QUANTITY_PLANNED ) into  ret1 
        from RRL_ORDER_ROWS rs2 , rrl_orders ords where  
        ords.id = rs2.order_id and ords.cond in ( 1,2,3,4,5) and 
        rs2.ware_id = ware_id6 and rs2.articul = articul1
        and rs2.condition =2  
        group by rs2.articul ;
      return ret1;
  exception
  when no_data_found then return 0;
  end;

function debug_truncate_orders(articul1 varchar2 , ware_id6 int) return number is
ret1 number;
  begin

      select  sum( rs2.quantity ) into ret1
      from RRL_ORDER_ROWS rs2, rrl_orders ords where   rs2.articul = articul1 and 
      ords.id = rs2.order_id and ords.cond in (0,1,2,3,4,5) and 
      rs2.ware_id = ware_id6 
      and rs2.condition =1 group by  rs2.articul ;
  
      return ret1;
  exception
  when no_data_found then return 0;
  when others then return -1;
  end;

function truncate_order_by_remains(  ware_id6 int )  return int is
  to_spis number;
  ret1 int;
  ware_id2 int;
  tmp_art varchar2(25);
  count_in_reserv number;
  id1 int;
  count_needed number;
  count_putted number;
  TMP_COMPL_REMAINS_HISTORY_ID int;
  
  cursor remains1 is  -- Курсор для формирования курсора остатков 
      select plts.articul, plts.expiry_date , plts.mod_id  , plts.uid_pallet ,
      sum( rm.remain ) remain
      from rrl_remains rm , rrl_cells cl , rrl_pallets plts
      where rm.cell = cl.cell and ( cl.otbor=1 or cl.blocked_for_remains=0 )
      and plts.uid_pallet=rm.uid_poleta and cl.ware_id=ware_id2 and rm.remain > 0 
      group by plts.articul, plts.expiry_date , plts.mod_id  , plts.uid_pallet 
      order by plts.articul , plts.expiry_date ; 
  
    
  cursor remains2 is -- Курсор остатков
  select plts.articul , plts.expdate  , plts.mod_id ,  plts.partion , 
  plts.quantity , plts.id
  from  TMP_COMPL_REMAINS plts
  where plts.articul=tmp_art and  plts.quantity>0
  order by articul,expdate ;
  
  cursor reserves is -- Курсор резервов 
       --  select sum( rs.qty ) qt , rs.articul   
       --  from RRL_COMPL_RESERVE rs where  rs.ware_id=ware_id2 and rs.articul = tmp_art
       --  group by rs.articul ; 
        select sum( rs2.QUANTITY_PLANNED ) qt  ,   rs2.articul 
        from RRL_ORDER_ROWS rs2 , rrl_orders ords where --rs.order_id =  ord_id1
        ords.id = rs2.order_id and ords.cond in ( 1,2,3,4,5) and 
        rs2.ware_id = ware_id2 and rs2.articul = tmp_art
        and rs2.condition =2  
          group by rs2.articul ;
         
         
         
  cursor rws is -- Строки заказов
  select rs2.id , rs2.articul , rs2.quantity , rs2.order_id 
  from RRL_ORDER_ROWS rs2, rrl_orders ords where --rs.order_id =  ord_id1
  ords.id = rs2.order_id and ords.cond in (0,1,2,3,4,5) and 
  rs2.ware_id = ware_id2 
  and rs2.condition =1 order by  rs2.articul , ords.ord1 , rs2.order_id ;
        
         
begin

-- ======== ФОРМИРУЕМ КУРСОР ОСТАТКОВ  ЗА МИНУСОМ РЕЗЕРВОВ ==========================
ware_id2:=ware_id6;
to_spis:=0;
id1:=0;
tmp_art:='';

delete from RABAEV.TMP_COMPL_REMAINS;
for rem1 in remains1 loop -- По всем остаткам 
     count_in_reserv:=0;
         
     if( (tmp_art<> rem1.articul) or ( tmp_art is null ) ) then -- Новый артикул 
         tmp_art:= rem1.articul;
         for rrr in reserves loop
             count_in_reserv:=  rrr.qt;   -- Сколько в резерве висит на данный товар.   
         end loop;       
     end if;   

      if( count_in_reserv<=0 or count_in_reserv < rem1.remain ) then
              to_spis := min2(   rem1.remain - count_in_reserv  , rem1.remain ) ;
              count_in_reserv:=0;
      else
              to_spis:=0;
              count_in_reserv:=count_in_reserv-rem1.remain;
      end if;
     
           
      if(  to_spis>0 ) then
      id1:=id1+1;
            insert into RABAEV.TMP_COMPL_REMAINS -- Таблица с остатками за минусом резерва.
            ( ID , WARE_ID   ,  ARTICUL        ,  QUANTITY  , PARTION   ,  EXPDATE   ,  MOD_ID    
            ) values ( id1, ware_id2 , rem1.articul , to_spis , rem1.uid_pallet ,
             rem1.expiry_date , rem1.mod_id  ) ;
        --select  RABAEV.TMP_COMPL_REMAINS_HISTORY_TRG.NEXTVAL  from dual;
             
      end if;

end loop;

-- ========= ЗАКОНЧИЛИ ФОРМИРОВАТЬ КУРСОР РЕЗЕРВОВ ЗА МИНУСОМ ОСТАТКОВ ========================



  tmp_art:='';
  count_in_reserv:=0;
  to_spis:=0;
 -- по всем строкам заказов в состоянии =1 .
 --    для каждой строки если строка обеспечена товаром , ставим строку резерва, 
 --    переводим статус строки заказа во 2 
 for r in rws loop
   

 
     to_spis:=0;
     tmp_art:= r.articul;
     count_needed:=r.quantity;
     count_putted:=0;
     for rm in remains2 loop
       if  count_needed>0 then -- Если заказ еще не обеспечен товаром
          to_spis:=min2( rm.quantity , count_needed  ); 
          
          count_putted:=count_putted+to_spis;       
          -- Устанавливаем плановую модификацию на строку заказа
          
          update rrl_order_rows rrrs set rrrs.mod_id = rm.mod_id , rrrs.QUANTITY_PLANNED= count_putted,
           rrrs.CONDITION=2 , PARTIONPLANNED=rm.partion   where rrrs.id = r.id    ; 
          
          -- Делаем запись резерва на данную строку остатка 
          insert into RRL_COMPL_RESERVE (
            ARTICUL     ,  PARTIONID   ,  QTY          ,  ORDERID      ,  ORDERROWID   ,
            CONDITION    ,  EXPDATE      ,  MOD_ID       ,  WARE_ID ) values
            ( rm.articul , rm.partion , rm.quantity , r.order_id , 
            r.id , 0, rm.expdate , rm.mod_id , ware_id6);
            -- Удаляем строку с остатком, пополняем обеспечение заказа до to_spis
          --if to_spis <= rm.quantity then -- Если остатка текущей партии не достаточно для потребности
          --     delete from TMP_COMPL_REMAINS rms5 where rms5.Id = rm.id ; 
          --else
             update TMP_COMPL_REMAINS rms5 set QUANTITY = QUANTITY-to_spis  where rms5.Id = rm.id ; 
             delete from TMP_COMPL_REMAINS rms5 where rms5.Id = rm.id and QUANTITY<=0 ;
         -- end if;

          count_needed:=count_needed-to_spis; 

        else
             null;  -- 
        end if;
        
     end loop;
     --CLOSE remains2;
     
     
 end loop;
ret1:= orders_check(  ware_id6  );
 commit;
 return 1;
end;
 
-- Данный заказы в состоянии 1 или 0  
-- Если строка в состоянии 0 - переводим ее в 1 состояние
function orders_start_plan(  ord_id1 int )  return int is
ord_state int;
begin
  select  ordd.cond  into ord_state  from rrl_orders ordd where ordd.id=ord_id1;
  if(ord_state>1) then 
      return 2;
  end if;
  update rrl_orders set cond=1 where id= ord_id1 and cond=0;
  update rrl_order_rows rs set condition=1 where rs.order_id= ord_id1 and condition=0 ;
  return 1;  
exception
       when no_data_found then return -1;
end;

-- Функция вычеркивает не распределенные строки заказов,
-- то есть переводит их в 4 статус
function orders_create_vycherk(  ord_id1 int )  return int is
ord_state int;
begin
  select  ordd.cond  into ord_state  from rrl_orders ordd where ordd.id=ord_id1;
  if(ord_state<>1) then 
      return 2;
  end if;
  update rrl_orders set cond=2 where id= ord_id1 and cond=1;
  update rrl_order_rows rs set condition=4 where rs.order_id= ord_id1 and condition=1 ;
  return 2;
  exception
       when no_data_found then return -1;
end;

-- Все заказы в первом статусе, строки которых во 2,3 и 4 статусах переводятся во 2 статус
function orders_check(  ware_id6 int )  return int is
         
   cursor finished_orders is
        select ords.id
        from RRL_ORDER_ROWS rs2 , RRL_ORDERS ords where rs2.order_id =  ords.id and
        rs2.ware_id = ware_id6 and ords.cond < 2
          group by ords.id having min(rs2.condition )>1;
begin
for fo in finished_orders loop
    update RRL_ORDERS o set cond=2 where o.id=fo.id;
end loop;
return 1;
end;


-- Функция делит Заказ на паллеты в случае настройки склада flag_DEV_ORDERS_BY_PALL_AUTO=1
-- В ином случае обновляем вычерки и модификацию в существующем паллете
function divide_order_bypal2( ord_id1 int ,  user_id11 varchar2 ) return int is
ware_id6 int;
flag_DEV_ORDERS_BY_PALL_AUTO int;
cond1 int;
row_id1 int;
ret2 int;
order_name varchar2(255);
puid1 varchar(255);
flag_trunc_order_by_remain int;
Partion varchar(255);
cursor order_rows is
       select rs.articul , rs.mod_id , rs.quantity_planned , rs.partionplanned  
              from rrl_order_rows rs where rs.order_id =ord_id1;
              
 cursor pallets is
 select plts.pallet_uid  puid1 , plts.pallet_uid  , plts.st_number 
  from rrl_sborka_pallets plts where plts.st_number=order_name;
       
              
begin

    select ords.ware_id , ords.cond , ords.ord_number into ware_id6 , cond1 , order_name 
    from RRL_ORDERS ords where ords.id= ord_id1;
    if(cond1<>2) then 
        return 0;
    end if;
    select DEV_ORDERS_BY_PALL_AUTO , plan_trunc_order_by_remain into flag_DEV_ORDERS_BY_PALL_AUTO , flag_trunc_order_by_remain
     from rrl_wares where id=ware_id6;
     
    if( flag_DEV_ORDERS_BY_PALL_AUTO=0 )then -- Если не делим паллеты автоматом, 
    -- тогда обновляем вычерки и модификацию
       --select plts.pallet_uid into puid1 from rrl_sborka_pallets plts where plts.st_number=order_name;
       for pal3 in pallets loop
       puid1 := pal3.pallet_uid;
       
       update rrl_sborka_pallets set rrl_sborka_pallets.original_st_number   = pal3.st_number ,
              rrl_sborka_pallets.original_order_number= pal3.st_number 
              where  rrl_sborka_pallets.pallet_uid=pal3.puid1;
       
        
           for orow in order_rows loop
            
               if( orow.quantity_planned>0 ) then --- ************ ОБНОВЛЕНИЕ *************** ---
               -- Определяем вес паллета 
                   Partion:=orow.partionplanned;
                   begin
                       select rs2.id  into row_id1 from rrl_sborka_pallet_rows rs2 where rs2.pallet_uid=puid1 and rs2.articul=orow.articul;   
                       ret2:=CHANGE_PALLET_ROW_QUANTITY( row_id1  , orow.quantity_planned , Partion );

                   exception
                     when no_data_found then null;
                   end;
               end if;
               
               if( orow.quantity_planned=0 ) then
                   begin
                      --- Вернуться сюда!!!  Вычерки не делаютсся.
                      --  null;
                    -- Смотрим настройку склада
                    if flag_trunc_order_by_remain=1 then 
                       update rrl_sborka_pallet_rows  set quantity=0, 
                              ORDER_WEIGHT=0,  PACK_COUNT=0 
                              where pallet_uid=puid1 and articul=orow.articul;   
                    end if;
                       
                   exception
                     when no_data_found then null;
                   end;
                   
               end if;
               
           end loop;
       
       end loop;
       
    else 
        null;
    end if;
    
     update  RRL_ORDERS set cond=4 where id= ord_id1;
    
return 4;
 exception
       when no_data_found then return -1;
       when others then return -2;
end;


-- Количество коробок для строки паллеты
function RRL_COUNT_KOR3(  row_id int) return int is
  articul1 varchar2(255);
  quantity1 number;
  CURRENT_MOD_ID1 int;
  ret1 number;
begin
  select RS.ARTICUL , RS.CURRENT_MOD_ID , RS.QUANTITY into articul1, CURRENT_MOD_ID1 , quantity1   
           from RABAEV.RRL_SBORKA_PALLET_ROWS RS where ID = row_id;       
  if(not CURRENT_MOD_ID1 is null) then
      ret1:= RRL_COUNT_KOR2( articul1 , quantity1 , CURRENT_MOD_ID1);
  else
     ret1:= RRL_COUNT_KOR( articul1 , quantity1  );
  end if;  
return ret1;
exception
         when no_data_found then 
           return 0;
end;

-- Количество коробок для строки паллеты весового товара 
function RRL_COUNT_KOR4(  row_id int) return varchar2 is
  articul1 varchar2(255);
  quantity1 number;
  CURRENT_MOD_ID1 int;
  ret1 number;
  type_w1 int;
   PACK_COUNT2 number; 
begin
  select RS.ARTICUL , RS.CURRENT_MOD_ID , RS.QUANTITY ,  RS.PACK_COUNT  
  into articul1, CURRENT_MOD_ID1 , quantity1 ,  PACK_COUNT2 
           from RABAEV.RRL_SBORKA_PALLET_ROWS RS where ID = row_id;
           
  select fff.type_w into type_w1  from rrl_articuls fff where acticul = articul1 ;  
  
           
  if(type_w1 = 6 or type_w1=8 ) and  (articul1<>'Т0000012233') then
             return '';
  end if;
  
    
  if(not PACK_COUNT2 is null) then
         if(not PACK_COUNT2=0 ) then
                return PACK_COUNT2;
         end if;
  end if;
  
  
  
  if(not CURRENT_MOD_ID1 is null) then
      ret1:= RRL_COUNT_KOR2( articul1 , quantity1 , CURRENT_MOD_ID1);
  else
     ret1:= RRL_COUNT_KOR( articul1 , quantity1  );
  end if;  
  if(ret1=0) then
    return '';
  end if;
return to_char(ret1);
exception
         when no_data_found then 
           return '';
end;


-- Функция принудительно меняет количество к сборке в строке паллета. 
-- при этом меняется плановый вес брутто, количество коробок, 
function CHANGE_PALLET_ROW_QUANTITY( row_id1 int , q number , Partion varchar2 ) return int is
     unit_count1 number;
     mod_id1 int;
    weight_brutto1 number;
    weight_tn1 number;
    defect_perc1 number;
    count_kor1 number;
    sborka_puid varchar2(50);
    art1 varchar2(255);
    type_w1 int;
    ret1 varchar2(255);
    
    PACK_COUNT2 number;
    ORDER_WEIGHT2 number;
    koef number;
begin

PACK_COUNT2:=0;
ORDER_WEIGHT2:=0;
    select rrl_sborka_pallet_rows.pallet_uid into sborka_puid
           from rrl_sborka_pallet_rows where id= row_id1;

    select pl.unit_count , pl.mod_id , pl.weight_brutto , pl.weight_tn , pl.defect_perc , pl.count_kor ,
    pl.articul 
    into unit_count1 , mod_id1,  weight_brutto1, weight_tn1, defect_perc1 , count_kor1 , art1 
    from rrl_pallets pl where pl.uid_pallet= Partion;
       
    select type_w into type_w1 from rrl_articuls where acticul=art1;
    begin
      koef:=q/unit_count1;
      PACK_COUNT2:=round((count_kor1*q)/unit_count1, 0);
      ORDER_WEIGHT2:=round(((weight_brutto1-weight_tn1)*q)/unit_count1, 1);
      exception
    when no_data_found then null;
    end;
    
    if( type_w1 in(0,1,2,3,4,5,6,7,8) ) then
    
    ret1:=RABAEV.RRL_UPDATE_PALLET_ROW3( 
    row_id1 ,
    art1 ,
    sborka_puid , 
    PACK_COUNT2  , -- Количество упаковок
    q, -- Штуки
    mod_id1 , -- Модификация 
    ORDER_WEIGHT2  , -- Вес N штук.
    Partion ,-- Данные паллета прихода.
    'VYCHERK'
 );
    end if;
    
--       update rrl_sborka_pallet_rows rs2 
--          set rs2.current_mod_id = orow.mod_id , rs2.quantity=orow.quantity_planned
--          where rs2.pallet_uid=puid1 and rs2.articul=orow.articul;  
                   
     return 1;
exception
     when no_data_found then return 0;
  
end;


function filter_show_weight_brutto( weight1 number ,  articul1 varchar2  ) return varchar2 is
    type_w1 int;
begin
    if(weight1=0) then 
    return '--';
    end if;  
    select type_w into type_w1 from rrl_articuls where acticul = articul1 ;--and type_w<>7;
return to_char(weight1);
    exception when no_data_found then return '';  
end;


-- Функция вызывается при прохождении паллета через весовой контроль, либо скан.
function finish_othod_pallet( PALLET_ID1 varchar2   ) return int is
    type_w1 int;  
    cursor sss is
    select pals.original_order_number 
    from rrl_sborka_pallet_rows rs , rrl_sborka_pallets pals where
           rs.pallet_uid = pals.pallet_uid and  pals.pallet_uid=PALLET_ID1 
           and ( pals.prooved=0 and pals.prooved_by_scan=0 ) and rs.quantity>0 ;
    ne_sobran int;
    original_order_number1 varchar2(255);
begin
  ne_sobran:=0;
    -- По всем артикулам данного ст, выясняем артикулы полностью собраны и в каком количестве.
    -- если все артикулы заказа собраны или вычеркнуты , переводим заказ в 9 статус.
    -- Иначе 
    select pl.original_order_number into original_order_number1
     from rrl_sborka_pallets pl where pl.pallet_uid=PALLET_ID1 ;
    
    if( original_order_number1 is null  ) then 
        return 0;
    end if;
    
    if( original_order_number1 =''  ) then 
        return 0;
    end if;
    
    for s in sss loop
      ne_sobran:=1;
    end loop;

    if( ne_sobran=0 ) then    
        update rrl_orders o set o.cond=9 where o.ord_number=original_order_number1 ;
        return 1;
    end if;
    
    exception
      when no_data_found then null;
      when others then null;
end;



function print_perc_defect( PALLET_ID1 varchar2 ) return varchar2 is
dp number;
begin
  if( PALLET_ID1 is null ) then
    return '';
  end if;
  
select round( rp.defect_perc , 2)  into dp from RRL_PALLETS rp where rp.uid_pallet=PALLET_ID1;
return concat( to_char(  dp ) , '%' );
       exception when no_data_found then return '';
end;

function print_brutto_defect( PALLET_ID1 varchar2 , weight1 number ) return varchar2 is
dp number;
begin
  if( PALLET_ID1 is null ) then
    return '';
  end if;
  
select  rp.defect_perc   into dp from RRL_PALLETS rp where rp.uid_pallet=PALLET_ID1;
return to_char( round( dp*weight1/100  ,2) );
       exception when no_data_found then return '';
end;




FUNCTION RRL_vlozennost ( ART varchar2    ) return number
-- КОЛИЧЕСТВО КОРОБОК 
IS
ttt number;
ret number;
ret2 number;
BEGIN

     ret:=0;
     select round (   A.COUNT_SHT_IN_KOR ,2 ) into ttt 
     from RRL_ARTICULS A where  A.ACTICUL=ART and A.COUNT_SHT_IN_KOR>0;

return ttt;
exception
when NO_DATA_FOUND then
    return 0;
    when others then 
    return 0;
END  RRL_vlozennost;


------------------------------------
function print_kolbasa_sobr( ei varchar2 , cnt number , cnt_kor number ) return varchar2 is
dp number;
begin
   if(ei='шт') then
   if( cnt_kor=0 ) then 
     return concat( to_char( round( cnt ,2 ))  , ei   ) ;
   end if;
         return concat( to_char( round( cnt/cnt_kor ,2 ) ) , ' кор.'   ) ;               
   end if;
   return concat(  to_char( round( cnt ,2 ) )  , concat( ' ' , ei)   ) ;               
end;


function print_ufa_sobr( ei varchar2 , cnt number , cnt_kor number ) return varchar2 is
dp number;
begin
   /*if(ei='шт') then
   if( cnt_kor=0 ) then 
     return concat( to_char( round( cnt ,2 ))  , ei   ) ;
   end if;
         return concat( to_char( round( cnt/cnt_kor ,2 ) ) , ' кор.'   ) ;               
   end if;
   */
    return concat( to_char( round( cnt/cnt_kor , 2 ) ) , ' кор.'   ) ;       
--   return concat(  to_char( round( cnt ,2 ) )  , concat( ' ' , ei)   ) ;               
end;




function order_vycherk_count( order_id1 int   ) return int is
ret int;
begin   
     select count(id) into ret from rrl_order_rows ors 
     where ors.order_id=order_id1 and ors.condition in (1,4);     
     return ret;     
     exception when no_data_found then return 0;
end;

function order_rows_count( order_id1 int   ) return int is
ret int;
begin   
     select count(id) into ret from rrl_order_rows ors where ors.order_id=order_id1;     
     return ret;     
     exception when no_data_found then return 0;
end;

function reset_2_first_status( order_id1 int   ) return int is
ret int;
cond1 int;
begin   


     select ords.cond into cond1 from rrl_orders ords where id=order_id1;  

--     if( cond1<>1 )then  
--         return 0;       
--     end if;            


     update rrl_order_rows ors set ors.partionplanned=null, ors.mod_id=null , ors.condition=0
            where ors.order_id=order_id1;     
     
     update rrl_orders   set cond=0
            where id=order_id1;     
     
     return 1;     
     exception when no_data_found then return 0;
end;

-- Удаляет все пустые паллеты
FUNCTION RRL_SBORKA_PAL_REMOVE_EMPTY( ST_NUMBER1 varchar2 , USER_ID1 varchar2  )
return int is

cursor curs2 is
    select rs.id , pts.PALLET_UID PALLET_UID
    from rrl_sborka_pallets pts , RRL_SBORKA_PALLET_ROWS rs  
    where
    pts.PALLET_UID=rs.PALLET_UID   and st_number  = ST_NUMBER1  and rs.quantity=0;


cursor curs1 is
    select pts.PALLET_UID PALLET_UID , count( rs.PALLET_UID ) bbb
    from rrl_sborka_pallets pts left join RRL_SBORKA_PALLET_ROWS rs on pts.PALLET_UID=rs.PALLET_UID(+)  
    where st_number  = ST_NUMBER1
    group by pts.PALLET_UID having count( rs.PALLET_UID )=0;

begin

    for c2 in curs2 loop
        delete from RRL_SBORKA_PALLET_ROWS where id=c2.id;
    end loop;


    for c in curs1 loop
        delete from rrl_sborka_pallets where PALLET_UID=c.PALLET_UID;
    end loop;
    return 1;
end;


-- Создает маллет с нужным номером. 
FUNCTION RRL_GIVE_PALLET_UID( ST_NUMBER1 varchar2 , USER_ID1 varchar2 ,  
  PALLET_NUMBER1 int    
 )
RETURN varchar2 IS 
tmpV varchar2(255);
    ret int;
    ADDR1 varchar2(255) ;
    PALLET_UID1     VARCHAR2 (100);
    STATE1    VARCHAR2(100) ;
    STDATE1 Date;
    ware_id1 int;
    NAPR1 varchar2(255);
    PALLET_NUMBER2 int;
     TRANSTASK_ID1 int; 
    id2 int;
BEGIN

ret:=0;

begin
  select pts.pallet_uid , pts.addr , pts.state , pts.STDATE , pts.Napr , pts.ware_id ,  TRANSTASK_ID 
  into PALLET_UID1 , ADDR1, STATE1 , STDATE1 , NAPR1 , 
  ware_id1 ,  TRANSTASK_ID1 
       from rrl_sborka_pallets pts where pts.st_number=st_number1 
       and pts.pallet_number = PALLET_NUMBER1 and rownum = 1 ;
  return PALLET_UID1;     
exception when no_data_found then 
  null  ;
end;

  select pts.pallet_uid , pts.addr , pts.state , pts.STDATE , pts.Napr , pts.ware_id ,  TRANSTASK_ID 
  into PALLET_UID1 , ADDR1, STATE1 , STDATE1 , NAPR1 , 
  ware_id1 ,  TRANSTASK_ID1 
       from rrl_sborka_pallets pts where pts.st_number=st_number1 and rownum = 1 ;

  select (max(PALLET_NUMBER )+1) into  PALLET_NUMBER2  from RRL_SBORKA_PALLETS PP 
       where  PP.ST_NUMBER = ST_NUMBER1 ;

-- PALLET_UID1:= Concat( 'OP_' , Concat( Concat( ST_NUMBER1 , '_'  ) ,  PALLET_NUMBER2  ) );
PALLET_UID1:= Concat( 'OP_' , Concat( Concat( ST_NUMBER1 , '_'  ) ,  PALLET_NUMBER1  ) );

begin   
    select pts.pallet_uid into tmpV 
    from rrl_sborka_pallets pts where pts.pallet_uid=PALLET_UID1 and rownum=1;
exception when no_data_found then 
    id2 := RABAEV.RRL_SBORKA_PALLETS_ADD2 (
        ST_NUMBER1,
        ADDR1 ,
        PALLET_NUMBER1  ,
        PALLET_UID1      ,
        STATE1     ,
        STDATE1  ,
        NAPR1  ,
        USER_ID1  ,
        ware_id1 );
end ;

update rrl_sborka_pallets set  TRANSTASK_ID = TRANSTASK_ID1
  where pallet_uid =PALLET_UID1 ;
RETURN PALLET_UID1;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 'error';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END ;





FUNCTION RRL_COPY_PALLET_ROW3( 
    row_id2 int ,
    count1  number , 
    PALLET_UID_NEW    VARCHAR2  ) RETURN int 
 IS 
 type_w1 int;
 ID1 int;
  PALLET_UID1    VARCHAR2(255) ;
  ARTICUL1       VARCHAR2(255) ;
  SHORTNAME1     VARCHAR2(1255) ;
  SHTRIHKOD1     VARCHAR2(255) ;
  EI1            VARCHAR2(255) ;
  TAREWEIGHT1    NUMBER;
  PATH1          VARCHAR2(1255) ;
  ORDER_WEIGHT1  NUMBER;
  TARESIZE1      NUMBER;
 QUANTITY1       NUMBER;
  SORTFIELD1     INTEGER;
  AUCTION1       VARCHAR2(255);
  DOCID1         VARCHAR2(255) ;
  ORIGINAL_QUANTITY1 number;
   ORIGINAL_ORDER_WEIGHT1 number;
  ware_id1 int ;
  PACK_COUNT1 int;
   PRIHOD_PALLET_UID1        VARCHAR2(250);
   CURRENT_MOD_ID1 int;
  CONDITION1 int;
  EXPIRY_DATE1    DATE;
  
BEGIN
  
if( count1<=0) then 
    return 0;
end if;


      select  PALLET_UID    ,
              ARTICUL       ,
              SHORTNAME     ,
              SHTRIHKOD     ,
              EI            ,
              TAREWEIGHT    ,
              PATH ,
              ORDER_WEIGHT  ,
              TARESIZE      ,
              QUANTITY      ,
              SORTFIELD     ,
              AUCTION       ,
              DOCID         , 
              ware_id ,
              PACK_COUNT , 
              ORIGINAL_QUANTITY ,
              ORIGINAL_ORDER_WEIGHT , 
              CURRENT_MOD_ID ,
              PRIHOD_PALLET_UID , CONDITION , EXPIRY_DATE
               into 
              PALLET_UID1    ,
              ARTICUL1       ,
              SHORTNAME1     ,
              SHTRIHKOD1     ,
              EI1            ,
              TAREWEIGHT1    ,
              PATH1 ,
              ORDER_WEIGHT1  ,
              TARESIZE1      ,
              QUANTITY1      ,
              SORTFIELD1     ,
              AUCTION1       ,
              DOCID1         , 
              ware_id1 ,
              PACK_COUNT1 , 
              ORIGINAL_QUANTITY1 ,
              ORIGINAL_ORDER_WEIGHT1    , 
              CURRENT_MOD_ID1 , 
              PRIHOD_PALLET_UID1  ,
              CONDITION1 , EXPIRY_DATE1
              from RABAEV.RRL_SBORKA_PALLET_ROWS where ID= row_id2 ;

              SELECT RRL_SBORKA_PALLET_ROWS_SQ.Nextval INTO ID1 FROM DUAL;

            INSERT INTO RABAEV.RRL_SBORKA_PALLET_ROWS
            (
            ID , 
              PALLET_UID    ,
              ARTICUL       ,
              SHORTNAME     ,
              SHTRIHKOD     ,
              EI            ,
              TAREWEIGHT    ,
              PATH ,
              ORDER_WEIGHT  ,
              TARESIZE      ,
              QUANTITY      ,
              SORTFIELD     ,
              AUCTION       ,
              DOCID         , 
              ware_id ,
              PACK_COUNT , 
              ORIGINAL_QUANTITY ,
              ORIGINAL_ORDER_WEIGHT,
              
              CURRENT_MOD_ID       ,
              PRIHOD_PALLET_UID     ,
              EXPIRY_DATE   ,
              CONDITION         
              
            )  values (
            ID1 ,
              PALLET_UID_NEW    ,
              ARTICUL1       ,
              SHORTNAME1     ,
              SHTRIHKOD1     ,
              EI1            ,
              TAREWEIGHT1    ,
              PATH1          ,
              (count1* ORIGINAL_ORDER_WEIGHT1/ORIGINAL_QUANTITY1 )  ,
              TARESIZE1      ,
              count1      ,
              SORTFIELD1     ,
              AUCTION1       ,
              DOCID1         , 
              ware_id1 ,
              PACK_COUNT1 ,
              ORIGINAL_QUANTITY1,
              ORIGINAL_ORDER_WEIGHT1 , 
              
              CURRENT_MOD_ID1       ,
              PRIHOD_PALLET_UID1     ,
              EXPIRY_DATE1   ,
              CONDITION1  
              
            );

begin
   select type_w into type_w1 from rrl_articuls where acticul=ARTICUL1;
exception 
  when no_data_found then null;
end;
 
   RETURN ID1;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END  ;



-- Возвращает время комплектации паллета.
-- Если время комплектации пусто, то возвращает время создания паллет + 1 день
function pallet_compl_date( pall_uid varchar2 ) return Date is
     check_time Date;
     create_time Date;
begin
    select  pts.create_date , pts.checking_time  into create_time , check_time
            from rrl_sborka_pallets pts where pts.pallet_uid = pall_uid ;
    
    if(check_time is null) then return create_time;
    end if;
    return check_time;
    
exception
  when no_data_found then return null;
end;


-- Размазывает паллет по заявке.
-- находим паллеты, 
function pallet_flatten( pall_uid varchar2 ) return int is
   pvolume number;
   pmass number;  
   st_number1 varchar2(255);
   norm_pvolume number;
   norm_pmass number;  
   host_pal varchar2(255);
begin
 norm_pvolume:= 2;
 norm_pmass:=1200;
    pvolume:=RRL_PAL_VOLUME( pall_uid );
    pmass:=RRL_PAL_WEIGHT( pall_uid );
    select pts.st_number into st_number1 from rrl_sborka_pallets pts 
           where pts.pallet_uid=pall_uid;
           
select pallet_uid into host_pal from (
select pts.pallet_uid from rrl_sborka_pallets pts 
       where pts.st_number=st_number1 and pts.pallet_uid<>pall_uid and
       RRL_PAL_VOLUME( pts.pallet_uid ) < norm_pvolume - pvolume
       and RRL_PAL_WEIGHT(pts.pallet_uid) < norm_pmass - pmass
       order by RRL_PAL_VOLUME( pts.pallet_uid ) desc ,
       RRL_PAL_WEIGHT(pts.pallet_uid) desc  ) where rownum<=1;
    
exception
  when no_data_found then return -1;
end;


-- Предсказывает колдичество паллет. просто делит количество на вложенность.

function perdiction_count_pall( st_number1 varchar2 ) return number is      
  cpall number;     
  begin
       cpall:=0 ;
       select  ( sum( max2( rs.quantity ,  rs.ORIGINAL_QUANTITY ) / art.norma_ukladki  )  )  into cpall
       from rrl_sborka_pallets pts , rrl_sborka_pallet_rows rs , rrl_articuls art
       where pts.pallet_uid = rs.pallet_uid and art.acticul = rs.articul
        and ( pts.st_number = st_number1 or   pts.pallet_uid = st_number1 ) ;
       
       if cpall<1 then
         return 1;
        end if;
         
       
  return round(cpall,0);
         
  exception  
         when no_data_found then return 0;
         when others then return 0;
  end;
  

-- Возвращает время начала смены.
function time_shift_start( time1 date ) return Date  is
  curr_time date;
  tmp varchar2(255);
  h int;
begin
         
  curr_time := time1;       
  h := to_number( to_char( curr_time , 'HH24'  ) ) ;
  if( h<=8 and h>=0 ) then
      curr_time := curr_time -  1 ;
      curr_time:= to_date( concat( to_char( curr_time , 'dd.mm.YYYY'  ) , ' 20:00:00'  ) , 'dd.mm.YYYY HH24:MI:SS' );
      return curr_time;
  end if;
   
  if( h>=8 and h<=20 ) then
      tmp:=concat( to_char( curr_time , 'dd.mm.YYYY'  ) , ' 08:00:00'  );
      curr_time:= to_date( tmp , 'dd.mm.YYYY HH24:MI:SS' );
      return curr_time;
  end if;
      
   if h>=20 then 
      curr_time:= to_date( concat( to_char( curr_time , 'dd.mm.YYYY'  ) , ' 20:00:00'  ) , 'dd.mm.YYYY HH24:MI:SS' );
      return curr_time;
   end if;      
  return curr_time;
end;


function time_shift_end( time1 date ) return Date  is
  curr_time date;
  tmp varchar2(255);
  h int;
begin
         
  curr_time := time1;       
  h := to_number( to_char( curr_time , 'HH24'  ) ) ;
  if( h<=8 and h>=0 ) then
      --
      curr_time:= to_date( concat( to_char( curr_time , 'dd.mm.YYYY'  ) , ' 08:00:00'  ) , 'dd.mm.YYYY HH24:MI:SS' );
      return curr_time;
  end if;
   
  if( h>=8 and h<20 ) then
      tmp:=concat( to_char( curr_time , 'dd.mm.YYYY'  ) , ' 20:00:00'  );
      curr_time:= to_date( tmp , 'dd.mm.YYYY HH24:MI:SS' );
      return curr_time;
  end if;
      
   if h>=20 then
      curr_time := curr_time + 1 ;
      curr_time:= to_date( concat( to_char( curr_time , 'dd.mm.YYYY'  ) , ' 08:00:00'  ) , 'dd.mm.YYYY HH24:MI:SS' );
      return curr_time;
   end if;      
  return curr_time;
end;

function can_edit_sb_pallet( pallet_uid1 varchar2 ) return int
cond1 int;
begin
  
    select condition into cond1 
           from rrl_sborka_pallets pts where pts.pallet_uid;

    if( cond1 =2 ) then 
        return 0;
    end if;

return 0;
exception 
         when no_data_found then return 0;
end;


begin
  -- Initialization
  null;
end compl;
/
