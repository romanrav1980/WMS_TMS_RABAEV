create or replace package body RRL_SCALE_PACKET_READ as
 function utc_stamp(p_text varchar2)return timestamp with time zone is
 begin
  if p_text is null or not regexp_like(p_text,'^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}[.][0-9]{6}[+]00:00$','c')then raise_application_error(-20886,'SCALE_UTC_TIMESTAMP_REQUIRED');end if;
  return to_timestamp_tz(p_text,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM');
 exception when others then
  if sqlcode=-20886 then raise;end if;
  raise_application_error(-20886,'SCALE_VALID_UTC_TIMESTAMP_REQUIRED');
 end;
 function validate_packet(p_source clob,p_capacity number,p_resolution number,
  p_expected_basis varchar2,p_sample_field varchar2,p_require_zero boolean)return clob is
  j json_object_t;result_json json_object_t:=json_object_t();samples json_array_t;x json_object_t;
  minimum number;maximum number;last_weight number;offset_no number;previous_offset number:=-1;first_offset number;span_ms number;
  zero_weight number;zero_text varchar2(30);measured_at timestamp with time zone;zero_at timestamp with time zone;now_at timestamp with time zone:=systimestamp;
 begin
  if p_source is null or dbms_lob.getlength(p_source)>32000 then raise_application_error(-20881,'SCALE_PACKET_BOUND_32000');end if;
  if p_capacity is null or p_resolution is null or p_resolution<=0 or p_capacity<p_resolution then raise_application_error(-20886,'SCALE_RESOLUTION_CAPACITY_INVALID');end if;
  if p_expected_basis is null or p_expected_basis not in('GROSS','NET')or p_sample_field is null or p_sample_field not in('gross_weight_kg','weight_kg')then raise_application_error(-20886,'SCALE_EXPLICIT_BASIS_REQUIRED');end if;
  RRL_STOCK_MATH.assert_base(p_capacity,9);RRL_STOCK_MATH.assert_base(p_resolution,9);
  j:=json_object_t.parse(p_source);
  if p_require_zero then
  if j.get_string('unit')is null or j.get_string('unit')!='KG'or j.get_string('basis')is null or j.get_string('basis')!=p_expected_basis
   or not j.has('zero_confirmed')or j.get_string('preset_tare_kg')is null or j.get_string('preset_tare_kg')!='0'
   then raise_application_error(-20886,'SCALE_KG_GROSS_ZERO_PRESET_REQUIRED');end if;
  if j.get_boolean('zero_confirmed')then null;else raise_application_error(-20886,'SCALE_ZERO_CONFIRMATION_REQUIRED');end if;
  measured_at:=utc_stamp(j.get_string('measured_at'));zero_at:=utc_stamp(j.get_string('zero_check_at'));
  if measured_at>now_at+numtodsinterval(2,'SECOND')or measured_at<now_at-numtodsinterval(30,'SECOND')
   or zero_at>measured_at or zero_at<measured_at-numtodsinterval(600,'SECOND')then raise_application_error(-20886,'SCALE_FRESH_ZERO_AND_MEASUREMENT_REQUIRED');end if;
  zero_text:=j.get_string('zero_check_kg');if substr(zero_text,1,1)='-'then zero_text:=substr(zero_text,2);end if;
  if regexp_like(zero_text,'^0{1,18}([.]0{1,9})?$','c')then zero_weight:=0;else zero_weight:=RRL_STOCK_MATH.quantity(zero_text);end if;
  if zero_weight>p_resolution then raise_application_error(-20886,'SCALE_ZERO_CHECK_OUTSIDE_RESOLUTION');end if;
  else
  if j.get_string('unit')is null or j.get_string('unit')!='KG'or j.get_string('basis')is null or j.get_string('basis')!='GROSS'
   or j.get_string('preset_tare_kg')is null or j.get_string('preset_tare_kg')!='0'
   or not j.has('tare_mode_clear')or not j.has('quality_confirmed')then
   raise_application_error(-20886,'ASSEMBLY_GROSS_QUALITY_NO_TARE_REQUIRED');end if;
  if j.get_boolean('tare_mode_clear')and j.get_boolean('quality_confirmed')then null;else
   raise_application_error(-20886,'ASSEMBLY_GROSS_QUALITY_NO_TARE_REQUIRED');end if;
  measured_at:=utc_stamp(j.get_string('measured_at'));
  if measured_at>systimestamp+numtodsinterval(2,'SECOND')or measured_at<systimestamp-numtodsinterval(30,'SECOND')then
   raise_application_error(-20886,'ASSEMBLY_FRESH_MEASUREMENT_REQUIRED');end if;
  end if;
  if not j.has('samples')or not j.get('samples').is_array then raise_application_error(-20886,'SCALE_SAMPLE_ARRAY_REQUIRED');end if;samples:=j.get_array('samples');
  if samples.get_size<5 or samples.get_size>25 then raise_application_error(-20881,'SCALE_SAMPLE_BOUND_5_25');end if;
  for i in 0..samples.get_size-1 loop
   x:=treat(samples.get(i)as json_object_t);offset_no:=x.get_number('offset_ms');last_weight:=RRL_STOCK_MATH.quantity(x.get_string(p_sample_field));
   if offset_no is null or offset_no!=trunc(offset_no)or offset_no<0 or offset_no>10000 or offset_no<=previous_offset or last_weight>p_capacity or mod(last_weight,p_resolution)!=0 then raise_application_error(-20886,'SCALE_SAMPLE_ORDER_OR_CAPACITY_INVALID');end if;
   if i=0 then first_offset:=offset_no;minimum:=last_weight;maximum:=last_weight;end if;
   minimum:=least(minimum,last_weight);maximum:=greatest(maximum,last_weight);previous_offset:=offset_no;
  end loop;
  span_ms:=previous_offset-first_offset;
  if first_offset!=0 or span_ms<2000 or maximum-minimum>p_resolution then raise_application_error(-20886,'SCALE_STABLE_WINDOW_REQUIRED');end if;
  result_json.put('weight_kg',RRL_STOCK_PLAN_HELPER.decimal_text(last_weight));result_json.put('basis',p_expected_basis);
  result_json.put('sample_min_kg',RRL_STOCK_PLAN_HELPER.decimal_text(minimum));result_json.put('sample_max_kg',RRL_STOCK_PLAN_HELPER.decimal_text(maximum));
  result_json.put('sample_count',samples.get_size);result_json.put('span_ms',span_ms);
  result_json.put('measured_at',j.get_string('measured_at'));
  if p_require_zero then result_json.put('zero_check_at',j.get_string('zero_check_at'));end if;
  return result_json.to_clob;
 end;
 function validate_json(p_source clob,p_capacity number,p_resolution number,
  p_expected_basis varchar2 default 'GROSS',p_sample_field varchar2 default 'gross_weight_kg')return clob is
 begin return validate_packet(p_source,p_capacity,p_resolution,p_expected_basis,p_sample_field,true);end;
 function validate_series_json(p_source clob,p_capacity number,p_resolution number)return clob is
 begin return validate_packet(p_source,p_capacity,p_resolution,'GROSS','weight_kg',false);end;
end;
/
