@@after_source_guard.sql
declare n number;begin
 select count(*)into n from USER_ERRORS where NAME in('RRL_WH_WEIGH_REQUEST_API','RRL_WH_WEIGH_ZERO_GUARD','RRL_WH_SCALE_API','RRL_ASSEMBLY_SCALE_API','RRL_WH_WEIGH_REQUEST_GUARD','RRL_WH_WEIGH_CLAIM_GUARD');
 if n!=0 then raise_application_error(-20886,'WH_ZERO_VERIFY_COMPILE_ERRORS');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';
 if n!=0 then raise_application_error(-20886,'WH_ZERO_VERIFY_GLOBAL_INVALID');end if;
 select count(*)into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_WH_WEIGH_ZERO';
 if n!=11 then raise_application_error(-20886,'WH_ZERO_COLUMN_COUNT');end if;
 select count(*)into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_WH_WEIGH_ZERO'and(
 (COLUMN_NAME in('CLAIM_ID','REQUEST_ID','DEVICE_ID')and DATA_TYPE='VARCHAR2'and CHAR_LENGTH=100)
 or(COLUMN_NAME='RECORDED_BY'and DATA_TYPE='NVARCHAR2'and CHAR_LENGTH=50)
 or(COLUMN_NAME in('ZERO_OBSERVED_AT','RECEIVED_AT')and DATA_TYPE='TIMESTAMP(6) WITH TIME ZONE')
 or(COLUMN_NAME in('ZERO_SOURCE_SHA256','PROFILE_SHA256')and DATA_TYPE='VARCHAR2'and CHAR_LENGTH=64)
 or(COLUMN_NAME in('ZERO_EVIDENCE_JSON','SOURCE_JSON','RESULT_JSON')and DATA_TYPE='CLOB'));
 if n!=11 then raise_application_error(-20886,'WH_ZERO_COLUMN_TYPES');end if;
 select count(*)into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_WH_WEIGH_ZERO'and NULLABLE='N';
 if n!=11 then raise_application_error(-20886,'WH_ZERO_COLUMNS_NOT_NULL');end if;
 select count(*)into n from USER_CONSTRAINTS where TABLE_NAME='RRL_WH_WEIGH_ZERO'and(STATUS!='ENABLED'or VALIDATED!='VALIDATED');
 if n!=0 then raise_application_error(-20886,'WH_ZERO_CONSTRAINTS_DISABLED');end if;
 select count(*)into n from USER_CONSTRAINTS c join USER_CONS_COLUMNS cc on cc.CONSTRAINT_NAME=c.CONSTRAINT_NAME
 where c.TABLE_NAME='RRL_WH_WEIGH_ZERO'and c.CONSTRAINT_TYPE='P'and cc.COLUMN_NAME='CLAIM_ID'and cc.POSITION=1;
 if n!=1 then raise_application_error(-20886,'WH_ZERO_CLAIM_PK_REQUIRED');end if;
 select count(*)into n from USER_CONS_COLUMNS cc join USER_CONSTRAINTS c on c.CONSTRAINT_NAME=cc.CONSTRAINT_NAME where c.TABLE_NAME='RRL_WH_WEIGH_ZERO'and c.CONSTRAINT_TYPE='P';
 if n!=1 then raise_application_error(-20886,'WH_ZERO_PK_SINGLE_COLUMN');end if;
 select count(*)into n from USER_CONSTRAINTS c join USER_CONS_COLUMNS cc on cc.CONSTRAINT_NAME=c.CONSTRAINT_NAME
 join USER_CONSTRAINTS r on r.CONSTRAINT_NAME=c.R_CONSTRAINT_NAME
 where c.TABLE_NAME='RRL_WH_WEIGH_ZERO'and c.CONSTRAINT_TYPE='R'and((cc.COLUMN_NAME='CLAIM_ID'and r.TABLE_NAME='RRL_WH_WEIGH_CLAIM')
 or(cc.COLUMN_NAME='REQUEST_ID'and r.TABLE_NAME='RRL_WH_WEIGH_REQUEST')or(cc.COLUMN_NAME='DEVICE_ID'and r.TABLE_NAME='RRL_WH_SCALE_DEVICE'));
 if n!=3 then raise_application_error(-20886,'WH_ZERO_NATIVE_IDENTITY_FKS_REQUIRED');end if;
 select count(distinct cc.COLUMN_NAME)into n from USER_CONS_COLUMNS cc join USER_CONSTRAINTS c on c.CONSTRAINT_NAME=cc.CONSTRAINT_NAME where c.TABLE_NAME='RRL_WH_WEIGH_ZERO'and c.CONSTRAINT_TYPE='R';
 if n!=3 then raise_application_error(-20886,'WH_ZERO_THREE_DISTINCT_FKS');end if;
 select count(*)into n from USER_CONSTRAINTS where TABLE_NAME='RRL_WH_WEIGH_ZERO'and CONSTRAINT_TYPE='C'and upper(SEARCH_CONDITION_VC)like'%IS JSON%';
 if n!=3 then raise_application_error(-20886,'WH_ZERO_JSON_CONSTRAINTS_REQUIRED');end if;
 select count(*)into n from USER_INDEXES i join USER_IND_COLUMNS c on c.INDEX_NAME=i.INDEX_NAME
 where i.TABLE_NAME='RRL_WH_WEIGH_ZERO'and i.STATUS='VALID'and i.UNIQUENESS='UNIQUE'and c.COLUMN_NAME='CLAIM_ID'and c.COLUMN_POSITION=1;
 if n!=1 then raise_application_error(-20886,'WH_ZERO_CLAIM_INDEX_REQUIRED');end if;
end;
/
