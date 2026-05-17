prompt [migration 2026-05-17-014] smoke

declare
  v_legacy_order_id number;
  v_customer_order_id number;
begin
  select ID
    into v_legacy_order_id
    from (
      select ID
        from RRL_ORDERS
       where ADDR is not null
       order by ID
    )
   where rownum = 1;

  v_customer_order_id := RRL_CUSTOMER_ORDER_API.import_legacy_order(
    p_legacy_order_id => v_legacy_order_id,
    p_created_by => 'SMOKE_014'
  );
end;
/

select co.CUSTOMER_ORDER_ID,
       co.LEGACY_ORDER_ID,
       co.ORDER_NO,
       c.CUSTOMER_NAME,
       count(r.CUSTOMER_ORDER_ROW_ID) ROW_COUNT
  from RRL_CUSTOMER_ORDER co
  join RRL_CUSTOMER c
    on c.CUSTOMER_ID = co.CUSTOMER_ID
  left join RRL_CUSTOMER_ORDER_ROW r
    on r.CUSTOMER_ORDER_ID = co.CUSTOMER_ORDER_ID
 where co.CREATED_BY = 'SMOKE_014'
 group by co.CUSTOMER_ORDER_ID, co.LEGACY_ORDER_ID, co.ORDER_NO, c.CUSTOMER_NAME
 order by co.CUSTOMER_ORDER_ID;

prompt [migration 2026-05-17-014] smoke invalid objects
select object_type, object_name, status
  from user_objects
 where status <> 'VALID'
 order by object_type, object_name;
