-- Read-only exact metadata/source/ledger acceptance; no quantity mutation.
declare n number;begin
 select count(*)into n from RRL_CELLS where CELL='CPT_13583852'and WARE_ID=13583852 and X=0 and Y=0 and Z=0 and IS_SYSTEM=1 and OTBOR=0 and BLOCKED_FOR_REMAINS=1 and BLOCKED_FOR_POPOLNENIE=1;
 if n!=1 then raise_application_error(-20886,'CASE_TRANSIT_VERIFY_CELL');end if;
 select count(*)into n from RRL_STOCK_POLICY_GUARD where POLICY_KEY=RRL_STOCK_LOCK_API.resource_key('CELL','CPT_13583852')and POLICY_VERSION=1 and LOCK_ID between 900000000 and 949999999;
 if n!=1 then raise_application_error(-20886,'CASE_TRANSIT_VERIFY_POLICY');end if;
 select count(*)into n from RRL_REMAINS where UID_POLETA='REUSE.RETURN:e6c16d0bbd';if n!=2 then raise_application_error(-20886,'CASE_TRANSIT_VERIFY_SOURCE_ROWSET');end if;
 select count(*)into n from RRL_REMAINS where UID_POLETA='REUSE.RETURN:e6c16d0bbd'and((CELL='QIPcdbf4c0962'and REMAIN=24 and HARD_RESERVED_BASE=1 and STOCK_VERSION=10)or(CELL='QRREe6c16d0bbd'and REMAIN=0 and HARD_RESERVED_BASE=0 and STOCK_VERSION=2));
 if n!=2 then raise_application_error(-20886,'CASE_TRANSIT_VERIFY_SOURCE_FACT');end if;
 select count(*)into n from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-15-case-transit-13583852'and STATUS='APPLIED';
 if n!=1 then raise_application_error(-20886,'CASE_TRANSIT_VERIFY_LEDGER');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'CASE_TRANSIT_VERIFY_INVALID');end if;
end;
/
select CELL,WARE_ID,IS_SYSTEM,OTBOR,BLOCKED_FOR_REMAINS,BLOCKED_FOR_POPOLNENIE from RRL_CELLS where CELL='CPT_13583852';
select rawtohex(POLICY_KEY) KEY_HEX,LOCK_ID,POLICY_VERSION from RRL_STOCK_POLICY_GUARD where POLICY_KEY=RRL_STOCK_LOCK_API.resource_key('CELL','CPT_13583852');
select CELL,REMAIN,HARD_RESERVED_BASE,STOCK_VERSION from RRL_REMAINS where UID_POLETA='REUSE.RETURN:e6c16d0bbd' order by CELL;
select *from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-15-case-transit-13583852';
