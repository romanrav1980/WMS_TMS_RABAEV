declare n number;begin
 select count(*)into n from RRL_OPC_SCALE_EVIDENCE;
 if n!=0 then raise_application_error(-20886,'OPC_EVIDENCE_NONEMPTY_HISTORY_PRESERVE');end if;
end;
/
drop trigger RRL_OPC_EVIDENCE_GUARD;
drop context RRL_OPC_EVIDENCE_CTX;
drop package RRL_OPC_EVIDENCE_API;
drop table RRL_OPC_SCALE_EVIDENCE;
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-15-opc-scale-evidence';
commit;
