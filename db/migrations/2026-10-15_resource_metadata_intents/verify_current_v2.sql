-- Additive reviewed v2 gate: UTF8 no BOM; exclude only BIN$ recycle-bin diagnostics.
@@after_source_guard.sql
declare n number;begin
 select count(*)into n from USER_ERRORS where NAME not like 'BIN$%';if n!=0 then raise_application_error(-20886,'RESOURCE_INTENT_COMPILE_ERRORS');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'RESOURCE_INTENT_GLOBAL_INVALID');end if;
 select count(*)into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_RESOURCE_INTENT_ABANDON';if n!=16 then raise_application_error(-20886,'RESOURCE_INTENT_COLUMNS');end if;
 select count(*)into n from USER_CONSTRAINTS where TABLE_NAME='RRL_RESOURCE_INTENT_ABANDON'and(STATUS!='ENABLED'or VALIDATED!='VALIDATED');if n!=0 then raise_application_error(-20886,'RESOURCE_INTENT_CONSTRAINTS');end if;
 select count(*)into n from USER_CONSTRAINTS where TABLE_NAME='RRL_RESOURCE_INTENT_ABANDON'and CONSTRAINT_TYPE='R'and DELETE_RULE='NO ACTION';if n!=2 then raise_application_error(-20886,'RESOURCE_INTENT_HISTORY_FKS');end if;
 select count(*)into n from USER_CONSTRAINTS c where c.TABLE_NAME='RRL_RESOURCE_INTENT_ABANDON'and c.CONSTRAINT_NAME='RRL_RESOURCE_INTENT_OLD_UK'and c.CONSTRAINT_TYPE='U'and c.DEFERRABLE='NOT DEFERRABLE'and c.DEFERRED='IMMEDIATE';if n!=1 then raise_application_error(-20886,'RESOURCE_INTENT_GLOBAL_ORIGINAL_IDENTITY');end if;
 select count(*)into n from USER_CONS_COLUMNS where TABLE_NAME='RRL_RESOURCE_INTENT_ABANDON'and CONSTRAINT_NAME='RRL_RESOURCE_INTENT_OLD_UK'and((POSITION=1 and COLUMN_NAME='DOMAIN')or(POSITION=2 and COLUMN_NAME='ORIGINAL_OPERATION_ID'));if n!=2 then raise_application_error(-20886,'RESOURCE_INTENT_IDENTITY_COLUMNS');end if;
 select count(*)into n from USER_CONS_COLUMNS where TABLE_NAME='RRL_RESOURCE_INTENT_ABANDON'and CONSTRAINT_NAME='RRL_RESOURCE_INTENT_OLD_UK';if n!=2 then raise_application_error(-20886,'RESOURCE_INTENT_IDENTITY_WIDTH');end if;
 select count(*)into n from USER_INDEXES where TABLE_NAME='RRL_RESOURCE_INTENT_ABANDON'and STATUS='VALID'and UNIQUENESS='UNIQUE';if n!=2 then raise_application_error(-20886,'RESOURCE_INTENT_VALID_UNIQUE_INDEXES');end if;
 select count(*)into n from USER_TRIGGERS where TRIGGER_NAME='RRL_RESOURCE_INTENT_GUARD'and TABLE_NAME='RRL_RESOURCE_INTENT_ABANDON'and STATUS='ENABLED'and TRIGGER_TYPE='BEFORE EACH ROW';if n!=1 then raise_application_error(-20886,'RESOURCE_INTENT_GUARD_DISABLED');end if;
 select count(*)into n from USER_CONSTRAINTS c join USER_CONS_COLUMNS cc on cc.CONSTRAINT_NAME=c.CONSTRAINT_NAME and cc.TABLE_NAME=c.TABLE_NAME where c.TABLE_NAME='RRL_RESOURCE_INTENT_ABANDON'and c.CONSTRAINT_TYPE='P'and cc.POSITION=1 and cc.COLUMN_NAME='CONTROL_OPERATION_ID';if n!=1 then raise_application_error(-20886,'RESOURCE_INTENT_CONTROL_PRIMARY_KEY');end if;
 select count(*)into n from USER_CONSTRAINTS c join USER_CONS_COLUMNS cc on cc.CONSTRAINT_NAME=c.CONSTRAINT_NAME and cc.TABLE_NAME=c.TABLE_NAME where c.TABLE_NAME='RRL_RESOURCE_INTENT_ABANDON'and c.CONSTRAINT_TYPE='P';if n!=1 then raise_application_error(-20886,'RESOURCE_INTENT_PRIMARY_KEY_WIDTH');end if;
 select count(*)into n from USER_CONSTRAINTS f join USER_CONS_COLUMNS fc on fc.CONSTRAINT_NAME=f.CONSTRAINT_NAME and fc.TABLE_NAME=f.TABLE_NAME join USER_CONSTRAINTS parent on parent.CONSTRAINT_NAME=f.R_CONSTRAINT_NAME and f.R_OWNER=user join USER_CONS_COLUMNS pc on pc.CONSTRAINT_NAME=parent.CONSTRAINT_NAME and pc.TABLE_NAME=parent.TABLE_NAME and pc.POSITION=fc.POSITION where f.TABLE_NAME='RRL_RESOURCE_INTENT_ABANDON'and f.CONSTRAINT_TYPE='R'and f.DELETE_RULE='NO ACTION'and((fc.COLUMN_NAME='CASE_TASK_ID'and parent.TABLE_NAME='RRL_CASE_PICK_TASK'and pc.COLUMN_NAME='CASE_PICK_TASK_ID')or(fc.COLUMN_NAME='TASK_ID'and parent.TABLE_NAME='RRL_WAREHOUSE_TASK'and pc.COLUMN_NAME='TASK_ID'));if n!=2 then raise_application_error(-20886,'RESOURCE_INTENT_EXACT_HISTORY_FKS');end if;
 RRL_RESOURCE_INTENT_API.verify_binding;
end;
/


