-- Applied by the automatic installer only to its new XEPDB1 after empty-target checks.
begin
 dbms_service.create_service('orcl','orcl');
 dbms_service.start_service('orcl');
end;
/
create or replace trigger SYS.RETAIL_CASE_START_ORCL
 after startup on database
begin
 DBMS_SERVICE.START_SERVICE('orcl');
exception when others then
 if SQLCODE != -44305 then raise; end if;
end;
/
alter system register;
