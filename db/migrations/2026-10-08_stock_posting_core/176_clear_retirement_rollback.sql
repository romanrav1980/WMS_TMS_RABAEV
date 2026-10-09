declare n number;begin select count(*) into n from RRL_STOCK_OPERATION;if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_CODE_ROLLBACK');end if;end;
/
create or replace FUNCTION        RRL_CLEAR_OTBOR_CELL(
    CELL1 varchar2 ,
    user_id1 varchar2
)
 RETURN varchar2 IS

tmpVar varchar2(250);
iii int;
otbor1 int;
first1 int;
new_event_uid int;
cursor rests is 
select UID_POLETA , REMAIN from(
select rm.UID_POLETA , rm.REMAIN from rrl_remains rm , rrl_pallets pp where rm.UID_POLETA=pp.UID_PALLET and rm.CELL=CELL1 order by pp.EXPIRY_DATE desc
)  ;

BEGIN

begin
first1:=1;
select otbor into otbor1 from rrl_cells where  cell=CELL1;
    exception when no_data_found  then return 'Такой ячейки нет';
end;

if( otbor1<>1  ) then 
    return 'Ячейка не является ячейкой отбора';
end if;

-- Для всех паллет из ячейки отбора , кроме паллета с самым большим сроком годности, спысываем остаток.
for rest in rests loop
DBMS_OUTPUT.put_line(  'flag1' );
    if( first1<>1 ) then
    
     SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_uid  FROM dual;
     
        insert into rrl_events ( date_event ,  id_event ,  CELL_FROM   ,
          CELL_TO     ,
          COUNT_EVENT  ,
          TYPE_EVENT   ,
          UID_POLETA   ,
          USER_ID   ) values ( SYSTIMESTAMP , new_event_uid ,  cell1 , 'none' , rest.REMAIN , 3 , rest.UID_POLETA , user_id1 );
DBMS_OUTPUT.put_line(  'flag2' );

    end if;
    first1:=0;
DBMS_OUTPUT.put_line(  'flag3' );

end loop;



    
RETURN 'ok';

exception when no_data_found then return 'нет данных';
--when others then return 'ошибка2';

END  RRL_CLEAR_OTBOR_CELL;
/

@@014b_recompile.sql
