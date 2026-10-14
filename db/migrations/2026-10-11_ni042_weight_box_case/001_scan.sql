create or replace package RRL_CASE_WEIGHT_SCAN authid definer as
 procedure assert_scan(p_request clob,p_article varchar2,p_line number,p_previous number);
end;
/
create or replace package body RRL_CASE_WEIGHT_SCAN as
 procedure assert_scan(p_request clob,p_article varchar2,p_line number,p_previous number)is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');b json_object_t;
  enabled number;version number;raw_scan varchar2(512);key_value varchar2(64);identity varchar2(100);mass number;n number;fact number;
 begin
  select nvl(max(SERIALIZED_WEIGHT_BOXES),0),max(POLICY_VERSION)into enabled,version from RRL_SKU_RECEIPT_POLICY where ARTICUL=p_article;
  if enabled=0 then
   if m.has('weighted_box_scan')then raise_application_error(-20886,'WEIGHT_BOX_SKU_MODE_DISABLED');end if;
   return;
  end if;
  if not m.has('weighted_box_scan')or not m.has('weighted_policy_version')or m.get_number('weighted_policy_version')is null
   or m.get_number('weighted_policy_version')!=version or d.get_array('units').get_size!=1 then
   raise_application_error(-20886,'WEIGHT_BOX_CURRENT_LABEL_SINGLE_PHYSICAL_UNIT_REQUIRED');end if;
  if lengthb(m.get_string('weighted_box_scan'))>512 then raise_application_error(-20886,'WEIGHT_BOX_SCAN_BOUND_512');end if;
  raw_scan:=m.get_string('weighted_box_scan');b:=json_object_t.parse(RRL_WEIGHT_BOX_READ.decode_json(raw_scan));
  RRL_WEIGHT_BOX_READ.assert_sku(p_article,b.get_string('gtin'));
  identity:=b.get_string('identity');mass:=RRL_STOCK_MATH.quantity(b.get_string('net_weight_kg'));
  key_value:=d.get_array('units').get_string(0);
  fact:=RRL_STOCK_MATH.quantity(m.get_string('fact_qty'));
  if fact-nvl(p_previous,0)!=mass then raise_application_error(-20886,'WEIGHT_BOX_FACT_DELTA_MUST_EQUAL_LABEL_NET_KG');end if;
  select count(*)into n from RRL_WMS_RECEIPT_UNIT u join RRL_PALLETS lot on lot.UID_PALLET=u.CURRENT_UID
   join RRL_CASE_PICK_LINE l on l.CASE_PICK_LINE_ID=p_line and l.ARTICUL=lot.ARTICUL and l.CELL_CODE=u.CURRENT_CELL
   join RRL_STOCK_RESERVATION r on r.RESERVATION_ID=u.HARD_RESERVATION_ID and r.UID_PALLET=u.CURRENT_UID and r.CELL=u.CURRENT_CELL
    and r.SOURCE_DOC_TYPE='PICK_WAVE'and r.SOURCE_DOC_ID=l.PICK_WAVE_ID and r.SOURCE_LINE_ID=l.PICK_TASK_ID
   where lot.ARTICUL=p_article and u.PHYSICAL_UNIT_KEY=key_value and u.UNIT_ID=identity and u.BASE_UOM='KG'and u.BASE_QTY=mass
    and u.STOCK_STATUS!='ISSUED'and r.RESERVATION_KIND='HARD'and r.STATUS in('ACTIVE','ALLOCATED','PICKING')and r.BASE_QTY>=mass;
  if n!=1 then raise_application_error(-20886,'WEIGHT_BOX_CURRENT_PHYSICAL_IDENTITY_MASS_OWN_HARD_REQUIRED');end if;
 end;
end;
/
