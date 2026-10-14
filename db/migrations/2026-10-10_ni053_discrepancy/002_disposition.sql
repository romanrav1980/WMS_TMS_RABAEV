create or replace package RRL_STOCK_STORE_DISPOSITION authid definer accessible by(package RRL_STOCK_STORE_RECEIPT_CMD) as
 procedure resolve_counts(p_snapshot clob,p_metadata clob,p_lines out json_array_t,p_has_issue out boolean);
 procedure declare_rows(p_operation varchar2,p_lines json_array_t,p_has_issue boolean,r in out nocopy json_array_t);
 procedure persist(p_operation varchar2,p_domain json_object_t,p_actor varchar2,p_result out json_array_t);
end;
/
create or replace package body RRL_STOCK_STORE_DISPOSITION as
 function nonnegative(p_text varchar2) return number is
 begin
  if regexp_like(p_text,'^0{1,18}([.]0{1,9})?$','c') then return 0;end if;
  return RRL_STOCK_MATH.quantity(p_text);
 end;
 function count_value(x json_object_t,p_name varchar2) return number is qty number:=0;
 begin
  if x.has(p_name) then qty:=nonnegative(x.get_string(p_name));end if;
  if qty is null or qty<0 then raise_application_error(-20886,'STORE_DISPOSITION_NONNEGATIVE_QTY_REQUIRED');end if;return qty;
 end;
 procedure resolve_counts(p_snapshot clob,p_metadata clob,p_lines out json_array_t,p_has_issue out boolean) is
  tree json_object_t:=json_object_t.parse(p_snapshot);m json_object_t:=json_object_t.parse(p_metadata);nodes json_array_t:=tree.get_array('nodes');observed json_array_t:=json_array_t();x json_object_t;o json_object_t;line_json json_object_t;
  type observed_map is table of json_object_t index by varchar2(200);by_uid observed_map;
  uid_text varchar2(200);article_text varchar2(160);unit_text varchar2(20);shipped number;accepted number;missing number;refused number;damaged number;extra_no number;scale_no number;line_no number:=0;reason_text varchar2(32767);
 begin
  p_lines:=json_array_t();p_has_issue:=false;
  if m.has('observations') then
   if not m.get('observations').is_array then raise_application_error(-20886,'STORE_DISPOSITION_ARRAY_REQUIRED');end if;
   observed:=m.get_array('observations');
  end if;
  if observed.get_size>200 then raise_application_error(-20881,'STORE_DISPOSITION_LINE_BOUND_200');end if;
  for i in 0..observed.get_size-1 loop
   o:=treat(observed.get(i) as json_object_t);uid_text:=o.get_string('lot_uid');
   if uid_text is null or by_uid.exists(uid_text) then raise_application_error(-20886,'STORE_DISPOSITION_DUPLICATE_OR_MISSING_LEAF');end if;by_uid(uid_text):=o;
  end loop;
  for i in 0..nodes.get_size-1 loop
   x:=treat(nodes.get(i) as json_object_t);
   if x.get_string('kind')='STOCK' then
    line_no:=line_no+1;uid_text:=x.get_string('uid');article_text:=x.get_string('article');unit_text:=x.get_string('base_uom');shipped:=RRL_STOCK_MATH.quantity(x.get_string('quantity'));
    if observed.get_size=0 then accepted:=shipped;missing:=0;refused:=0;damaged:=0;extra_no:=0;
    else
     if not by_uid.exists(uid_text) then raise_application_error(-20886,'STORE_DISPOSITION_COMPLETE_LEAF_COVERAGE_REQUIRED');end if;
     o:=by_uid(uid_text);accepted:=count_value(o,'accepted');missing:=count_value(o,'missing');refused:=count_value(o,'refused');damaged:=count_value(o,'damaged');extra_no:=count_value(o,'extra');
    end if;
    if shipped is null or shipped<=0 or accepted+missing+refused+damaged!=shipped then raise_application_error(-20886,'STORE_DISPOSITION_TOTAL_MISMATCH');end if;
    select BASE_SCALE into scale_no from RRL_STOCK_UOM_CONVERSION where ARTICUL=article_text and INPUT_UOM=unit_text and BASE_UOM=unit_text
     and POLICY_VERSION=(select max(POLICY_VERSION) from RRL_STOCK_UOM_CONVERSION where ARTICUL=article_text and INPUT_UOM=unit_text and BASE_UOM=unit_text);
    RRL_STOCK_MATH.assert_base(accepted,scale_no);RRL_STOCK_MATH.assert_base(missing,scale_no);RRL_STOCK_MATH.assert_base(refused,scale_no);RRL_STOCK_MATH.assert_base(damaged,scale_no);RRL_STOCK_MATH.assert_base(extra_no,scale_no);
    p_has_issue:=p_has_issue or missing>0 or refused>0 or damaged>0 or extra_no>0;
    line_json:=json_object_t();line_json.put('line_no',line_no);line_json.put('lot_uid',uid_text);line_json.put('article',article_text);line_json.put('base_uom',unit_text);
    line_json.put('shipped',RRL_STOCK_PLAN_HELPER.decimal_text(shipped));line_json.put('accepted',RRL_STOCK_PLAN_HELPER.decimal_text(accepted));line_json.put('missing',RRL_STOCK_PLAN_HELPER.decimal_text(missing));line_json.put('refused',RRL_STOCK_PLAN_HELPER.decimal_text(refused));line_json.put('damaged',RRL_STOCK_PLAN_HELPER.decimal_text(damaged));line_json.put('extra',RRL_STOCK_PLAN_HELPER.decimal_text(extra_no));p_lines.append(line_json);
   end if;
  end loop;
  if observed.get_size>0 and observed.get_size!=line_no then raise_application_error(-20886,'STORE_DISPOSITION_FOREIGN_LEAF');end if;
  reason_text:=m.get_string('case_note');
  if reason_text is not null and lengthb(reason_text)>2000 then raise_application_error(-20886,'STORE_CASE_NOTE_TOO_LONG');end if;
  if p_has_issue and trim(reason_text) is null then raise_application_error(-20886,'STORE_DISCREPANCY_REASON_REQUIRED');end if;
 exception when no_data_found then raise_application_error(-20886,'STORE_DISPOSITION_BASE_POLICY_REQUIRED');
 end;
 procedure declare_rows(p_operation varchar2,p_lines json_array_t,p_has_issue boolean,r in out nocopy json_array_t) is x json_object_t;
  procedure obligation(p_index number,p_kind varchar2,p_qty varchar2) is
  begin if nonnegative(p_qty)>0 then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STORE_DELIVERY_OBLIGATION',p_operation||':'||RRL_STOCK_PLAN_HELPER.decimal_text(p_index)||':'||p_kind);end if;end;
 begin
  if p_has_issue then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STORE_DISCREPANCY_CASE',p_operation);end if;
  for i in 0..p_lines.get_size-1 loop x:=treat(p_lines.get(i) as json_object_t);
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STORE_RECEIPT_LINE',p_operation||':'||RRL_STOCK_PLAN_HELPER.decimal_text(i+1));
   obligation(i+1,'MISSING_INVESTIGATION',x.get_string('missing'));obligation(i+1,'REFUSED_RETURN_DECISION',x.get_string('refused'));obligation(i+1,'DAMAGED_RETURN_DECISION',x.get_string('damaged'));obligation(i+1,'EXCESS_REVIEW',x.get_string('extra'));
  end loop;
 end;
 procedure persist(p_operation varchar2,p_domain json_object_t,p_actor varchar2,p_result out json_array_t) is
  lines json_array_t:=p_domain.get_array('disposition');x json_object_t;line_no number;uid_text varchar2(200);article_text varchar2(160);unit_text varchar2(20);shipped number;accepted number;missing number;refused number;damaged number;extra_no number;load_op varchar2(100):=p_domain.get_string('load_operation_id');addr_text varchar2(255):=p_domain.get_string('store_address');reason_text varchar2(2000):=p_domain.get_string('case_note');
  procedure obligation(p_kind varchar2,p_qty number) is
  begin if p_qty>0 then insert into RRL_STORE_DELIVERY_OBLIGATION(CASE_ID,LINE_NO,KIND,BASE_QTY,BASE_UOM)values(p_operation,line_no,p_kind,p_qty,unit_text);end if;end;
 begin
  if p_domain.get_boolean('has_discrepancy') then
   insert into RRL_STORE_DISCREPANCY_CASE(CASE_ID,LOAD_OPERATION_ID,STORE_ADDR,REASON_TEXT,REPORTED_BY)values(p_operation,load_op,addr_text,reason_text,p_actor);
  end if;
  p_result:=json_array_t();
  for i in 0..lines.get_size-1 loop
   x:=treat(lines.get(i) as json_object_t);line_no:=x.get_number('line_no');uid_text:=x.get_string('lot_uid');article_text:=x.get_string('article');unit_text:=x.get_string('base_uom');
   shipped:=RRL_STOCK_MATH.quantity(x.get_string('shipped'));accepted:=nonnegative(x.get_string('accepted'));missing:=nonnegative(x.get_string('missing'));refused:=nonnegative(x.get_string('refused'));damaged:=nonnegative(x.get_string('damaged'));extra_no:=nonnegative(x.get_string('extra'));
   insert into RRL_STORE_RECEIPT_LINE(OPERATION_ID,LINE_NO,LOT_UID,ARTICLE,BASE_UOM,SHIPPED_BASE_QTY,ACCEPTED_BASE_QTY,MISSING_BASE_QTY,REFUSED_BASE_QTY,DAMAGED_BASE_QTY,REPORTED_EXTRA_BASE_QTY)
    values(p_operation,line_no,uid_text,article_text,unit_text,shipped,accepted,missing,refused,damaged,extra_no);
   obligation('MISSING_INVESTIGATION',missing);obligation('REFUSED_RETURN_DECISION',refused);obligation('DAMAGED_RETURN_DECISION',damaged);obligation('EXCESS_REVIEW',extra_no);
   x.put('accepted_quantity',x.get_string('accepted'));p_result.append(x);
  end loop;
 end;
end;
/
