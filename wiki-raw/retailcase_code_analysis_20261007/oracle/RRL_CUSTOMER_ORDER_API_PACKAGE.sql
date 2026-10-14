package RRL_CUSTOMER_ORDER_API as
  function normalize_key(p_value varchar2) return varchar2 deterministic;

  function ensure_customer_from_legacy_addr(
    p_legacy_addr varchar2,
    p_created_by  varchar2 default null
  ) return number;

  function import_legacy_order(
    p_legacy_order_id number,
    p_created_by      varchar2 default null
  ) return number;

  procedure sync_fulfillment_from_legacy(
    p_customer_order_id number,
    p_created_by        varchar2 default null
  );
end RRL_CUSTOMER_ORDER_API;
