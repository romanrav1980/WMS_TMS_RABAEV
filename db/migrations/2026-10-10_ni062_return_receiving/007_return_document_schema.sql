declare n number;begin
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_PRIHOD_NAKLAD' and COLUMN_NAME='DOCUMENT_KIND';
 if n=0 then execute immediate 'alter table RRL_PRIHOD_NAKLAD add(DOCUMENT_KIND varchar2(30 byte) default ''LEGACY_RECEIPT'' not null)';end if;
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_PRIHOD_NAKLAD' and COLUMN_NAME='RETURN_APPROVAL_OPERATION_ID';
 if n=0 then execute immediate 'alter table RRL_PRIHOD_NAKLAD add(RETURN_APPROVAL_OPERATION_ID varchar2(100 byte))';end if;
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_PRIHOD_NAKLAD' and COLUMN_NAME='RETURN_DOCUMENT_REFERENCE';
 if n=0 then execute immediate 'alter table RRL_PRIHOD_NAKLAD add(RETURN_DOCUMENT_REFERENCE varchar2(100 byte))';end if;
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_STORE_RETURN_RECEIPT' and COLUMN_NAME='NAKLAD_ID';
 if n=0 then execute immediate 'alter table RRL_STORE_RETURN_RECEIPT add(NAKLAD_ID number)';end if;
end;
/
begin execute immediate 'alter table RRL_PRIHOD_NAKLAD add constraint RRL_PRIHOD_RETURN_KIND_CHECK check(DOCUMENT_KIND=''LEGACY_RECEIPT'' or(DOCUMENT_KIND=''STORE_RETURN'' and RETURN_APPROVAL_OPERATION_ID is not null and RETURN_DOCUMENT_REFERENCE is not null))';exception when others then if sqlcode!=-2264 then raise;end if;end;
/
begin execute immediate 'alter table RRL_PRIHOD_NAKLAD add constraint RRL_PRIHOD_RETURN_APPROVAL_FK foreign key(RETURN_APPROVAL_OPERATION_ID) references RRL_STORE_RETURN_APPROVAL(OPERATION_ID)';exception when others then if sqlcode!=-2264 then raise;end if;end;
/
begin execute immediate 'alter table RRL_STORE_RETURN_RECEIPT modify NAKLAD_ID not null';exception when others then if sqlcode!=-1442 then raise;end if;end;
/
