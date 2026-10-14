declare n number;begin
 select count(*)into n from USER_INDEXES where INDEX_NAME='RRL_IW_ONWARD_HU_SOURCE_IX';
 if n=0 then execute immediate 'create index RRL_IW_ONWARD_HU_SOURCE_IX on RRL_INTERWARE_ONWARD_BIND(WARE_ID,ROOT_UID,SOURCE_CELL,ST_ID)';end if;
 select count(*)into n from USER_INDEXES where INDEX_NAME='RRL_IW_REC_HU_SOURCE_IX';
 if n=0 then execute immediate 'create index RRL_IW_REC_HU_SOURCE_IX on RRL_IW_RECOVERY_ST_BIND(WARE_ID,ROOT_UID,SOURCE_CELL,ST_ID)';end if;
 dbms_stats.gather_table_stats(user,'RRL_INTERWARE_ONWARD_BIND',cascade=>true);
 dbms_stats.gather_table_stats(user,'RRL_IW_RECOVERY_ST_BIND',cascade=>true);
end;
/
