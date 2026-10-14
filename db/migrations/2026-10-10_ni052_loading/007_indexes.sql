-- Bound the two runtime predicates that otherwise scan physical-load history under a trip lock.
declare n number;begin
 select count(*) into n from USER_INDEXES where INDEX_NAME='RRL_TT_HU_LOAD_VEH_I1';
 if n=0 then execute immediate 'create index RRL_TT_HU_LOAD_VEH_I1 on RRL_TT_HU_LOAD_FACT(VEHICLE_ID,STATUS,TT_ID)';end if;
 select count(*) into n from USER_INDEXES where INDEX_NAME='RRL_TT_HU_LOAD_ST_SB_I1';
 if n=0 then execute immediate 'create index RRL_TT_HU_LOAD_ST_SB_I1 on RRL_TT_HU_LOAD_ST(SBORKA_PALLET_ID,ACTIVE_FLAG)';end if;
end;
/
