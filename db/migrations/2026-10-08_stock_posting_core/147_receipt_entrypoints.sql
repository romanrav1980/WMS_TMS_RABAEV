create or replace procedure RRL_ACCEPT_ORDER2(order_id int) authid definer is
 state varchar2(20);
begin
 select STATE into state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if state='PREPARED' then RRL_ACCEPT_ORDER2_SP_OLD(order_id);return; end if;
 if state!='ACTIVE' then raise_application_error(-20885,'STOCK_RELEASE_NOT_ACTIVE');end if;
 raise_application_error(-20886,'SAP_SCANNED_RECEIPT_REQUIRED: use receiving.html?receipt_document_id='||to_char(order_id,'TM9')||'; reverse physical receipt with RRL_STORNO_ORDER3');
end;
/

create or replace procedure RRL_ACCEPT_ORDER2_2(order_id int,user_id1 varchar2) authid definer is
 state varchar2(20);
begin
 select STATE into state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if state='PREPARED' then RRL_ACCEPT_ORDER2_2_SP_OLD(order_id,user_id1);return; end if;
 if state!='ACTIVE' then raise_application_error(-20885,'STOCK_RELEASE_NOT_ACTIVE');end if;
 raise_application_error(-20886,'SAP_SCANNED_RECEIPT_REQUIRED: use receiving.html?receipt_document_id='||to_char(order_id,'TM9')||'; reverse physical receipt with RRL_STORNO_ORDER3');
end;
/

create or replace function RRL_ACCEPT_ORDER2_3(order_id int,user_id1 varchar2) return int authid definer is
 state varchar2(20);
begin
 select STATE into state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if state='PREPARED' then return RRL_ACCEPT_ORDER2_3_SP_OLD(order_id,user_id1); end if;
 if state!='ACTIVE' then raise_application_error(-20885,'STOCK_RELEASE_NOT_ACTIVE');end if;
 raise_application_error(-20886,'SAP_SCANNED_RECEIPT_REQUIRED: use receiving.html?receipt_document_id='||to_char(order_id,'TM9')||'; reverse physical receipt with RRL_STORNO_ORDER3');
end;
/

create or replace procedure RRL_ACCEPT_ORDER3(order_id int,user_id1 varchar2) authid definer is
 state varchar2(20);
begin
 select STATE into state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if state='PREPARED' then RRL_ACCEPT_ORDER3_SP_OLD(order_id,user_id1);return; end if;
 if state!='ACTIVE' then raise_application_error(-20885,'STOCK_RELEASE_NOT_ACTIVE');end if;
 raise_application_error(-20886,'SAP_SCANNED_RECEIPT_REQUIRED: use receiving.html?receipt_document_id='||to_char(order_id,'TM9')||'; reverse physical receipt with RRL_STORNO_ORDER3');
end;
/

create or replace procedure RRL_OTKAT_ORDER2(order_id int) authid definer is
 state varchar2(20);
begin
 select STATE into state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if state='PREPARED' then RRL_OTKAT_ORDER2_SP_OLD(order_id);return; end if;
 if state!='ACTIVE' then raise_application_error(-20885,'STOCK_RELEASE_NOT_ACTIVE');end if;
 raise_application_error(-20886,'SAP_SCANNED_RECEIPT_REQUIRED: use receiving.html?receipt_document_id='||to_char(order_id,'TM9')||'; reverse physical receipt with RRL_STORNO_ORDER3');
end;
/
