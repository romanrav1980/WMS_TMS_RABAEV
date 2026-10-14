create or replace trigger RRL_PHYSICAL_VERSION_GUARD before insert or update of PHYSICAL_VERSION on RRL_REMAINS for each row
declare expected_no number;begin
 RRL_STOCK_WRITE_GUARD.require_effect('STOCK',:new.UID_POLETA,:new.CELL);
 if inserting then expected_no:=case when :new.REMAIN!=0 then 1 else 0 end;
 else expected_no:=:old.PHYSICAL_VERSION+case when :new.REMAIN!=:old.REMAIN then 1 else 0 end;end if;
 if :new.PHYSICAL_VERSION is null or :new.PHYSICAL_VERSION!=expected_no then raise_application_error(-20863,'PHYSICAL_STOCK_VERSION_CONFLICT');end if;
end;
/
