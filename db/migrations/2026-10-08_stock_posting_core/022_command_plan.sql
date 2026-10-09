-- Private compiler: derives all anchors from a typed command, never from caller-supplied lock lists.
create or replace package RRL_STOCK_COMMAND_PLAN authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_move(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob);
end;
/
create or replace package body RRL_STOCK_COMMAND_PLAN as
 procedure compile_move(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob) is
  v_doc json_object_t;v_lines json_array_t;v_line json_object_t;
  v_policies json_array_t:=json_array_t();v_resources json_array_t:=json_array_t();
  v_seen varchar2(32767);v_uid varchar2(200);v_article varchar2(160);v_from varchar2(60);v_to varchar2(60);
  procedure policy(p_kind varchar2,p_id varchar2) is v json_object_t:=json_object_t();
  begin
   v.put('key_hex',rawtohex(RRL_STOCK_LOCK_API.resource_key(p_kind,p_id)));v.put('mode',4);v_policies.append(v);
  end;
  procedure anchor(p_rank number,p_kind varchar2,p_id varchar2) is v json_object_t:=json_object_t();
  begin
   v.put('rank',p_rank);v.put('key_hex',rawtohex(RRL_STOCK_LOCK_API.resource_key(p_kind,p_id)));v_resources.append(v);
  end;
  procedure check_text(p_obj json_object_t,p_name varchar2,p_max number,p_value out varchar2) is v json_element_t;
  begin
   v:=p_obj.get(p_name);
   if v is null or not v.is_string then raise_application_error(-20880,'COMMAND_FIELD_INVALID: '||p_name); end if;
   p_value:=p_obj.get_string(p_name);
   if p_value is null or length(p_value)>p_max or instr(p_value,chr(0))>0 then
    raise_application_error(-20880,'COMMAND_FIELD_INVALID: '||p_name);
   end if;
  end;
 begin
  v_doc:=json_object_t.parse(p_request);v_doc.on_error(1);
  v_lines:=v_doc.get_array('lines');
  if v_lines is null or v_lines.get_size<1 or v_lines.get_size>200 then
   raise_application_error(-20881,'COMMAND_LINES_INVALID');
  end if;
  -- RELEASE precedes all row locks; config writers must take matching exclusive fences.
  policy('RELEASE','STOCK');policy('CONFIG','WAREHOUSE');anchor(10,'OP',p_operation);
  anchor(70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  for i in 0..v_lines.get_size-1 loop
   v_line:=treat(v_lines.get(i) as json_object_t);
   if v_line is null then raise_application_error(-20881,'COMMAND_LINE_NOT_OBJECT'); end if;
   v_line.on_error(1);
   check_text(v_line,'uid',200,v_uid);check_text(v_line,'article',160,v_article);
   check_text(v_line,'source_cell',60,v_from);check_text(v_line,'target_cell',60,v_to);
   policy('SKU',v_article);policy('CELL',v_from);policy('CELL',v_to);
   anchor(30,'HU',v_uid);anchor(50,'STOCK',v_uid);anchor(40,'SLOT','CELL:'||v_from);anchor(40,'SLOT','CELL:'||v_to);
  end loop;
  p_policies:=v_policies.to_clob;p_resources:=v_resources.to_clob;
 end;
end;
/
