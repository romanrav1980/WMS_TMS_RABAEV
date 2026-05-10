create trigger RRL_t_event_update_remain
  AFTER INSERT
  on RRL_events
  for each row
declare
  vRemain number;
  procedure UpRemain
    -- ѕроцедура увеличивает остаток в €чейке :new.cell_to на :new.count_event
  is

  begin
    -- смотрим, что лежит в новой €чейке
    -- провер€ем только наличие по текущей полете... ’орошо было бы проверить эту €чейку на
    -- наличие в ней чего-нить от других полет и сделать какие-нибудь выводы ...
    select sum(remain) into vRemain
    from RRL_remains
    where cell = :new.cell_to
    and uid_poleta = :new.uid_poleta;

    if vRemain is null then
      -- в €чейке таких полет не обнаружено. добавл€ем запись
     insert into RRL_remains (uid_poleta, cell, remain) 
     values (:new.uid_poleta, :new.cell_to, :new.count_event);
    else
      -- есть какой-то остаток
      update RRL_remains
      set remain = remain+:new.count_event
      where cell = :new.cell_to
      and uid_poleta = :new.uid_poleta;
    end if;   
    
  end;


  
  
  
  
  procedure DownRemain
    -- ѕроцедура уменьшает остаток в €чейке :new.cell_from на :new.count_event
  is
  begin
    select sum(remain) into vRemain -- на вс€кий случай сделали сумму
    from RRL_remains
    where cell = :new.cell_from
    and uid_poleta = :new.uid_poleta;

    if vRemain is null then 
      -- странно, однако, в €чейке не та полета, или €чейка совсем пуста€...
      -- запишем отрицательный остаток 
      insert into RRL_remains(uid_poleta, cell, remain) 
      values (:new.uid_poleta :new.cell_from, -:new.count_event);
    elsif vRemain = :new.count_event then
      -- из €чейки все будет выбрано подчистую, она останетс€ пуста€.
      -- поэтому наверно остаток можно удалить
      delete from RRL_remains
      where cell = :new.cell_from
      and uid_poleta = :new.uid_poleta;
    else
      -- остаток какой-то не нулевой остаетс€ (может быть и отрицательный)
      -- проапдейтим остаток
      update RRL_remains
      set remain = remain-:new.count_event
      where cell = :new.cell_from
      and uid_poleta = :new.uid_poleta;
    end if;   
  end;  

begin

  if :new.type_event = 1 then  
    -- если событие это приемка
    -- добавл€ем запись в таблицу остатков
    UpRemain;
  elsif :new.type_event = 2 then  
    -- если событие это перемещение
    -- мен€ем данные в таблице остатков
    DownRemain;
    UpRemain;
  elsif :new.type_event = 3 then  
    -- если событие это отбор
    DownRemain;
  end if;
end;

