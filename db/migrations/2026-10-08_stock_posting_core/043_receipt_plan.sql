create or replace package RRL_STOCK_RECEIPT_PLAN authid definer
 accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_RECEIPT_CORE) as
 procedure compile_receipt(p_request clob,p_operation varchar2,p_hints clob,p_policies out clob,p_resources out clob,p_domain out clob);
end;
/
create or replace package body RRL_STOCK_RECEIPT_PLAN as
 procedure compile_receipt(p_request clob,p_operation varchar2,p_hints clob,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);s json_object_t;m json_object_t;h json_object_t;
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();o RRL_SAP_SUPPLY_ORDER%rowtype;
  v_article varchar2(160);v_uid varchar2(200);v_task number;v_target varchar2(60);v_slot number;v_line varchar2(30);
 begin
  if p_hints is null or dbms_lob.getlength(p_hints)>4194304 then raise_application_error(-20871,'RECEIPT_PLAN_REQUIRED');end if;
  h:=json_object_t.parse(p_hints);s:=d.get_object('source');m:=d.get_object('metadata');
  declare
 v_json_sql_1_1 varchar2(32767):=s.get_string('order_id');
begin
select * into o from RRL_SAP_SUPPLY_ORDER where ORDER_ID=v_json_sql_1_1;
end;
  v_line:=m.get_string('line_number');
  select ARTICUL into v_article from RRL_SAP_SUPPLY_LINE where ORDER_ID=o.ORDER_ID and LINE_NUMBER=v_line;
  if h.get_string('article')!=v_article or h.get_number('order_revision')!=o.REVISION or h.get_number('naklad_id')!=o.NAKLAD_ID then
   raise_application_error(-20890,'CLOSURE_CHANGED: receipt source');end if;
  v_uid:=m.get_string('sscc');v_target:=h.get_object('placement').get_string('cell');v_slot:=h.get_object('placement').get_number('slot_id');
  if v_uid is null or v_target is null then raise_application_error(-20871,'RECEIPT_IDENTITY_REQUIRED');end if;
  select RRL_WAREHOUSE_TASK_SQ.nextval into v_task from dual;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_SAP_SUPPLY_ORDER',o.ORDER_ID);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PRIHOD_NAKLAD',RRL_STOCK_PLAN_HELPER.decimal_text(o.NAKLAD_ID));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_SAP_SUPPLY_LINE',o.ORDER_ID||':'||v_line);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v_task));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_RECEIPT_SLOT_CLAIM',RRL_STOCK_PLAN_HELPER.decimal_text(v_task));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_RECEIPT_LABEL',v_uid);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','PALLET:'||v_uid);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','SAP.RECEIPT:'||p_operation);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','SAP.OUTBOX:'||p_operation);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  RRL_STOCK_PLAN_HELPER.stock_closure(f,r,v_uid,v_article,o.RECEIVE_CELL,v_target);
  if v_slot is not null then RRL_STOCK_PLAN_HELPER.anchor(r,40,'SLOT',RRL_STOCK_PLAN_HELPER.decimal_text(v_slot));end if;
  for u in(select UNIT_KEY from json_table(p_hints,'$.unit_bindings[*]' columns(UNIT_KEY varchar2(64) path '$.key'))) loop
   RRL_STOCK_PLAN_HELPER.anchor(r,60,'UNIT',u.UNIT_KEY);
  end loop;
  for a in(select SYSTEM_CODE,CODE_HASH from json_table(p_hints,'$.aliases[*]' columns(SYSTEM_CODE varchar2(40) path '$.system',CODE_HASH varchar2(64) path '$.hash'))) loop
   RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','MARK:'||a.SYSTEM_CODE||':'||a.CODE_HASH);
  end loop;
  RRL_STOCK_PLAN_HELPER.anchor(r,30,'HU',v_uid);
  for a in(select SYSTEM_CODE,CODE_HASH from json_table(p_hints,'$.aggregations[*]' columns(SYSTEM_CODE varchar2(40) path '$.system',CODE_HASH varchar2(64) path '$.hash'))) loop
   RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','AGG:'||a.SYSTEM_CODE||':'||a.CODE_HASH);
  end loop;
  h.put('task_id',v_task);h.put('warehouse_id',o.WARE_ID);h.put('receive_cell',o.RECEIVE_CELL);
  h.put('uid',v_uid);h.put('source_order_id',o.ORDER_ID);h.put('line_number',v_line);
  p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=h.to_clob;
 end;
end;
/
