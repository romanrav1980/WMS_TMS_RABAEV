-- One-time PREPARED provisioning. Publishing policy keys never occurs inside a posting transaction.
declare v_offset number;v_count number;v_state varchar2(20);
begin
 select STATE into v_state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if v_state!='PREPARED' then raise_application_error(-20808,'CATALOG_BOOTSTRAP_REQUIRES_PREPARED'); end if;
 lock table RRL_STOCK_POLICY_GUARD in exclusive mode;
 select nvl(max(LOCK_ID),900000000) into v_offset from RRL_STOCK_POLICY_GUARD;
 select count(*) into v_count from (
  select RRL_STOCK_LOCK_API.resource_key('RELEASE','STOCK') K from dual
  union select RRL_STOCK_LOCK_API.resource_key('SKU',ARTICUL) from (select ARTICUL from RRL_PALLETS where ARTICUL is not null group by ARTICUL)
  union select RRL_STOCK_LOCK_API.resource_key('SKU',ARTICUL) from RRL_SAP_ARTICLE_META where ARTICUL is not null
  union select RRL_STOCK_LOCK_API.resource_key('SKU',ARTICUL) from RRL_SKU_RECEIPT_POLICY where ARTICUL is not null
  union select RRL_STOCK_LOCK_API.resource_key('CELL',CELL) from RRL_CELLS where CELL is not null
 ) j where not exists(select 1 from RRL_STOCK_POLICY_GUARD p where p.POLICY_KEY=j.K);
 if v_offset+v_count>949999999 then raise_application_error(-20808,'POLICY_LOCK_ID_RANGE_EXHAUSTED'); end if;
 insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID,POLICY_VERSION)
 select K,v_offset+row_number() over(order by K),1 from (
  select RRL_STOCK_LOCK_API.resource_key('RELEASE','STOCK') K from dual
  union select RRL_STOCK_LOCK_API.resource_key('SKU',ARTICUL) from (select ARTICUL from RRL_PALLETS where ARTICUL is not null group by ARTICUL)
  union select RRL_STOCK_LOCK_API.resource_key('SKU',ARTICUL) from RRL_SAP_ARTICLE_META where ARTICUL is not null
  union select RRL_STOCK_LOCK_API.resource_key('SKU',ARTICUL) from RRL_SKU_RECEIPT_POLICY where ARTICUL is not null
  union select RRL_STOCK_LOCK_API.resource_key('CELL',CELL) from RRL_CELLS where CELL is not null
 ) j where not exists(select 1 from RRL_STOCK_POLICY_GUARD p where p.POLICY_KEY=j.K);
 commit;
end;
/
