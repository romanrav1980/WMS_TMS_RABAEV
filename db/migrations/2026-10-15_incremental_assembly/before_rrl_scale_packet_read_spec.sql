create or replace package RRL_SCALE_PACKET_READ authid definer as
 function utc_stamp(p_text varchar2)return timestamp with time zone;
 function validate_json(p_source clob,p_capacity number,p_resolution number,
  p_expected_basis varchar2 default 'GROSS',p_sample_field varchar2 default 'gross_weight_kg')return clob;
end;
/
