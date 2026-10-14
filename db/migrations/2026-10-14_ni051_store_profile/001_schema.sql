-- MIGRATION_ID: 2026-10-14-1490-ni051-store-profile
-- Профиль магазина: только параметры, которых нет в RRL_ADDR и смежных политиках (окна приёма, подсобка,
-- рампа и внешние габариты ТС на подъезде, способ разгрузки, примечание о подъезде). NULL = не задано, ни на что
-- не влияет. RRL_ADDR не имеет PK-constraint (только UNIQUE index), поэтому FK не создаётся: существование
-- неудалённого адреса проверяет guard в CONFIG-транзакции. Контакты и коды доступа не хранятся.
-- Окна: режим UNCONFIGURED (строк нет) или WEEKLY (строки = полная неделя, отсутствующий день закрыт),
-- интервалы [FROM,TO) без пересечений, не более 8 в день и 56 в неделю (API + проверка ниже).
declare n number;begin
 select count(*) into n from USER_TABLES where TABLE_NAME='RRL_STORE_PROFILE';
 if n=0 then execute immediate 'create table RRL_STORE_PROFILE(
 STORE_ADDR varchar2(255) not null, PROFILE_VERSION number not null check(PROFILE_VERSION>=1),
 RECEIVING_WINDOW_MODE varchar2(12) default ''UNCONFIGURED'' not null check(RECEIVING_WINDOW_MODE in(''UNCONFIGURED'',''WEEKLY'')),
 TIMEZONE_REGION varchar2(64),
 BACKROOM_FLAG number(1) check(BACKROOM_FLAG in(0,1)), BACKROOM_PALLETS number(6) check(BACKROOM_PALLETS between 0 and 100000),
 BACKROOM_ROLLS number(6) check(BACKROOM_ROLLS between 0 and 100000), UNATTENDED_DROP_FLAG number(1) check(UNATTENDED_DROP_FLAG in(0,1)),
 STORAGE_TEMP_CLASS varchar2(10) check(STORAGE_TEMP_CLASS in(''AMBIENT'',''CHILLED'',''FROZEN'')),
 RAMP_FLAG number(1) check(RAMP_FLAG in(0,1)), RAMP_HEIGHT_MM number(6) check(RAMP_HEIGHT_MM between 0 and 100000),
 MAX_VEHICLE_OUTER_HEIGHT_MM number(6) check(MAX_VEHICLE_OUTER_HEIGHT_MM between 1 and 100000),
 MAX_VEHICLE_OUTER_LENGTH_MM number(6) check(MAX_VEHICLE_OUTER_LENGTH_MM between 1 and 100000),
 DEFAULT_UNLOAD_METHOD varchar2(10) check(DEFAULT_UNLOAD_METHOD in(''PALLET'',''ROLL_CAGE'',''MANUAL'')),
 LOADER_REQUIRED number(1) check(LOADER_REQUIRED in(0,1)), ACCESS_NOTE varchar2(1000 char),
 UPDATED_BY varchar2(100) not null, UPDATED_AT timestamp default systimestamp not null,
 constraint RRL_STORE_PROFILE_PK primary key(STORE_ADDR),
 constraint RRL_STORE_PROFILE_BACKROOM_CK check(not(BACKROOM_FLAG=0 and(nvl(BACKROOM_PALLETS,0)>0 or nvl(BACKROOM_ROLLS,0)>0))),
 constraint RRL_STORE_PROFILE_RAMP_CK check(not(RAMP_FLAG=0 and nvl(RAMP_HEIGHT_MM,0)>0)),
 constraint RRL_STORE_PROFILE_TZ_CK check(RECEIVING_WINDOW_MODE!=''WEEKLY'' or TIMEZONE_REGION is not null))';end if;
 select count(*) into n from USER_TABLES where TABLE_NAME='RRL_STORE_RECEIVING_WINDOW';
 if n=0 then execute immediate 'create table RRL_STORE_RECEIVING_WINDOW(
 STORE_ADDR varchar2(255) not null, WEEKDAY number(1) not null check(WEEKDAY between 1 and 7),
 FROM_MINUTE number(4) not null check(FROM_MINUTE between 0 and 1439), TO_MINUTE number(4) not null check(TO_MINUTE between 1 and 1440),
 constraint RRL_STORE_RECEIVING_WINDOW_CK check(FROM_MINUTE<TO_MINUTE),
 constraint RRL_STORE_RECEIVING_WINDOW_PK primary key(STORE_ADDR,WEEKDAY,FROM_MINUTE),
 constraint RRL_STORE_RECEIVING_WINDOW_FK foreign key(STORE_ADDR) references RRL_STORE_PROFILE(STORE_ADDR))';end if;
 select count(*) into n from USER_TABLES where TABLE_NAME='RRL_STORE_PROFILE_CHANGE';
 if n=0 then execute immediate 'create table RRL_STORE_PROFILE_CHANGE(
 OPERATION_ID varchar2(100) primary key, STORE_ADDR varchar2(255) not null, PROFILE_VERSION number not null,
 ACTOR varchar2(100) not null, REASON_TEXT varchar2(1000 char) not null, REQUEST_HASH varchar2(64) not null,
 REQUEST_JSON clob not null check(REQUEST_JSON is json), RESULT_JSON clob not null check(RESULT_JSON is json),
 CREATED_AT timestamp default systimestamp not null,
 constraint RRL_STORE_PROFILE_CHANGE_U1 unique(STORE_ADDR,PROFILE_VERSION))';end if;
