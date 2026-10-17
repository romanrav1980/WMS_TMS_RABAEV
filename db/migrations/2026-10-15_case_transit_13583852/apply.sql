-- MIGRATION_ID: 2026-10-15-case-transit-13583852
-- One warehouse metadata repair through existing configuration owner; no quantities.
declare n number;v_lock_id number;release_state varchar2(20);begin
 RRL_STOCK_CONFIG_API.begin_change('admin','warehouse_settings_edit');
 select count(*)into n from RUSERS where ID='admin'and nvl(DELETED,0)=0 and upper(trim(USER_GROUP))='GLOBAL_ADMIN';
 if n!=1 then raise_application_error(-20882,'CASE_TRANSIT_CURRENT_ADMIN_REQUIRED');end if;
 select STATE into release_state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if release_state is null or release_state not in('PREPARED','ACTIVE')then raise_application_error(-20886,'CASE_TRANSIT_RELEASE_CLOSED');end if;
 select count(*)into n from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-15-case-transit-13583852';
 if n!=0 then raise_application_error(-20886,'CASE_TRANSIT_MIGRATION_EXISTS');end if;
 select count(*)into n from RRL_WARES where ID=13583852;if n!=1 then raise_application_error(-20886,'CASE_TRANSIT_WARE_REQUIRED');end if;
 select count(*)into n from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=1136 and WARE_ID=13583852 and STATUS='IN_PROGRESS'and ASSIGNED_TO='WHREQ15.OP'and PICKED_QTY=0 and CONTENT_VERSION=2;
 if n!=1 then raise_application_error(-20886,'CASE_TRANSIT_QA_CONTEXT_CHANGED');end if;
 select count(*)into n from RRL_ASSEMBLY_SESSION where CASE_PICK_TASK_ID=1136;if n!=0 then raise_application_error(-20886,'CASE_TRANSIT_QA_ASSEMBLY_EXISTS');end if;
 select count(*)into n from RRL_REMAINS where UID_POLETA='REUSE.RETURN:e6c16d0bbd';if n!=2 then raise_application_error(-20886,'CASE_TRANSIT_SOURCE_ROWSET_CHANGED');end if;
 select count(*)into n from RRL_REMAINS where UID_POLETA='REUSE.RETURN:e6c16d0bbd'and((CELL='QIPcdbf4c0962'and REMAIN=24 and HARD_RESERVED_BASE=1 and STOCK_VERSION=10)or(CELL='QRREe6c16d0bbd'and REMAIN=0 and HARD_RESERVED_BASE=0 and STOCK_VERSION=2));
 if n!=2 then raise_application_error(-20886,'CASE_TRANSIT_SOURCE_FACT_CHANGED');end if;
 select count(*)into n from RRL_CELLS where CELL='CPT_13583852';if n!=0 then raise_application_error(-20886,'CASE_TRANSIT_CELL_ALREADY_EXISTS');end if;
 select count(*)into n from RRL_REMAINS where CELL='CPT_13583852';if n!=0 then raise_application_error(-20886,'CASE_TRANSIT_UNKNOWN_CONTENT');end if;
 lock table RRL_STOCK_POLICY_GUARD in exclusive mode wait 5;
 select count(*)into n from RRL_STOCK_POLICY_GUARD where POLICY_KEY=RRL_STOCK_LOCK_API.resource_key('CELL','CPT_13583852');
 if n!=0 then raise_application_error(-20886,'CASE_TRANSIT_POLICY_ALREADY_EXISTS');end if;
 select nvl(max(LOCK_ID),900000000)+1 into v_lock_id from RRL_STOCK_POLICY_GUARD;
 if v_lock_id<900000000 or v_lock_id>949999999 then raise_application_error(-20886,'CASE_TRANSIT_POLICY_LOCK_RANGE');end if;
 insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,IS_SYSTEM,OTBOR,BLOCKED_FOR_REMAINS,BLOCKED_FOR_POPOLNENIE)values('CPT_13583852',13583852,0,0,0,1,0,1,1);
 insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID,POLICY_VERSION)values(RRL_STOCK_LOCK_API.resource_key('CELL','CPT_13583852'),v_lock_id,1);
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'CASE_TRANSIT_GLOBAL_INVALID');end if;
 insert into RRL_SCHEMA_MIGRATIONS(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values('2026-10-15-case-transit-13583852','Bounded CASE transit metadata for WARE13583852; no quantity changes',sysdate,user,'apply.sql','rollback.sql','APPLIED');
 commit;RRL_STOCK_CONFIG_API.end_change;
exception when others then rollback;RRL_STOCK_CONFIG_API.end_change;raise;end;
/
