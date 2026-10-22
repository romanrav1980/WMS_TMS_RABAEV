declare n number;begin
 select count(*)into n from USER_INDEXES where INDEX_NAME='RRL_TRADE_TOPUP_SAP_ORDER_UK' and INDEX_TYPE='FUNCTION-BASED NORMAL' and UNIQUENESS='UNIQUE' and STATUS='VALID';
 if n<>1 then raise_application_error(-20999,'TOPUP_ORDER_KEY_NOT_APPLIED');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;
end;
/