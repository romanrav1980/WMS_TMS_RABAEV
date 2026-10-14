-- Publish existing CASE transit cells, including ACTIVE installations.
declare v_offset number;v_count number;
begin
 RRL_STOCK_CONFIG_API.begin_change('admin','warehouse_settings_edit');
 lock table RRL_STOCK_POLICY_GUARD in exclusive mode;
 select nvl(max(LOCK_ID),900000000) into v_offset from RRL_STOCK_POLICY_GUARD;
 select count(*) into v_count from RRL_CELLS c where c.IS_SYSTEM=1 and c.CELL='CPT_'||RRL_STOCK_PLAN_HELPER.decimal_text(c.WARE_ID)
  and not exists(select 1 from RRL_STOCK_POLICY_GUARD g where g.POLICY_KEY=RRL_STOCK_LOCK_API.resource_key('CELL',c.CELL));
 if v_offset+v_count>949999999 then raise_application_error(-20808,'POLICY_LOCK_ID_RANGE_EXHAUSTED');end if;
 insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID,POLICY_VERSION)
 select RRL_STOCK_LOCK_API.resource_key('CELL',c.CELL),v_offset+row_number() over(order by c.CELL),1
 from RRL_CELLS c where c.IS_SYSTEM=1 and c.CELL='CPT_'||RRL_STOCK_PLAN_HELPER.decimal_text(c.WARE_ID)
 and not exists(select 1 from RRL_STOCK_POLICY_GUARD g where g.POLICY_KEY=RRL_STOCK_LOCK_API.resource_key('CELL',c.CELL));
 commit;RRL_STOCK_CONFIG_API.end_change;
exception when others then rollback;RRL_STOCK_CONFIG_API.end_change;raise;
end;
/
