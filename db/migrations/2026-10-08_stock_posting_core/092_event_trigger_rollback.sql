declare n number;begin select count(*) into n from RRL_STOCK_OPERATION;if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_TRIGGER_ROLLBACK');end if;end;
/
create or replace TRIGGER RABAEV."BIN$UX1xZvUbS6/gYw8CAAo/Yg==$0" AFTER INSERT
  ON "RABAEV"."RRL_EVENTS"   for each row
declare
  vRemain number;
  procedure UpRemain
  is

  begin
    select sum(remain) into vRemain
    from RRL_remains
    where cell = :new.cell_to
    and uid_poleta = :new.uid_poleta;

    if vRemain is null then
     insert into RRL_remains (uid_poleta, cell, remain , othod_nakl_id , TIME_OF_LAST_UPDATE )
     values (:new.uid_poleta, :new.cell_to, :new.count_event , :new.othod_nakl_id , SYSTIMESTAMP );
    else
      update RRL_remains
      set remain = remain+:new.count_event , othod_nakl_id =  :new.othod_nakl_id , TIME_OF_LAST_UPDATE = SYSTIMESTAMP
      where cell = :new.cell_to
      and uid_poleta = :new.uid_poleta;
    end if;

  end;






  procedure DownRemain
  is
  begin
    select sum(remain) into vRemain
    from RRL_remains
    where cell = :new.cell_from
    and uid_poleta = :new.uid_poleta;

    if vRemain is null then
      insert into RRL_remains(uid_poleta, cell, remain ,  TIME_OF_LAST_UPDATE  )
      values (:new.uid_poleta , :new.cell_from, -:new.count_event , SYSTIMESTAMP );
    elsif vRemain = :new.count_event then
      delete from RRL_remains
      where cell = :new.cell_from
      and uid_poleta = :new.uid_poleta;
    else
      update RRL_remains
      set remain = remain-:new.count_event , TIME_OF_LAST_UPDATE=SYSTIMESTAMP
      where cell = :new.cell_from
      and uid_poleta = :new.uid_poleta;
    end if;
  end;

begin

    if(:new.count_event<>0) then
      if :new.type_event = 1 then
        UpRemain;
      elsif :new.type_event = 2 then
        DownRemain;
        UpRemain;
      elsif :new.type_event = 3 then
        DownRemain;
      end if;
    end if;

end;
/