end;
/
create or replace trigger RRL_STORE_PROFILE_GUARD before insert or update or delete on RRL_STORE_PROFILE for each row
declare n number;begin
 if nvl(sys_context('RRL_STOCK_WRITE_CTX','MODE'),chr(0))!='CONFIG'
 or nvl(sys_context('RRL_STOCK_WRITE_CTX','CONFIG_PERMISSION'),chr(0))!='warehouse_settings_edit'
 or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null
 or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)
 then raise_application_error(-20863,'STORE_PROFILE_CONFIGURATION_REQUIRED');end if;
 if deleting then raise_application_error(-20863,'STORE_PROFILE_DELETE_FORBIDDEN');end if;
 RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
 select count(*) into n from RRL_ADDR where ADDR=:new.STORE_ADDR and nvl(DELETED3,0)=0;
 if n!=1 then raise_application_error(-20886,'STORE_PROFILE_ADDRESS_MISSING_OR_AMBIGUOUS');end if;
 if updating and :new.STORE_ADDR!=:old.STORE_ADDR then raise_application_error(-20863,'STORE_PROFILE_KEY_IMMUTABLE');end if;
end;
/
create or replace trigger RRL_STORE_RECEIVING_WINDOW_GUARD before insert or update or delete on RRL_STORE_RECEIVING_WINDOW for each row
declare mode_name varchar2(12);begin
 if nvl(sys_context('RRL_STOCK_WRITE_CTX','MODE'),chr(0))!='CONFIG'
 or nvl(sys_context('RRL_STOCK_WRITE_CTX','CONFIG_PERMISSION'),chr(0))!='warehouse_settings_edit'
 or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null
 or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)
 then raise_application_error(-20863,'STORE_PROFILE_CONFIGURATION_REQUIRED');end if;
 if inserting then select RECEIVING_WINDOW_MODE into mode_name from RRL_STORE_PROFILE where STORE_ADDR=:new.STORE_ADDR;
  if mode_name!='WEEKLY' then raise_application_error(-20886,'STORE_WINDOWS_REQUIRE_WEEKLY_MODE');end if;end if;
end;
/
create or replace trigger RRL_STORE_PROFILE_CHANGE_GUARD before insert or update or delete on RRL_STORE_PROFILE_CHANGE
begin
 if updating or deleting then raise_application_error(-20863,'STORE_PROFILE_HISTORY_IMMUTABLE');end if;
 if nvl(sys_context('RRL_STOCK_WRITE_CTX','MODE'),chr(0))!='CONFIG'
 or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null
 or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)
 then raise_application_error(-20863,'STORE_PROFILE_CONFIGURATION_REQUIRED');end if;
end;
/
