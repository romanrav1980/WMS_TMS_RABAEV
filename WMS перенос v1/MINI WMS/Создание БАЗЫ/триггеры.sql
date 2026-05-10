DROP TRIGGER RABAEV.RRL_PRIHOD_NAKLAD_TRG;

CREATE OR REPLACE TRIGGER RABAEV.RRL_PRIHOD_NAKLAD_TRG
BEFORE INSERT 
ON RABAEV.RRL_PRIHOD_NAKLAD FOR EACH ROW
DECLARE
BEGIN


if :New.ID is null then
  SELECT RRL_PRIH_ORD_ID.NEXTVAL
    INTO :New.ID
    FROM dual;
    end if;
    



END;
/

ALTER TRIGGER RABAEV.RRL_PRIHOD_NAKLAD_TRG DISABLE;


DROP TRIGGER RABAEV.SFERA_EAN_TRG;

CREATE OR REPLACE TRIGGER RABAEV.SFERA_EAN_TRG
BEFORE INSERT 
ON RABAEV.SFERA_EAN FOR EACH ROW
DECLARE
BEGIN


if :New.”»ƒ is null then
  SELECT SFERA_EAN_ID.NEXTVAL
    INTO :New.”»ƒ
    FROM dual;
    end if;
    



END;
/


DROP TRIGGER RABAEV.RRL_T_EVENT_UPDATE_REMAIN;

CREATE OR REPLACE TRIGGER RABAEV.RRL_t_event_update_remain
  AFTER INSERT
  ON RABAEV.RRL_EVENTS   for each row
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
     insert into RRL_remains (uid_poleta, cell, remain , othod_nakl_id , TIME_OF_LAST_UPDATE ) 
     values (:new.uid_poleta, :new.cell_to, :new.count_event , :new.othod_nakl_id , SYSTIMESTAMP );
    else
      -- есть какой-то остаток
      update RRL_remains
      set remain = remain+:new.count_event , othod_nakl_id =  :new.othod_nakl_id , TIME_OF_LAST_UPDATE = SYSTIMESTAMP 
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
      insert into RRL_remains(uid_poleta, cell, remain ,  TIME_OF_LAST_UPDATE  ) 
      values (:new.uid_poleta , :new.cell_from, -:new.count_event , SYSTIMESTAMP );
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
      set remain = remain-:new.count_event , TIME_OF_LAST_UPDATE=SYSTIMESTAMP
      where cell = :new.cell_from
      and uid_poleta = :new.uid_poleta;
    end if;   
  end;  

begin

    if(:new.count_event<>0) then
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
    end if;
  
end;
/


DROP TRIGGER RABAEV.ORDER_MOV_HIST_TRG;

CREATE OR REPLACE TRIGGER RABAEV.ORDER_MOV_HIST_TRG
BEFORE INSERT 
ON RABAEV.ORDER_MOV_HIST FOR EACH ROW
DECLARE
BEGIN

if :New.ID is null then

  SELECT RABAEV.ORDER_MOV_HIST_ID.NEXTVAL
    INTO :New.ID 
        FROM dual;
        
end if;
    
 

END;
/


DROP TRIGGER RABAEV.RRL_TR_VEHICLE_TRG;

CREATE OR REPLACE TRIGGER RABAEV.RRL_TR_VEHICLE_TRG
BEFORE INSERT 
ON RABAEV.RRL_TR_VEHICLE FOR EACH ROW
DECLARE
BEGIN

    if :New.ID is null then

      SELECT  RABAEV.RRL_TR_VEHICLE_SQ.NEXTVAL 
        INTO   :New.ID 
            FROM dual;           
    end if;
        

END;
/


DROP TRIGGER RABAEV.RRL_SBORKA_PALLETS_TRG;

CREATE OR REPLACE TRIGGER RABAEV.RRL_SBORKA_PALLETS_TRG
BEFORE INSERT 
ON RABAEV.RRL_SBORKA_PALLETS FOR EACH ROW
DECLARE
BEGIN


if :New.ID is null then
  SELECT RRL_SBORKA_PALLETS_SQ.NEXTVAL
    INTO :New.ID
    FROM dual;
    end if;
 

  SELECT SYSTIMESTAMP
    INTO :New.CREATE_DATE
    FROM dual;


END;
/


DROP TRIGGER RABAEV.RRL_SBORKA_PALLETS_HISTORY_TRG;

CREATE OR REPLACE TRIGGER RABAEV.RRL_SBORKA_PALLETS_HISTORY_TRG
BEFORE INSERT 
ON RABAEV.RRL_SBORKA_PALLETS_HISTORY FOR EACH ROW
DECLARE
BEGIN

if :New.ID is null then

  SELECT  RABAEV.RRL_SBORKA_PALLETS_HISTSQ.NEXTVAL 
    INTO   :New.ID 
        FROM dual;
        
        
    SELECT  SYSDATE 
    INTO   :New.TIME1 
        FROM dual;      
        
end if;
    
 

END;
/


DROP TRIGGER RABAEV.RRL_TR_VODITEL_TRG;

CREATE OR REPLACE TRIGGER RABAEV.RRL_TR_VODITEL_TRG
BEFORE INSERT 
ON RABAEV.RRL_TR_VODITEL FOR EACH ROW
DECLARE
BEGIN

    if :New.ID is null then

      SELECT  RABAEV.RRL_TR_VODITEL_SQ.NEXTVAL 
        INTO   :New.ID 
            FROM dual;           
    end if;
        

END;
/


