declare n number;begin select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_SUP_HANDOVER_GUARD','RRL_SUP_CONFIRM_GUARD')and STATUS!='VALID';if n>0 then raise_application_error(-20808,'SUP_HANDOVER_INVALID');end if;end;
/
