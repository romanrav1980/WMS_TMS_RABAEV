create or replace trigger RRL_FORECAST_LOAD_GUARD before insert or update or delete on RRL_FORECAST_LOAD for each row
begin
 if not inserting or RRL_FORECAST_PROJECTOR.load_write_allowed(:new.LOAD_OPERATION_ID)!=1 then raise_application_error(-20863,'FORECAST_IMMUTABLE_NATIVE_SOURCE');end if;
end;
/
create or replace trigger RRL_FORECAST_LEAF_GUARD before insert or update or delete on RRL_FORECAST_LEAF for each row
begin
 if not inserting or RRL_FORECAST_PROJECTOR.load_write_allowed(:new.LOAD_OPERATION_ID)!=1 then raise_application_error(-20863,'FORECAST_IMMUTABLE_NATIVE_LEAF');end if;
end;
/
create or replace trigger RRL_FORECAST_ORIGIN_GUARD before insert or update or delete on RRL_FORECAST_CASE_ORIGIN for each row
begin
 if not inserting or RRL_FORECAST_PROJECTOR.load_write_allowed(:new.FIRST_LOAD_OPERATION)!=1 then raise_application_error(-20863,'FORECAST_IMMUTABLE_CASE_ORIGIN');end if;
end;
/
create or replace trigger RRL_FORECAST_DAY_GUARD before insert or update or delete on RRL_FORECAST_DAY for each row
begin
 if deleting then raise_application_error(-20863,'FORECAST_DAILY_PROJECTION_ONLY');end if;
 if RRL_FORECAST_PROJECTOR.day_write_allowed(:new.WARE_ID,:new.DAY_UTC)!=1 or RRL_FORECAST_PROJECTOR.load_write_allowed(:new.LAST_LOAD_OPERATION)!=1 then raise_application_error(-20863,'FORECAST_DAILY_PROJECTION_ONLY');end if;
 if updating and(:new.WARE_ID!=:old.WARE_ID or :new.DAY_UTC!=:old.DAY_UTC or :new.LOAD_COUNT<=:old.LOAD_COUNT or :new.TOP_PLACES<=:old.TOP_PLACES)then raise_application_error(-20863,'FORECAST_COUNTER_IDENTITY_IMMUTABLE');end if;
end;
/
create or replace trigger RRL_FORECAST_SKU_DAY_GUARD before insert or update or delete on RRL_FORECAST_SKU_DAY for each row
begin
 if deleting then raise_application_error(-20863,'FORECAST_SKU_PROJECTION_ONLY');end if;
 if RRL_FORECAST_PROJECTOR.day_write_allowed(:new.WARE_ID,:new.DAY_UTC)!=1 then raise_application_error(-20863,'FORECAST_SKU_PROJECTION_ONLY');end if;
 if updating and(:new.WARE_ID!=:old.WARE_ID or :new.DAY_UTC!=:old.DAY_UTC or :new.ARTICLE!=:old.ARTICLE or :new.BASE_UOM!=:old.BASE_UOM or :new.WORK_KIND!=:old.WORK_KIND or :new.BASE_QTY<=:old.BASE_QTY or :new.LEAF_COUNT<=:old.LEAF_COUNT or :new.SOURCE_COUNT<=:old.SOURCE_COUNT)then raise_application_error(-20863,'FORECAST_SKU_IDENTITY_IMMUTABLE');end if;
end;
/
