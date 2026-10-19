create or replace package body RRL_TRADE_PICK_CONTEXT as
 g_line RRL_TRADE_ORDER_LINE%rowtype;g_ware number;g_actor varchar2(50);g_tx varchar2(100);g_valid boolean;
 procedure clear_line is begin g_line.CUSTOMER_ORDER_ROW_ID:=null;g_actor:=null;g_tx:=null;g_valid:=false;g_ware:=null;end;
 procedure enter_line(p_row number,p_actor varchar2)is n number;
 begin
  clear_line;
  begin
   select *into g_line from RRL_TRADE_ORDER_LINE where CUSTOMER_ORDER_ROW_ID=p_row;
   select WARE_ID into g_ware from RRL_TRADE_ORDER_LINK where CUSTOMER_ORDER_ID=g_line.CUSTOMER_ORDER_ID;
  exception when no_data_found then return;end;
  select count(*)into n from RRL_TRADE_ORDER_LINK l
   join RRL_TRADE_DOCUMENT d on d.WARE_ID=l.WARE_ID and d.ENTITY_TYPE='ORDER'and d.EXTERNAL_ID=l.EXTERNAL_ID and d.VERSION_NO=l.DOCUMENT_VERSION and d.STATUS='ACCEPTED'
   join RRL_TRADE_DOCUMENT r on r.WARE_ID=l.WARE_ID and r.ENTITY_TYPE='RECIPIENT'and r.EXTERNAL_ID=l.RECIPIENT_ID and r.VERSION_NO=l.RECIPIENT_VERSION and r.STATUS='ACCEPTED'
   join RRL_TRADE_DOCUMENT s on s.WARE_ID=l.WARE_ID and s.ENTITY_TYPE='SKU'and s.EXTERNAL_ID=g_line.SKU_ID and s.VERSION_NO=g_line.SKU_VERSION and s.STATUS='ACCEPTED'
   join RRL_TRADE_SITE ts on ts.WARE_ID=l.WARE_ID and ts.ENABLED=1
   where l.CUSTOMER_ORDER_ID=g_line.CUSTOMER_ORDER_ID and json_value(r.BODY_JSON,'$.active')='true'and json_value(s.BODY_JSON,'$.active')='true';
  g_valid:=n=1;g_actor:=p_actor;g_tx:=dbms_transaction.local_transaction_id(false);
 end;
 function reason(p_uid varchar2,p_cell varchar2,p_ware number)return varchar2 is
  n number;v_owner varchar2(100);v_sku varchar2(100);v_mrc number;v_expiry date;
 begin
  if g_line.CUSTOMER_ORDER_ROW_ID is null or g_tx is null or g_tx<>dbms_transaction.local_transaction_id(false)then return 'TRADE_ORDER_BINDING_REQUIRED';end if;
  if not g_valid or p_ware<>g_ware then return 'TRADE_ORDER_BINDING_STALE';end if;
  select min(a.OWNER_ID),min(a.SKU_ID),min(a.MRC),min(a.EXPIRY_DATE)into v_owner,v_sku,v_mrc,v_expiry
   from RRL_TRADE_STOCK_ATTR a join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=a.PHYSICAL_UNIT_KEY
   where u.CURRENT_UID=p_uid and u.CURRENT_CELL=p_cell and u.STOCK_STATUS<>'ISSUED';
  if v_sku is null or v_sku<>g_line.SKU_ID or v_mrc<>g_line.MRC then return 'TRADE_ORDER_SKU_MRC_MISMATCH';end if;
  if v_expiry<g_line.MIN_EXPIRY_DATE then return 'TRADE_ORDER_OSG_NOT_MET';end if;
  if v_owner<>g_line.SOURCE_OWNER_ID and v_owner<>g_line.TARGET_OWNER_ID then return 'TRADE_ORDER_OWNER_MISMATCH';end if;
  if g_line.BUYOUT_MODE='BEFORE_PICK'and v_owner<>g_line.TARGET_OWNER_ID then return 'TRADE_BUYOUT_REQUIRED_BEFORE_PICK';end if;
  if RRL_TRADE_STOCK_GUARD.owner_allowed(g_actor,p_ware,v_owner,1)<>1 then return 'TRADE_OWNER_ACCESS_DENIED';end if;
  select count(*)into n from RRL_TRADE_DOCUMENT where WARE_ID=p_ware and ENTITY_TYPE='OWNER'and EXTERNAL_ID=v_owner and STATUS='ACCEPTED'and json_value(BODY_JSON,'$.active')='true';
  if n<>1 then return 'TRADE_ORDER_OWNER_INACTIVE';end if;
  return null;
 end;
end;

/
