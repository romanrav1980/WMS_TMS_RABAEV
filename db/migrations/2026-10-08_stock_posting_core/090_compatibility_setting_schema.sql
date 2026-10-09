declare n number;begin
 select count(*) into n from USER_TABLES where TABLE_NAME='RRL_STOCK_SETTING_AUDIT';
 if n=0 then execute immediate 'create table RRL_STOCK_SETTING_AUDIT(
  SETTING_KEY varchar2(100) not null,SETTING_VERSION number not null,OLD_VALUE varchar2(100),NEW_VALUE varchar2(100) not null,
  REASON varchar2(1000) not null,CHANGED_BY varchar2(50) not null,CHANGED_AT timestamp default systimestamp not null,
  constraint RRL_STOCK_SETTING_AUDIT_PK primary key(SETTING_KEY,SETTING_VERSION))';end if;
end;
/
merge into RRL_SYSTEM_SETTINGS d using(select 'STOCK_LEGACY_TRIGGER_ENABLED' SETTING_KEY from dual)s on(d.SETTING_KEY=s.SETTING_KEY)
 when not matched then insert(SETTING_KEY,SETTING_VALUE,DESCRIPTION,UPDATED_AT,UPDATED_BY)
 values(s.SETTING_KEY,'0','Stock posting compatibility; database-wide; default OFF',sysdate,user);
commit;
