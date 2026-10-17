declare n number;begin
 select count(*)into n from RRL_WH_SCALE_CAPTURE where json_value(RESULT_JSON,'$.signature_domain' returning varchar2(40))='ASM_FINAL';
 if n!=0 then raise_application_error(-20886,'ASM_FINAL_ROLLBACK_ARCHIVE_HISTORY_EXISTS');end if;
 select count(*)into n from RRL_ASSEMBLY_SESSION s join RRL_WH_SCALE_CAPTURE c on c.CAPTURE_KEY=s.FINAL_CAPTURE_KEY
  where json_value(c.RESULT_JSON,'$.signature_domain' returning varchar2(40))='ASM_FINAL';
 if n!=0 then raise_application_error(-20886,'ASM_FINAL_ROLLBACK_SESSION_HISTORY_EXISTS');end if;
 select count(*)into n from RRL_WH_WEIGH_REQUEST where EXPIRES_AT>=systimestamp
  and json_value(SNAPSHOT_JSON,'$.signature_domain' returning varchar2(40))='ASM_FINAL';
 if n!=0 then raise_application_error(-20886,'ASM_FINAL_ROLLBACK_LIVE_REQUEST_EXISTS');end if;
end;
/
