whenever sqlerror exit failure rollback
declare n number;begin
 select count(*)into n from(select WARE_ID,SKM_ID,EXTERNAL_DOCUMENT_ID from RRL_TRADE_BUYOUT group by WARE_ID,SKM_ID,EXTERNAL_DOCUMENT_ID having count(*)>1);
 if n>0 then raise_application_error(-20999,'TRADE_BUYOUT_KEY_ROLLBACK_REFUSED_MULTIPLE_PENDING_OR_HISTORY');end if;
end;
/
drop index RRL_TRADE_BUYOUT_DOC_UK;
alter table RRL_TRADE_BUYOUT add constraint RRL_TRADE_BUYOUT_EXT_UK unique(WARE_ID,SKM_ID,EXTERNAL_DOCUMENT_ID);
delete from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-19-tradecase-buyout-external-key';
commit;
