create or replace package compl is

  -- Author  : RRABAEV
  -- Created : 29.05.2011 15:39:59
  -- Purpose : Комплектация и сборка товара, деление на паллеты
  


  -- Public function and procedure declarations
  function update_seq( articul1 varchar2 , ware_id1 int , SQ1 int, SQGROUP int ) return int;
  function show_sq( articul1  varchar2 , ware_id1 int ) return int ;
  function show_sq_gr( articul1 varchar2 , ware_id1  int ) return int ;
  
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

-- Порядок сборки для артикула
function show_sq( articul1 varchar2 , ware_id1  int ) return int is
  ret1 int;
begin

    select SQ.SEQ into ret1 from RRL_COMPL_SEQ SQ where articul=articul1 and ware_id=ware_id1;
    return ret1;
    exception
      when no_data_found then return 101;
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


begin
  -- Initialization
  null;
end compl;
/
