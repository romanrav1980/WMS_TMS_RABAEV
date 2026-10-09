declare n number;begin select count(*) into n from RRL_STOCK_OPERATION;if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_CODE_ROLLBACK');end if;end;
/
create or replace FUNCTION        RRL_REVIZION_CELL

(
    CELL1 varchar2 ,
    count1 number ,
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
 --      
 -- возврат ок.    
 
is

cursor rema is select rm.REMAIN , rm.UID_POLETA from rrl_remains rm  where rm.CELL=CELL1 and   rm.REMAIN>0 
order by  rm.TIME_OF_LAST_UPDATE desc;

tmp varchar2(255);
to_spis number;
ostatok number;
begin
ostatok:=count1;

for  rr in rema  loop

    if(ostatok>=rr.REMAIN) then
    -- все ок.  
        null;

    else -- Если остаток спиания меньше остатка в ячейке, то  данная партия в количестве [rr.REMAIN-ostatok] 
         -- списывается в недостачу. если ostatok<0 , то списывается вся партия . 

        if(rr.REMAIN<ostatok) then
            to_spis:=rr.REMAIN;
        else
            to_spis:=rr.REMAIN-ostatok ;
        end if;

        tmp := RABAEV.RRL_INTERNAL_MOVE2(
        rr.UID_POLETA , 
        'INVENT' ,
        to_spis ,
        user_id1 );


    end if;

ostatok:=ostatok- rr.REMAIN;
end loop;

-- если ostatok > 0  , то в ячейке не хватает  партий, их надо найти или спросить.
-- Если количество  превышает, указанное по учету, на величину менее 100 штук то  , 
 --     Списать с ячейки претензий с последней партией , находящейся  в ячейке отбора
-- если ostatok < 0 , то в ячейке зафиксирована недостача в количестве ostatok.  возвращаем ок.

if( ostatok > 0  ) then 
null;
-- Вываливаемся с ошибкой, либо берем остатки из ячейки недостач - последние упавшие. 
    return 'neok';
else 
 -- Порождаем сообщение о недостаче. 
    return 'ok';
end if;


return 'ok';

exception 
when no_data_found then  return 'neok';
when others then raise;


END RRL_REVIZION_CELL;
/
