declare n number;cols varchar2(100);begin
 for r in(select 'RRL_WARES_PK'NAME,'P'KIND,'ID'COL from dual union all select 'RRL_WARES_NAME_UK','U','NAME'from dual)loop
  select count(*)into n from USER_CONSTRAINTS c join USER_INDEXES i on i.INDEX_NAME=c.INDEX_NAME and c.INDEX_OWNER=user
   where c.TABLE_NAME='RRL_WARES'and c.CONSTRAINT_NAME=r.NAME and c.CONSTRAINT_TYPE=r.KIND
    and c.STATUS='ENABLED'and c.VALIDATED='VALIDATED'and c.DEFERRABLE='NOT DEFERRABLE'
    and i.INDEX_TYPE='NORMAL'and i.UNIQUENESS='UNIQUE'and i.STATUS='VALID'and i.TABLE_NAME='RRL_WARES'and i.INDEX_NAME=r.NAME;
  if n!=1 then raise_application_error(-20886,'WARES_KEY_EXPECTED_KEY:'||r.NAME);end if;
  select listagg(COLUMN_NAME,',')within group(order by POSITION)into cols from USER_CONS_COLUMNS where CONSTRAINT_NAME=r.NAME;
  if cols is null or cols!=r.COL then raise_application_error(-20886,'WARES_KEY_COLUMNS:'||r.NAME);end if;
  select listagg(COLUMN_NAME,',')within group(order by COLUMN_POSITION)into cols from USER_IND_COLUMNS where INDEX_NAME=r.NAME;
  if cols is null or cols!=r.COL then raise_application_error(-20886,'WARES_KEY_INDEX_COLUMNS:'||r.NAME);end if;
 end loop;
 select count(*)into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_WARES'and COLUMN_NAME in('ID','NAME')and NULLABLE='N';if n!=2 then raise_application_error(-20886,'WARES_KEY_NOT_NULL_REQUIRED');end if;
 select count(*)into n from USER_CONSTRAINTS where TABLE_NAME='RRL_WARES'and CONSTRAINT_NAME='RRL_WARES_NAME_NN'and CONSTRAINT_TYPE='C'and STATUS='ENABLED'and VALIDATED='VALIDATED'
  and regexp_replace(upper(SEARCH_CONDITION_VC),'[[:space:]"]','')='NAMEISNOTNULL';if n!=1 then raise_application_error(-20886,'WARES_KEY_NAME_NN');end if;
 select count(*)into n from USER_CONS_COLUMNS where CONSTRAINT_NAME='RRL_WARES_NAME_NN'and COLUMN_NAME='NAME';if n!=1 then raise_application_error(-20886,'WARES_KEY_NAME_NN_COLUMN');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'WARES_KEY_INVALID_AFTER');end if;
 select count(*)into n from USER_ERRORS where NAME not like 'BIN$%';if n!=0 then raise_application_error(-20886,'WARES_KEY_ERRORS_AFTER');end if;
end;
/
